"""Extend only the three seeded introductory IT courses; preserve prior results.

Default: transaction preview rolled back. --apply: insert missing curriculum.
--pdf: build/attach missing PDFs for all lessons in these three courses.
PDF rendering uses existing Chrome helper and validates extracted Vietnamese text.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text
from app.core.database import engine
from app.core.config import settings
from app.services.analytics_service import normalize_topic
from training.it_curriculum import CURRICULUM
from training.normalize_it_chapters import chapter_title

REFERENCES = {
 'mang-may-tinh-co-ban': ['https://www.netacad.com/courses/networking-basics', 'https://developer.mozilla.org/en-US/docs/Web/HTTP'],
 'cau-truc-du-lieu-giai-thuat-co-ban': ['https://opendatastructures.org/', 'https://docs.python.org/3/tutorial/datastructures.html', 'https://docs.python.org/3/library/heapq.html'],
 'kiem-thu-phan-mem-nhap-mon': ['https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf'],
}


def expand(apply=False):
    report=[]
    with engine.connect() as conn:
        transaction=conn.begin()
        try:
            for slug, chapters in CURRICULUM.items():
                course=conn.execute(text('SELECT id,title FROM courses WHERE slug=:s'),dict(s=slug)).mappings().one()
                added_lessons=added_questions=0
                for order,(name,lessons) in enumerate(chapters,3):
                    numbered_name=chapter_title(name,order)
                    matches=conn.execute(text('SELECT id FROM chapters WHERE course_id=:c AND chapter_name IN (:n,:numbered)'),dict(c=course['id'],n=name,numbered=numbered_name)).scalars().all()
                    if len(matches)>1:
                        raise ValueError(f'Duplicate chapter: {name}')
                    chapter_id=matches[0] if matches else conn.execute(text('INSERT INTO chapters (course_id,chapter_name,order_index) VALUES (:c,:n,:o)'),dict(c=course['id'],n=numbered_name,o=order)).lastrowid
                    quiz=conn.execute(text('SELECT id FROM quizzes WHERE chapter_id=:ch'),dict(ch=chapter_id)).scalar()
                    if not quiz:
                        quiz=conn.execute(text("INSERT INTO quizzes (course_id,chapter_id,title,description,source,duration,passing_score,grading_method) VALUES (:c,:ch,:t,:d,'manual',20,70,'latest')"),dict(c=course['id'],ch=chapter_id,t=f'Ôn tập chương: {name}',d='10 câu, 5 câu cho mỗi bài. Bài luyện không thay thế sản phẩm thực hành hoặc tự chứng nhận thành thạo.')).lastrowid
                    for lesson_order,item in enumerate(lessons,1):
                        matches=conn.execute(text('SELECT id FROM lessons WHERE chapter_id=:ch AND title=:t'),dict(ch=chapter_id,t=item['title'])).scalars().all()
                        if len(matches)>1:
                            raise ValueError(f"Duplicate lesson: {item['title']}")
                        if matches:
                            # Leave existing lesson content and its questions untouched on rerun.
                            continue
                        body=item['body']+'\n## Đọc thêm\n'+'\n'.join(REFERENCES[slug])
                        lid=conn.execute(text("INSERT INTO lessons (chapter_id,title,description,duration,order_index,is_free,status) VALUES (:ch,:t,:d,0,:o,1,'published')"),dict(ch=chapter_id,t=item['title'],d=body,o=lesson_order)).lastrowid
                        topic=conn.execute(text('INSERT INTO course_topics (course_id,name,normalized_name,lesson_id,confirmed) VALUES (:c,:n,:k,:l,1)'),dict(c=course['id'],n=item['title'],k=normalize_topic(item['title']),l=lid)).lastrowid
                        added_lessons+=1
                        for index,(prompt,correct,b,c,d,explanation) in enumerate(item['questions']):
                            options=[b,c,d]
                            position=(index+lesson_order)%4
                            options.insert(position,correct)
                            assert len(set(options))==4
                            conn.execute(text('''INSERT INTO questions (quiz_id,content,option_a,option_b,option_c,option_d,correct_answer,topic,topic_id,difficulty,explanation,order_index,knowledge_chapter_id,knowledge_lesson_id)
                                VALUES (:q,:content,:a,:b,:c,:d,:answer,:topic,:tid,:difficulty,:explanation,:o,:ch,:l)'''),dict(q=quiz,content=prompt,a=options[0],b=options[1],c=options[2],d=options[3],answer='ABCD'[position],topic=item['title'],tid=topic,difficulty='medium' if index>=3 else 'easy',explanation=explanation,o=(lesson_order-1)*5+index+1,ch=chapter_id,l=lid))
                            added_questions+=1
                # Update catalog summary, not the original quiz or prior learning records.
                description=(f"Khóa nhập môn {course['title'].lower()}: 6 chương, 12 bài đọc có ví dụ, bài tập và tài liệu PDF. "
                             'Có 60 câu quiz phân loại theo chương/bài trong bài kiểm tra nền tảng và bốn bộ ôn chương; một bài thực hành tổng hợp với tiêu chí tự kiểm tra. Video tham khảo có ở các bài nền tảng. Phạm vi nhập môn, chưa thay thế đào tạo chuyên sâu.')
                conn.execute(text('UPDATE courses SET description=:d WHERE id=:c'),dict(d=description,c=course['id']))
                report.append(dict(course_id=course['id'],slug=slug,added_lessons=added_lessons,added_questions=added_questions))
            if apply: transaction.commit()
            else: transaction.rollback()
        except BaseException:
            transaction.rollback()
            raise
    return report


def build_pdfs():
    from pypdf import PdfReader
    from training.lesson_docs.build_pdfs import find_chrome, render
    chrome=find_chrome()
    with engine.connect() as conn:
        rows=conn.execute(text('''SELECT l.*,ch.chapter_name,ch.order_index AS chapter_no,c.title AS course_title,c.slug
            FROM lessons l JOIN chapters ch ON ch.id=l.chapter_id JOIN courses c ON c.id=ch.course_id
            WHERE c.slug IN (:a,:b,:c) ORDER BY c.id,ch.order_index,l.order_index'''),dict(zip(('a','b','c'),CURRICULUM))).mappings().all()
    dest=Path(settings.upload_dir).resolve()/'documents'
    dest.mkdir(parents=True,exist_ok=True)
    # Source copies are retained for review and subsequent PDF regeneration.
    sources=Path(__file__).parent/'lesson_docs'/'it_expanded'
    sources.mkdir(parents=True,exist_ok=True)
    def build(row):
        lid=row['id']
        if row['document_url']:
            return dict(lesson_id=lid,state='kept-existing')
        body=row['description'] or ''
        (sources/f'lesson_{lid}.md').write_text(body,encoding='utf-8')
        digest=sha256(body.encode('utf-8')).hexdigest()[:12]
        filename=f'it_lesson_{lid}_{digest}.pdf'
        output=dest/filename
        with tempfile.TemporaryDirectory(prefix=f'it_pdf_{lid}_') as tmp:
            page=Path(tmp)/'lesson.html'
            page.write_text(render(dict(course_title=row['course_title'],chapter_no=row['chapter_no'],chapter_name=chapter_title(row['chapter_name'],row['chapter_no']).split(': ',1)[1],lesson_no=row['order_index'],title=row['title'],description='Tài liệu học tập nhập môn · nội dung và bài tập tự luyện'),body),encoding='utf-8')
            subprocess.run([chrome,'--headless=new','--disable-gpu','--no-pdf-header-footer',f'--user-data-dir={Path(tmp)/"profile"}',f'--print-to-pdf={output}',page.as_uri()],check=True,capture_output=True,timeout=90,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        reader=PdfReader(str(output))
        extracted='\n'.join(p.extract_text() or '' for p in reader.pages)
        if len(extracted)<500 or 'Mục tiêu' not in extracted:
            raise ValueError(f'PDF text validation failed: {lid}')
        with engine.begin() as conn:
            conn.execute(text('UPDATE lessons SET document_url=:url WHERE id=:id AND (document_url IS NULL OR document_url=\'\')'),dict(url=f'/uploads/documents/{filename}',id=lid))
        return dict(lesson_id=lid,state='attached',pages=len(reader.pages),text_chars=len(extracted))
    results=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks=[pool.submit(build,row) for row in rows]
        for task in as_completed(tasks):
            result=task.result()
            results.append(result)
            print(json.dumps(result),flush=True)
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--apply',action='store_true')
    group.add_argument('--pdf',action='store_true')
    args=parser.parse_args()
    if args.pdf: build_pdfs()
    else: print(json.dumps(expand(args.apply),ensure_ascii=True,indent=2))
