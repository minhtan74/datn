"""Live HTTP functional audit. Run prepare, then browser audit, then finish."""
import csv
import io
import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import httpx

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent
STATE = ROOT / 'functional-account-state.json'
OUT = ROOT / 'functional-account-api.json'
ACCOUNTS = {'admin':'admin@gmail.com','teacher_an':'an.nguyen@studyonline.vn',
            'teacher_binh':'binh.tran@studyonline.vn','student_em':'em.hoang@gmail.com',
            'student_phuong':'phuong.vu@gmail.com'}
clients = {}
results = []
state = {}

def save():
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    OUT.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

def call(role, method, path, name, expect=200, validate=None, **kwargs):
    start=time.perf_counter()
    try:
        r=clients[role].request(method,path,**kwargs)
        try: body=r.json()
        except ValueError: body={'content_type':r.headers.get('content-type'),'bytes':len(r.content)}
        passed=r.status_code in ([expect] if isinstance(expect,int) else expect)
        if passed and validate: passed=bool(validate(body))
        evidence={k:v for k,v in body.items() if k not in ('token','user')} if isinstance(body,dict) else body
        results.append(dict(name=name,role=role,method=method,path=path,status=r.status_code,
                            expected=expect,passed=passed,ms=round((time.perf_counter()-start)*1000,1),response=evidence))
        save()
        print(f'{"PASS" if passed else "FAIL"} {role} {name} [{r.status_code}]',flush=True)
        return body,r
    except Exception as e:
        results.append(dict(name=name,role=role,method=method,path=path,passed=False,ms=round((time.perf_counter()-start)*1000,1),error=str(e)))
        save(); print(f'FAIL {name}: {type(e).__name__}',flush=True)
        return {},None

def login():
    for role,email in ACCOUNTS.items():
        clients[role]=httpx.Client(base_url='http://127.0.0.1:8080',timeout=180)
        b,_=call(role,'POST','/api/auth/login','Đăng nhập tài khoản mẫu',json={'email':email,'password':'123456'},validate=lambda b:'token' in b)
        clients[role].headers['Authorization']='Bearer '+b['token']
        call(role,'GET','/api/auth/me','Xác minh tài khoản và vai trò')

def snapshot(label):
    snap={}
    for name,path in [('summary','/api/reports/summary'),('learning','/api/reports/learning'),('users','/api/users'),('courses','/api/courses'),('payments','/api/payments/manage?page_size=100')]:
        b,_=call('admin','GET',path,'Số liệu hệ thống '+label+' / '+name)
        snap[name]=b.get('data')
        if name=='payments': snap['payment_counts']=b.get('counts')
    state[label]=snap;save()

def prepare():
    global state
    state={'run':datetime.now().strftime('AUDIT_%Y%m%d_%H%M%S'),'accounts':ACCOUNTS,'started_at':datetime.now().isoformat(),'fixture_courses':[]}
    login();snapshot('before')
    for role in ACCOUNTS:
        for name,path in [('Danh sách khóa học','/api/courses'),('Danh sách quiz','/api/quizzes'),('Tổng quan học tập','/api/analytics/overview')]:
            call(role,'GET',path,name)
    for role in ['student_em','student_phuong','teacher_an','teacher_binh']:
        call(role,'GET','/api/users','Chặn xem danh sách người dùng',403)
        call(role,'GET','/api/reports/summary','Chặn xem báo cáo admin',403)
    for role in ['student_em','student_phuong']:
        call(role,'POST','/api/courses','Chặn học viên tạo khóa',403,json={'title':state['run']})
        call(role,'POST','/api/ai/generate-quiz','Chặn học viên sinh đề',403,json={'course_id':7})
        call(role,'GET','/api/payments/manage','Chặn học viên quản lý giao dịch',403)
    # A temporary account for admin writes, leaving sample account credentials intact.
    email=state['run'].lower()+'@audit.local'
    call('admin','POST','/api/users','Admin tạo tài khoản',json={'fullname':state['run'],'email':email,'password':'Audit123456','role':'student'})
    users,_=call('admin','GET','/api/users','Tìm tài khoản vừa tạo')
    uid=next(u['id'] for u in users['data'] if u['email']==email)
    state['temporary_user']=uid;save()
    call('admin','PUT','/api/users','Admin cập nhật tài khoản',json={'id':uid,'fullname':state['run']+' edited','email':email,'role':'student','password':'Audit234567'})
    call('admin','PUT','/api/users/status','Admin khóa tài khoản',json={'id':uid,'is_active':0})
    call('admin','POST','/api/auth/login','Tài khoản bị khóa không đăng nhập được',403,json={'email':email,'password':'Audit234567'})
    call('admin','PUT','/api/users/status','Admin mở khóa tài khoản',json={'id':uid,'is_active':1})
    call('admin','POST','/api/auth/login','Tài khoản mở khóa đăng nhập được',json={'email':email,'password':'Audit234567'})
    for owner in ['teacher_an','teacher_binh']:
        b,_=call(owner,'POST','/api/courses','Giảng viên tạo khóa test',json={'title':state['run']+' '+owner,'description':'Dữ liệu kiểm thử chức năng tự dọn','price':0,'status':'published'})
        cid=int(b['id']);state['fixture_courses'].append(cid);save()
        call(owner,'PUT','/api/courses','Giảng viên sửa khóa test',json={'id':cid,'title':state['run']+' '+owner,'description':'Kiểm thử học tập Python','price':0,'status':'published'})
        other='teacher_binh' if owner=='teacher_an' else 'teacher_an'
        call(other,'PUT','/api/courses','Chặn sửa khóa của giảng viên khác',403,json={'id':cid,'title':'unauthorized'})
        if owner=='teacher_binh': continue
        state['course_id']=cid
        ch,_=call(owner,'POST','/api/chapters','Tạo chương',json={'course_id':cid,'chapter_name':'Kiến thức Python kiểm thử'})
        state['chapter_id']=int(ch['id']);state['lessons']=[];save()
        for i,title in enumerate(['Biến và kiểu dữ liệu','Vòng lặp và điều kiện']):
            b,_=call(owner,'POST','/api/lessons','Tạo bài học '+str(i+1),json={'chapter_id':state['chapter_id'],'title':title,'description':'Biến là tên dùng để lưu giá trị trong bộ nhớ. Vòng lặp for dùng để duyệt các phần tử trong danh sách. Hàm len trả về số phần tử. Danh sách là kiểu dữ liệu lưu nhiều phần tử theo thứ tự. Điều kiện if dùng để rẽ nhánh. Python sử dụng thụt lề để xác định khối lệnh.','order_index':i,'video_url':'','document_url':''})
            state['lessons'].append(int(b['id']));save()
        b,_=call(owner,'POST','/api/quizzes','Tạo đề 6 câu, 3 lượt, đạt 70%',json={'course_id':cid,'title':state['run']+' kiểm tra cuối khóa','duration':10,'max_attempts':3,'passing_score':70,'grading_method':'latest'})
        state['quiz_id']=int(b['id']);state['correct_values']={};save()
        for i in range(6):
            b,_=call(owner,'POST','/api/quizzes/questions','Tạo câu hỏi '+str(i+1),json={'quiz_id':state['quiz_id'],'content':f'Câu kiểm thử {i+1}: {i+1} + 1 bằng bao nhiêu?','option_a':str(i+1),'option_b':str(i+2),'option_c':str(i+3),'option_d':str(i+4),'correct_answer':'B','explanation':f'{i+1} + 1 = {i+2}','difficulty':'easy','knowledge_chapter_id':state['chapter_id'],'knowledge_lesson_id':state['lessons'][i//3],'order_index':i})
        b,_=call(owner,'GET',f"/api/quizzes/questions?quiz_id={state['quiz_id']}",'Đọc đáp án gốc của giảng viên')
        state['correct_values']={str(q['id']):q['option_b'] for q in b['data']};save()
        for role in ['student_em','student_phuong',other]:
            call(role,'GET',f"/api/quizzes/questions?quiz_id={state['quiz_id']}",'Chặn mở đề khi chưa có quyền',403)
    # Five CSV exports and invalid filters.
    for kind in ['payments','enrollments','courses','learning','topics']:
        _,r=call('admin','GET','/api/reports/export?type='+kind,'Xuất CSV '+kind,validate=lambda b:b.get('bytes',0)>10)
        if r is not None and r.status_code==200:
            p=ROOT/('functional-export-'+kind+'.csv');p.write_bytes(r.content)
    call('admin','GET','/api/payments/manage?status=abc','Từ chối trạng thái giao dịch sai',400)
    for status in ['completed','failed','refunded','pending']:
        call('admin','GET','/api/payments/manage?status='+status,'Lọc giao dịch '+status,validate=lambda b,s=status:all(x['status']==s for x in b['data']))
    save()

def finish():
    login()
    cid=state['course_id'];qid=state['quiz_id']
    for role in ['student_em','student_phuong']:
        for name,path in [('Tiến độ sau khi học',f'/api/progress?course_id={cid}'),('Phân tích sau các lượt làm',f'/api/analytics/overview?course_id={cid}'),('So sánh các lượt quiz',f'/api/analytics/quiz-progress?quiz_id={qid}'),('Gợi ý học tập sau làm bài',f'/api/recommendations?course_id={cid}'),('Lịch sử kết quả',f'/api/quizzes/results?quiz_id={qid}')]:
            call(role,'GET',path,name)
        call(role,'POST','/api/recommendations/refresh','Lưu gợi ý học tập',json={'course_id':cid})
    # Confirm actual quiz grade through displayed shuffled values using remaining attempts.
    for role in ['student_em','student_phuong']:
        b,_=call(role,'GET',f'/api/quizzes/questions?quiz_id={qid}','Không mở thêm đề khi hết 3 lượt',403)
    call('teacher_an','POST','/api/quizzes/submit','Giảng viên làm thử đúng 6/6',json={'quiz_id':qid,'answers':{k:'B' for k in state['correct_values']}},validate=lambda b:b.get('percent')==100)
    call('teacher_binh','POST','/api/quizzes/submit','Chặn giảng viên khác nộp bài',403,json={'quiz_id':qid,'answers':{}})
    paid=state['fixture_courses'][1]
    call('teacher_binh','PUT','/api/courses','Đặt giá khóa test thanh toán 10000đ',json={'id':paid,'title':state['run']+' teacher_binh','price':10000,'status':'published'})
    call('student_em','POST','/api/enrollments','Chặn ghi danh miễn phí khóa trả phí',403,json={'course_id':paid})
    b,_=call('student_em','POST','/api/payments/vnpay/create','Khởi tạo đơn VNPay khóa test',json={'course_id':paid},validate=lambda b:bool(b.get('payment_url')) and b.get('amount')==10000)
    state['payment_test']={k:v for k,v in b.items() if k!='payment_url'}
    if b.get('payment_url'):
        from urllib.parse import urlparse,parse_qs
        url=urlparse(b['payment_url']);params=parse_qs(url.query)
        state['payment_test']['host']=url.hostname
        state['payment_test']['amount_gateway']=params.get('vnp_Amount')
    save()
    call('student_em','GET',f'/api/payments/check?course_id={paid}','Đơn chờ chưa cấp quyền học',validate=lambda b:not b.get('enrolled') and not b.get('paid'))
    call('student_em','GET',f'/api/lessons?id={state["lessons"][0]}','Đọc nội dung bài đã ghi danh')
    # Live AI: upload bounded local material and verify index status, not merely HTTP 200.
    material=('Tài liệu Python kiểm thử. Biến trong Python là tên dùng để lưu trữ giá trị trong bộ nhớ. '
      'Danh sách trong Python lưu nhiều phần tử theo thứ tự và có thể thay đổi. '
      'Hàm len trả về số phần tử của danh sách. Vòng lặp for dùng để duyệt từng phần tử của danh sách. '
      'Câu lệnh if kiểm tra điều kiện và chọn nhánh thực thi. Python dùng thụt lề để xác định khối lệnh. '
      'Hàm được định nghĩa bằng từ khóa def. Từ khóa return trả kết quả từ hàm. '
      'Kiểu int lưu số nguyên và kiểu str lưu chuỗi ký tự. Toán tử cộng hai số nguyên trả về tổng của chúng.')
    b,_=call('teacher_an','POST','/api/ai/documents','Tải tài liệu TXT và lập chỉ mục RAG',files={'file':('audit-python.txt',material.encode(),'text/plain')},data={'course_id':str(cid),'lesson_id':str(state['lessons'][0]),'title':state['run']+' tài liệu Python'},validate=lambda b:b.get('data',{}).get('status')=='indexed')
    if b.get('data',{}).get('id'): state['document_id']=b['data']['id'];save()
    for role in ['student_em','student_phuong']:
        call(role,'POST','/api/ai/chat','AI từ chối câu hỏi rỗng',400,json={'course_id':cid,'message':''})
        for message in ['Biến trong Python dùng để làm gì?','Ai vô địch World Cup năm 2018?']:
            b,_=call(role,'POST','/api/ai/chat','AI Tutor: '+message,json={'course_id':cid,'message':message},validate=lambda b:bool(b.get('data',{}).get('answer')))
            conv=b.get('data',{}).get('conversation_id')
            if conv:
                call(role,'GET',f'/api/ai/conversations/{conv}','Đọc lịch sử hội thoại')
                other='student_phuong' if role=='student_em' else 'student_em'
                call(other,'GET',f'/api/ai/conversations/{conv}','Chặn đọc hội thoại người khác',[403,404])
                call(role,'DELETE',f'/api/ai/conversations/{conv}','Xóa hội thoại test')
    b,_=call('teacher_an','POST','/api/ai/generate-quiz','Sinh đề AI live 3 câu dễ',json={'course_id':cid,'lesson_id':state['lessons'][0],'number_of_questions':3,'difficulty':'easy'},validate=lambda b:len(b.get('data',{}).get('questions',[]))>0)
    if b.get('success') and b.get('data',{}).get('questions'):
        call('teacher_an','POST','/api/ai/quiz/approve','Duyệt và lưu đề AI',json={'course_id':cid,'title':state['run']+' AI','questions':b['data']['questions']})
    snapshot('during')
    save()

def cleanup():
    login()
    if state.get('document_id'):
        call('teacher_an','DELETE',f"/api/ai/documents?id={state['document_id']}",'Dọn tài liệu test')
    # Fixture-only cleanup; direct DB removal is needed for courses with submitted results.
    sys.path.insert(0,str(ROOT.parent/'backend'))
    from app.core.database import SessionLocal
    from sqlalchemy import text
    with SessionLocal() as db:
        for cid in state.get('fixture_courses',[]):
            row=db.execute(text('SELECT title FROM courses WHERE id=:id'),{'id':cid}).scalar()
            if row and row.startswith(state['run']):
                db.execute(text('DELETE FROM courses WHERE id=:id'),{'id':cid})
        db.commit()
        remaining=db.execute(text('SELECT COUNT(*) FROM courses WHERE title LIKE :prefix'),{'prefix':state['run']+'%'}).scalar()
    results.append({'name':'Dọn khóa test, kết quả và dữ liệu phụ thuộc','role':'cleanup','passed':remaining==0,'remaining_courses':remaining})
    if state.get('temporary_user'):
        call('admin','DELETE',f"/api/users?id={state['temporary_user']}",'Dọn tài khoản test')
    if state.get('registered_user'):
        call('admin','DELETE',f"/api/users?id={state['registered_user']}",'Dọn tài khoản tự đăng ký')
    snapshot('after')
    state['finished_at']=datetime.now().isoformat();save()
    print('TOTAL',len(results),'PASS',sum(x['passed'] for x in results),'FAIL',sum(not x['passed'] for x in results))

def extended():
    login()
    cid=state['course_id'];ch=state['chapter_id']
    clients['public']=httpx.Client(base_url='http://127.0.0.1:8080',timeout=30)
    email=state['run'].lower()+'registered@audit.local'
    body={'fullname':state['run']+' đăng ký','email':email,'password':'Audit123456','confirm_password':'Audit123456'}
    call('public','POST','/api/auth/register','Tự đăng ký học viên',json=body)
    call('public','POST','/api/auth/register','Chặn đăng ký trùng email',409,json=body)
    b,_=call('public','POST','/api/auth/login','Đăng nhập tài khoản tự đăng ký',json={'email':email,'password':'Audit123456'})
    clients['registered_student']=httpx.Client(base_url='http://127.0.0.1:8080',timeout=30,headers={'Authorization':'Bearer '+b['token']})
    state['registered_user']=b['user']['id'];save()
    call('registered_student','POST','/api/auth/change-password','Đổi mật khẩu tài khoản test',json={'old_password':'Audit123456','new_password':'Audit345678'})
    call('public','POST','/api/auth/login','Mật khẩu cũ không còn dùng được',401,json={'email':email,'password':'Audit123456'})
    call('public','POST','/api/auth/login','Mật khẩu mới đăng nhập được',json={'email':email,'password':'Audit345678'})
    call('registered_student','PUT','/api/users','Cập nhật hồ sơ học viên',json={'id':state['registered_user'],'fullname':state['run']+' hồ sơ cập nhật','email':email,'role':'student','bio':'Kiểm thử cập nhật hồ sơ'})
    call('student_em','POST','/api/enrollments','Chặn ghi danh miễn phí khóa trả phí',402,json={'course_id':state['fixture_courses'][1]})
    call('teacher_an','DELETE',f'/api/courses?id={cid}','Chặn xóa khóa đã có học viên',409)
    call('teacher_an','POST','/api/ai/documents','Từ chối định dạng tài liệu không hỗ trợ',400,files={'file':('audit.exe',b'not executable','application/octet-stream')},data={'course_id':str(cid)})
    b,_=call('teacher_an','POST','/api/chapters/review','Tạo bộ ôn tập chương',json={'chapter_id':ch})
    review=b['data']['quiz_id'];state['review_quiz_id']=review;save()
    for i in range(6):
        call('teacher_an','POST','/api/quizzes/questions','Tạo câu ôn tập chương '+str(i+1),json={'quiz_id':review,'content':f'Ôn tập {i+1}: {i+1} + 2 bằng bao nhiêu?','option_a':str(i),'option_b':str(i+3),'option_c':str(i+5),'option_d':str(i+7),'correct_answer':'B','knowledge_chapter_id':ch,'knowledge_lesson_id':state['lessons'][i//3]})
    source,_=call('teacher_an','GET',f'/api/quizzes/questions?quiz_id={review}','Đọc đề ôn tập gốc')
    correct={str(q['id']):q['option_b'] for q in source['data']}
    browser=json.loads((ROOT/'functional-account-browser.json').read_text(encoding='utf-8'))
    for role,target in [('student_em',0),('student_phuong',3)]:
        for n in [target,6]:
            opened,_=call(role,'GET',f'/api/quizzes/questions?quiz_id={review}','Mở lượt ôn tập chương')
            answers={}
            for i,q in enumerate(opened['data']):
                answers[str(q['id'])]=next(k for k in 'ABCD' if q.get('option_'+k.lower()) and ((q['option_'+k.lower()]==correct[str(q['id'])])==(i<n)))
            b,_=call(role,'POST','/api/quizzes/submit',f'Ôn tập chương {n}/6 câu đúng',json={'quiz_id':review,'answers':answers,'attempt_token':opened['attempt_token']},validate=lambda b,n=n:b.get('percent')==n/6*100)
            call(role,'POST','/api/quizzes/submit','Từ chối nộp lại lượt đã hoàn tất',403,json={'quiz_id':review,'answers':answers,'attempt_token':opened['attempt_token']})
            rec,_=call(role,'GET',f'/api/recommendations?course_id={cid}',f'Gợi ý sau ôn tập {n}/6')
            if n==target:
                call(role,'POST','/api/recommendations/study','Ghi nhận mốc trước khi ôn lại chương',json={'course_id':cid,'knowledge_kind':'chapter','unit_id':ch})
            else:
                call(role,'GET',f'/api/recommendations/progress?course_id={cid}','So sánh trước/sau ôn tập chương')
        own=next(x['data']['result_id'] for x in browser if x['role']==role and 'Làm quiz' in x['name'] and x['passed'])
        other='student_phuong' if role=='student_em' else 'student_em'
        call(other,'GET',f'/api/quizzes/results?id={own}','Chặn học viên đọc kết quả của người khác',[403,404])
        call(role,'GET',f'/api/analytics/overview?course_id={cid}','Ôn tập không làm thay đổi điểm chính thức',validate=lambda b:b['data']['avg_quiz_score']==100)
    snapshot('during_extended');save()

def exports():
    clients['admin']=httpx.Client(base_url='http://127.0.0.1:8080',timeout=30)
    b,_=call('admin','POST','/api/auth/login','Đăng nhập tài khoản mẫu',json={'email':ACCOUNTS['admin'],'password':'123456'})
    clients['admin'].headers['Authorization']='Bearer '+b['token']
    for kind in ['payments','enrollments','courses','learning','topics']:
        _,r=call('admin','GET','/api/reports/export?type='+kind,'Xuất CSV '+kind,validate=lambda b:b.get('bytes',0)>10)
        if r is not None and r.status_code==200:
            (ROOT/('functional-export-'+kind+'.csv')).write_bytes(r.content)
    save()

if __name__=='__main__':
    action=sys.argv[1]
    if action!='prepare':
        state=json.loads(STATE.read_text(encoding='utf-8'));results=json.loads(OUT.read_text(encoding='utf-8'))
    {'prepare':prepare,'finish':finish,'extended':extended,'cleanup':cleanup,'exports':exports}[action]()
