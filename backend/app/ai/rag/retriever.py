"""Truy hồi ngữ cảnh: embed câu hỏi -> top-k chunk cùng khóa + re-rank lai (hybrid).

Hybrid = 0.55 * cosine(embedding) + 0.45 * độ trùng từ khóa (lexical) — giúp bắt
đúng đoạn chứa thuật ngữ khóa ("def", "phi trạng thái", "typeof"...).
"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.core.config import settings

from . import embeddings, vector_store

# Từ dừng tiếng Việt: xuất hiện quá phổ biến nên bỏ qua khi tính độ trùng từ khóa
_STOP = {
    "là", "và", "của", "có", "trong", "được", "cho", "các", "một", "những", "khi",
    "gì", "nào", "thì", "này", "đó", "với", "ra", "để", "hay", "hoặc", "không",
    "nó", "bạn", "tôi", "về", "ở", "trên", "dưới", "theo", "như", "vì", "sao",
}


# Tách văn bản thành tập từ khóa (chữ thường, bỏ từ 1 ký tự và từ dừng)
def _tokens(text: str) -> set[str]:
    words = re.findall(r"[0-9A-Za-zÀ-ỹ_]+", text.lower())
    return {w for w in words if len(w) > 1 and w not in _STOP}


# Truy hồi các đoạn tài liệu liên quan nhất tới câu hỏi
def retrieve(
    db: Session,
    question: str,
    *,
    course_id: int,
    lesson_id: int | None = None,
    lesson_only: bool = False,
    k: int | None = None,
) -> list[dict]:
    k = k or settings.ai_max_context_chunks
    # Bước 1: tạo vector câu hỏi, lấy nhóm ứng viên gấp 3 lần k (tối thiểu 8) theo cosine
    qv = embeddings.embed_query(question)
    pool = vector_store.search(
        db, qv, course_id=course_id, lesson_id=lesson_id, lesson_only=lesson_only, k=max(k * 3, 8)
    )
    if not pool:
        return []

    # Bước 2: xếp hạng lại theo điểm lai = 0.55 * cosine + 0.45 * tỷ lệ từ khóa của câu hỏi có trong đoạn
    q_tok = _tokens(question)
    for c in pool:
        overlap = len(q_tok & _tokens(c["content"])) / (len(q_tok) or 1)
        c["cosine"] = c["score"]
        c["hybrid"] = round(0.55 * c["score"] + 0.45 * overlap, 4)

    pool.sort(key=lambda c: c["hybrid"], reverse=True)
    top = pool[:k]
    # 'score' để pipeline lọc ngưỡng vẫn là cosine gốc (giữ chặn câu hỏi lạc đề)
    for c in top:
        c["score"] = c["cosine"]
    return top
