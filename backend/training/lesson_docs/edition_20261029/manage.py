"""Build an additive lesson edition, stage embeddings, apply atomically, verify, rollback.

Run from backend: .venv/Scripts/python.exe training/lesson_docs/edition_20261029/manage.py prepare
Then render.cjs, followed by assemble, index, apply, verify as separate phases.
Original files and document rows are retained. No assessment answers are copied.
"""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sys

HERE=Path(__file__).resolve().parent
BACKEND=HERE.parents[2]
sys.path.insert(0,str(BACKEND))
os.chdir(BACKEND)
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import text
from pypdf import PdfReader,PdfWriter
from app.core.database import engine
from app.core.media import resolve_upload_path
from training.lesson_docs.build_pdfs import render

OUT=HERE/'generated'
MANIFEST=OUT/'manifest.json'
MAPPING={'python-co-ban':'python','javascript-tu-zero-den-hero':'javascript','lap-trinh-java-can-ban':'java',
 'html-css-nhap-mon':'html_css','reactjs-chuyen-sau':'react','mysql-thiet-ke-csdl':'mysql',
 'mang-may-tinh-co-ban':'network','cau-truc-du-lieu-giai-thuat-co-ban':'algorithms','kiem-thu-phan-mem-nhap-mon':'testing'}

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def load():return json.loads(MANIFEST.read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def protected():
    queries={t:'SELECT * FROM '+t+' ORDER BY id'for t in ['users','courses','chapters','quizzes','questions','results','enrollments','lesson_progress','payments','ai_conversations','ai_messages']}
    queries['result_answers']='SELECT * FROM result_answers ORDER BY result_id,question_id'
    queries['lessons']='SELECT id,chapter_id,title,description,video_url,order_index,is_free FROM lessons ORDER BY id'
    with engine.connect()as conn:
        return {k:hashlib.sha256(json.dumps([dict(r)for r in conn.execute(text(q)).mappings()],sort_keys=True,default=str,ensure_ascii=False).encode()).hexdigest()for k,q in queries.items()}

def prepare():
    OUT.mkdir(exist_ok=True)
    if MANIFEST.exists():raise RuntimeError('Manifest already exists; reuse staged phases instead of overwriting the original snapshot.')
    with engine.connect()as conn:
        rows=[dict(x)for x in conn.execute(text('''SELECT l.*,ch.course_id,ch.chapter_name,ch.order_index AS chapter_no,
            c.title AS course_title,c.slug,c.teacher_id FROM lessons l JOIN chapters ch ON ch.id=l.chapter_id
            JOIN courses c ON c.id=ch.course_id ORDER BY c.id,ch.order_index,ch.id,l.order_index,l.id''')).mappings()]
        indexed={x[0]for x in conn.execute(text("SELECT DISTINCT lesson_id FROM documents WHERE status='indexed' AND lesson_id IS NOT NULL"))}
    manifest={'edition':'20261029','protected_before':protected(),'lessons':[],'courses':[],'excluded':[]}
    sources={}
    tasks=[]
    for row in rows:
        key=MAPPING.get(row['slug'])
        if row['course_title'].strip().lower()=='nguyên lí hdh':key='os'
        if not key:
            if row['course_title'].startswith('PYTEST'):
                manifest['excluded'].append({'id':row['id'],'title':row['title'],'course':row['course_title'],'reason':'Test fixture'});continue
            raise RuntimeError('Unmapped real course '+row['course_title'])
        if key not in sources:
            full=(HERE/(key+'.md')).read_text(encoding='utf-8')
            sections=dict(re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |^# |\Z)',full,re.M|re.S))
            reference=full.split('# Tài liệu tham khảo\n',1)[1].strip()
            sources[key]=(sections,reference)
        sections,reference=sources[key]
        body=sections[row['title']].strip()
        assert len(body)>300
        source=Path(resolve_upload_path(row['document_url'])).resolve()
        if not source.is_file():raise RuntimeError('Missing original material '+str(source))
        original_pages=len(PdfReader(source).pages)
        identity=hashlib.sha256((digest(source)+body+reference).encode()).hexdigest()[:12]
        stem=f"lesson_{row['id']}_{identity}"
        page=OUT/(stem+'.html');appendix=OUT/(stem+'_appendix.pdf');bundle=OUT/(stem+'.pdf')
        meta={'course_title':row['course_title'],'chapter_no':row['chapter_no'],'chapter_name':row['chapter_name'],
              'lesson_no':row['order_index'],'title':row['title']+' — Thực hành và hỏi đáp','description':'Phần bổ sung cho bài học · biên soạn 29/10/2026'}
        page.write_text(render(meta,'## Tình huống, ví dụ và tự kiểm tra\n'+body+'\n\n## Nguồn học tiếp\n'+reference),encoding='utf-8')
        upload_name='edition_20261029_'+stem+'.pdf'
        record={k:row[k]for k in ['id','title','course_id','course_title','chapter_id','chapter_name','teacher_id']}
        record.update(source=str(source),source_sha256=digest(source),old_url=row['document_url'],original_pages=original_pages,
                      appendix=str(appendix),bundle=str(bundle),upload_name=upload_name,new_url='/uploads/documents/'+upload_name,
                      has_core_index=row['id']in indexed,content_sha256=identity)
        manifest['lessons'].append(record);tasks.append({'html':str(page),'pdf':str(appendix)})
    for cid in sorted({r['course_id']for r in manifest['lessons']}):
        lessons=[r for r in manifest['lessons']if r['course_id']==cid]
        toc='## Mục lục\n'+'\n'.join(f"- {r['chapter_name']}: {r['title']}"for r in lessons)
        page=OUT/f'course_{cid}_toc.html';pdf=OUT/f'course_{cid}_toc.pdf'
        meta={'course_title':lessons[0]['course_title'],'chapter_no':'Tổng hợp','chapter_name':'Giáo trình và thực hành','lesson_no':'Toàn khóa','title':lessons[0]['course_title'],'description':'Tài liệu gốc kèm thực hành bổ sung · 29/10/2026'}
        page.write_text(render(meta,toc),encoding='utf-8');tasks.append({'html':str(page),'pdf':str(pdf)})
        manifest['courses'].append({'id':cid,'title':lessons[0]['course_title'],'toc':str(pdf),'complete':str(OUT/f'course_{cid}_complete.pdf')})
    assert len(manifest['lessons'])==101 and len(manifest['courses'])==10
    dump(MANIFEST,manifest);dump(OUT/'render-tasks.json',tasks)
    print('Prepared',len(manifest['lessons']),'lessons and',len(manifest['courses']),'course packages',flush=True)

def assemble():
    m=load()
    for r in m['lessons']:
        assert digest(r['source'])==r['source_sha256']
        appendix=PdfReader(r['appendix']);text_content='\n'.join(p.extract_text()or''for p in appendix.pages)
        assert len(text_content)>300 and 'Nguồn học tiếp'in text_content
        writer=PdfWriter();writer.append(r['source'],import_outline=False);writer.append(r['appendix'],import_outline=False)
        writer.add_outline_item('Thực hành và hỏi đáp',r['original_pages'])
        writer.write(r['bundle']);r['pages']=len(writer.pages);r['sha256']=digest(r['bundle'])
    for course in m['courses']:
        writer=PdfWriter();writer.append(course['toc'],import_outline=False)
        for r in m['lessons']:
            if r['course_id']==course['id']:
                start=len(writer.pages);writer.append(r['bundle'],import_outline=False);writer.add_outline_item(r['chapter_name']+' — '+r['title'],start)
        writer.write(course['complete']);course['pages']=len(writer.pages);course['sha256']=digest(course['complete'])
    dump(MANIFEST,m);print('Assembled',sum(r['pages']-r['original_pages']for r in m['lessons']),'additional pages',flush=True)

def index():
    from app.ai.rag import embeddings,text_splitter
    m=load()
    for n,r in enumerate(m['lessons'],1):
        cache=OUT/(Path(r['bundle']).stem+'.rag.json')
        if cache.exists():continue
        pdf=PdfReader(r['bundle']);start=r['original_pages']if r['has_core_index']else 0
        pages=[(i+1,pdf.pages[i].extract_text()or'')for i in range(start,len(pdf.pages))]
        chunks=text_splitter.split_pages(pages)
        vectors=embeddings.embed_texts([c['text']for c in chunks])
        assert chunks and len(chunks)==len(vectors)and all(len(v)==384 for v in vectors)
        data=[{'idx':c['index'],'page':c['page'],'content':c['text'],'embedding':json.dumps(v),'tokens':text_splitter.approx_tokens(c['text'])}for c,v in zip(chunks,vectors)]
        dump(cache,{'pdf_sha256':r['sha256'],'chunks':data})
        print('Staged RAG',n,'/',len(m['lessons']),r['id'],len(chunks),flush=True)

def apply():
    m=load()
    if m.get('applied'):raise RuntimeError('Already applied; verify instead.')
    assert protected()==m['protected_before'],'Protected learning/user data changed during preparation; investigate before applying.'
    upload=BACKEND/'uploads'/'documents';upload.mkdir(exist_ok=True)
    staged=[]
    for r in m['lessons']:
        assert digest(r['bundle'])==r['sha256']
        cache=json.loads((OUT/(Path(r['bundle']).stem+'.rag.json')).read_text(encoding='utf-8'))
        assert cache['pdf_sha256']==r['sha256']
        dest=upload/r['upload_name']
        if dest.exists():assert digest(dest)==r['sha256']
        else:shutil.copy2(r['bundle'],dest)
        staged.append((r,cache,dest))
    # All learner-visible URLs and RAG rows become visible together on commit.
    with engine.begin()as conn:
        for r,cache,dest in staged:
            current=conn.execute(text('SELECT title,document_url FROM lessons WHERE id=:id FOR UPDATE'),{'id':r['id']}).mappings().one()
            assert current['title']==r['title']and current['document_url']==r['old_url'],'Lesson changed since preparation'
            chunks=cache['chunks']
            created=conn.execute(text('''INSERT INTO documents(course_id,lesson_id,uploaded_by,title,filename,file_path,file_type,status,pages,chunk_count)
                VALUES(:c,:l,:u,:t,:fn,:path,'pdf','indexed',:p,:n)'''),{'c':r['course_id'],'l':r['id'],'u':r['teacher_id'],
                't':r['title']+' — Thực hành bổ sung 29/10/2026','fn':r['upload_name'],'path':str(dest),'p':r['pages'],'n':len(chunks)})
            r['document_id']=created.lastrowid
            payload=[dict(ch,d=r['document_id'],c=r['course_id'],l=r['id'])for ch in chunks]
            conn.execute(text('''INSERT INTO document_chunks(document_id,course_id,lesson_id,chunk_index,page,content,embedding,token_count)
                VALUES(:d,:c,:l,:idx,:page,:content,:embedding,:tokens)'''),payload)
            conn.execute(text('UPDATE lessons SET document_url=:url WHERE id=:id'),{'url':r['new_url'],'id':r['id']})
    m['applied']=True;dump(MANIFEST,m)
    assert protected()==m['protected_before'],'Unexpected protected-data change'
    print('Applied atomically:',len(staged),'lessons and indexed documents',flush=True)

def verify():
    from fastapi.testclient import TestClient
    from app.main import app
    m=load();assert m.get('applied')
    c=TestClient(app);b=c.post('/api/auth/login',json={'email':'admin@gmail.com','password':'123456'}).json()
    h={'Authorization':'Bearer '+b['token']};checks=[]
    with engine.connect()as conn:
        for r in m['lessons']:
            b=c.get('/api/lessons',params={'id':r['id']},headers=h).json()['data'];assert b['document_url']==r['new_url']
            response=c.get(b['document_src']);assert response.status_code==200 and hashlib.sha256(response.content).hexdigest()==r['sha256']
            rows=conn.execute(text('SELECT page,content FROM document_chunks WHERE document_id=:id ORDER BY chunk_index'),{'id':r['document_id']}).mappings().all()
            pdf=PdfReader(r['bundle']);joined=lambda s:re.sub(r'\s+','',s)
            # The splitter may overlap sentences, but each stored chunk must use an actual physical PDF page.
            for row in rows:
                assert 1<=row['page']<=len(pdf.pages)
                text_page=joined(pdf.pages[row['page']-1].extract_text()or'')
                assert joined(row['content'])in text_page,'Chunk/page mismatch'
            checks.append({'lesson_id':r['id'],'course_id':r['course_id'],'http':response.status_code,'sha256_matches':True,'pages':r['pages'],'rag_chunks':len(rows)})
    assert protected()==m['protected_before']
    dump(OUT/'verification.json',{'lessons':checks,'protected_unchanged':True,'total_lessons':len(checks),'courses':m['courses']})
    print('Verified authenticated downloads, hashes, RAG page alignment and protected data:',len(checks),flush=True)

def rollback():
    m=load();assert m.get('applied')
    with engine.begin()as conn:
        for r in m['lessons']:
            current=conn.execute(text('SELECT document_url FROM lessons WHERE id=:id FOR UPDATE'),{'id':r['id']}).scalar()
            assert current==r['new_url'],'Subsequent edit detected; do not overwrite'
            conn.execute(text('UPDATE lessons SET document_url=:url WHERE id=:id'),{'url':r['old_url'],'id':r['id']})
            conn.execute(text('DELETE FROM documents WHERE id=:id AND filename=:name'),{'id':r['document_id'],'name':r['upload_name']})
    m['applied']=False;dump(MANIFEST,m);print('Rolled back edition only; original files retained.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('phase',choices=['prepare','assemble','index','apply','verify','rollback'])
    globals()[parser.parse_args().phase]()
