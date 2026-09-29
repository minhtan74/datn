"""Nạp tài liệu vào vector store: extract -> split -> embed -> lưu document_chunks."""
from __future__ import annotations

import logging
import os

from sqlalchemy.orm import Session

from app.core.database import execute, q_one
from app.core.media import resolve_upload_path

from . import document_loader, embeddings, text_splitter, vector_store

logger = logging.getLogger("rag")


# Tạo bản ghi tài liệu mới ở trạng thái 'pending' (chưa lập chỉ mục)
def create_document(
    db: Session,
    *,
    course_id: int,
    lesson_id: int | None,
    title: str,
    filename: str,
    file_path: str,
    file_type: str,
    uploaded_by: int | None,
) -> dict:
    res = execute(
        db,
        "INSERT INTO documents (course_id, lesson_id, uploaded_by, title, filename, file_path, file_type, status) "
        "VALUES (:c, :l, :u, :t, :fn, :fp, :ft, 'pending')",
        c=course_id,
        l=lesson_id,
        u=uploaded_by,
        t=title,
        fn=filename,
        fp=file_path,
        ft=file_type,
    )
    return q_one(db, "SELECT * FROM documents WHERE id = :id", id=res.lastrowid)


# Lập chỉ mục 1 tài liệu cho RAG
def ingest_document(db: Session, document_id: int) -> dict:
    doc = q_one(db, "SELECT * FROM documents WHERE id = :id", id=document_id)
    if not doc:
        raise ValueError("Không tìm thấy tài liệu.")

    logger.info("[RAG] Processing document: %s (%s)", document_id, doc["file_type"])
    try:
        # Bước 1: trích xuất văn bản (theo từng trang nếu là PDF)
        pages, total_pages = document_loader.extract(doc["file_path"], doc["file_type"])
        logger.info("[RAG] Extracted pages: %s (có text: %d)", total_pages, len(pages))
        # Bước 2: chia thành các đoạn nhỏ; không có đoạn nào nghĩa là PDF dạng ảnh scan (không có lớp chữ)
        chunks = text_splitter.split_pages(pages)
        if not chunks:
            raise ValueError(
                "Tài liệu không chứa lớp văn bản có thể đọc. "
                "Vui lòng sử dụng PDF có text hoặc bổ sung OCR."
            )
        logger.info("[RAG] Created chunks: %d", len(chunks))

        # Bước 3: tạo embedding cho mọi đoạn và ước lượng số token
        vecs = embeddings.embed_texts([c["text"] for c in chunks])
        tokens = [text_splitter.approx_tokens(c["text"]) for c in chunks]
        logger.info("[RAG] Embeddings generated")

        # xoá chunk cũ (nếu ingest lại) rồi thêm mới
        execute(db, "DELETE FROM document_chunks WHERE document_id = :d", d=document_id)
        # Bước 4: lưu các đoạn + vector vào CSDL
        n = vector_store.add_chunks(
            db,
            document_id=document_id,
            course_id=doc["course_id"],
            lesson_id=doc["lesson_id"],
            chunks=chunks,
            embeddings=vecs,
            token_counts=tokens,
        )
        # Đánh dấu tài liệu đã lập chỉ mục thành công
        execute(
            db,
            "UPDATE documents SET status='indexed', pages=:p, chunk_count=:n, error=NULL WHERE id=:id",
            p=total_pages,
            n=n,
            id=document_id,
        )
        logger.info("[RAG] Indexed successfully: document_id=%s chunks=%d", document_id, n)
    # Có lỗi: đánh dấu 'failed' kèm lý do (tối đa 500 ký tự) rồi báo lỗi lên trên
    except Exception as e:  # noqa: BLE001
        logger.warning("[RAG] Indexing failed for document_id=%s: %s", document_id, e)
        execute(
            db,
            "UPDATE documents SET status='failed', error=:err WHERE id=:id",
            err=str(e)[:500],
            id=document_id,
        )
        raise

    return q_one(db, "SELECT * FROM documents WHERE id = :id", id=document_id)


_resolve_upload_path = resolve_upload_path


def ensure_lesson_document(db: Session, lesson_id: int) -> bool:
    """Tự động nạp PDF đính kèm bài học (lessons.document_url) vào RAG khi học viên
    lần đầu bấm "Hỏi AI" trên trang bài học — không cần giảng viên upload lại thủ công
    qua màn hình Tài liệu. Bỏ qua nếu bài học đã có tài liệu (đã nạp hoặc từng thử/lỗi)."""
    # Bài học đã có tài liệu (đã nạp hoặc đã từng thử) thì không nạp lại
    if q_one(db, "SELECT id FROM documents WHERE lesson_id = :l", l=lesson_id):
        return True

    # Lấy link PDF của bài học; không có PDF hoặc file không tồn tại thì bỏ qua
    lesson = q_one(
        db,
        "SELECT l.title, l.document_url, ch.course_id "
        "FROM lessons l JOIN chapters ch ON ch.id = l.chapter_id WHERE l.id = :id",
        id=lesson_id,
    )
    if not lesson or not lesson["document_url"]:
        return False

    file_path = _resolve_upload_path(lesson["document_url"])
    if not file_path or not os.path.exists(file_path):
        return False

    # Tạo tài liệu và lập chỉ mục ngay; lỗi thì trả False (trạng thái 'failed' đã được ghi)
    doc = create_document(
        db,
        course_id=lesson["course_id"],
        lesson_id=lesson_id,
        title=lesson["title"],
        filename=os.path.basename(file_path),
        file_path=file_path,
        file_type="pdf",
        uploaded_by=None,
    )
    try:
        ingest_document(db, doc["id"])
    except Exception:  # noqa: BLE001 — đã ghi status='failed' bên trong ingest_document
        return False
    return True
