"""Trả lời trích xuất (extractive) — dùng khi KHÔNG cấu hình LLM (chạy offline).

Chọn câu theo điểm lai: 0.4 * cosine(câu, câu hỏi) + 0.6 * độ trùng từ khóa.
Trả 1–3 câu liên quan nhất, giữ đúng thứ tự trong tài liệu.
"""
from __future__ import annotations

import re

import numpy as np

from . import embeddings
from .retriever import _tokens

# Mẫu tách câu theo dấu kết thúc câu
_SPLIT = re.compile(r"(?<=[.!?…])\s+")


# Tách đoạn thành câu, bỏ câu quá ngắn hoặc mảnh câu bị cắt dở ở ranh giới đoạn
def _sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    out = []
    for s in _SPLIT.split(text):
        s = s.strip(" -•\t")
        # bỏ mảnh câu bị cắt ở ranh giới chunk (bắt đầu bằng dấu phẩy / chữ thường)
        if len(s) >= 25 and not s[0] in ",.;:)" and not s[0].islower():
            out.append(s)
    return out


# Chọn câu trả lời trực tiếp từ tài liệu (không cần LLM)
def answer(question: str, chunks: list[dict], *, max_sentences: int = 2) -> str:
    # Gom mọi câu (không trùng) từ các đoạn đã truy hồi làm ứng viên
    cands: list[str] = []
    for c in chunks:
        for s in _sentences(c["content"]):
            if s not in cands:
                cands.append(s)
    if not cands:
        return ""

    # Chấm điểm từng câu: 0.4 * cosine(câu, câu hỏi) + 0.6 * độ trùng từ khóa
    q_tok = _tokens(question)
    qv = np.array(embeddings.embed_query(question), dtype=np.float32)
    mv = np.array(embeddings.embed_texts(cands), dtype=np.float32)
    denom = (np.linalg.norm(mv, axis=1) * (np.linalg.norm(qv) or 1e-9)) + 1e-9
    cos = (mv @ qv) / denom

    scored = []
    for i, s in enumerate(cands):
        overlap = len(q_tok & _tokens(s)) / (len(q_tok) or 1)
        scored.append((i, 0.4 * float(cos[i]) + 0.6 * overlap))

    # Giữ tối đa 2 câu điểm >= 0.2 (không câu nào đạt thì lấy câu tốt nhất)
    best = sorted(scored, key=lambda x: x[1], reverse=True)[: max_sentences + 3]
    keep = [i for i, sc in best if sc >= 0.2][:max_sentences]
    if not keep:
        keep = [best[0][0]]
    keep.sort()
    return " ".join(cands[i] for i in keep)
