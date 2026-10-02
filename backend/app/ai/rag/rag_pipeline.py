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
    f"\"{NO_ANSWER}\". Ngữ cảnh chỉ nói về chủ đề gần giống (ví dụ hỏi MongoDB nhưng ngữ cảnh nói về MySQL) "
    "mà không trả lời trực tiếp câu hỏi thì cũng trả lời câu đó. Tuyệt đối không bịa thông tin, không bịa nguồn, "
    "không dùng kiến thức ngoài ngữ cảnh. Trả lời ngắn gọn, rõ ràng, bằng tiếng Việt."
)

# Chỉ dẫn viết lại câu hỏi nối tiếp ("cho ví dụ đi", "còn cái kia?") thành câu hỏi đầy đủ để tìm tài liệu
_REWRITE_SYSTEM = (
    "Viết lại câu hỏi cuối của học viên thành MỘT câu hỏi đầy đủ, tự hiểu được mà không cần đọc hội thoại "
    "(thay các từ như 'nó', 'cái đó', 'ví dụ đi' bằng chủ đề cụ thể trong hội thoại). "
    "Nếu câu hỏi đã đầy đủ thì giữ nguyên. Chỉ trả về câu hỏi, không giải thích."
)


# Câu trả lời của LLM là lời từ chối (LLM có thể diễn đạt hơi khác câu mẫu NO_ANSWER)
def _is_refusal(text: str) -> bool:
    return "không tìm thấy thông tin phù hợp" in text.lower()


# Câu dùng để tìm tài liệu: câu hỏi nối tiếp phải được bổ sung ngữ cảnh từ hội thoại, nếu không phần tìm kiếm
# chỉ thấy "cho ví dụ đi" và từ chối nhầm. Có LLM thì nhờ LLM viết lại; offline thì ghép câu hỏi trước nếu câu hiện tại ngắn.
def _search_query(question: str, history: list[dict] | None, use_llm: bool) -> str:
    prev_user = [m["content"] for m in (history or []) if m.get("role") == "user"]
    if not prev_user:
        return question
    if use_llm:
        convo = "\n".join(
            f"{'Học viên' if m['role'] == 'user' else 'Trợ giảng'}: {m['content'][:400]}" for m in (history or [])[-4:]
        )
        prompt = f"HỘI THOẠI:\n{convo}\n\nCÂU HỎI CUỐI: {question}"
        out = model_manager.generate(_REWRITE_SYSTEM, prompt, max_tokens=120)
        out = out.strip().strip('"').strip()
        return question if (not out or out.startswith("[Lỗi gọi LLM") or len(out) > 400) else out
    return f"{prev_user[-1]} {question}" if len(question.split()) <= 6 else question


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

    use_llm = model_manager.active_provider() != "stub"

    # Truy hồi các đoạn liên quan trong tài liệu của khóa (hoặc của bài học); câu hỏi nối tiếp được viết lại trước
    query = _search_query(question, history, use_llm)
    if query != question:
        logger.info("[RAG] follow-up rewritten -> %r", query)
    chunks = retriever.retrieve(
        db, query, course_id=course_id, lesson_id=lesson_id, lesson_only=lesson_only
    )

    # Ngưỡng "có tài liệu liên quan hay không": xét độ tương đồng embedding TỐT NHẤT.
    # Offline: dưới rag_similarity_threshold thì coi như ngoài phạm vi tài liệu.
    # Có LLM: chỉ loại ngay câu lạc đề rõ ràng (dưới rag_llm_min_similarity); còn lại để LLM đọc ngữ cảnh
    # và tự trả lời "không tìm thấy" nếu tài liệu không có — tránh từ chối nhầm câu đã tìm đúng đoạn nhưng cosine thấp.
    threshold = settings.rag_llm_min_similarity if use_llm else settings.rag_similarity_threshold
    best_cosine = max((c.get("cosine", c["score"]) for c in chunks), default=0.0)
    # Độ trùng từ khoá hiếm tốt nhất: câu hỏi chứa thuật ngữ có trong tài liệu (vd "PUT", "PATCH") nhưng embedding chấm thấp
    best_lexical = max((c.get("lexical", 0.0) for c in chunks), default=0.0)
    logger.info(
        "[RAG] retrieved_chunks=%d best_similarity=%.4f best_lexical=%.4f threshold=%.2f",
        len(chunks), best_cosine, best_lexical, threshold,
    )
    passes = best_cosine >= threshold or (use_llm and best_lexical >= settings.rag_llm_min_lexical)
    if not chunks or not passes:
        logger.info("[RAG] below threshold -> refusing (no_answer)")
        return {"answer": NO_ANSWER, "sources": [], "used_context": False}
    # Có LLM: ghép thêm đoạn liền trước / liền sau để LLM đọc trọn ý (danh sách, định nghĩa bị cắt ngang giữa
    # 2 đoạn). Offline giữ nguyên đoạn ngắn vì bộ trích xuất chọn câu theo từng đoạn.
    relevant = retriever.expand_neighbors(db, chunks) if use_llm else chunks

    # Ghép các đoạn thành NGỮ CẢNH, mỗi đoạn gắn nhãn [Nguồn i] + tên tài liệu + số trang
    ctx_parts = []
    for i, c in enumerate(relevant, start=1):
        loc = f" (trang {c['page']})" if c.get("page") else ""
        ctx_parts.append(f"[Nguồn {i}] {c['document_title']}{loc}\n{c['content']}")
    context = "\n\n".join(ctx_parts)

    if not use_llm:
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

        if text.startswith("[Lỗi gọi LLM"):
            # LLM lỗi (hết hạn mức, mất mạng...): dự phòng bằng trích xuất offline từ chính các đoạn tìm được,
            # chỉ khi tài liệu đủ liên quan theo ngưỡng chặt của chế độ offline (tránh trả lời câu lạc đề)
            fallback = extractive.answer(question, chunks) if best_cosine >= settings.rag_similarity_threshold else ""
            if not fallback:
                return {"answer": text.strip(), "sources": [], "used_context": False}
            logger.warning("[RAG] LLM lỗi -> trả lời trích xuất dự phòng")
            text = f"{fallback}\n\n(Trợ giảng AI đang tạm gián đoạn — đây là nội dung trích trực tiếp từ tài liệu khóa học.)"
        if _is_refusal(text):
            return {"answer": NO_ANSWER, "sources": [], "used_context": False}

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
