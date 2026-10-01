"""(DEMO) Gắn tài liệu PDF cho các bài học đang chỉ có đường dẫn mẫu (vd "docs/py_02.pdf").

    python training/lesson_docs/seed_lesson_docs.py            # áp dụng
    python training/lesson_docs/seed_lesson_docs.py --dry-run  # chỉ liệt kê, không ghi

Với mỗi bài có trong pdf/lesson_<id>.pdf mà lessons.document_url còn là đường dẫn mẫu (không trỏ tới /uploads/):
chép file vào uploads/documents (tên ngẫu nhiên như file giảng viên tải lên) rồi cập nhật lessons.document_url.
Bài đã có PDF thật được giữ nguyên; chạy lại nhiều lần không tạo trùng.
Khi học viên bấm "Hỏi AI", hệ thống tự nạp PDF này vào RAG (ingest.ensure_lesson_document).
"""
import os
import secrets
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal, execute, q_all  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "pdf")


def main() -> None:
    dry = "--dry-run" in sys.argv
    dest_dir = os.path.join(os.path.abspath(settings.upload_dir), "documents")
    os.makedirs(dest_dir, exist_ok=True)
    db = SessionLocal()
    done = skipped = 0
    try:
        for row in q_all(db, "SELECT id, title, document_url FROM lessons ORDER BY id"):
            src = os.path.join(PDF_DIR, f"lesson_{row['id']}.pdf")
            url = row["document_url"] or ""
            if not os.path.exists(src):
                continue
            # Đã trỏ tới file upload thật thì giữ nguyên
            if "/uploads/" in url:
                skipped += 1
                continue
            name = f"{int(time.time())}_{secrets.token_hex(6)}.pdf"
            new_url = f"{settings.public_base_url.rstrip('/')}/uploads/documents/{name}"
            print(f"  {'[thử] ' if dry else ''}bài {row['id']:2d} {row['title']}  ->  {name}")
            if not dry:
                shutil.copyfile(src, os.path.join(dest_dir, name))
                execute(db, "UPDATE lessons SET document_url = :u WHERE id = :id", u=new_url, id=row["id"])
            done += 1
    finally:
        db.close()
    print(f"Xong. {'Sẽ gắn' if dry else 'Đã gắn'} {done} tài liệu, giữ nguyên {skipped} bài đã có PDF thật.")


if __name__ == "__main__":
    main()
