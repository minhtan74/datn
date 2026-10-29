"""Small follow-up checks; kept separate from the fifty first responses."""
import importlib.util
import json
import threading
from datetime import datetime
from pathlib import Path
import httpx

D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('qa_core',D/'ai-qa-account-audit.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.rows=[];m.lock=threading.Lock()
m.state={'started_at':datetime.now().isoformat(),'conversations':[]}
def save():
    (D/'ai-everyday-controls.json').write_text(json.dumps(m.rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (D/'ai-everyday-controls-state.json').write_text(json.dumps(m.state,ensure_ascii=False,indent=2),encoding='utf-8')
m.save=save

def main():
    m.state['before_counts']=m.counts()
    for role in ['student_em','student_phuong']:
        c=httpx.Client(base_url='http://127.0.0.1:8080',timeout=210)
        b=c.post('/api/auth/login',json={'email':m.ACCOUNTS[role],'password':'123456'}).json();c.headers['Authorization']='Bearer '+b['token'];m.clients[role]=c
    try:
        m.ask('student_phuong','formal-primary-key','Theo tài liệu, khóa chính có được chứa các giá trị trùng nhau hay không?',course=6,rubric='Khóa chính phải duy nhất, không trùng.')
        m.ask('student_em','formal-conversion','Trong Python, cách dùng int() và str() để chuyển đổi giữa số và chuỗi như thế nào?',course=1,rubric='Giải thích đổi kiểu từ tài liệu biến/kiểu dữ liệu.')
        m.ask('student_em','repeat-print-error','sao em gõ print("2" + 3) nó báo lỗi vậy, sửa hộ em với',course=1,rubric='Thử lại nguyên văn ca daily-05; không thay kết quả ban đầu.')
        m.ask('student_em','formal-indentation','Khối lệnh sau if trong Python cần thụt lề như thế nào?',course=1,rubric='Quy tắc thụt lề theo tài liệu if/else.')
    finally:
        for role,conv in m.state['conversations']:m.request(role,'DELETE',f'/api/ai/conversations/{conv}',f'cleanup-{conv}')
        m.state['after_counts']=m.counts();m.state['finished_at']=datetime.now().isoformat();save()

if __name__=='__main__':main()
