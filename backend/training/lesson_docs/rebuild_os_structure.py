"""Audit every local PDF and rebuild active lessons using the OS lecture structure.

Run from backend: .venv/Scripts/python training/lesson_docs/rebuild_os_structure.py
The output is separate from the original files. --apply updates local lesson links
and reindexes matching RAG documents, with a ledger for restoring previous links.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from pypdf import PdfReader, PdfWriter
from app.core.config import settings
from app.core.database import SessionLocal, execute, q_all
from app.core.media import resolve_upload_path
from build_pdfs import find_chrome, load_lessons, md_to_html
from complete_materials import make_pdf, course_key
import complete_materials

OUT = HERE / 'rebuilt'


def write_json(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


def render_lecture(meta, body):
    course = html.escape(meta['course_title'])
    position = f"Chương {meta['chapter_no']} · Bài {meta['lesson_no']}"
    safe_position = html.escape(position)
    # Chrome's page margin boxes repeat the heading and page number on every page.
    css = '''
    @page { size: A4; margin: 23mm 19mm 20mm;
      @top-left { content: "Bài giảng " COURSE; font: 9pt Arial; color: #475569; }
      @top-right { content: POSITION; font: 9pt Arial; color: #475569; }
      @bottom-left { content: "StudyOnline · Tài liệu học tập"; font: 9pt Arial; color: #64748b; }
      @bottom-right { content: "Trang " counter(page); font: 9pt Arial; color: #64748b; }
    }
    body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; color: #172033; }
    .position { font: bold 10pt Arial; color: #334155; text-transform: uppercase; }
    h1 { font-size: 21pt; line-height: 1.2; margin: 8pt 0; color: #1e3a5f; }
    .source { font-size: 10pt; color: #64748b; margin-bottom: 16pt; }
    h2 { font-size: 14pt; margin: 16pt 0 6pt; break-after: avoid; color: #1e3a5f; }
    p { margin: 6pt 0; text-align: justify; }
    li { margin: 4pt 0; }
    ul,ol { padding-left: 22pt; }
    code { font-family: Consolas, monospace; font-size: 9.5pt; }
    pre { padding: 10pt; background: #f1f5f9; border-left: 2pt solid #94a3b8;
      white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.4; }
    .obj { background: #f3f6fa; border-left: 3pt solid #1e3a5f; padding: 1pt 12pt 6pt; }
    .obj h2 { margin-top: 8pt; }
    '''
    css = css.replace('COURSE', json.dumps(meta['course_title'], ensure_ascii=False)).replace('POSITION', json.dumps(position, ensure_ascii=False))
    body = re.sub(r'^## Bài tập[^\n]*', '## Câu hỏi ôn tập và bài tập vận dụng', body, flags=re.M)
    title = html.escape(meta['title'])
    return f'<!doctype html><html lang="vi"><meta charset="utf-8"><style>{css}</style><body><div class="position">{safe_position}</div><h1>{meta["chapter_no"]}.{meta["lesson_no"]}. {title}</h1><p class="source">Tài liệu học tập {course} · Nội dung biên soạn trong dự án StudyOnline.</p>{md_to_html(body)}</body></html>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--skip-audit', action='store_true', help='Reuse the existing audit when rebuilding after a source correction')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    with SessionLocal() as db:
        rows = q_all(db, 'SELECT l.id,l.title,l.description,l.document_url,l.order_index,ch.id AS chapter_id,ch.chapter_name,ch.order_index AS chapter_order,c.id AS course_id,c.title AS course_title FROM lessons l JOIN chapters ch ON ch.id=l.chapter_id JOIN courses c ON c.id=ch.course_id ORDER BY c.id,ch.order_index,ch.id,l.order_index,l.id')
    if not args.apply:
        write_json('lessons_current.json', rows)
        audit = []
        files = [] if args.skip_audit else sorted(set((HERE.parents[1] / 'uploads').rglob('*.pdf')) | set(HERE.rglob('*.pdf')))
        for path in files:
            if OUT in path.parents:
                continue
            entry = {'path': str(path.relative_to(HERE.parents[1])), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            try:
                reader = PdfReader(path)
                text = '\n'.join(p.extract_text() or '' for p in reader.pages)
                entry.update(pages=len(reader.pages), text_chars=len(text), readable=bool(text.strip()), objectives='Mục tiêu' in text, review=('Câu hỏi ôn tập' in text or 'Bài tập' in text))
            except Exception as exc:
                entry.update(readable=False, error=str(exc))
            audit.append(entry)
        if not args.skip_audit:
            write_json('all_pdfs_audit.json', audit)
            print(f'Audited {len(audit)} PDF files; unreadable: {sum(not x["readable"] for x in audit)}', flush=True)
        source_meta = {r['lesson_id']: r for r in json.loads((HERE / 'lessons.json').read_text(encoding='utf-8'))}
        contents = load_lessons()
        for row in rows:
            if row['id'] == 46 and row['title'] == 'Khái niệm cơ sở dữ liệu':
                source_meta[46] = dict(course_title=row['course_title'], chapter_no=1, lesson_no=1, title=row['title'])
        for row in rows:
            if course_key(row['course_title']) != 'os':
                if row['id'] not in contents or source_meta.get(row['id'], {}).get('title') != row['title']:
                    raise RuntimeError(f'No matching source for lesson {row["id"]}: {row["title"]}')
                if '## Mục tiêu' not in contents[row['id']] or not ('## Bài tập' in contents[row['id']] or '## Câu hỏi ôn tập' in contents[row['id']]):
                    raise RuntimeError(f'Missing objectives/review: {row["id"]}')
        chrome = find_chrome()
        complete_materials.render = render_lecture
        verification = []
        for row in rows:
            lid = row['id']
            target = OUT / f'lesson_{lid}.pdf'
            os_course = course_key(row['course_title']) == 'os'
            if os_course:
                # Retain original diagrams, equations, author credits and typography.
                shutil.copyfile(resolve_upload_path(row['document_url']), target)
            else:
                make_pdf(source_meta[lid], contents[lid], target, chrome)
            reader = PdfReader(target)
            text = '\n'.join(p.extract_text() or '' for p in reader.pages)
            if 'Mục tiêu bài học' not in text or 'Câu hỏi ôn tập' not in text:
                raise RuntimeError(f'Structure verification failed: {lid}')
            verification.append({'lesson_id': lid, 'course': row['course_title'], 'title': row['title'], 'pages': len(reader.pages), 'text_chars': len(text), 'os_original_preserved': os_course, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
            print(f'Verified lesson {lid}: {len(reader.pages)} pages', flush=True)
        # Preserve the existing extra workbook after the last lesson of each course.
        for cid in sorted({r['course_id'] for r in rows}):
            last = [r for r in rows if r['course_id'] == cid][-1]
            if course_key(last['course_title']) == 'os':
                continue  # The preserved OS bundle already includes its workbook.
            meta = dict(course_title=last['course_title'], chapter_no='Học thêm', lesson_no='Tổng hợp', title='Học thêm, bài tập và hướng dẫn giải')
            workbook = OUT / f'supplement_course_{cid}.pdf'
            make_pdf(meta, (HERE / 'supplements' / f'{course_key(last["course_title"])}.md').read_text(encoding='utf-8'), workbook, chrome)
            target = OUT / f'lesson_{last["id"]}.pdf'
            writer = PdfWriter()
            writer.append(str(target))
            writer.append(str(workbook))
            with (OUT / 'bundle.tmp.pdf').open('wb') as stream:
                writer.write(stream)
            (OUT / 'bundle.tmp.pdf').replace(target)
        for entry in verification:
            path = OUT / f'lesson_{entry["lesson_id"]}.pdf'
            entry['pages'] = len(PdfReader(path).pages)
            entry['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json('verification.json', verification)
        print(f'Completed {len(verification)} lessons.', flush=True)
        return

    verified = {r['lesson_id']: r for r in json.loads((OUT / 'verification.json').read_text(encoding='utf-8'))}
    for row in rows:
        path = OUT / f'lesson_{row["id"]}.pdf'
        if verified[row['id']]['title'] != row['title'] or hashlib.sha256(path.read_bytes()).hexdigest() != verified[row['id']]['sha256']:
            raise RuntimeError(f'Changed source/output: {row["id"]}')
    from app.ai.rag import ingest
    ledger_path = OUT / 'applied.json'
    ledger = json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else []
    upload = Path(settings.upload_dir).resolve() / 'documents'
    with SessionLocal() as db:
        for row in rows:
            if course_key(row['course_title']) == 'os':
                continue
            dest = upload / f'os_structure_lesson_{row["id"]}.pdf'
            url = f'{settings.public_base_url.rstrip("/")}/uploads/documents/{dest.name}'
            old_path = resolve_upload_path(row['document_url'])
            if row['document_url'] == url:
                retry_docs = q_all(db, "SELECT id FROM documents WHERE lesson_id=:lid AND file_path=:path AND status <> 'indexed'", lid=row['id'], path=str(dest))
                for doc in retry_docs:
                    ingest.ingest_document(db, doc['id'])
                continue
            shutil.copyfile(OUT / f'lesson_{row["id"]}.pdf', dest)
            ledger.append(dict(lesson_id=row['id'], previous_url=row['document_url'], new_url=url))
            write_json('applied.json', ledger)
            docs = q_all(db, 'SELECT id,file_path FROM documents WHERE lesson_id=:lid', lid=row['id'])
            matches = [d for d in docs if Path(d['file_path']).resolve() == dest.resolve() or (old_path and Path(d['file_path']).resolve() == Path(old_path).resolve())]
            if docs and not matches:
                raise RuntimeError(f'No primary RAG document matches lesson {row["id"]}')
            for doc in matches:
                execute(db, "UPDATE documents SET file_path=:p,filename=:f,status='pending' WHERE id=:id", p=str(dest), f=dest.name, id=doc['id'])
                ingest.ingest_document(db, doc['id'])
            execute(db, 'UPDATE lessons SET document_url=:url WHERE id=:id', url=url, id=row['id'])
            if not docs and not ingest.ensure_lesson_document(db, row['id']):
                raise RuntimeError(f'Indexing failed: {row["id"]}')
            print(f'Applied lesson {row["id"]}', flush=True)


if __name__ == '__main__':
    main()
