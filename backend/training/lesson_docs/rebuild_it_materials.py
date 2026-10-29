"""Build and validate detailed PDFs, then attach them in a separate transaction.

Run from backend:
  python training/lesson_docs/rebuild_it_materials.py --build
  python training/lesson_docs/rebuild_it_materials.py --apply
Previous URLs/files are retained in manifest.json. No lesson/quiz/results are rewritten.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
from app.core.config import settings
from app.core.database import engine
from app.core.media import resolve_upload_path
from sqlalchemy import text
from pypdf import PdfReader, PdfWriter
from training.lesson_docs.build_pdfs import CSS, find_chrome, md_to_html
from training.lesson_docs.it_detailed_content import DETAILS
from training.expand_it_courses import CURRICULUM, REFERENCES
from training.seed_it_courses import COURSES

OUT=HERE/'it_detailed'
MANIFEST=OUT/'manifest.json'
EXTRA_CSS='''
@page { @bottom-right { content: "Trang " counter(page); font-size: 8pt; color: #64748b; } }
h1,h2 { break-after: avoid; }
p,li { orphans: 3; widows: 3; }
pre { font-size: 8.5pt; break-inside: auto; }
.path { font-size: 9pt; color: #475569; }
.scope { background: #f8fafc; padding: 10pt; border: 1px solid #e2e8f0; }
.toc { padding-left: 18pt; }
.toc li { margin-bottom: 5pt; }
'''


def snapshot():
    """Protected state hashes, without exporting personal learning data."""
    with engine.connect() as conn:
        queries={
            'results':'SELECT * FROM results ORDER BY id',
            'answers':'SELECT * FROM result_answers ORDER BY result_id,question_id',
            'enrollments':'SELECT * FROM enrollments ORDER BY id',
            'progress':'SELECT * FROM lesson_progress ORDER BY id',
            'questions':'SELECT * FROM questions ORDER BY id',
            'quizzes':'SELECT * FROM quizzes ORDER BY id',
            'videos':'SELECT id,video_url FROM lessons ORDER BY id',
        }
        return {name:hashlib.sha256(json.dumps([dict(r) for r in conn.execute(text(sql)).mappings()],sort_keys=True,default=str).encode()).hexdigest() for name,sql in queries.items()}


def source_bodies():
    bodies={}
    for course in COURSES:
        for _,lessons in course['chapters']:
            for title,body,questions in lessons:
                bodies[title]=(body,questions)
    for chapters in CURRICULUM.values():
        for _,lessons in chapters:
            for lesson in lessons:
                bodies[lesson['title']]=(lesson['body'],lesson['questions'])
    return bodies


def read_lessons():
    with engine.connect() as conn:
        rows=conn.execute(text('''SELECT l.*,ch.chapter_name,ch.order_index AS chapter_no,
            ch.course_id,c.title AS course_title,c.slug,c.teacher_id
            FROM lessons l JOIN chapters ch ON ch.id=l.chapter_id JOIN courses c ON c.id=ch.course_id
            WHERE c.slug IN (:a,:b,:c) ORDER BY c.id,ch.order_index,ch.id,l.order_index,l.id'''),dict(zip(('a','b','c'),CURRICULUM))).mappings().all()
    return [dict(row) for row in rows]


def compose(row,course_rows,bodies):
    title=row['title']
    base,questions=bodies[title]
    if base.startswith('## '):
        sections=dict(re.findall(r'## ([^\n]+)\n(.*?)(?=\n## |\Z)',base,flags=re.S))
        goal=sections['Mục tiêu'].strip()
        theory=sections['Kiến thức trọng tâm'].strip()
        practice='## Bài tập vận dụng bổ sung\n'+sections['Bài tập thực hành'].strip()+'\n\n## Hướng giải bài tập bổ sung\n'+sections['Gợi ý tự kiểm tra'].strip()
        base='## Mục tiêu bài học\n'+goal+'\n\n## Kiến thức nền\n'+theory
    else:
        parts=base.strip().split('\n\n')
        goal=parts[0].replace('Mục tiêu: ','',1)
        goal=goal[:1].upper()+goal[1:]
        practice='## Bài tập vận dụng bổ sung\n'+parts[-1].removeprefix('Tự luyện: ')
        base='## Mục tiêu bài học\n'+goal+'\n\n## Kiến thức nền\n'+'\n\n'.join(parts[1:-1])
    chapter_lessons=[r for r in course_rows if r['chapter_id']==row['chapter_id']]
    recap='\n'.join(f'- {q[1]}. {q[5]}' for q in questions)
    check='\n'.join(f'{i}. {q[0]}' for i,q in enumerate(questions,1))
    guidance=f'''## Vị trí bài học trong khóa
- Khóa học: {row['course_title']}.
- {row['chapter_name']}.
- Các bài trong chương: {'; '.join(r['title'] for r in chapter_lessons)}.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

'''
    return guidance+base+'\n\n'+DETAILS[title]+'\n\n'+practice+f'''

## Câu hỏi tự kiểm tra
{check}

## Gợi ý đáp án và điểm cần nhớ
{recap}

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
'''+'\n'.join('- '+link for link in REFERENCES[row['slug']])+'\n'


def html_page(row,body):
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>{CSS}{EXTRA_CSS}</style></head><body>
<div class="tag">{html.escape(row['course_title'])}</div>
<p class="path">{html.escape(row['chapter_name'])} · Bài {row['order_index']}</p>
<h1>{html.escape(row['title'])}</h1>
<p class="sub">Tài liệu học tập chi tiết · Lý thuyết, ví dụ, thực hành và hướng giải</p>
{md_to_html(body)}</body></html>'''


def print_pdf(chrome,page,output):
    with tempfile.TemporaryDirectory(prefix='it_detail_') as tmp:
        subprocess.run([chrome,'--headless=new','--disable-gpu','--no-pdf-header-footer',
            f'--user-data-dir={Path(tmp)/"profile"}',f'--print-to-pdf={output}',page.as_uri()],
            check=True,capture_output=True,timeout=90,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=read_lessons()
    assert len(rows)==36 and set(DETAILS)=={r['title'] for r in rows}
    bodies=source_bodies()
    chrome=find_chrome()
    before=snapshot()
    def one(row):
        lid=row['id']
        course_rows=[r for r in rows if r['course_id']==row['course_id']]
        body=compose(row,course_rows,bodies)
        (OUT/f'lesson_{lid}.md').write_text(body,encoding='utf-8')
        page=OUT/f'lesson_{lid}.html'
        page.write_text(html_page(row,body),encoding='utf-8')
        output=OUT/f'lesson_{lid}.pdf'
        print_pdf(chrome,page,output)
        reader=PdfReader(str(output))
        extracted='\n'.join(p.extract_text() or '' for p in reader.pages)
        for marker in ['Mục tiêu','Câu hỏi tự kiểm tra','Gợi ý đáp án','Tài liệu đọc thêm']:
            if marker not in extracted:
                raise ValueError(f'Missing Vietnamese text {marker}: {lid}')
        if len(extracted)<3000 or len(reader.pages)<2:
            raise ValueError(f'Insufficient PDF content: {lid}')
        old=resolve_upload_path(row['document_url'])
        old_reader=PdfReader(old) if old and Path(old).is_file() else None
        old_chars=sum(len(p.extract_text() or '') for p in old_reader.pages) if old_reader else 0
        if len(extracted)<=old_chars and not Path(row['document_url'] or '').name.startswith('it_detailed_'):
            raise ValueError(f'New document is not more detailed: {lid}')
        digest=hashlib.sha256(output.read_bytes()).hexdigest()
        return dict(lesson_id=lid,course_id=row['course_id'],title=row['title'],
            original_url=row['document_url'],pdf=str(output),sha256=digest,
            pages=len(reader.pages),text_chars=len(extracted),original_text_chars=old_chars,
            new_url=f'/uploads/documents/it_detailed_{lid}_{digest[:12]}.pdf')
    results=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for task in as_completed([pool.submit(one,row) for row in rows]):
            result=task.result()
            results.append(result)
            print(json.dumps({k:result[k] for k in ('lesson_id','pages','text_chars')}),flush=True)
    results.sort(key=lambda r:r['lesson_id'])
    books=[]
    for cid in sorted({r['course_id'] for r in rows}):
        selected=[r for r in rows if r['course_id']==cid]
        title=selected[0]['course_title']
        toc='<ol class="toc">'
        for row in selected:
            toc+=f'<li>{html.escape(row["chapter_name"])} — {html.escape(row["title"])}</li>'
        toc+='</ol>'
        cover=OUT/f'course_{cid}_cover.html'
        cover.write_text(f'<!doctype html><html lang="vi"><meta charset="utf-8"><style>{CSS}{EXTRA_CSS}</style><body><div class="tag">Tài liệu toàn khóa</div><h1>{html.escape(title)}</h1><p class="scope">Phạm vi nhập môn. Gồm 6 chương, 12 bài; có mục lục PDF để chuyển đến từng bài. Đọc cùng video tham khảo và làm bài tập thực hành. Bản tổng hợp này không phải chứng chỉ hoặc tài liệu luyện thi được công nhận.</p><h2>Mục lục</h2>{toc}</body></html>',encoding='utf-8')
        cover_pdf=OUT/f'course_{cid}_cover.pdf'
        print_pdf(chrome,cover,cover_pdf)
        writer=PdfWriter()
        writer.append(str(cover_pdf),import_outline=False)
        current_chapter=None
        parent=None
        for row in selected:
            first_page=len(writer.pages)
            writer.append(str(OUT/f'lesson_{row["id"]}.pdf'),import_outline=False)
            if current_chapter!=row['chapter_id']:
                current_chapter=row['chapter_id']
                parent=writer.add_outline_item(row['chapter_name'],first_page)
            writer.add_outline_item(row['title'],first_page,parent=parent)
        writer.add_metadata({'/Title':title,'/Subject':'Tài liệu nhập môn theo chương và bài học'})
        book=OUT/f'course_{cid}_complete.pdf'
        writer.write(str(book))
        books.append(dict(course_id=cid,title=title,pdf=str(book),pages=len(PdfReader(str(book)).pages)))
    assert snapshot()==before,'Protected learning data changed during build'
    MANIFEST.write_text(json.dumps(dict(lessons=results,books=books,protected_before=before),ensure_ascii=False,indent=2),encoding='utf-8')
    print('Built and validated 36 lesson PDFs and 3 course books.',flush=True)


def apply():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    rows=manifest['lessons']
    # Validate every artifact before changing any URL.
    for row in rows:
        if hashlib.sha256(Path(row['pdf']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError(f"PDF changed after validation: {row['lesson_id']}")
    before=snapshot()
    dest=Path(settings.upload_dir).resolve()/'documents'
    dest.mkdir(parents=True,exist_ok=True)
    with engine.begin() as conn:
        # Abort if a teacher changed a document after the build; no silent replacement.
        for row in rows:
            current=conn.execute(text('SELECT document_url FROM lessons WHERE id=:id FOR UPDATE'),dict(id=row['lesson_id'])).scalar_one()
            if current not in (row['original_url'],row['new_url']):
                raise ValueError(f"Document changed since build: {row['lesson_id']}")
            if conn.execute(text('SELECT COUNT(*) FROM documents WHERE lesson_id=:id'),dict(id=row['lesson_id'])).scalar():
                raise ValueError(f"Existing AI document needs synchronization: {row['lesson_id']}")
        for row in rows:
            shutil.copyfile(row['pdf'],dest/Path(row['new_url']).name)
            conn.execute(text('UPDATE lessons SET document_url=:u WHERE id=:id'),dict(u=row['new_url'],id=row['lesson_id']))
    assert snapshot()==before,'Protected learning data changed during apply'
    manifest['applied']=True
    manifest['protected_records_unchanged']=True
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Attached 36 detailed PDFs; old files retained; videos/quiz/results unchanged.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--build',action='store_true')
    mode.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.build: build()
    else: apply()
