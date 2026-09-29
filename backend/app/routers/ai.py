"""/api/ai/* — PHASE 6 RAG AI Tutor (tài liệu + hội thoại)."""
from __future__ import annotations

import os
import secrets
import time

from fastapi import APIRouter, Body, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.ai import model_manager, quiz_generator, tutor
from app.ai.quiz_generator import QuizGenError
from app.ai.rag import embeddings as emb
from app.ai.rag import ingest
from app.core.config import settings
from app.core.database import execute, get_db, q_all, q_one, q_scalar
from app.core.dependencies import get_current_user, require_roles
from app.core.responses import ApiError, ok
from app.routers.chapters import ensure_review_quiz
from app.routers.enrollments import _is_enrolled
from app.routers.lessons import ensure_lesson_review_quiz
from app.routers.quizzes import _grading_method, _quiz_settings

from ._common import assert_owns_course, iv, sv

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Đuôi file tài liệu được hỗ trợ -> loại tài liệu dùng khi trích xuất văn bản (.md xử lý như .txt)
_EXT_TYPE = {".pdf": "pdf", ".docx": "docx", ".txt": "txt", ".md": "txt"}


# GET /api/ai/status — cho biết đang dùng LLM nào (hoặc chế độ offline) và model embedding nào
@router.get("/status")
def status(_: dict = Depends(get_current_user)):
    return ok(data={"llm": model_manager.info(), "embedding": emb.model_info()})


# ── Tài liệu (giảng viên) ───────────────────────────────────────────────────

# POST /api/ai/documents — giảng viên tải tài liệu lên và lập chỉ mục cho RAG AI Tutor
@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    course_id: int = Form(...),
    lesson_id: int | None = Form(default=None),
    title: str | None = Form(default=None),
    user: dict = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    # Chỉ nhận PDF / DOCX / TXT
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _EXT_TYPE:
        raise ApiError("Chỉ hỗ trợ tài liệu PDF, DOCX, TXT.", 400)

    # Khóa học phải tồn tại và thuộc quyền của giảng viên đang tải
    if not q_one(db, "SELECT id FROM courses WHERE id = :id", id=course_id):
        raise ApiError("Khóa học không tồn tại.", 404)
    assert_owns_course(db, user, course_id)

    # Lưu file vào uploads/documents với tên ngẫu nhiên (thời gian + chuỗi hex)
    folder = os.path.join(settings.upload_dir, "documents")
    os.makedirs(folder, exist_ok=True)
    stored = f"{int(time.time())}_{secrets.token_hex(6)}{ext}"
    path = os.path.join(folder, stored)

    # Ghi theo từng khối 1MB, vượt 20MB thì xóa file và báo lỗi
    size = 0
    with open(path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > 20 * 1024 * 1024:
                out.close()
                os.remove(path)
                raise ApiError("File quá lớn. Giới hạn: 20MB.", 400)
            out.write(chunk)

    # Tạo bản ghi documents ở trạng thái 'pending'
    doc = ingest.create_document(
        db,
        course_id=course_id,
        lesson_id=int(lesson_id) if lesson_id else None,
        title=(title or file.filename or stored).strip(),
        filename=file.filename or stored,
        file_path=path,
        file_type=_EXT_TYPE[ext],
        uploaded_by=user["id"],
    )
    # Lập chỉ mục: trích xuất văn bản -> chia đoạn -> tạo embedding -> lưu document_chunks.
    # Thất bại vẫn trả về tài liệu (trạng thái 'failed' + lý do) để giao diện hiển thị lỗi
    try:
        doc = ingest.ingest_document(db, doc["id"])
        return ok(
            f"Đã nạp tài liệu — {doc['chunk_count']} đoạn được lập chỉ mục.", data=doc
        )
    except Exception as e:  # noqa: BLE001
        failed = q_one(db, "SELECT * FROM documents WHERE id = :id", id=doc["id"])
        return ok(f"Tải lên xong nhưng lập chỉ mục thất bại: {e}", data=failed)


# GET /api/ai/documents — danh sách tài liệu AI (giảng viên chỉ thấy tài liệu khóa của mình)
@router.get("/documents")
def list_documents(
    course_id: int | None = Query(default=None),
    user: dict = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    if course_id:
        assert_owns_course(db, user, course_id)
    # Ghép câu truy vấn động: lọc theo khóa (nếu có) và theo giảng viên phụ trách (nếu không phải admin)
    sql = (
        "SELECT d.*, c.title AS course_title, l.title AS lesson_title "
        "FROM documents d JOIN courses c ON c.id = d.course_id "
        "LEFT JOIN lessons l ON l.id = d.lesson_id"
    )
    params = {}
    conds = []
    if course_id:
        conds.append("d.course_id = :c")
        params["c"] = course_id
    if user["role"] != "admin":
        conds.append("c.teacher_id = :tid")
        params["tid"] = user["id"]
    if conds:
        sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY d.created_at DESC"
    return ok(data=q_all(db, sql, **params))


# DELETE /api/ai/documents?id=X — xóa tài liệu, các đoạn vector của nó và file trên đĩa
@router.delete("/documents")
def delete_document(
    id: int = Query(default=0),
    user: dict = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    if not id:
        raise ApiError("Thiếu id.")
    doc = q_one(db, "SELECT file_path, course_id FROM documents WHERE id = :id", id=id)
    if not doc:
        raise ApiError("Không tìm thấy tài liệu.", 404)
    assert_owns_course(db, user, doc["course_id"])
    execute(db, "DELETE FROM documents WHERE id = :id", id=id)  # chunks cascade
    if doc and doc["file_path"] and os.path.exists(doc["file_path"]):
        try:
            os.remove(doc["file_path"])
        except OSError:
            pass
    return ok("Đã xóa tài liệu.")


# ── Hội thoại (học viên / giảng viên) ──────────────────────────────────────

# POST /api/ai/chat — gửi câu hỏi cho AI Tutor, nhận câu trả lời kèm nguồn trích dẫn
@router.post("/chat")
def chat(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Kiểm tra dữ liệu: phải có khóa học, có câu hỏi và không vượt độ dài tối đa
    course_id = int(body.get("course_id") or 0)
    message = (body.get("message") or "").strip()
    if not course_id:
        raise ApiError("Thiếu course_id.")
    if not message:
        raise ApiError("Vui lòng nhập câu hỏi.")
    if len(message) > settings.rag_max_question_length:
        raise ApiError(
            f"Câu hỏi quá dài (tối đa {settings.rag_max_question_length} ký tự).", 400
        )

    # Chỉ học viên đã đăng ký khóa học mới được hỏi AI về tài liệu của khóa đó —
    # tránh lộ nội dung khóa học khác (kể cả khóa trả phí chưa mua).
    if user.get("role") == "student" and not _is_enrolled(db, user["id"], course_id):
        raise ApiError("Bạn chưa đăng ký khóa học này.", 403)

    # Hỏi trong trang bài học -> chỉ tìm trong tài liệu của bài đó; có conversation_id -> hỏi tiếp cuộc trò chuyện cũ
    lesson_id = int(lesson_id_raw) if (lesson_id_raw := body.get("lesson_id")) else None
    conversation_id = body.get("conversation_id")

    if lesson_id:
        # Bài học có PDF đính kèm nhưng chưa từng được nạp vào RAG -> tự nạp ngay lần hỏi đầu tiên.
        ingest.ensure_lesson_document(db, lesson_id)

    # Chạy RAG + lưu câu hỏi/câu trả lời vào lịch sử hội thoại
    res = tutor.chat(
        db,
        user_id=user["id"],
        course_id=course_id,
        message=message,
        lesson_id=lesson_id,
        lesson_only=bool(lesson_id),
        conversation_id=int(conversation_id) if conversation_id else None,
    )
    return ok(data=res)


# GET /api/ai/conversations — danh sách cuộc trò chuyện của user (lọc theo khóa nếu có)
@router.get("/conversations")
def conversations(
    course_id: int | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ok(data=tutor.list_conversations(db, user["id"], course_id))


# GET /api/ai/conversations/{cid} — toàn bộ tin nhắn của 1 cuộc trò chuyện (chỉ của chính user)
@router.get("/conversations/{cid}")
def conversation_messages(
    cid: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = tutor.get_conversation(db, cid, user["id"])
    if not conv:
        raise ApiError("Không tìm thấy cuộc trò chuyện.", 404)
    return ok(data={"conversation": conv, "messages": tutor.get_messages(db, cid, user["id"])})


# DELETE /api/ai/conversations/{cid} — xóa cuộc trò chuyện của chính user
@router.delete("/conversations/{cid}")
def delete_conversation(
    cid: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not tutor.delete_conversation(db, cid, user["id"]):
        raise ApiError("Không tìm thấy cuộc trò chuyện.", 404)
    return ok("Đã xóa cuộc trò chuyện.")


# ── AI Quiz Generator (giảng viên) — PHASE 9 ───────────────────────────────

# POST /api/ai/generate-quiz — sinh bản nháp câu hỏi trắc nghiệm từ tài liệu (chưa lưu)
@router.post("/generate-quiz")
def generate_quiz(
    body: dict = Body(default={}),
    user: dict = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    # Kiểm tra khóa học + quyền sở hữu, đọc tham số: bài học (tùy chọn), số câu (mặc định 5), độ khó
    course_id = iv(body, "course_id")
    if not course_id:
        raise ApiError("Thiếu course_id.")
    assert_owns_course(db, user, course_id)
    lesson_id = body.get("lesson_id")
    chapter_id = iv(body, "chapter_id")
    n = iv(body, "number_of_questions", 5)
    difficulty = sv(body, "difficulty", "medium") or "medium"
    # Phân bổ độ khó (tùy chọn): {"easy": x, "medium": y, "hard": z}
    raw_mix = body.get("difficulty_mix")
    mix = None
    if isinstance(raw_mix, dict):
        mix = {lvl: iv(raw_mix, lvl) for lvl in ("easy", "medium", "hard")}
        if any(v < 0 or v > 20 for v in mix.values()):
            raise ApiError("Số câu mỗi mức độ khó phải từ 0 đến 20.")

    # Gọi bộ sinh quiz; lỗi nghiệp vụ (chưa có tài liệu, model trả sai JSON...) trả mã 422
    try:
        result = quiz_generator.generate(
            db,
            course_id=course_id,
            lesson_id=int(lesson_id) if lesson_id else None,
            n=n,
            difficulty=difficulty,
            chapter_id=chapter_id or None,
            mix=mix,
        )
    except QuizGenError as e:
        raise ApiError(str(e), 422)
    # AI KHÔNG tự lưu — chỉ trả preview để giảng viên duyệt.
    return ok(data=result)


# POST /api/ai/quiz/approve — giảng viên duyệt bản nháp: kiểm tra lại từng câu rồi lưu thành quiz thật
# (có chapter_id / review_lesson_id -> thêm vào cuối bộ câu hỏi ôn tập của chương / bài học thay vì tạo quiz mới)
@router.post("/quiz/approve")
def approve_quiz(
    body: dict = Body(default={}),
    user: dict = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    course_id = iv(body, "course_id")
    title = sv(body, "title")
    questions = body.get("questions")
    lesson_id = body.get("lesson_id")
    chapter_id = iv(body, "chapter_id")
    review_lesson_id = iv(body, "review_lesson_id")

    # Bắt buộc có khóa học, tiêu đề quiz (trừ khi thêm vào bộ ôn tập) và ít nhất 1 câu hỏi
    if not course_id or not (title or chapter_id or review_lesson_id):
        raise ApiError("Thiếu course_id hoặc tiêu đề quiz.")
    if not isinstance(questions, list) or not questions:
        raise ApiError("Danh sách câu hỏi trống.")
    if len(title) > 255:
        raise ApiError("Tiêu đề quiz tối đa 255 ký tự.")
    assert_owns_course(db, user, course_id)
    if not q_one(db, "SELECT id FROM courses WHERE id = :id", id=course_id):
        raise ApiError("Khóa học không tồn tại.", 404)

    # Nguồn bản nháp: "ai" (AI sinh, mặc định) hoặc "word" (nhập từ file Word)
    source = sv(body, "source") or "ai"
    if source not in ("ai", "word"):
        raise ApiError("Nguồn câu hỏi không hợp lệ.")

    # Kiểm tra từng câu; 1 câu sai là từ chối cả lô.
    # AI luôn sinh đủ 4 phương án; đề nhập từ Word được phép 2–4 phương án (vd câu Đúng / Sai)
    clean = []
    for i, q in enumerate(questions, start=1):
        content = str((q or {}).get("question") or "").strip()
        opts = (q or {}).get("options") or {}
        A, B, C, D = (str(opts.get(k) or "").strip() for k in ("A", "B", "C", "D"))
        ca = str((q or {}).get("correct_answer") or "").strip().upper()
        filled = {"A": A, "B": B, "C": C, "D": D}
        enough = all([A, B, C, D]) if source == "ai" else bool(A and B)
        if not content or not enough or ca not in filled or not filled[ca]:
            raise ApiError(f"Câu {i} chưa hợp lệ (thiếu nội dung, phương án hoặc đáp án đúng).")
        clean.append(
            {
                "content": content, "A": A, "B": B, "C": C, "D": D, "ca": ca,
                "explanation": str((q or {}).get("explanation") or "").strip() or None,
                "difficulty": (str((q or {}).get("difficulty") or "").strip().lower() or None),
                "topic": (str((q or {}).get("topic") or "").strip()[:100] or None),
            }
        )

    if chapter_id or review_lesson_id:
        # Chương / bài học phải thuộc đúng khóa học đã kiểm tra quyền ở trên
        if review_lesson_id:
            belongs = q_one(
                db, "SELECT l.id FROM lessons l JOIN chapters ch ON ch.id = l.chapter_id "
                "WHERE l.id = :id AND ch.course_id = :c", id=review_lesson_id, c=course_id,
            )
            if not belongs:
                raise ApiError("Bài học không thuộc khóa học này.", 404)
            quiz_id = ensure_lesson_review_quiz(db, review_lesson_id)
            msg = f"Đã thêm {len(clean)} câu vào bộ ôn tập của bài học."
        else:
            if not q_one(db, "SELECT id FROM chapters WHERE id = :id AND course_id = :c", id=chapter_id, c=course_id):
                raise ApiError("Chương không thuộc khóa học này.", 404)
            quiz_id = ensure_review_quiz(db, chapter_id)
            msg = f"Đã thêm {len(clean)} câu vào bộ ôn tập của chương."
        # Nối tiếp sau các câu ôn tập đã có
        start = int(q_scalar(db, "SELECT COALESCE(MAX(order_index) + 1, 0) FROM questions WHERE quiz_id = :q", q=quiz_id))
    else:
        # Tạo quiz mới với source='ai' để phân biệt quiz do AI sinh, kèm cài đặt làm bài (thời gian / điểm đạt / số lượt)
        res = execute(
            db,
            "INSERT INTO quizzes (course_id, lesson_id, title, description, source, "
            "duration, passing_score, max_attempts, grading_method) "
            "VALUES (:c, :l, :t, :d, :src, :duration, :passing_score, :max_attempts, :grading)",
            c=course_id,
            l=int(lesson_id) if lesson_id else None,
            t=title,
            d=sv(body, "description"),
            src=source,
            grading=_grading_method(body),
            **_quiz_settings(body),
        )
        quiz_id = res.lastrowid
        start = 0
        msg = "Đã lưu quiz nhập từ Word." if source == "word" else "Đã lưu quiz do AI sinh (đã duyệt)."
    # Lưu từng câu hỏi theo thứ tự; độ khó ngoài easy/medium/hard thì để trống
    for i, q in enumerate(clean, start=start):
        execute(
            db,
            "INSERT INTO questions (quiz_id, content, option_a, option_b, option_c, option_d, "
            "correct_answer, order_index, topic, difficulty, explanation) "
            "VALUES (:q, :c, :a, :b, :cc, :d, :ans, :oi, :tp, :df, :ex)",
            q=quiz_id, c=q["content"], a=q["A"], b=q["B"], cc=q["C"], d=q["D"],
            ans=q["ca"], oi=i, tp=q["topic"],
            df=q["difficulty"] if q["difficulty"] in ("easy", "medium", "hard") else None,
            ex=q["explanation"],
        )
    return ok(msg, data={"quiz_id": int(quiz_id), "question_count": len(clean)})
