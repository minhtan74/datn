"""Vector store tối giản trên MySQL (bảng document_chunks, cột embedding JSON).

Truy vấn: tải chunk theo course (+lesson nếu có), tính cosine similarity bằng numpy,
lấy top-k. Đủ nhanh cho quy mô DATN (vài trăm–vài nghìn chunk / khóa).
"""
from __future__ import annotations

import json
from collections.abc import Callable

import numpy as np
from sqlalchemy.orm import Session

from app.core.database import execute, q_all


# Lưu từng đoạn văn bản kèm vector embedding (dạng JSON) vào bảng document_chunks
def add_chunks(
    db: Session,
    *,
    document_id: int,
    course_id: int,
    lesson_id: int | None,
    chunks: list[dict],
    embeddings: list[list[float]],
    token_counts: list[int],
) -> int:
    n = 0
    for ch, emb, tk in zip(chunks, embeddings, token_counts):
        execute(
            db,
            "INSERT INTO document_chunks "
            "(document_id, course_id, lesson_id, chunk_index, page, content, embedding, token_count) "
            "VALUES (:d, :c, :l, :idx, :pg, :content, :emb, :tk)",
            d=document_id,
            c=course_id,
            l=lesson_id,
            idx=ch["index"],
            pg=ch["page"],
            content=ch["text"],
            emb=json.dumps(emb),
            tk=tk,
        )
        n += 1
    return n


# Tải các đoạn đã lập chỉ mục của khóa học; có lesson_id thì lọc theo bài
# (lesson_only=True: chỉ tài liệu của bài; False: tài liệu của bài + tài liệu chung của khóa)
def _load(db: Session, course_id: int, lesson_id: int | None, lesson_only: bool = False) -> list[dict]:
    sql = (
        "SELECT dc.id, dc.document_id, dc.page, dc.content, dc.embedding, d.title AS document_title "
        "FROM document_chunks dc JOIN documents d ON d.id = dc.document_id "
        "WHERE dc.course_id = :c AND d.status = 'indexed'"
    )
    params = {"c": course_id}
    if lesson_id:
        if lesson_only:
            sql += " AND dc.lesson_id = :l"
        else:
            sql += " AND (dc.lesson_id = :l OR dc.lesson_id IS NULL)"
        params["l"] = lesson_id
    return q_all(db, sql, **params)


def search(
    db: Session,
    query_vec: list[float],
    *,
    course_id: int,
    lesson_id: int | None = None,
    lesson_only: bool = False,
    k: int = 5,
    lexical_score: Callable[[list[str]], list[float]] | None = None,
    k_lexical: int = 0,
) -> list[dict]:
    # Tải toàn bộ vector ứng viên của khóa học
    rows = _load(db, course_id, lesson_id, lesson_only)
    if not rows:
        return []

    # Ghép thành ma trận numpy rồi tính cosine similarity giữa câu hỏi và mọi đoạn cùng lúc
    mat = np.array(
        [json.loads(r["embedding"]) if isinstance(r["embedding"], str) else r["embedding"] for r in rows],
        dtype=np.float32,
    )
    q = np.array(query_vec, dtype=np.float32)
    denom = (np.linalg.norm(mat, axis=1) * (np.linalg.norm(q) or 1e-9)) + 1e-9
    sims = (mat @ q) / denom

    # Lấy k đoạn có độ tương đồng cao nhất; thêm k_lexical đoạn trùng từ khoá nhiều nhất (nếu có hàm chấm từ khoá)
    # để không bỏ lỡ đoạn chứa thuật ngữ hiếm ("alt", "Fragment", "đoàn xe") mà embedding chấm thấp
    order = [int(i) for i in np.argsort(-sims)[:k]]
    lex = [0.0] * len(rows)
    if lexical_score and k_lexical:
        lex = lexical_score([r["content"] for r in rows])
        for i in sorted(range(len(rows)), key=lambda j: -lex[j])[:k_lexical]:
            if lex[i] > 0 and i not in order:
                order.append(i)
    out = []
    for i in order:
        r = rows[i]
        out.append(
            {
                "chunk_id": r["id"],
                "document_id": r["document_id"],
                "document_title": r["document_title"],
                "page": r["page"],
                "content": r["content"],
                "score": round(float(sims[i]), 4),
                "lexical": round(float(lex[i]), 4),
            }
        )
    return out
