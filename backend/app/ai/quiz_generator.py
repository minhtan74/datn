"""PHASE 9 — AI Quiz Generator.

Lesson/tài liệu -> ngữ cảnh -> (LLM fine-tuned / Gemini / heuristic) -> JSON quiz
-> validate + repair + khử trùng lặp. KHÔNG tự lưu: giảng viên phải duyệt.
"""
from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import BoundedSemaphore
from typing import Callable

from sqlalchemy.orm import Session

from app.ai import model_manager
from app.ai.rag import document_loader, ingest, retriever
from app.core.database import q_all, q_one
from app.core.media import resolve_upload_path

# Tên tiếng Việt của các mức độ khó (dùng trong prompt)
DIFF_VI = {"easy": "dễ", "medium": "trung bình", "hard": "khó"}

# Chỉ dẫn hệ thống cho LLM: chỉ trả về JSON đúng schema, câu hỏi phải bám sát ngữ liệu
_SYSTEM = (
    "Bạn là công cụ sinh đề trắc nghiệm của StudyOnline. Trả về DUY NHẤT một đối tượng JSON "
    "hợp lệ theo schema: "
    '{"questions":[{"question","options":{"A","B","C","D"},"correct_answer","explanation","difficulty","topic",'
    '"objectives","evidence","knowledge_lesson_id"}]}. '
    "knowledge_lesson_id là mã bài học cung cấp trong NGỮ LIỆU mà câu hỏi kiểm tra; "
    "chỉ chọn một mã trong danh sách, dùng null nếu chưa xác định rõ hoặc câu tổng hợp nhiều bài. "
    "correct_answer là một trong A/B/C/D; objectives là mảng số thứ tự các mục tiêu bài học mà câu hỏi liên quan "
    "(1 hoặc vài mục tiêu; [] nếu không có danh sách mục tiêu hoặc câu không gắn mục tiêu cụ thể); evidence là câu/cụm trích NGUYÊN VĂN từ NGỮ LIỆU (tối đa 200 ký tự) "
    "làm căn cứ cho đáp án đúng. Không thêm bất kỳ chữ nào ngoài JSON. "
    "Câu hỏi phải bám sát NGỮ LIỆU được cung cấp, không bịa kiến thức ngoài ngữ liệu. "
    "Mỗi câu phải đủ dữ kiện và chỉ có một đáp án đúng rõ ràng. Các phương án nhiễu phải hợp lý, "
    "xuất phát từ lỗi hiểu hoặc lỗi áp dụng thường gặp, tương đương về cách diễn đạt; "
    "không gợi đáp án bằng độ dài, từ khóa hay các phương án sai hiển nhiên. "
    "Không dùng mẹo đánh đố, câu chữ mơ hồ hoặc chi tiết vụn vặt để tăng độ khó. "
    "Tình huống có thể mới nhưng cách giải phải suy ra được từ ngữ liệu. "
    "Nếu ngữ liệu không đủ để tạo câu đạt yêu cầu, trả ít câu hơn; không cố tạo cho đủ số lượng."
)


# Lỗi nghiệp vụ khi sinh quiz (router chuyển thành mã 422 kèm thông báo)
class QuizGenError(Exception):
    pass


# ── mục tiêu bài học ───────────────────────────────────────────────────────

# Dòng tiêu đề phần mục tiêu: "Mục tiêu bài học", "Mục tiêu:", "Sau bài học này, học viên có thể:"...
_OBJ_HEAD = re.compile(
    r"^(?:#+\s*)?(?:mục tiêu(?: bài học| học tập| của bài(?: học)?)?"
    r"|sau (?:khi học xong |khi hoàn thành )?bài(?: học)?(?: này)?,? (?:học viên|bạn|người học) (?:có thể|sẽ)[^:]*)"
    r"\s*:?$",
    re.IGNORECASE,
)
# Dòng báo hết phần mục tiêu: tiêu đề mục đánh số ("1. Biến trong Python"), số La Mã, "Chương 2 / Phần II",
# hoặc dòng CHỈ gồm tên phần ("Nội dung", "Giới thiệu:") — mục tiêu bắt đầu bằng "Giới thiệu tên..." không bị cắt
_OBJ_END = re.compile(
    r"^(?:#+\s|\d+[.)]\s|\d+(?:\.\d+)+\.?\s|[IVX]+[.)]\s|(?:chương|phần)\s+(?:\d+|[IVX]+)\b"
    r"|(?:nội dung|giới thiệu|tóm tắt)(?: bài học| chính)?\s*:?$)",
    re.IGNORECASE,
)
_OBJ_BULLET = re.compile(r"^[-•*–▪●◦+]\s*")
_OBJ_NUM = re.compile(r"^\d+[.)]\s+")
MAX_OBJECTIVES = 10


# Mục tiêu là 1 câu ngắn; dài hơn mức này là đoạn văn nội dung
OBJ_MAX_LEN = 200
# Từ nối hay mở đầu câu văn nội dung, gần như không bao giờ mở đầu một mục tiêu bài học
_BODY_START = re.compile(
    r"^(?:để|nhưng|vì|do đó|khi|nếu|tuy|mặc dù|ngoài ra|như vậy|theo|trong|đây là|điều này|nói cách khác|ví dụ)\b",
    re.IGNORECASE,
)


# Mục tiêu bị coi là đoạn văn nội dung: câu dẫn kết thúc bằng ":", quá dài, gồm từ 2 câu trở lên,
# hoặc mở đầu bằng từ nối của câu văn ("Để hỗ trợ...", "Trong môi trường...")
def _looks_like_body(item: str) -> bool:
    return (
        item.endswith(":")
        or len(item) > OBJ_MAX_LEN
        or bool(re.search(r"[.!?]\s+[A-ZÀ-Ỹ]", item))
        or bool(_BODY_START.match(item))
    )


# Tách danh sách mục tiêu nằm ngay sau dòng "Mục tiêu bài học" trong văn bản tài liệu.
# B1: gom dòng — mục tiêu gạch đầu dòng (hoặc dòng thường, vì PDF hay mất ký hiệu bullet) kết thúc ở tiêu đề mục
#     kế tiếp ("1.2.1 ..."); mục tiêu đánh số "1. ..." lấy hết các dòng đánh số; dòng bắt đầu bằng chữ thường là
#     phần PDF tự ngắt xuống dòng của mục tiêu trước -> nối lại.
# B2: lọc — PDF mất bullet thì đoạn văn ngay sau phần mục tiêu trông giống mục tiêu: dừng ở mục đầu tiên trông
#     như đoạn văn (_looks_like_body).
def _parse_objectives(text: str) -> list[str]:
    lines = [l.strip() for l in (text or "").splitlines()]
    start = next((i for i, l in enumerate(lines) if _OBJ_HEAD.match(l)), None)
    if start is None:
        return []
    items: list[str] = []
    numbered = None
    for line in lines[start + 1:]:
        if not line:
            if items:
                break
            continue
        is_num = bool(_OBJ_NUM.match(line))
        if numbered is None:
            numbered = is_num
        if items and line[0].islower():
            items[-1] += " " + line
        elif numbered and is_num:
            items.append(_OBJ_NUM.sub("", line))
        elif not numbered and (_OBJ_BULLET.match(line) or not _OBJ_END.match(line)):
            items.append(_OBJ_BULLET.sub("", line))
        else:
            break
        if len(items) > MAX_OBJECTIVES:
            break

    out: list[str] = []
    for item in items[:MAX_OBJECTIVES]:
        item = item.strip()
        if _looks_like_body(item):
            break
        out.append(item.strip(" .;"))
    return [o for o in out if len(o) >= 5]


# Tài liệu bài học dài tối đa bao nhiêu ký tự thì đưa NGUYÊN VĂN vào prompt (tài liệu mẫu mỗi bài ~2–3 nghìn ký tự);
# dài hơn mới phải truy hồi từng đoạn liên quan. Ôn tập chương được gấp rưỡi vì gồm nhiều bài.
FULL_DOC_MAX = 12000


# Tài liệu của 1 bài học + mục tiêu bài học. Đọc file đã nạp RAG của bài, hoặc PDF đính kèm bài học;
# tài liệu không có phần "Mục tiêu bài học" thì thử tìm trong mô tả bài. Không có -> ("", [])
def _lesson_material(db: Session, lesson_id: int) -> tuple[str, list[str]]:
    lesson = q_one(db, "SELECT document_url, description FROM lessons WHERE id = :id", id=lesson_id) or {}
    files = [
        (d["file_path"], d["file_type"])
        for d in q_all(db, "SELECT file_path, file_type FROM documents WHERE lesson_id = :l ORDER BY id", l=lesson_id)
    ]
    attached = resolve_upload_path(lesson.get("document_url"))
    if attached:
        ext = os.path.splitext(attached)[1].lstrip(".").lower()
        files.append((attached, ext if ext in ("pdf", "docx", "txt") else "pdf"))
    text = ""
    for path, file_type in files:
        if not path or not os.path.exists(path):
            continue
        try:
            pages, _ = document_loader.extract(path, file_type)
        except Exception:  # noqa: BLE001 — file hỏng thì thử nguồn khác
            continue
        text = "\n".join(t for _, t in pages).strip()
        if text:
            break
    objectives = _parse_objectives(text) or _parse_objectives(lesson.get("description") or "")
    return text, objectives


# Tách từ để so khớp căn cứ: chữ thường, bỏ dấu câu / ký hiệu code
def _words(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", (text or "").lower())


# Căn cứ AI trích có thật sự nằm trong tài liệu không: >= 85% số từ của căn cứ xuất hiện trong ngữ liệu
# (cho phép lệch nhẹ do PDF ngắt dòng / model sửa dấu câu, nhưng không chấp nhận căn cứ tự bịa)
def _grounded(evidence: str, context_words: set[str]) -> bool:
    words = [w for w in _words(evidence) if len(w) > 1]
    if len(words) < 3:
        return False
    return sum(w in context_words for w in words) / len(words) >= 0.85


# Bỏ các đoạn tài liệu trùng khi gom kết quả truy hồi của nhiều truy vấn
def _unique_chunks(chunks: list[dict]) -> list[dict]:
    seen: set = set()
    out = []
    for c in chunks:
        key = c.get("chunk_id") or c.get("content")
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


# ── ngữ cảnh ───────────────────────────────────────────────────────────────

# Ngữ liệu cho câu hỏi ôn tập chương: tài liệu các bài trong chương đủ ngắn thì dùng nguyên văn từng bài;
# dài thì gom đoạn liên quan của từng bài (chia đều số đoạn); không có thì tìm trong tài liệu toàn khóa
def _build_chapter_context(db: Session, course_id: int, chapter_id: int) -> tuple[str, str, list[dict], list[str]]:
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
    objectives: list[str] = []
    texts: list[tuple[str, str]] = []  # (tên bài, nguyên văn tài liệu bài)
    for l in lessons:
        # Bài có PDF đính kèm nhưng chưa nạp vào RAG -> nạp luôn (giống AI Tutor)
        ingest.ensure_lesson_document(db, l["id"])
        text, lesson_goals = _lesson_material(db, l["id"])
        if text:
            texts.append((l["title"], text))
        # Mục tiêu của chương = mục tiêu các bài trong chương, ghi kèm tên bài
        objectives += [f"{l['title']}: {o}" for o in lesson_goals]
    objectives = objectives[:15]

    if texts and sum(len(t) for _, t in texts) <= FULL_DOC_MAX * 3 // 2:
        body = "\n\n".join(f"=== Bài: {title} ===\n{text}" for title, text in texts)
        return f"{header}\n\n{body}".strip(), name, [{"content": body, "full_document": True}], objectives

    if lessons:
        per_lesson = max(2, 8 // len(lessons))
        for l in lessons:
            chunks += retriever.retrieve(
                db, l["title"], course_id=course_id, lesson_id=l["id"], lesson_only=True, k=per_lesson
            )
        chunks = retriever.expand_neighbors(db, chunks[:8], max_chars=FULL_DOC_MAX * 3 // 2)
    if not chunks:
        query = " ".join([name] + [l["title"] for l in lessons])
        chunks = retriever.retrieve(db, query, course_id=course_id, k=6)

    if not chunks:
        # Không có tài liệu RAG: chỉ dùng được khi các bài có mô tả làm ngữ liệu
        if any(l.get("description") for l in lessons):
            return header, name, [], objectives
        raise QuizGenError(
            "Chương chưa có tài liệu hoặc mô tả bài học để sinh câu hỏi. Hãy thêm mô tả bài học "
            "hoặc tải tài liệu trong mục \"Tài liệu AI Tutor\" trước."
        )
    body = "\n\n".join(c["content"] for c in chunks)
    return f"{header}\n\n{body}".strip(), name, chunks, objectives


# Tạo ngữ liệu cho việc sinh câu hỏi:
# - bài học có tài liệu đủ ngắn -> dùng NGUYÊN VĂN tài liệu bài (câu hỏi phủ toàn bộ bài, không sót phần nào)
# - tài liệu dài -> truy hồi theo TỪNG mục tiêu bài học để ngữ liệu phủ đủ các mục tiêu
# - còn lại -> lấy tiêu đề bài/khóa làm truy vấn, truy hồi 6 đoạn tài liệu liên quan
def _build_context(db: Session, course_id: int, lesson_id: int | None) -> tuple[str, str, list[dict], list[str]]:
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

    objectives: list[str] = []
    chunks: list[dict] = []
    if lesson_id:
        # PDF đính kèm bài chưa nạp vào RAG -> nạp luôn (giống AI Tutor và câu hỏi ôn tập chương)
        ingest.ensure_lesson_document(db, lesson_id)
        text, objectives = _lesson_material(db, lesson_id)
        if text and len(text) <= FULL_DOC_MAX:
            return f"{header}\n\n{text}", topic_hint, [{"content": text, "full_document": True}], objectives
        for o in objectives:
            chunks += retriever.retrieve(
                db, f"{topic_hint}. {o}", course_id=course_id, lesson_id=lesson_id, lesson_only=True, k=3
            )
        # Ghép đoạn liền kề để mỗi phần ngữ liệu trọn ý (danh sách, định nghĩa dài không bị cắt ngang)
        chunks = retriever.expand_neighbors(db, _unique_chunks(chunks)[:10], max_chars=FULL_DOC_MAX)
    # Dùng lại bộ truy hồi của RAG, tìm trong tài liệu của khóa (và bài, nếu có)
    if not chunks:
        chunks = retriever.retrieve(db, query, course_id=course_id, lesson_id=lesson_id, k=6)
    if not chunks:
        # chưa có tài liệu RAG -> dùng nội dung bài học / mô tả khóa
        if lesson_id and header:
            return header, topic_hint, [], objectives
        raise QuizGenError(
            "Khóa học chưa có tài liệu nào được lập chỉ mục. Hãy tải tài liệu trong mục "
            "\"Tài liệu AI Tutor\" trước, hoặc chọn một bài học đã có mô tả."
        )

    # Ghép tiêu đề + các đoạn tài liệu thành ngữ liệu
    body = "\n\n".join(c["content"] for c in chunks)
    return f"{header}\n\n{body}".strip(), topic_hint, chunks, objectives


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
                     seen: set[str], objectives: list[str] | None = None) -> list[dict]:
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
        if len({_norm(v) for v in (A, B, C, D)}) != 4:
            continue
        ca = str(q.get("correct_answer") or "").strip().upper()
        if ca not in {"A", "B", "C", "D"}:
            continue
        key = _norm(content)
        if key in seen:
            continue
        seen.add(key)
        # Các số thứ tự mục tiêu model gắn cho câu (mảng, 1 số, hoặc chuỗi "1, 3") -> nội dung mục tiêu;
        # số ngoài danh sách thì bỏ, câu không gắn mục tiêu nào vẫn giữ
        related: list[str] = []
        if objectives:
            for num in re.findall(r"\d+", json.dumps(q.get("objectives", q.get("objective")))):
                if 1 <= int(num) <= len(objectives) and objectives[int(num) - 1] not in related:
                    related.append(objectives[int(num) - 1])
        out.append(
            {
                "question": content,
                "options": {"A": A, "B": B, "C": C, "D": D},
                "correct_answer": ca,
                "explanation": str(q.get("explanation") or "").strip(),
                "difficulty": (str(q.get("difficulty") or difficulty).strip().lower()
                               if str(q.get("difficulty") or "").strip().lower() in DIFF_VI else difficulty),
                "topic": str(q.get("topic") or topic_hint).strip()[:100],
                "knowledge_lesson_id": q.get('knowledge_lesson_id'),
                "objectives": related,
                "evidence": str(q.get("evidence") or "").strip()[:300],
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
        # Không tạo phương án giả để bù số lượng khi tài liệu thiếu thuật ngữ.
        if len(distract) < 3:
            continue
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
                "difficulty": "easy",
                "topic": topic_hint[:100],
            }
        )
        if len(out) >= n:
            break
    return out


# ── API chính ─────────────────────────────────────────────────────────────

# Mô tả từng mức độ khó cho LLM để câu hỏi thật sự khác nhau về độ khó (không chỉ khác nhãn)
DIFF_GUIDE = {
    "easy": (
        "nhận biết/ghi nhớ MỘT kiến thức: nhận diện định nghĩa, khái niệm hoặc sự kiện "
        "có trực tiếp trong ngữ liệu; không cần kết hợp điều kiện hay suy luận nhiều bước"
    ),
    "medium": (
        "thông hiểu/vận dụng MỘT quy tắc: giải thích quan hệ, so sánh đơn giản hoặc áp dụng "
        "kiến thức vào ví dụ quen thuộc; phải xử lý thông tin, không chỉ nhớ lại định nghĩa"
    ),
    "hard": (
        "phân tích/vận dụng cao: kết hợp ít nhất HAI kiến thức hoặc điều kiện có ý nghĩa "
        "để giải tình huống mới, phát hiện lỗi hoặc chọn giải pháp theo ràng buộc; "
        "cần nhiều bước suy luận, không chỉ thay số vào một công thức hay hỏi định nghĩa khó nhớ"
    ),
}
# Tổng số câu tối đa cho 1 lần sinh khi phân bổ nhiều mức độ khó
MAX_TOTAL = 30

# Giới hạn chung cho sinh/kiểm tra quiz để các lượt sinh đồng thời không dồn API.
_llm_slots = BoundedSemaphore(2)


# Chỉ dẫn cho lượt AI tự giải lại đề (không cho biết đáp án đã đánh) để phát hiện câu đánh sai đáp án.
# Bắt suy luận ("work") TRƯỚC rồi mới chọn đáp án: thử thực tế, nếu để "answer" đứng trước thì model
# chốt đáp án rồi mới biện minh và bỏ lọt câu sai (câu đọc code vòng lặp lồng: 0/3 lần bắt được -> 4/4).
_VERIFY_SYSTEM = (
    "Bạn là giáo viên chấm đề trắc nghiệm. Với MỖI câu: trước tiên tự suy luận từng bước trong trường \"work\" "
    "(với đoạn code: chạy tay từng dòng, ghi giá trị biến sau mỗi vòng lặp), CHƯA nhìn các phương án; "
    "sau đó mới đối chiếu kết quả với các phương án và chọn đáp án. "
    "Đánh giá mức tư duy từ cách giải thực tế, không đoán từ độ dài câu hỏi. "
    + " ".join(f"{level}: {guide}." for level, guide in DIFF_GUIDE.items())
    + ' Trả về DUY NHẤT JSON: {"answers":[{"i":<số thứ tự câu>,"work":"<các bước suy luận>",'
    '"answer":"A|B|C|D","reason":"<kết luận 1 câu>","difficulty":"easy|medium|hard",'
    '"difficulty_reason":"<lý do phân mức theo thao tác tư duy>"}]}'
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
        assessed = str(a.get("difficulty") or "").strip().lower()
        if assessed in DIFF_GUIDE:
            q["difficulty_review"] = {
                "assessed": assessed,
                "matches_requested": assessed == q["difficulty"],
                "reason": str(a.get("difficulty_reason") or "").strip()[:500],
            }
        if ans == q["correct_answer"]:
            q["verified"] = ans  # lưu đáp án AI giải ra để giao diện so với đáp án hiện tại
        else:
            q["verify"] = {"answer": ans, "reason": str(a.get("reason") or "").strip()[:500]}


# Sinh 1 lô n câu ở đúng 1 mức độ khó (LLM hoặc heuristic); seen dùng chung để các lô không trùng nhau
def _generate_batch(context: str, topic_hint: str, *, n: int, difficulty: str,
                    seen: set[str], provider: str, objectives: list[str] | None = None,
                    coverage: dict[str, int] | None = None,
                    mix: dict[str, int] | None = None) -> list[dict]:
    if provider == "stub":
        # Điền chỗ trống chỉ hỗ trợ nhận biết; không giả lập các mức tư duy cao hơn.
        if difficulty != "easy":
            return []
        return _heuristic(context, n=n, difficulty=difficulty, topic_hint=topic_hint, seen=seen)

    # Có LLM: tạo hướng dẫn (số câu, độ khó + mô tả mức, chủ đề) + ngữ liệu làm prompt
    instr = (
        f"Tạo {n} câu hỏi trắc nghiệm mức {DIFF_VI[difficulty]} ({DIFF_GUIDE[difficulty]}) về \"{topic_hint}\", "
        "mỗi câu 4 lựa chọn A-D, một đáp án đúng và một giải thích ngắn. Trả JSON schema StudyOnline."
    )
    if mix:
        allocation = "; ".join(f"{count} câu {DIFF_VI[level]} (difficulty={level})" for level, count in mix.items())
        instr = (
            f"Tạo tổng cộng {n} câu hỏi trắc nghiệm về \"{topic_hint}\". Phân bổ: {allocation}. "
            "Mỗi câu có bốn lựa chọn A-D, một đáp án đúng, giải thích ngắn và nhãn difficulty đúng mức yêu cầu. "
            + " ".join(f"{level}: {DIFF_GUIDE[level]}." for level in mix)
            + " Trả JSON schema StudyOnline; xen kẽ nội dung để bao quát các mục tiêu bài học."
        )
    goals = ""
    if objectives:
        # Đề xoay quanh mục tiêu bài học: mỗi câu liên quan 1 hoặc vài mục tiêu (không bắt buộc gắn đúng 1),
        # cả đề nhìn chung bao quát các mục tiêu; gợi ý (không ép) các mục tiêu mà các lô trước còn ít câu
        coverage = coverage or {}
        least = min(coverage.get(o, 0) for o in objectives)
        todo = [str(i) for i, o in enumerate(objectives, 1) if coverage.get(o, 0) == least]
        instr += (
            " Câu hỏi xoay quanh các MỤC TIÊU BÀI HỌC bên dưới: mỗi câu có thể liên quan tới 1 hoặc vài mục tiêu "
            "(ghi các số thứ tự vào mảng \"objectives\"), không bắt buộc mỗi câu chỉ gắn 1 mục tiêu; cả đề nên bao quát "
            f"các mục tiêu, chú ý thêm các mục tiêu số {', '.join(todo)}. Tránh hỏi chi tiết vụn vặt không phục vụ "
            "mục tiêu nào."
        )
        goals = "MỤC TIÊU BÀI HỌC:\n" + "\n".join(f"{i}. {o}" for i, o in enumerate(objectives, 1)) + "\n\n"
    user = f"Hướng dẫn: {instr}\n\n{goals}NGỮ LIỆU:\n{context}"
    # Câu tình huống kèm giải thích và căn cứ có thể vượt 300 token/câu.
    # Chừa đủ chỗ để JSON không bị cắt rồi phải gọi lại toàn bộ lô.
    max_tokens = min(8192, 600 + 600 * n)
    context_words = set(_words(context))
    # Gọi LLM tối đa 2 lần; lần 2 nhắc thêm "chỉ trả về JSON" nếu lần 1 không parse được
    for extra in ("", "\n\nLƯU Ý: chỉ trả về JSON hợp lệ, không giải thích thêm."):
        text = model_manager.generate(_SYSTEM, user + extra, max_tokens=max_tokens)
        data = _extract_json(text)
        if mix and isinstance(data, dict) and isinstance(data.get("questions"), list):
            # Không đoán mức độ khi model bỏ nhãn trong một lô gồm nhiều mức.
            data = {**data, "questions": [q for q in data["questions"]
                    if isinstance(q, dict) and str(q.get("difficulty") or "").strip().lower() in mix]}
        questions = (
            _clean_questions(data, n=len(data.get("questions", [])) if mix and isinstance(data, dict) else n,
                             difficulty=difficulty, topic_hint=topic_hint, seen=seen, objectives=objectives)
            if data else []
        )
        if mix:
            counts = dict.fromkeys(mix, 0)
            selected = []
            for q in questions:
                if counts[q["difficulty"]] < mix[q["difficulty"]]:
                    selected.append(q)
                    counts[q["difficulty"]] += 1
            questions = selected
        if questions:
            # Lô được yêu cầu ở mức nào thì gắn đúng mức đó (model đôi khi tự gắn nhãn khác)
            for q in questions:
                if not mix:
                    q["difficulty"] = difficulty
                # Đối chiếu căn cứ AI trích với tài liệu: không khớp -> giảng viên cần kiểm tra câu này
                q["grounded"] = _grounded(q["evidence"], context_words)
            return questions
    return []


# Hàm chính: tạo ngữ liệu -> sinh từng lô theo mức độ khó (LLM hoặc heuristic nếu offline) -> trả bản nháp.
# mix = {"easy": x, "medium": y, "hard": z} để phân bổ độ khó; không có mix thì sinh n câu cùng 1 mức.
def generate(db: Session, *, course_id: int, lesson_id: int | None,
             n: int, difficulty: str, chapter_id: int | None = None,
             mix: dict[str, int] | None = None,
             on_progress: Callable[[dict], None] | None = None) -> dict:
    def notify(event: dict) -> None:
        if on_progress:
            on_progress(event)

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

    notify({"type": "status", "message": "Đang đọc tài liệu để sinh câu hỏi…"})
    # Có chapter_id -> sinh câu hỏi ôn tập bao quát cả chương
    if chapter_id:
        context, topic_hint, chunks, objectives = _build_chapter_context(db, course_id, chapter_id)
    else:
        context, topic_hint, chunks, objectives = _build_context(db, course_id, lesson_id)
    seen = _existing_questions(db, course_id)
    structure = None
    if db is not None:
        from app.services.knowledge import outline
        structure = outline(db, course_id)
        allowed = [l for l in structure['lessons'] if (not chapter_id or l['chapter_id'] == chapter_id)
                   and (not lesson_id or l['id'] == lesson_id)]
        context += '\n\nMÃ BÀI HỌC ĐƯỢC PHÉP (knowledge_lesson_id):\n' + '\n'.join(f"{l['id']}: {l['title']}" for l in allowed)
    provider = model_manager.active_provider()
    if provider == "stub" and not any(lvl == "easy" for lvl, _ in plan):
        raise QuizGenError(
            "Chế độ offline chỉ tạo câu nhận biết mức dễ. Hãy chọn câu dễ hoặc cấu hình LLM "
            "để tạo câu trung bình/khó."
        )

    questions: list[dict] = []
    distribution: dict[str, int] = {}
    coverage: dict[str, int] = {o: 0 for o in objectives}  # số câu đã có của mỗi mục tiêu bài học

    def accept(lvl: str, k: int, batch: list[dict]) -> None:
        # Mỗi worker có tập seen riêng; chỉ thread điều phối gộp và loại trùng giữa các mức.
        accepted = []
        for q in batch:
            key = _norm(q["question"])
            if key in seen:
                continue
            seen.add(key)
            if structure is not None:
                from app.services.knowledge import resolve
                candidate = q.get('knowledge_lesson_id')
                if not any(str(l['id']) == str(candidate) for l in allowed):
                    candidate = None
                body = {'topic': q.get('topic')}
                if candidate:
                    body.update(knowledge_lesson_id=int(candidate), knowledge_chapter_id=chapter_id)
                q.update(resolve(db, course_id, body, dict(chapter_id=chapter_id, lesson_id=lesson_id), structure))
            accepted.append(q)
            for o in q.get("objectives") or []:
                if o in coverage:
                    coverage[o] += 1
        distribution[lvl] = len(accepted)
        questions.extend(accepted)
        notify({"type": "batch", "difficulty": lvl, "requested": k,
                "questions": [dict(q) for q in accepted]})

    # Tối đa 12 câu vừa ngân sách đầu ra: gửi ngữ liệu một lần cho cả phân bổ.
    if provider != "stub" and 1 < len(plan) and sum(k for _, k in plan) <= 12:
        notify({"type": "status", "message": "Đang sinh bản nháp theo phân bổ độ khó…"})
        with _llm_slots:
            batch = _generate_batch(context, topic_hint, n=sum(k for _, k in plan), difficulty="medium",
                                    seen=set(seen), provider=provider, objectives=objectives,
                                    coverage=coverage, mix=dict(plan))
        for lvl, k in plan:
            accept(lvl, k, [q for q in batch if q["difficulty"] == lvl])
    elif provider != "stub" and len(plan) > 1:
        notify({"type": "status", "message": "Đang sinh các nhóm độ khó song song…"})

        def work(lvl: str, k: int) -> list[dict]:
            # Không đưa Session DB vào worker; ngữ liệu đã đọc xong trước khi chạy song song.
            with _llm_slots:
                return _generate_batch(context, topic_hint, n=k, difficulty=lvl, seen=set(existing),
                                       provider=provider, objectives=objectives, coverage=dict(initial_coverage))

        existing = set(seen)
        initial_coverage = dict(coverage)
        with ThreadPoolExecutor(max_workers=2) as pool:
            pending = {pool.submit(work, lvl, k): (lvl, k) for lvl, k in plan}
            for future in as_completed(pending):
                lvl, k = pending[future]
                accept(lvl, k, future.result())
        order = {lvl: i for i, (lvl, _) in enumerate(plan)}
        questions.sort(key=lambda q: order[q["difficulty"]])
    else:
        for lvl, k in plan:
            notify({"type": "status", "message": f"Đang sinh câu hỏi mức {DIFF_VI[lvl]}…"})
            batch = _generate_batch(context, topic_hint, n=k, difficulty=lvl, seen=set(seen), provider=provider,
                                    objectives=objectives, coverage=coverage)
            accept(lvl, k, batch)
    gen_by = "heuristic" if provider == "stub" else f"{provider}:{model_manager.info()['model']}"

    if not questions:
        raise QuizGenError(
            "Không sinh được câu hỏi từ ngữ liệu hiện có."
            if provider == "stub"
            else "Model không trả về JSON hợp lệ sau 2 lần thử. Vui lòng thử lại hoặc giảm số câu."
        )

    # Giải lại cả bản nháp một lần, dùng chung ngữ liệu cho các mức độ khó.
    # Tránh ba lượt kiểm tra riêng khi giảng viên chọn dễ/trung bình/khó.
    if provider != "stub":
        notify({"type": "status", "message": f"Đã nhận {len(questions)} câu. Đang kiểm tra đáp án và độ khó…"})
        with _llm_slots:
            _verify(context, questions)

    unverified = sum(1 for q in questions if not q.get("verified") and not q.get("verify"))
    warnings = ([
        "Chế độ offline chỉ tạo câu dễ; các câu trung bình/khó được yêu cầu chưa được sinh."
    ] if provider == "stub" and any(lvl != "easy" for lvl, _ in plan) else [])
    if provider != "stub" and unverified:
        warnings.append(
            f"Chưa tự kiểm tra được đáp án của {unverified} câu. "
            "Vui lòng kiểm tra nội dung và đáp án trước khi duyệt."
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
            "difficulty_basis": "Mức tư duy dự kiến; giảng viên cần thẩm định trước khi sử dụng.",
            "warnings": warnings,
            # Kết quả AI tự giải lại: số câu khớp đáp án / số câu AI giải ra đáp án khác (cần giảng viên xem)
            "verification": {
                "unverified": unverified,
                "verified": sum(1 for q in questions if q.get("verified")),
                "flagged": sum(1 for q in questions if q.get("verify")),
                # Số câu có căn cứ AI trích KHÔNG tìm thấy trong tài liệu (chế độ offline không có căn cứ -> không tính)
                "ungrounded": sum(1 for q in questions if q.get("grounded") is False),
                "difficulty_flagged": sum(
                    1 for q in questions
                    if q.get("difficulty_review", {}).get("matches_requested") is False
                ),
            },
            # Ngữ liệu: nguyên văn tài liệu bài/chương, hoặc các đoạn truy hồi khi tài liệu quá dài
            "context_mode": "full_document" if chunks and chunks[0].get("full_document") else "retrieval",
            "context_chars": len(context),
            "context_chunks": len(chunks),
            "topic": topic_hint,
            # Mục tiêu bài học đọc từ tài liệu (rỗng = tài liệu không có phần mục tiêu, sinh theo nội dung như cũ)
            "objectives": objectives,
        },
    }
