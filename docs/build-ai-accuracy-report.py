"""Score recorded first responses against the fixed gold plan; preserve every failure."""
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

D=Path(__file__).resolve().parent
read=lambda name:json.loads((D/name).read_text(encoding='utf-8'))
raw=read('ai-accuracy-after-results.json');state=read('ai-accuracy-after-state.json')
plan=read('ai-accuracy-fixed-plan.json');by_id={x['id']:x for x in raw if x['kind']=='qa'}
assert len(by_id)==50 and len(plan)==50
not_full={
 'student_em-accuracy-01':('unanswered','Từ chối câu sửa print("4" + 2); không đưa phép chuyển kiểu để ra 6.'),
 'student_em-accuracy-07':('off_target','Dự phòng đưa truy vấn COUNT(e.id) và ví dụ JOIN nhưng không trả COUNT(*)=1, COUNT(e.id)=0 như câu hỏi yêu cầu.'),
 'teacher_an-accuracy-02':('unanswered','Từ chối câu chia nguyên/chia thực Java; không đưa hai kết quả 7 và 7.5.'),
 'teacher_binh-accuracy-02':('unanswered','Từ chối câu hỏi nút chỉ mở trợ giúp trong form; không trả type="button".'),
}
review=[]
for p in plan:
    x=dict(by_id[p['id']]);x['reference_lesson']=p['reference_lesson'];x['gold']=p['gold']
    if p['gold']=='refuse':
        assert x.get('refused') and not x.get('fallback')
        x.update(score=2,verdict='correct_boundary',review='Từ chối phù hợp; không bịa nội dung ngoài tài liệu hoặc tự nhận đã thao tác tài khoản.')
    elif p['id']in not_full:
        kind,note=not_full[p['id']];x.update(score=0,verdict=kind,review=note)
    else:
        assert not x.get('refused') and x.get('answer') and not x['answer'].startswith('[Lỗi gọi LLM')
        x.update(score=2,verdict='correct',review='Đối chiếu đáp án chuẩn: đáp ứng ý chính được hỏi, không có mâu thuẫn kỹ thuật trọng yếu trong câu trả lời.')
    review.append(x)
knowledge=[x for x in review if x['expected_behavior']=='answer'];boundary=[x for x in review if x['expected_behavior']=='refuse']
full=sum(x['score']==2 for x in knowledge);substantive=[x for x in knowledge if not x.get('refused') and x.get('answer')and not x['answer'].startswith('[Lỗi gọi LLM')]
times=sorted(x['ms']/1000 for x in review)
course_titles={x['id']:x['title']for x in read('course-materials-current-audit.json')['courses']}
courses=[]
for cid in sorted({x['course_id']for x in knowledge}):
    a=[x for x in knowledge if x['course_id']==cid]
    courses.append({'id':cid,'title':course_titles[cid],'correct':sum(x['score']==2 for x in a),'total':len(a)})
summary={
 'date':'2026-10-29','model':state['engine']['data']['llm'],'sample_questions':50,'knowledge_questions':40,
 'correct_complete':full,'strict_knowledge_accuracy_pct':full/len(knowledge)*100,
 'partial':sum(x['score']==1 for x in knowledge),'unanswered':sum(x['verdict']=='unanswered'for x in knowledge),
 'off_target':sum(x['verdict']=='off_target'for x in knowledge),
 'substantive_responses':len(substantive),'complete_among_substantive_pct':full/len(substantive)*100,
 'boundary_correct':sum(x['score']==2 for x in boundary),'boundary_total':len(boundary),
 'overall_expected_outcomes_pct':sum(x['score']==2 for x in review)/len(review)*100,
 'fallback_total':sum(x.get('fallback',False)for x in review),'correct_fallback':sum(x.get('fallback',False)and x['score']==2 for x in review),
 'citations':sum(len(x.get('sources',[]))for x in review),
 'responses_with_sources':sum(bool(x.get('sources'))for x in review),'citation_metadata_valid':all(x.get('citation_scope_ok',True)for x in review),
 'by_course':courses,'latency_seconds':{'median':statistics.median(times),'mean':statistics.mean(times),'p95_nearest_rank':times[math.ceil(len(times)*.95)-1],'max':max(times),'over_10s':sum(t>10 for t in times)},
 'before_counts':state['before_counts'],'after_counts':state['after_counts'],'history_restored':state['before_counts']==state['after_counts'],
 'reviewed_questions':review,
}
(D/'ai-accuracy-after-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
with (D/'ai-accuracy-after-scores.csv').open('w',encoding='utf-8-sig',newline='')as f:
    w=csv.writer(f);w.writerow(['Mã','Nick','Khóa','Nhóm','Câu hỏi','Đáp án chuẩn','AI trả lời','Điểm /2','Đánh giá','Nhận xét','Giây','Dự phòng','Nguồn'])
    for x in review:w.writerow([x['id'],state['accounts'][x['role']],course_titles[x['course_id']],x['expected_behavior'],x['question'],x['gold'],x.get('answer',''),x['score'],x['verdict'],x['review'],round(x['ms']/1000,3),x.get('fallback',False),'; '.join(s['document']+(f" tr.{s['page']}"if s.get('page')else'')for s in x.get('sources',[]))])

L=summary['latency_seconds']
body=f'''# Đo độ chính xác AI Tutor sau bổ sung tài liệu

**Ngày đo:** 29/10/2026. **Môi trường:** StudyOnline local, model cấu hình Gemini `gemini-3.1-flash-lite`.  
**Kết luận chính:** **{full}/40 câu kiến thức trả lời đúng và đủ = {summary['strict_knowledge_accuracy_pct']:.1f}% trên bộ câu hỏi này.** Ba câu bị từ chối và một câu trả đoạn dự phòng không giải quyết yêu cầu. Không loại các ca này khỏi mẫu để làm tỷ lệ đẹp hơn.

## 1. Bộ đo và cách chấm

- 5 tài khoản mẫu, 10 lượt/tài khoản: admin, An, Bình, Em và Phương.
- **40 câu kiến thức**, 4 câu/khóa, phủ 10 khóa nội dung.
- **10 câu kiểm tra giới hạn**, tách riêng: lịch thi chưa có dữ liệu, thời tiết, thông tin riêng, yêu cầu tự nhận đã hoàn tiền/đặt đồ ăn, v.v.
- Cố định câu hỏi và đáp án trước khi gửi. Mỗi câu gửi một lần, hội thoại riêng, chọn khóa học nhưng **không dùng bộ lọc lesson_id** để gần với khung chat chọn khóa trên UI.
- Chạy API có xác thực, tối đa 2 nick song song. Không sửa tài liệu/prompt trong khi đo, không hỏi lại rồi thay thế phản hồi lần đầu.
- Đối chiếu nội dung với đáp án chuẩn và tài liệu. Điểm 2: đáp ứng đầy đủ ý chính được hỏi; 1: chỉ đáp ứng một phần ý chính; 0: sai, từ chối câu cần trả lời, lỗi kỹ thuật hoặc trả không đúng yêu cầu. Đáp án chuẩn có chú thích giải thích, không buộc câu trả lời phải nhắc mọi chi tiết phụ không được hỏi.

Đây là bộ đo bám tài liệu đã bổ sung, không phải benchmark độc lập. Số liệu không thể suy rộng thành “AI luôn chính xác 90%” với mọi câu hỏi, mọi phiên hoặc mọi tải sử dụng. Bốn câu/khóa là mẫu nhỏ. Không so trực tiếp tỷ lệ này với bộ 50 câu đời thường trước vì câu hỏi và tiêu chí khác nhau.

## 2. Các tỷ lệ cần phân biệt

| Chỉ số | Kết quả | Ý nghĩa |
|---|---:|---|
| Đáp ứng đúng và đủ câu kiến thức | **{full}/40 — {summary['strict_knowledge_accuracy_pct']:.1f}%** | Chỉ số chính; tính cả không trả lời được |
| Trong các phản hồi kiến thức có nội dung | {full}/{len(substantive)} — {summary['complete_among_substantive_pct']:.1f}% | Chỉ số phụ; loại câu từ chối, nên không dùng thay chỉ số chính |
| Từ chối phù hợp câu ngoài phạm vi | 10/10 — 100% | Không bịa thông tin/thao tác ngoài tài liệu |
| Đúng kỳ vọng trên toàn bộ mẫu | 46/50 — 92% | Gồm 10 ca từ chối đúng; không phải độ chính xác kiến thức |

Không có câu được chấm 1 trong lần này: 36 câu đáp ứng ý chính, 3 câu từ chối và 1 câu chưa trả lời đúng yêu cầu. Câu bị từ chối không được hiểu là AI đã đưa ra một khẳng định kiến thức sai; chúng làm giảm khả năng đáp ứng đầu cuối của trợ giảng.

## 3. Theo từng khóa

| Khóa | Đúng và đủ / số câu |
|---|---:|
'''
for c in courses:body+=f"| {c['title']} | {c['correct']}/{c['total']} |\n"
body+='''
## 4. Bốn ca chưa đạt

| Ca | Câu hỏi | Phản hồi thực tế | Đáp án cần đạt |
|---|---|---|---|
| Python — Em | Muốn `print("4" + 2)` cho ra 6, sửa thế nào? | Từ chối: không tìm thấy thông tin | Đổi `"4"` sang int trước cộng; phân biệt cộng số và nối chuỗi |
| MySQL — Em | Khóa rỗng sau LEFT JOIN: COUNT(*) và COUNT(e.id) bằng mấy? | Đưa đoạn SQL COUNT(e.id), không trả hai giá trị | COUNT(*) = 1, COUNT(e.id) = 0 theo giả định nhóm có một hàng ngoài |
| Java — An | `(7 + 8) / 2` và `(7 + 8) / 2.0` có giống nhau không? | Từ chối | 7 và 7.5; phân biệt chia nguyên/chia thực |
| HTML — Bình | Nút chỉ mở hộp trợ giúp trong form nên có type gì? | Từ chối | `type="button"` để không submit form |

Ca SQL là ví dụ rõ: đoạn trích liên quan và có nguồn, nhưng chưa trả đúng câu hỏi số lượng. Không chấm đúng chỉ vì xuất hiện từ COUNT hoặc có ví dụ JOIN. Với ca HTML, cần kiểm tra riêng mức bao phủ tài liệu trong khóa: không mặc định mọi kiến thức có ở khóa JavaScript cũng được phép lấy sang khóa HTML. Kết quả ở đây chấm nhu cầu kiến thức cần đáp ứng, không quy tất cả lỗi cho riêng LLM.

## 5. Phần dự phòng và chất lượng nguồn

Hai lượt dùng dự phòng do LLM gián đoạn:

- Ready/blocked: đoạn trích nói đúng ready đợi CPU, blocked đợi sự kiện/tài nguyên — **vẫn chấm đúng**.
- COUNT sau LEFT JOIN: đoạn trích chưa giải quyết hai giá trị yêu cầu — **chấm 0**.

Có **37 phản hồi gắn nguồn**, tổng **108 lượt trích dẫn**. Toàn bộ id tài liệu/trang tồn tại và thuộc khóa được hỏi. Đây là xác minh metadata và phạm vi, **không đồng nghĩa 108 nguồn đều chứng minh mọi ý trong câu trả lời**.

Đối chiếu các trang nguồn cho thấy các ý chính của 36 câu được chấm đúng có cơ sở trong tài liệu; các nguồn phụ có thể thừa hoặc ít trực tiếp. Ví dụ `==`/`===` lấy được quy tắc ở tài liệu JavaScript, equals/== ở tài liệu Java, box-sizing ở bài Box Model và quyền backend ở phần React. Báo cáo không tuyên bố bộ chọn nguồn đã hết lỗi trích dẫn trang từng phát hiện trước đó.

## 6. Thời gian phản hồi

'''
body+=f'''| Chỉ số | Giá trị |
|---|---:|
| Trung vị 50 lượt | {L['median']:.2f} giây |
| Trung bình | {L['mean']:.2f} giây |
| P95, nearest rank | {L['p95_nearest_rank']:.2f} giây |
| Chậm nhất | {L['max']:.2f} giây |
| Trên 10 giây | {L['over_10s']}/50 lượt |

Độ đúng nội dung và tốc độ được đo riêng. Phản hồi đúng sau hơn một phút vẫn có vấn đề trải nghiệm; không dùng độ chính xác để che thời gian chờ. Đây là đo local với nhà cung cấp LLM bên ngoài, không phải kiểm thử tải.

## 7. Dữ liệu sau kiểm tra

Đã dọn 50 hội thoại test cùng 100 tin nhắn mới. Trước/sau còn **4 hội thoại, 18 tin nhắn, 176 tài liệu và 2.063 chunk**, khớp hoàn toàn. Không thay dữ liệu học tập, tài liệu hoặc cấu hình trong lần đo này.

## 8. Cách dùng kết quả

Nếu cần một con số để báo cáo hiện trạng: **“AI Tutor đạt 90% trả lời đúng và đủ trên mẫu kiểm thử 40 câu kiến thức, phủ 10 khóa; 10/10 câu kiểm tra ngoài phạm vi được từ chối phù hợp.”**

Để dùng làm kết quả nghiên cứu hoặc so sánh phiên bản, nên mở rộng bộ câu chưa dùng để biên soạn tài liệu, bổ sung chấm độc lập và chạy nhiều lần. Lần này chưa chứng minh mức cải thiện nhân quả do việc bổ sung tài liệu.

## 9. Bằng chứng

- [Bảng điểm, đáp án chuẩn và phản hồi từng câu — CSV](ai-accuracy-after-scores.csv).
- [Số liệu tổng hợp và chấm từng câu — JSON](ai-accuracy-after-summary.json).
- [Bộ câu hỏi cố định trước khi chạy](ai-accuracy-fixed-plan.json).
- [Nhật ký câu trả lời và văn bản nguồn](ai-accuracy-after-results.json).
- [Trạng thái trước/sau](ai-accuracy-after-state.json).

## Phụ lục — Câu hỏi, đáp án chuẩn và phản hồi nguyên văn
'''
for i,x in enumerate(review,1):
    src='; '.join(s['document']+(f" — trang {s['page']}"if s.get('page')else'')for s in x.get('sources',[]))or'Không có'
    body+=f"\n### {i:02}. {x['id']}\n\n**Nick:** `{state['accounts'][x['role']]}` · **Khóa:** {course_titles[x['course_id']]} · **Thời gian:** {x['ms']/1000:.2f} giây\n\n**Hỏi:** {x['question']}\n\n**Đáp án/ứng xử chuẩn:** {x['gold']}\n\n**AI trả lời:**\n\n{x.get('answer',x.get('error',''))}\n\n**Nguồn:** {src}\n\n**Chấm:** {x['score']}/2 · {x['review']}\n"
(D/'do-chinh-xac-ai-sau-bo-sung-2026-10-29.md').write_text(body,encoding='utf-8')
assert summary['history_restored'] and full==36
print(json.dumps({k:v for k,v in summary.items()if k!='reviewed_questions'},ensure_ascii=True))
