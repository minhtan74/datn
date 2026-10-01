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
    ("sample_docs/java_can_ban.txt", 3, None, "Lập Trình Java Căn Bản — Tài liệu tổng hợp"),
    ("sample_docs/html_css_nhap_mon.txt", 4, None, "HTML & CSS Nhập Môn — Tài liệu tổng hợp"),
    ("sample_docs/reactjs_chuyen_sau.txt", 5, None, "ReactJS Chuyên Sâu — Tài liệu tổng hợp"),
    ("sample_docs/mysql_thiet_ke_csdl.txt", 6, None, "MySQL & Thiết Kế CSDL — Tài liệu tổng hợp"),
    # Khóa Nguyên lí hệ điều hành (id 35) chỉ có trong CSDL đang dùng, không có trong sample_data.sql
    ("sample_docs/nguyen_li_he_dieu_hanh.txt", 35, None, "Nguyên Lí Hệ Điều Hành — Tài liệu tổng hợp"),
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
            # Khóa không tồn tại trong CSDL này thì bỏ qua; người tải lên ghi là giảng viên của khóa
            course = q_one(db, "SELECT teacher_id FROM courses WHERE id = :c", c=course_id)
            if not course:
                print(f"  ! bỏ qua (không có khóa {course_id}): {title}")
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
                uploaded_by=course["teacher_id"],
            )
            doc = ingest.ingest_document(db, doc["id"])
            print(f"  + {title}  ->  {doc['chunk_count']} đoạn (status={doc['status']})")
            done += 1
    finally:
        db.close()
    print(f"Xong. Đã nạp {done} tài liệu mới.")


if __name__ == "__main__":
    main()
