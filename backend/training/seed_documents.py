"""(DEMO) Nạp sẵn vài tài liệu mẫu vào RAG để AI Tutor hoạt động ngay.

    python training/seed_documents.py

Bỏ qua nếu tài liệu cùng tên đã tồn tại. Không phụ thuộc HTTP — gọi thẳng pipeline.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.rag import ingest  # noqa: E402
from app.core.database import SessionLocal, q_one  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# (đường dẫn file, course_id, lesson_id, tiêu đề)
DOCS = [
    ("sample_docs/python_co_ban.txt", 1, None, "Python Cơ Bản — Tài liệu tổng hợp"),
    ("sample_docs/javascript_nen_tang.txt", 2, None, "JavaScript Nền Tảng — Tài liệu tổng hợp"),
    ("sample_docs/http_web_co_ban.txt", 2, None, "HTTP và Nền Tảng Web"),
]


def main():
    db = SessionLocal()
    done = 0
    try:
        for rel, course_id, lesson_id, title in DOCS:
            path = os.path.join(HERE, rel)
            if not os.path.exists(path):
                print(f"  ! bỏ qua (không thấy file): {rel}")
                continue
            if q_one(db, "SELECT id FROM documents WHERE title = :t AND course_id = :c", t=title, c=course_id):
                print(f"  = đã có: {title}")
                continue
            doc = ingest.create_document(
                db,
                course_id=course_id,
                lesson_id=lesson_id,
                title=title,
                filename=os.path.basename(path),
                file_path=path,
                file_type="txt",
                uploaded_by=None,
            )
            doc = ingest.ingest_document(db, doc["id"])
            print(f"  + {title}  ->  {doc['chunk_count']} đoạn (status={doc['status']})")
            done += 1
    finally:
        db.close()
    print(f"Xong. Đã nạp {done} tài liệu mới.")


if __name__ == "__main__":
    main()
