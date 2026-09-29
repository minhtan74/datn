"""AI Tutor — điều phối hội thoại RAG: lưu ai_conversations / ai_messages."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.ai.rag import rag_pipeline
from app.core.database import execute, q_all, q_one


# Danh sách cuộc trò chuyện của user (kèm số tin nhắn), mới cập nhật lên đầu
def list_conversations(db: Session, user_id: int, course_id: int | None = None) -> list[dict]:
    sql = (
        "SELECT c.*, "
        "(SELECT COUNT(*) FROM ai_messages m WHERE m.conversation_id = c.id) AS message_count "
        "FROM ai_conversations c WHERE c.user_id = :u"
    )
    params = {"u": user_id}
    if course_id:
        sql += " AND c.course_id = :c"
        params["c"] = course_id
    sql += " ORDER BY c.updated_at DESC, c.id DESC"
    return q_all(db, sql, **params)


# Lấy 1 cuộc trò chuyện, chỉ khi thuộc về đúng user (chống xem trộm hội thoại người khác)
def get_conversation(db: Session, conversation_id: int, user_id: int) -> dict | None:
    return q_one(
        db,
        "SELECT * FROM ai_conversations WHERE id = :id AND user_id = :u",
        id=conversation_id,
        u=user_id,
    )


# Toàn bộ tin nhắn của cuộc trò chuyện theo thứ tự; cột sources (JSON) được chuyển về list
def get_messages(db: Session, conversation_id: int, user_id: int) -> list[dict]:
    if not get_conversation(db, conversation_id, user_id):
        return []
    rows = q_all(
        db,
        "SELECT id, role, content, sources, created_at FROM ai_messages "
        "WHERE conversation_id = :c ORDER BY id ASC",
        c=conversation_id,
    )
    for r in rows:
        if isinstance(r.get("sources"), str):
            try:
                r["sources"] = json.loads(r["sources"])
            except ValueError:
                r["sources"] = None
    return rows


# Xóa cuộc trò chuyện của chính user (tin nhắn bị xóa theo)
def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
    if not get_conversation(db, conversation_id, user_id):
        return False
    execute(db, "DELETE FROM ai_conversations WHERE id = :id", id=conversation_id)
    return True


# Tạo cuộc trò chuyện mới; tiêu đề lấy từ câu hỏi đầu tiên
def _create_conversation(db: Session, user_id: int, course_id: int | None, lesson_id: int | None, title: str) -> int:
    res = execute(
        db,
        "INSERT INTO ai_conversations (user_id, course_id, lesson_id, title) VALUES (:u, :c, :l, :t)",
        u=user_id,
        c=course_id,
        l=lesson_id,
        t=title[:200] or "Cuộc trò chuyện mới",
    )
    return res.lastrowid


# Xử lý 1 lượt hỏi đáp với AI Tutor
def chat(
    db: Session,
    *,
    user_id: int,
    course_id: int,
    message: str,
    lesson_id: int | None = None,
    lesson_only: bool = False,
    conversation_id: int | None = None,
) -> dict:
    message = (message or "").strip()

    # Có conversation_id hợp lệ thì hỏi tiếp, không thì tạo cuộc trò chuyện mới
    conv = get_conversation(db, conversation_id, user_id) if conversation_id else None
    if conv:
        conversation_id = conv["id"]
    else:
        conversation_id = _create_conversation(
            db, user_id, course_id, lesson_id, title=message[:60] or "Cuộc trò chuyện mới"
        )

    # Lấy lịch sử trước đó để LLM hiểu ngữ cảnh câu hỏi nối tiếp
    history = get_messages(db, conversation_id, user_id)

    # lưu tin nhắn người dùng
    execute(
        db,
        "INSERT INTO ai_messages (conversation_id, role, content) VALUES (:c, 'user', :m)",
        c=conversation_id,
        m=message,
    )

    # Chạy RAG để sinh câu trả lời dựa trên tài liệu khóa học
    result = rag_pipeline.answer(
        db, message, course_id=course_id, lesson_id=lesson_id, lesson_only=lesson_only, history=history
    )

    # Lưu câu trả lời của AI kèm nguồn trích dẫn, rồi cập nhật thời điểm của cuộc trò chuyện
    execute(
        db,
        "INSERT INTO ai_messages (conversation_id, role, content, sources) "
        "VALUES (:c, 'assistant', :m, :s)",
        c=conversation_id,
        m=result["answer"],
        s=json.dumps(result["sources"], ensure_ascii=False) if result["sources"] else None,
    )
    execute(
        db,
        "UPDATE ai_conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = :id",
        id=conversation_id,
    )

    return {
        "conversation_id": conversation_id,
        "answer": result["answer"],
        "sources": result["sources"],
        "used_context": result["used_context"],
    }
