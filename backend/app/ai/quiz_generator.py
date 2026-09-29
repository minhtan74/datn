"""PHASE 9 — AI Quiz Generator.

Lesson/tài liệu -> ngữ cảnh -> (LLM fine-tuned / Gemini / heuristic) -> JSON quiz
-> validate + repair + khử trùng lặp. KHÔNG tự lưu: giảng viên phải duyệt.
"""
from __future__ import annotations

import json
import re

from sqlalchemy.orm import Session

from app.ai import model_manager
from app.ai.rag import ingest, retriever
from app.core.database import q_all, q_one

# Tên tiếng Việt của các mức độ khó (dùng trong prompt)
DIFF_VI = {"easy": "dễ", "medium": "trung bình", "hard": "khó"}

# Chỉ dẫn hệ thống cho LLM: chỉ trả về JSON đúng schema, câu hỏi phải bám sát ngữ liệu
_SYSTEM = (
    "Bạn là công cụ sinh đề trắc nghiệm của StudyOnline. Trả về DUY NHẤT một đối tượng JSON "
    "hợp lệ theo schema: "
    '{"questions":[{"question","options":{"A","B","C","D"},"correct_answer","explanation","difficulty","topic"}]}. '
    "correct_answer là một trong A/B/C/D. Không thêm bất kỳ chữ nào ngoài JSON. "
    "Câu hỏi phải bám sát NGỮ LIỆU được cung cấp, không bịa kiến thức ngoài ngữ liệu."
)


# Lỗi nghiệp vụ khi sinh quiz (router chuyển thành mã 422 kèm thông báo)
class QuizGenError(Exception):
    pass


# ── ngữ cảnh ───────────────────────────────────────────────────────────────

# Ngữ liệu cho câu hỏi ôn tập chương: gom tài liệu của từng bài trong chương (chia đều số đoạn),
# không có thì tìm trong tài liệu toàn khóa theo tên chương + tên các bài
def _build_chapter_context(db: Session, course_id: int, chapter_id: int) -> tuple[str, str, list[dict]]:
    chapter = q_one(
        db, "SELECT id, chapter_name FROM chapters WHERE id = :id AND course_id = :c",
        id=chapter_id, c=course_id,
    )
    if not chapter:
        raise QuizGenError("Chương không tồn tại trong khóa học này.")
    lessons = q_all(
        db,
        "SELECT id, title, description FROM lessons WHERE chapter_id = :ch "
        "ORDER BY order_index ASC, id ASC",
        ch=chapter_id,
    )
    name = chapter["chapter_name"]
    # Phần đầu ngữ liệu: tên chương + danh sách bài (kèm mô tả nếu có)
    header = "\n".join(
        [f"Chương: {name}"]
        + [f"- {l['title']}: {l['description']}" if l.get("description") else f"- {l['title']}" for l in lessons]
    )

    chunks: list[dict] = []
    if lessons:
        per_lesson = max(2, 8 // len(lessons))
        for l in lessons:
            # Bài có PDF đính kèm nhưng chưa nạp vào RAG -> nạp luôn (giống AI Tutor)
            ingest.ensure_lesson_document(db, l["id"])
            chunks += retriever.retrieve(
                db, l["title"], course_id=course_id, lesson_id=l["id"], lesson_only=True, k=per_lesson
            )
        chunks = chunks[:8]
    if not chunks:
        query = " ".join([name] + [l["title"] for l in lessons])
        chunks = retriever.retrieve(db, query, course_id=course_id, k=6)

    if not chunks:
        # Không có tài liệu RAG: chỉ dùng được khi các bài có mô tả làm ngữ liệu
        if any(l.get("description") for l in lessons):
            return header, name, []
        raise QuizGenError(
            "Chương chưa có tài liệu hoặc mô tả bài học để sinh câu hỏi. Hãy thêm mô tả bài học "
            "hoặc tải tài liệu trong mục \"Tài liệu AI Tutor\" trước."
        )
    body = "\n\n".join(c["content"] for c in chunks)
    return f"{header}\n\n{body}".strip(), name, chunks


# Tạo ngữ liệu cho việc sinh câu hỏi: lấy tiêu đề bài/khóa làm truy vấn, rồi truy hồi 6 đoạn tài liệu liên quan
def _build_context(db: Session, course_id: int, lesson_id: int | None) -> tuple[str, str, list[dict]]:
    course = q_one(db, "SELECT id, title FROM courses WHERE id = :id", id=course_id)
    if not course:
        raise QuizGenError("Khóa học không tồn tại.")

    if lesson_id:
        lesson = q_one(db, "SELECT id, title, description FROM lessons WHERE id = :id", id=lesson_id)
        if not lesson:
            raise QuizGenError("Bài học không tồn tại.")
        query = lesson["title"]
        header = f"Bài học: {lesson['title']}\n{lesson.get('description') or ''}".strip()
        topic_hint = lesson["title"]
    else:
        query = course["title"]
        header = f"Khóa học: {course['title']}"
        topic_hint = course["title"]

    # Dùng lại bộ truy hồi của RAG, tìm trong tài liệu của khóa (và bài, nếu có)
    chunks = retriever.retrieve(db, query, course_id=course_id, lesson_id=lesson_id, k=6)
    if not chunks:
        # chưa có tài liệu RAG -> dùng nội dung bài học / mô tả khóa
        if lesson_id and header:
            return header, topic_hint, []
        raise QuizGenError(
            "Khóa học chưa có tài liệu nào được lập chỉ mục. Hãy tải tài liệu trong mục "
            "\"Tài liệu AI Tutor\" trước, hoặc chọn một bài học đã có mô tả."
        )

    # Ghép tiêu đề + các đoạn tài liệu thành ngữ liệu
    body = "\n\n".join(c["content"] for c in chunks)
    return f"{header}\n\n{body}".strip(), topic_hint, chunks


# Tập câu hỏi đã có trong khóa (đã chuẩn hóa) để loại câu AI sinh trùng
def _existing_questions(db: Session, course_id: int) -> set[str]:
    rows = q_all(
        db,
        "SELECT q.content FROM questions q JOIN quizzes qz ON qz.id = q.quiz_id "
        "WHERE qz.course_id = :c",
        c=course_id,
    )
    return {_norm(r["content"]) for r in rows}


# Chuẩn hóa chuỗi để so trùng: bỏ khoảng trắng thừa, chuyển chữ thường
def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


# ── parse / validate ──────────────────────────────────────────────────────

# Tách đối tượng JSON từ output của LLM: bỏ ```json, tìm cặp { } cân bằng đầu tiên,
# parse lỗi thì thử lại sau khi bỏ dấu phẩy thừa trước } hoặc ]
def _extract_json(text: str) -> dict | None:
    text = re.sub(r"```(?:json)?", "", text or "").strip().strip("`").strip()
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                blob = text[start : i + 1]
                for attempt in (blob, re.sub(r",\s*([}\]])", r"\1", blob)):
                    try:
                        return json.loads(attempt)
                    except json.JSONDecodeError:
                        continue
                return None
    return None


# Kiểm tra từng câu LLM trả về: đủ nội dung, đủ 4 phương án, đáp án A–D, không trùng; lấy tối đa n câu
def _clean_questions(data: dict, *, n: int, difficulty: str, topic_hint: str,
                     seen: set[str]) -> list[dict]:
    raw = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for q in raw:
        if not isinstance(q, dict):
            continue
        content = str(q.get("question") or "").strip()
        opts = q.get("options") or {}
        if not content or not isinstance(opts, dict):
            continue
        A, B, C, D = (str(opts.get(k) or "").strip() for k in ("A", "B", "C", "D"))
        if not all([A, B, C, D]):
            continue
        ca = str(q.get("correct_answer") or "").strip().upper()
        if ca not in {"A", "B", "C", "D"}:
            continue
        key = _norm(content)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "question": content,
                "options": {"A": A, "B": B, "C": C, "D": D},
                "correct_answer": ca,
                "explanation": str(q.get("explanation") or "").strip(),
                "difficulty": (str(q.get("difficulty") or difficulty).strip().lower()
                               if str(q.get("difficulty") or "").strip().lower() in DIFF_VI else difficulty),
                "topic": str(q.get("topic") or topic_hint).strip()[:100],
            }
        )
        if len(out) >= n:
            break
    return out


# ── heuristic (khi không có LLM): câu hỏi ĐIỀN CHỖ TRỐNG từ tài liệu ───────

# Các mẫu tìm "thuật ngữ khóa" trong câu: sau các cụm định nghĩa ("là", "gọi là"...), trong ngoặc kép,
# hoặc từ trông giống code/tên riêng viết hoa
_KEY_AFTER = re.compile(
    r"(?:là|gọi là|được gọi là|dùng để|nghĩa là|viết tắt của|có tên)\s+([“\"']?[\wÀ-ỹ][\wÀ-ỹ .()/+-]{2,40}?[”\"']?)(?=[,.;:]|\s+(?:và|hoặc|khi|nếu|để|trong|của)\b|$)",
    re.IGNORECASE,
)
_QUOTED = re.compile(r"[“\"']([\wÀ-ỹ][\wÀ-ỹ .()/+-]{1,40})[”\"']")
_CODEISH = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{2,}(?:\(\))?|[A-Z]{2,}\d*)\b")


# Tách ngữ liệu thành câu, chỉ giữ câu dài 40–220 ký tự, bắt đầu bằng chữ hoa (câu hoàn chỉnh)
def _sentences(text: str) -> list[str]:
    out = []
    for s in re.split(r"(?<=[.!?…])\s+|\n+", text):
        s = re.sub(r"\s+", " ", s).strip()
        if 40 <= len(s) <= 220 and s[:1].isalpha() and s[:1].upper() == s[:1] \
                and not s.lower().startswith(("bài học", "khóa học", "tài liệu")):
            out.append(s)
    return out


# Tìm thuật ngữ khóa của câu theo thứ tự ưu tiên: cụm định nghĩa -> ngoặc kép -> từ dạng code dài nhất
def _key_term(sentence: str) -> str | None:
    for rx in (_KEY_AFTER, _QUOTED):
        m = rx.search(sentence)
        if m:
            t = m.group(1).strip(" \"'“”.")
            if 2 <= len(t) <= 40:
                return t
    codes = [m.group(1) for m in _CODEISH.finditer(sentence)]
    codes = [c for c in codes if c.lower() not in {"html", "the", "và", "các"}]
    if codes:
        return max(codes, key=len)
    return None


# Sinh câu hỏi không cần LLM: che thuật ngữ khóa bằng "______", đáp án nhiễu là các thuật ngữ khác
# có độ dài gần giống, xoay vòng vị trí đáp án đúng qua A/B/C/D
def _heuristic(context: str, *, n: int, difficulty: str, topic_hint: str,
               seen: set[str]) -> list[dict]:
    sents = _sentences(context)
    pairs: list[tuple[str, str]] = []
    for s in sents:
        kt = _key_term(s)
        if kt and kt.lower() in s.lower():
            pairs.append((s, kt))

    pool = list({kt for _, kt in pairs})
    letters = ["A", "B", "C", "D"]
    out: list[dict] = []
    for i, (s, kt) in enumerate(pairs):
        blanked = re.sub(re.escape(kt), "______", s, count=1, flags=re.IGNORECASE)
        key = _norm(blanked)
        if key in seen:
            continue
        distract = [p for p in pool if p.lower() != kt.lower()]
        distract.sort(key=lambda p: abs(len(p) - len(kt)))
        distract = distract[:3]
        while len(distract) < 3:
            distract.append(f"(không có trong tài liệu {len(distract)})")
        opts = distract + [kt]
        pos = i % 4
        opts.insert(pos, opts.pop())  # đưa đáp án đúng về vị trí pos
        seen.add(key)
        out.append(
            {
                "question": f"Điền từ/cụm từ thích hợp vào chỗ trống: “{blanked}”",
                "options": dict(zip(letters, opts)),
                "correct_answer": letters[pos],
                "explanation": f"Theo tài liệu khóa học: {s}",
                "difficulty": difficulty,
                "topic": topic_hint[:100],
            }
        )
        if len(out) >= n:
            break
    return out


# ── API chính ─────────────────────────────────────────────────────────────

# Mô tả từng mức độ khó cho LLM để câu hỏi thật sự khác nhau về độ khó (không chỉ khác nhãn)
DIFF_GUIDE = {
    "easy": "nhận biết/ghi nhớ: hỏi trực tiếp định nghĩa, khái niệm, sự kiện có sẵn trong ngữ liệu",
    "medium": "thông hiểu/vận dụng: giải thích, so sánh đơn giản, áp dụng kiến thức vào ví dụ quen thuộc",
    "hard": "phân tích/vận dụng cao: tình huống mới, suy luận nhiều bước, phân biệt các khái niệm dễ nhầm",
}
# Tổng số câu tối đa cho 1 lần sinh khi phân bổ nhiều mức độ khó
MAX_TOTAL = 30


# Chỉ dẫn cho lượt AI tự giải lại đề (không cho biết đáp án đã đánh) để phát hiện câu đánh sai đáp án.
# Bắt suy luận ("work") TRƯỚC rồi mới chọn đáp án: thử thực tế, nếu để "answer" đứng trước thì model
# chốt đáp án rồi mới biện minh và bỏ lọt câu sai (câu đọc code vòng lặp lồng: 0/3 lần bắt được -> 4/4).
_VERIFY_SYSTEM = (
    "Bạn là giáo viên chấm đề trắc nghiệm. Với MỖI câu: trước tiên tự suy luận từng bước trong trường \"work\" "
    "(với đoạn code: chạy tay từng dòng, ghi giá trị biến sau mỗi vòng lặp), CHƯA nhìn các phương án; "
    "sau đó mới đối chiếu kết quả với các phương án và chọn đáp án. "
    'Trả về DUY NHẤT JSON: {"answers":[{"i":<số thứ tự câu>,"work":"<các bước suy luận>","answer":"A|B|C|D","reason":"<kết luận 1 câu>"}]}'
)


# AI giải lại các câu vừa sinh mà không biết đáp án. Khớp -> verified; lệch -> gắn verify {answer, reason}
# để giảng viên xem lại. Lỗi gọi model / JSON hỏng thì bỏ qua (không chặn việc sinh câu hỏi).
def _verify(context: str, questions: list[dict]) -> None:
    listing = "\n\n".join(
        f"Câu {i}: {q['question']}\n" + "\n".join(f"{k}. {v}" for k, v in q["options"].items())
        for i, q in enumerate(questions)
    )
    text = model_manager.generate(
        _VERIFY_SYSTEM,
        f"NGỮ LIỆU:\n{context}\n\nĐỀ CẦN GIẢI:\n{listing}",
        max_tokens=min(8192, 300 + 450 * len(questions)),  # phần "work" khá dài
    )
    data = _extract_json(text)
    answers = data.get("answers") if isinstance(data, dict) else None
    if not isinstance(answers, list):
        return
    for a in answers:
        if not isinstance(a, dict):
            continue
        try:
            i = int(a.get("i"))
        except (TypeError, ValueError):
            continue
        ans = str(a.get("answer") or "").strip().upper()[:1]
        if not 0 <= i < len(questions) or ans not in {"A", "B", "C", "D"}:
            continue
        q = questions[i]
        if ans == q["correct_answer"]:
            q["verified"] = ans  # lưu đáp án AI giải ra để giao diện so với đáp án hiện tại
        else:
            q["verify"] = {"answer": ans, "reason": str(a.get("reason") or "").strip()[:500]}


# Sinh 1 lô n câu ở đúng 1 mức độ khó (LLM hoặc heuristic); seen dùng chung để các lô không trùng nhau
def _generate_batch(context: str, topic_hint: str, *, n: int, difficulty: str,
                    seen: set[str], provider: str) -> list[dict]:
    if provider == "stub":
        # Heuristic điền chỗ trống: chỉ gắn nhãn độ khó, không điều chỉnh được độ khó thật
        return _heuristic(context, n=n, difficulty=difficulty, topic_hint=topic_hint, seen=seen)

    # Có LLM: tạo hướng dẫn (số câu, độ khó + mô tả mức, chủ đề) + ngữ liệu làm prompt
    instr = (
        f"Tạo {n} câu hỏi trắc nghiệm mức {DIFF_VI[difficulty]} ({DIFF_GUIDE[difficulty]}) về \"{topic_hint}\", "
        "mỗi câu 4 lựa chọn A-D, một đáp án đúng và một giải thích ngắn. Trả JSON schema StudyOnline."
    )
    user = f"Hướng dẫn: {instr}\n\nNGỮ LIỆU:\n{context}"
    # ~230 token/câu (JSON tiếng Việt: question + 4 lựa chọn + explanation) + đệm.
    # Cố định 1400 sẽ bị cắt cụt JSON khi n lớn (vd n=20 cần ~4900 token) -> parse lỗi.
    max_tokens = min(8192, 300 + 230 * n)
    # Gọi LLM tối đa 2 lần; lần 2 nhắc thêm "chỉ trả về JSON" nếu lần 1 không parse được
    for extra in ("", "\n\nLƯU Ý: chỉ trả về JSON hợp lệ, không giải thích thêm."):
        text = model_manager.generate(_SYSTEM, user + extra, max_tokens=max_tokens)
        data = _extract_json(text)
        questions = _clean_questions(data, n=n, difficulty=difficulty, topic_hint=topic_hint, seen=seen) if data else []
        if questions:
            # Lô được yêu cầu ở mức nào thì gắn đúng mức đó (model đôi khi tự gắn nhãn khác)
            for q in questions:
                q["difficulty"] = difficulty
            # AI tự giải lại để bắt câu đánh sai đáp án (hay gặp ở câu khó / câu đọc code)
            _verify(context, questions)
            return questions
    return []


# Hàm chính: tạo ngữ liệu -> sinh từng lô theo mức độ khó (LLM hoặc heuristic nếu offline) -> trả bản nháp.
# mix = {"easy": x, "medium": y, "hard": z} để phân bổ độ khó; không có mix thì sinh n câu cùng 1 mức.
def generate(db: Session, *, course_id: int, lesson_id: int | None,
             n: int, difficulty: str, chapter_id: int | None = None,
             mix: dict[str, int] | None = None) -> dict:
    if mix:
        plan = [(lvl, max(0, int(mix.get(lvl) or 0))) for lvl in ("easy", "medium", "hard")]
        plan = [(lvl, k) for lvl, k in plan if k > 0]
        if not plan:
            raise QuizGenError("Cần ít nhất 1 câu trong phân bổ độ khó.")
        if sum(k for _, k in plan) > MAX_TOTAL:
            raise QuizGenError(f"Tổng số câu tối đa là {MAX_TOTAL}.")
        plan = [(lvl, min(k, 20)) for lvl, k in plan]
    else:
        plan = [(difficulty if difficulty in DIFF_VI else "medium", max(1, min(int(n), 20)))]

    # Có chapter_id -> sinh câu hỏi ôn tập bao quát cả chương
    if chapter_id:
        context, topic_hint, chunks = _build_chapter_context(db, course_id, chapter_id)
    else:
        context, topic_hint, chunks = _build_context(db, course_id, lesson_id)
    seen = _existing_questions(db, course_id)
    provider = model_manager.active_provider()

    # Sinh lần lượt từng mức; mức nào lỗi thì bỏ qua, vẫn trả các mức sinh được (meta báo thiếu)
    questions: list[dict] = []
    distribution: dict[str, int] = {}
    for lvl, k in plan:
        batch = _generate_batch(context, topic_hint, n=k, difficulty=lvl, seen=seen, provider=provider)
        distribution[lvl] = len(batch)
        questions += batch
    gen_by = "heuristic" if provider == "stub" else f"{provider}:{model_manager.info()['model']}"

    if not questions:
        raise QuizGenError(
            "Không sinh được câu hỏi từ ngữ liệu hiện có."
            if provider == "stub"
            else "Model không trả về JSON hợp lệ sau 2 lần thử. Vui lòng thử lại hoặc giảm số câu."
        )

    return {
        "questions": questions,
        "meta": {
            "generated_by": gen_by,
            "requested": sum(k for _, k in plan),
            "returned": len(questions),
            "difficulty": plan[0][0] if len(plan) == 1 else "mixed",
            # Số câu yêu cầu / nhận được theo từng mức độ khó
            "distribution_requested": dict(plan),
            "distribution": distribution,
            # Kết quả AI tự giải lại: số câu khớp đáp án / số câu AI giải ra đáp án khác (cần giảng viên xem)
            "verification": {
                "verified": sum(1 for q in questions if q.get("verified")),
                "flagged": sum(1 for q in questions if q.get("verify")),
            },
            "context_chunks": len(chunks),
            "topic": topic_hint,
        },
    }
