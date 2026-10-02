"""Truy hồi ngữ cảnh: embed câu hỏi -> top-k chunk cùng khóa + re-rank lai (hybrid).

Hybrid = 0.55 * cosine(embedding) + 0.45 * độ trùng từ khóa (lexical) — giúp bắt
đúng đoạn chứa thuật ngữ khóa ("def", "phi trạng thái", "typeof"...).
"""
from __future__ import annotations

import math
import re

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import q_all

from . import embeddings, vector_store

# Từ dừng tiếng Việt: xuất hiện quá phổ biến nên bỏ qua khi tính độ trùng từ khóa
_STOP = {
    "là", "và", "của", "có", "trong", "được", "cho", "các", "một", "những", "khi",
    "gì", "nào", "thì", "này", "đó", "với", "ra", "để", "hay", "hoặc", "không",
    "nó", "bạn", "tôi", "về", "ở", "trên", "dưới", "theo", "như", "vì", "sao",
    # từ đệm của câu hỏi ("dùng để làm gì", "thế nào", "cho biết") — hiếm trong tài liệu nên IDF chấm quá cao
    "làm", "dùng", "thế", "biết", "hãy", "ạ",
}


# Tách văn bản thành tập từ khóa (chữ thường, bỏ từ 1 ký tự và từ dừng)
def _tokens(text: str) -> set[str]:
    words = re.findall(r"[0-9A-Za-zÀ-ỹ_]+", text.lower())
    return {w for w in words if len(w) > 1 and w not in _STOP}


# Hàm chấm độ trùng từ khoá có trọng số IDF: từ càng hiếm trong tài liệu của khoá càng có giá trị
# ("fragment", "alt" nặng hơn "dùng", "làm"). Điểm 0..1 cho từng đoạn = tổng IDF từ trùng / tổng IDF từ của câu hỏi.
def idf_overlap(q_tok: set[str]):
    def score(texts: list[str]) -> list[float]:
        toks = [_tokens(t) for t in texts]
        n = len(toks)
        idf = {w: math.log((n + 1) / (1 + sum(1 for t in toks if w in t))) + 1 for w in q_tok}
        total = sum(idf.values()) or 1.0
        return [sum(idf[w] for w in q_tok & t) / total for t in toks]
    return score


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
    # Bước 1: tạo vector câu hỏi, lấy nhóm ứng viên gấp 3 lần k (tối thiểu 8) theo cosine,
    # cộng thêm k đoạn trùng từ khoá hiếm nhiều nhất (đoạn chứa thuật ngữ đặc thù mà embedding chấm thấp)
    q_tok = _tokens(question)
    qv = embeddings.embed_query(question)
    pool = vector_store.search(
        db, qv, course_id=course_id, lesson_id=lesson_id, lesson_only=lesson_only, k=max(k * 3, 8),
        lexical_score=idf_overlap(q_tok) if q_tok else None, k_lexical=k,
    )
    if not pool:
        return []

    # Bước 2: xếp hạng lại theo điểm lai = 0.55 * cosine + 0.45 * độ trùng từ khoá có trọng số IDF
    # (từ hiếm như "fragment" quyết định hơn từ chung như "react", "dùng")
    for c in pool:
        c["cosine"] = c["score"]
        c.setdefault("lexical", 0.0)
        c["hybrid"] = round(0.55 * c["score"] + 0.45 * c["lexical"], 4)

    pool.sort(key=lambda c: c["hybrid"], reverse=True)
    top = pool[:k]
    # 'score' để pipeline lọc ngưỡng vẫn là cosine gốc (giữ chặn câu hỏi lạc đề)
    for c in top:
        c["score"] = c["cosine"]
    return top


# Nối 2 đoạn liền nhau của cùng tài liệu: đoạn sau bắt đầu bằng phần đuôi của đoạn trước (overlap của
# text_splitter) -> bỏ phần trùng để không lặp chữ
def _join(a: str, b: str) -> str:
    for k in range(min(len(a), len(b), 120), 9, -1):
        if a.endswith(b[:k]):
            return a + b[k:]
    return f"{a}\n{b}"


# Mở rộng ngữ cảnh: đoạn tìm được thường chỉ là phần đầu của một ý dài (vd "bốn điều kiện sau ..." mà các
# điều kiện nằm ở các đoạn liền sau, do đoạn chỉ ~380 ký tự). Ghép mỗi đoạn với `before` đoạn liền trước và
# `after` đoạn liền sau trong cùng tài liệu thành 1 đoạn văn liền mạch; các cửa sổ chồng nhau thì gộp lại.
# Giữ thứ tự xếp hạng và thông tin (điểm, trang, tài liệu) của đoạn tìm được tốt nhất trong mỗi đoạn văn.
def expand_neighbors(db: Session, chunks: list[dict], *, before: int | None = None, after: int | None = None,
                     max_chars: int | None = None) -> list[dict]:
    before = settings.rag_neighbor_before if before is None else before
    after = settings.rag_neighbor_after if after is None else after
    max_chars = max_chars or settings.rag_max_context_chars
    hits = [c for c in chunks if c.get("chunk_index") is not None]
    if not hits or (before == 0 and after == 0):
        return chunks

    # Gộp cửa sổ [idx - before, idx + after] của các đoạn cùng tài liệu; cửa sổ chạm / chồng nhau thành 1 đoạn văn
    windows: dict[int, list[list]] = {}
    for rank, c in enumerate(hits):
        lo, hi = c["chunk_index"] - before, c["chunk_index"] + after
        spans = windows.setdefault(c["document_id"], [])
        for s in spans:
            if lo <= s[1] + 1 and hi >= s[0] - 1:
                s[0], s[1] = min(s[0], lo), max(s[1], hi)
                s[2].append(rank)
                break
        else:
            spans.append([lo, hi, [rank]])

    # Lấy nội dung các đoạn cần thêm (1 truy vấn cho mỗi tài liệu)
    texts: dict[tuple[int, int], str] = {}
    for doc_id, spans in windows.items():
        lo, hi = min(s[0] for s in spans), max(s[1] for s in spans)
        for r in q_all(db, "SELECT chunk_index, content FROM document_chunks WHERE document_id = :d "
                           "AND chunk_index BETWEEN :lo AND :hi", d=doc_id, lo=lo, hi=hi):
            texts[(doc_id, r["chunk_index"])] = r["content"]

    out = []
    for doc_id, spans in windows.items():
        for lo, hi, ranks in spans:
            best = dict(hits[min(ranks)])
            body = ""
            for i in range(lo, hi + 1):
                if (doc_id, i) in texts:
                    body = _join(body, texts[(doc_id, i)]) if body else texts[(doc_id, i)]
            best["content"] = body or best["content"]
            best["rank"] = min(ranks)
            out.append(best)
    out.sort(key=lambda c: c["rank"])

    # Giới hạn tổng độ dài ngữ cảnh: giữ các đoạn văn xếp hạng cao trước (luôn giữ đoạn đầu tiên)
    kept, total = [], 0
    for c in out:
        if kept and total + len(c["content"]) > max_chars:
            break
        kept.append(c)
        total += len(c["content"])
    return kept
