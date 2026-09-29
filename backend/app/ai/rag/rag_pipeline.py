"""RAG pipeline: truy hồi -> tạo prompt có ràng buộc -> LLM -> câu trả lời + nguồn.

Nguyên tắc (đề bài §14): CHỈ trả lời dựa trên tài liệu khóa học; không đủ ngữ
cảnh thì trả đúng câu "Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học.";
KHÔNG bịa nguồn.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.ai import model_manager
from app.ai.rag import extractive, retriever
from app.core.config import settings

logger = logging.getLogger("rag")

# Câu trả lời cố định khi tài liệu không có thông tin phù hợp (chống AI bịa)
NO_ANSWER = "Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học."

# Chỉ dẫn hệ thống cho LLM: chỉ trả lời dựa trên ngữ cảnh, không bịa, trả lời tiếng Việt
_SYSTEM = (
    "Bạn là trợ giảng AI của nền tảng học trực tuyến StudyOnline. "
    "CHỈ được trả lời dựa trên phần NGỮ CẢNH được cung cấp (trích từ tài liệu khóa học). "
    "Nếu ngữ cảnh không chứa thông tin để trả lời, hãy trả lời đúng một câu: "
    f"\"{NO_ANSWER}\". Tuyệt đối không bịa thông tin, không bịa nguồn. "
    "Trả lời ngắn gọn, rõ ràng, bằng tiếng Việt."
)


# Trả lời 1 câu hỏi theo quy trình RAG: truy hồi -> kiểm tra ngưỡng -> sinh câu trả lời -> gắn nguồn
def answer(
    db: Session,
    question: str,
    *,
    course_id: int,
    lesson_id: int | None = None,
    lesson_only: bool = False,
    history: list[dict] | None = None,
) -> dict:
    question = (question or "").strip()
    if not question:
        return {"answer": NO_ANSWER, "sources": [], "used_context": False}

    logger.info(
        "[RAG] course_id=%s lesson_id=%s lesson_only=%s query=%r",
        course_id, lesson_id, lesson_only, question,
    )

    # Truy hồi các đoạn liên quan trong tài liệu của khóa (hoặc của bài học)
    chunks = retriever.retrieve(
        db, question, course_id=course_id, lesson_id=lesson_id, lesson_only=lesson_only
    )

    # Ngưỡng "có tài liệu liên quan hay không": xét độ tương đồng embedding TỐT NHẤT.
    # Nếu vượt ngưỡng -> tin vào xếp hạng hybrid của retriever (giữ cả các đoạn khớp
    # từ khoá nhưng cosine thấp). Nếu không -> coi như câu hỏi ngoài phạm vi tài liệu.
    best_cosine = max((c.get("cosine", c["score"]) for c in chunks), default=0.0)
    logger.info(
        "[RAG] retrieved_chunks=%d best_similarity=%.4f threshold=%.2f",
        len(chunks), best_cosine, settings.rag_similarity_threshold,
    )
    if not chunks or best_cosine < settings.rag_similarity_threshold:
        logger.info("[RAG] below threshold -> refusing (no_answer)")
        return {"answer": NO_ANSWER, "sources": [], "used_context": False}
    relevant = chunks

    # Ghép các đoạn thành NGỮ CẢNH, mỗi đoạn gắn nhãn [Nguồn i] + tên tài liệu + số trang
    ctx_parts = []
    for i, c in enumerate(relevant, start=1):
        loc = f" (trang {c['page']})" if c.get("page") else ""
        ctx_parts.append(f"[Nguồn {i}] {c['document_title']}{loc}\n{c['content']}")
    context = "\n\n".join(ctx_parts)

    if model_manager.active_provider() == "stub":
        # Không có LLM -> trả lời trích xuất từ chính ngữ cảnh (chạy offline khi bảo vệ)
        text = extractive.answer(question, relevant)
        if not text:
            return {"answer": NO_ANSWER, "sources": [], "used_context": False}
    else:
        hist_txt = ""
        for m in (history or [])[-4:]:
            who = "Học viên" if m["role"] == "user" else "Trợ giảng"
            hist_txt += f"{who}: {m['content']}\n"

        user_prompt = (
            (f"LỊCH SỬ HỘI THOẠI:\n{hist_txt}\n" if hist_txt else "")
            + f"NGỮ CẢNH:\n{context}\n\n"
            + f"CÂU HỎI: {question}\n\n"
            + "Hãy trả lời câu hỏi chỉ dựa trên NGỮ CẢNH ở trên."
        )
        text = model_manager.generate(_SYSTEM, user_prompt)

        if text.strip() == NO_ANSWER or text.startswith("[Lỗi gọi LLM"):
            return {"answer": text.strip(), "sources": [], "used_context": False}

    # Nguồn = các tài liệu/trang liên quan nhất (top 3 theo hybrid, khử trùng lặp)
    ranked = sorted(relevant, key=lambda c: c.get("hybrid", c["score"]), reverse=True)
    seen = set()
    sources = []
    for c in ranked:
        key = (c["document_id"], c["page"])
        if key in seen:
            continue
        # chỉ trích nguồn có độ tương đồng đủ tốt (luôn giữ ít nhất nguồn số 1)
        if sources and c.get("cosine", c["score"]) < 0.40:
            continue
        seen.add(key)
        sources.append(
            {
                "document_id": c["document_id"],
                "document": c["document_title"],
                "page": c["page"],
                "score": round(c.get("cosine", c["score"]), 4),
            }
        )
        if len(sources) >= 3:
            break

    logger.info("[RAG] LLM response generated (provider=%s, sources=%d)", model_manager.active_provider(), len(sources))
    return {"answer": text, "sources": sources, "used_context": True}
