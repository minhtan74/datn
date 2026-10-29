"""Summarize recorded observations, preserving first attempts and corrected harness checks."""
import csv
import json
import math
import statistics
from pathlib import Path

D=Path(__file__).resolve().parent
read=lambda p:json.loads((D/p).read_text(encoding='utf-8'))
api=read('functional-account-api.json')
ui=read('functional-account-browser.json')
state=read('functional-account-state.json')
latest_api={(x['role'],x['name'],x.get('method'),x.get('path')):x for x in api}
latest_ui={(x['role'],x['name']):x for x in ui}
normal=sorted(x['ms'] for x in api if 'ms' in x and not x.get('path','').startswith('/api/ai/'))
semantic=[]
def check(name,passed,evidence):
    semantic.append({'name':name,'passed':bool(passed),'evidence':evidence})
for role in ['student_em','student_phuong']:
    scores=[x['data']['percent'] for x in ui if x['role']==role and x['name'].startswith('Làm quiz') and x['passed']]
    check(role+' / điểm qua giao diện',scores==[0,50,100],scores)
    p=next(x['response']['data'] for x in api if x['role']==role and x['name']=='Phân tích sau các lượt làm')
    check(role+' / tiến độ và điểm chính thức',p['completion_pct']==100 and p['avg_quiz_score']==100 and p['quiz_attempts']==3,p)
    p=next(x['response']['data'][0] for x in api if x['role']==role and x['name']=='So sánh trước/sau ôn tập chương')
    expected=100 if role=='student_em' else 50
    check(role+' / cải thiện ôn tập',p['difference_pct']==expected and p['after']['needs_review'] is False,{'before':p['before']['avg_score'],'after':p['after']['avg_score'],'difference_pct':p['difference_pct'],'same_questions':p['same_questions']})
for key in ['summary','learning']:
    check('Khôi phục số liệu '+key,state['before'][key]['overview']==state['after'][key]['overview'],state['after'][key]['overview'])
check('Khôi phục số người dùng',len(state['before']['users'])==len(state['after']['users']),len(state['after']['users']))
check('Khôi phục danh sách khóa',{c['id'] for c in state['before']['courses']}=={c['id'] for c in state['after']['courses']},len(state['after']['courses']))
ai=next(x for x in api if x['name']=='Sinh đề AI live 3 câu dễ')
questions=ai['response']['data']['questions']
check('Câu AI đủ số lượng, phương án, đáp án và bằng chứng',len(questions)==3 and all(len(q['options'])==4 and q['correct_answer'] in q['options'] and q.get('grounded') and q.get('verified')==q['correct_answer'] and q.get('evidence') for q in questions),ai['response']['data']['meta'])
summary={
 'date':'2026-10-29','timezone':'Asia/Saigon','run':state['run'],
 'api':{'recorded_http_requests':sum('method'in x for x in api),'unique_scenarios':sum('method'in x for x in latest_api.values()),'latest_failed':sum(not x['passed'] for x in latest_api.values()),'first_expectation_mismatches':sum(not x['passed'] for x in api)},
 'browser':{'recorded_attempts':len(ui),'unique_scenarios':len(latest_ui),'latest_failed':sum(not x['passed'] for x in latest_ui.values()),'initial_harness_failures':sum(not x['passed'] for x in ui)},
 'non_ai_api_latency_ms':{'n':len(normal),'median':statistics.median(normal),'p95_nearest_rank':normal[math.ceil(len(normal)*.95)-1],'max':max(normal)},
 'semantic_checks':semantic,
 'baseline':{'business':state['before']['summary']['overview'],'learning':state['before']['learning']['overview']},
 'ai_tutor':[{'role':x['role'],'name':x['name'],'ms':x['ms'],'fallback':'tạm gián đoạn' in x.get('response',{}).get('data',{}).get('answer',''),'response':x.get('response',{}).get('data')} for x in api if x['name'].startswith('AI Tutor:')],
 'ai_quiz':{'ms':ai['ms'],'meta':ai['response']['data']['meta']},
}
(D/'functional-account-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
with (D/'functional-account-checks.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['Kênh','Vai trò','Kịch bản','Kết quả cuối','HTTP','Thời gian (ms)'])
    for x in latest_api.values():writer.writerow(['API' if 'method'in x else 'Cleanup',x['role'],x['name'],'PASS' if x['passed'] else 'FAIL',x.get('status',''),x.get('ms','')])
    for x in latest_ui.values():writer.writerow(['Browser',x['role'],x['name'],'PASS' if x['passed'] else 'FAIL','',x.get('ms','')])
print(json.dumps({'api':summary['api'],'browser':summary['browser'],'latency':summary['non_ai_api_latency_ms'],'semantic_passed':sum(x['passed'] for x in semantic),'semantic_total':len(semantic)}))
if any(not x['passed'] for x in semantic):raise SystemExit('Semantic checks failed')
