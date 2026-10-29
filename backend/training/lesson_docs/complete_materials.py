"""Kiểm tra tài liệu thực tế, dựng PDF và bổ sung có lưu nhật ký.

Chạy từ backend: python training/lesson_docs/complete_materials.py [--build | --apply]
Mặc định chỉ kiểm tra; --apply yêu cầu PDF đã dựng bằng --build.
Giữ file gốc, ghi URL trước/sau để đối chiếu; không dùng ID khóa demo để chọn nội dung.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from app.core.config import settings
from app.core.database import SessionLocal, execute, q_all, q_one
from app.core.media import resolve_upload_path
from app.ai.rag import ingest
from pypdf import PdfReader, PdfWriter
from build_pdfs import find_chrome, load_lessons, render

OUT = HERE / "completed"
KEYWORDS = [("python", "python"), ("javascript", "javascript"), ("java", "java"),
            ("html", "html_css"), ("react", "react"), ("mysql", "mysql"),
            ("hệ điều hành", "os"), ("hđh", "os"), ("hdh", "os")]


def course_key(title):
    return next((key for word, key in KEYWORDS if word in title.lower()), None)


def pdf_text(path):
    if not path or not Path(path).is_file():
        return ""
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def make_pdf(meta, content, output, chrome):
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "material.html"
        page.write_text(render(meta, content), encoding="utf-8")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={Path(tmp) / 'profile'}",
                        f"--print-to-pdf={output}", page.as_uri()],
                       check=True, capture_output=True, timeout=90)
    if len(pdf_text(output)) < 500:
        raise RuntimeError(f"PDF chưa trích xuất được nội dung: {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    db = SessionLocal()
    try:
        courses = q_all(db, "SELECT id,title,teacher_id FROM courses ORDER BY id")
        lessons = q_all(db, "SELECT l.*,ch.course_id,ch.chapter_name FROM lessons l "
                        "JOIN chapters ch ON ch.id=l.chapter_id "
                        "ORDER BY ch.course_id,ch.order_index,ch.id,l.order_index,l.id")
        contents = load_lessons()
        source_meta = {r["lesson_id"]: r for r in json.loads((HERE / "lessons.json").read_text(encoding="utf-8"))}
        audit = []
        for lesson in lessons:
            path = resolve_upload_path(lesson["document_url"])
            text = pdf_text(path)
            audit.append({"lesson_id": lesson["id"], "course_id": lesson["course_id"],
                          "title": lesson["title"], "original_url": lesson["document_url"],
                          "file_exists": bool(path and Path(path).is_file()),
                          "text_chars": len(text), "missing": not text.strip()})
        (OUT / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
        if not (OUT / "audit_before.json").exists():
            (OUT / "audit_before.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Kiểm tra {len(courses)} khóa, {len(lessons)} bài; thiếu {sum(a['missing'] for a in audit)} PDF đọc được.", flush=True)
        if not args.build and not args.apply:
            return
        chrome = find_chrome() if args.build else None
        missing_ids = {a["lesson_id"] for a in audit if a["missing"]}
        plans = []
        # Dùng nội dung bài đã có nhưng chỉ khi ID và tiêu đề khớp dữ liệu thật.
        for lesson in lessons:
            if lesson["id"] not in missing_ids:
                continue
            lid = lesson["id"]
            if lid not in contents or source_meta.get(lid, {}).get("title") != lesson["title"]:
                raise RuntimeError(f"Không có nội dung khớp bài {lid}: {lesson['title']}")
            output = OUT / f"lesson_{lid}.pdf"
            if args.build:
                meta = {**source_meta[lid], "title": lesson["title"]}
                make_pdf(meta, contents[lid], output, chrome)
                print(f"Dựng tài liệu bài {lid}", flush=True)
            plans.append((lesson, output))
        for course in courses:
            key = course_key(course["title"])
            course_lessons = [l for l in lessons if l["course_id"] == course["id"]]
            if not key or not course_lessons:
                raise RuntimeError(f"Chưa có học thêm phù hợp khóa {course['title']}")
            last = course_lessons[-1]
            workbook = OUT / f"supplement_course_{course['id']}.pdf"
            bundle = OUT / f"bundle_lesson_{last['id']}.pdf"
            if args.build:
                meta = dict(course_title=course["title"], chapter_no="Học thêm", lesson_no="Tổng hợp",
                            title="Học thêm, bài tập và hướng dẫn giải", chapter_name="Thực hành mở rộng")
                make_pdf(meta, (HERE / "supplements" / f"{key}.md").read_text(encoding="utf-8"), workbook, chrome)
                ledger_file = OUT / "changes.json"
                old_changes = json.loads(ledger_file.read_text(encoding="utf-8")) if ledger_file.exists() else []
                previous = next((change["previous_url"] for change in old_changes
                                 if change["lesson_id"] == last["id"]), last["document_url"])
                generated = OUT / f"lesson_{last['id']}.pdf"
                # Không ghép thêm lần nữa vào PDF đã có phần học thêm khi chạy lại.
                primary = generated if generated.exists() else Path(resolve_upload_path(previous))
                writer = PdfWriter()
                writer.append(str(primary))
                writer.append(str(workbook))
                with bundle.open("wb") as stream:
                    writer.write(stream)
                print(f"Dựng học thêm khóa {course['id']}; ghép vào bài {last['id']}", flush=True)
            # Nếu bài cuối cũng thiếu, chỉ gắn bản ghép một lần.
            plans = [(l, p) for l, p in plans if l["id"] != last["id"]]
            plans.append((last, bundle))
        if not args.apply:
            return
        if any(not path.is_file() for _, path in plans):
            raise RuntimeError("Chạy --build trước khi --apply")
        upload_dir = Path(settings.upload_dir).resolve() / "documents"
        upload_dir.mkdir(parents=True, exist_ok=True)
        ledger_path = OUT / "changes.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
        for lesson, src in plans:
            dest = upload_dir / f"completed_{src.name}"
            url = f"{settings.public_base_url.rstrip('/')}/uploads/documents/{dest.name}"
            # Chạy lại không ghi đè hoặc nạp trùng PDF đã được gắn.
            if lesson["document_url"] == url:
                pending = q_all(db, "SELECT id FROM documents WHERE lesson_id=:l AND status <> 'indexed'", l=lesson["id"])
                for doc in pending:
                    ingest.ingest_document(db, doc["id"])
                continue
            old_path = resolve_upload_path(lesson["document_url"])
            shutil.copyfile(src, dest)
            ledger.append(dict(lesson_id=lesson["id"], previous_url=lesson["document_url"], new_url=url,
                               original_file=old_path))
            ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
            execute(db, "UPDATE lessons SET document_url=:url WHERE id=:id", url=url, id=lesson["id"])
            # Đồng bộ bản ghi tài liệu chính đang trỏ file cũ để quiz đọc đúng bản bổ sung.
            documents = q_all(db, "SELECT id,file_path FROM documents WHERE lesson_id=:l", l=lesson["id"])
            match = next((d for d in documents if old_path and Path(d["file_path"]).resolve() == Path(old_path).resolve()), None)
            if match:
                execute(db, "UPDATE documents SET file_path=:p,filename=:f,status='pending' WHERE id=:id",
                        p=str(dest), f=dest.name, id=match["id"])
                ingest.ingest_document(db, match["id"])
            else:
                if not ingest.ensure_lesson_document(db, lesson["id"]):
                    raise RuntimeError(f"Không lập chỉ mục được bài {lesson['id']}; xem documents.error")
            print(f"Gắn và lập chỉ mục bài {lesson['id']}", flush=True)
        # Học thêm độc lập theo khóa để AI Tutor tìm được cả khi hỏi ngoài bài cuối.
        for course in courses:
            title = f"{course['title']} — Học thêm và thực hành tổng hợp"
            doc = q_one(db, "SELECT id,status FROM documents WHERE course_id=:c AND lesson_id IS NULL AND title=:t",
                        c=course["id"], t=title)
            if not doc:
                src = OUT / f"supplement_course_{course['id']}.pdf"
                dest = upload_dir / f"completed_{src.name}"
                shutil.copyfile(src, dest)
                doc = ingest.create_document(db, course_id=course["id"], lesson_id=None,
                        title=title, filename=dest.name, file_path=str(dest), file_type="pdf", uploaded_by=course["teacher_id"])
            if doc.get("status") != "indexed":
                ingest.ingest_document(db, doc["id"])
            print(f"Lập chỉ mục học thêm khóa {course['id']}", flush=True)
    finally:
        db.close()


if __name__ == "__main__":
    main()
