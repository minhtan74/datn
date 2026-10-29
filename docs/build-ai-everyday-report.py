import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

D=Path(__file__).resolve().parent
read=lambda name:json.loads((D/name).read_text(encoding='utf-8'))
raw=read('ai-everyday-results.json');state=read('ai-everyday-state.json')
questions=sorted([x for x in raw if x['kind']=='qa'],key=lambda x:(list(state['accounts']).index(x['role']),x['id']))
assert len(questions)==50,'Wait for all 50 first responses before building the final report.'
good={f'{role}-daily-{n:02}' for role,ns in {
 'student_em':[1,2,3,4],'student_phuong':[1,4],'teacher_an':[1,2,3,4],
 'teacher_binh':[1,2,3,4,5,6,7],'admin':[4]}.items() for n in ns}
notes={
 'student_em-daily-05':'Từ chối yêu cầu sửa lỗi trộn chuỗi và số, không hỏi thêm hoặc hướng dẫn đổi kiểu.',
 'student_em-daily-06':'Dự phòng trích đoạn if và ví dụ vòng lặp, không sửa đoạn code thiếu thụt lề được đưa vào.',
 'student_em-daily-07':'Dự phòng trả tiêu đề tài liệu và mục tiêu bài học; không hỗ trợ cảm xúc hoặc đề xuất bước học nhỏ.',
 'student_phuong-daily-02':'Từ chối câu hỏi về trùng id ngay sau ví dụ khóa chính; tài liệu #55 trang 1 có quy tắc khóa chính duy nhất.',
 'student_phuong-daily-03':'Không giải thích điều kiện NULL/NOT NULL hoặc hỏi rõ thiết kế mã lớp.',
 'student_phuong-daily-05':'Hỏi học viên chưa ghi danh; dự phòng trả ví dụ khóa học/chưa có học viên và đếm ghi danh, không giải đúng truy vấn yêu cầu.',
 'student_phuong-daily-06':'Chưa có câu SQL cụ thể; nên xin câu lệnh/lỗi thay vì chỉ từ chối.',
 'teacher_binh-daily-08':'Đưa được bước dùng console.log/F12, nhưng phản hồi còn chung chung, chưa ghi nhận cảm xúc hoặc xin đoạn code/lỗi cụ thể.',
 'admin-daily-02':'Không có danh sách tiến trình thật để chọn app nên không nên đoán; có thể hỏi thêm hoặc hướng cách kiểm tra.',
 'admin-daily-06':'Chưa rõ bài 2 của chương nào; nên hỏi rõ thay vì chỉ từ chối.',
}
study_categories={'colloquial','followup','typo','debug','study_plan','wrong_premise'}
labels={'useful':'Đáp ứng rõ yêu cầu','partial':'Hỗ trợ một phần','fallback_unhelpful':'Dự phòng không giải quyết yêu cầu','refusal':'Từ chối bằng câu mẫu','llm_error':'Lộ thông báo lỗi LLM'}
category_names={'colloquial':'Cách hỏi thân mật','followup':'Hỏi nối tiếp','typo':'Gõ tắt/sai chính tả','debug':'Sửa lỗi và giải thích code','emotion':'Than khó/nản học','study_plan':'Lộ trình và kế hoạch học','unknown_platform':'Yêu cầu dữ liệu/thao tác tài khoản','social':'Chào/cảm ơn/nhận diện AI','ambiguous':'Câu hỏi thiếu ngữ cảnh','out_of_scope':'Chuyện ngoài khóa','wrong_premise':'Câu hỏi có tiền đề sai'}
for x in questions:
    if x['id'] in good:
        assert not x['refused'] and not x['fallback']
        x['assessment']='useful'
    elif x['id']=='teacher_binh-daily-08':x['assessment']='partial'
    elif x.get('answer','').startswith('[Lỗi gọi LLM'):x['assessment']='llm_error'
    elif x['fallback']:x['assessment']='fallback_unhelpful'
    elif x['refused']:x['assessment']='refusal'
    else:raise ValueError('Manual review required for '+x['id'])
    if x['assessment']=='llm_error':x['review_note']='HTTP 200 nhưng nội dung là lỗi kỹ thuật ReadTimeout; không có câu trả lời hữu ích hoặc thông báo thân thiện.'
    elif x['id'] in notes:x['review_note']=notes[x['id']]
    elif x['assessment']=='useful':x['review_note']='Đối chiếu thủ công: trả lời đúng ý chính và đáp ứng yêu cầu của câu này.'
    elif x['expected_behavior']=='unknown_platform':x['review_note']='Không bịa lịch, đề thi, giao dịch hoặc thao tác tài khoản; nhưng không chỉ dẫn luồng hỗ trợ cụ thể.'
    elif x['expected_behavior']=='out_of_scope':x['review_note']='Từ chối phù hợp giới hạn trợ giảng theo tài liệu; không chấm là trả lời sai kiến thức.'
    elif x['expected_behavior']=='social':x['review_note']='Không phản hồi xã giao tự nhiên; dùng câu từ chối tài liệu.'
    elif x['expected_behavior']=='ambiguous':x['review_note']='Không đoán bừa, nhưng thiếu câu hỏi làm rõ.'
    elif x['expected_behavior']=='study_plan':x['review_note']='Không lập kế hoạch/lộ trình hoặc hướng dẫn người học chọn nội dung ôn.'
    else:x['review_note']='Chưa đáp ứng nhu cầu học tập ở cách hỏi này; từ chối không đồng nghĩa nội dung kiến thức bị nói sai.'

times=sorted(x['ms']/1000 for x in questions)
counts=Counter(x['assessment']for x in questions)
academic=[x for x in questions if x['expected_behavior']in study_categories]
summary={'date':'2026-10-29','question_count':50,'accounts':state['accounts'],'assessment_counts':dict(counts),
 'academic_context_count':len(academic),'academic_assessments':dict(Counter(x['assessment'] for x in academic)),
 'by_category':{k:{'total':sum(x['expected_behavior']==k for x in questions),'assessments':dict(Counter(x['assessment'] for x in questions if x['expected_behavior']==k))}for k in category_names},
 'latency_seconds':{'median':statistics.median(times),'mean':statistics.mean(times),'p95_nearest_rank':times[math.ceil(len(times)*.95)-1],'max':max(times),'over_10s':sum(t>10 for t in times),'over_30s':sum(t>30 for t in times)},
 'http_200':sum(x.get('status')==200 for x in questions),'fallback_count':sum(x.get('fallback',False)for x in questions),
 'before_counts':state['before_counts'],'after_counts':state['after_counts'],'history_restored':state['before_counts']==state['after_counts'],
 'reviewed_questions':questions}
controls=read('ai-everyday-controls.json') if (D/'ai-everyday-controls.json').exists() else []
summary['additional_controls']=[x for x in controls if x['kind']=='qa']
(D/'ai-everyday-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
with (D/'ai-everyday-questions.csv').open('w',encoding='utf-8-sig',newline='')as f:
    w=csv.writer(f);w.writerow(['Mã','Tài khoản','Nhóm','Câu hỏi','AI trả lời','Giây','Dự phòng','Đánh giá','Nhận xét','Nguồn'])
    for x in questions:w.writerow([x['id'],state['accounts'][x['role']],category_names[x['expected_behavior']],x['question'],x['answer'],round(x['ms']/1000,3),x['fallback'],labels[x['assessment']],x['review_note'],'; '.join(s['document']+(f" tr.{s['page']}"if s.get('page') else '')for s in x['sources'])])

L=summary['latency_seconds']
body=f'''# Thử AI Tutor bằng 50 câu hỏi đời thường, thực tế

**Ngày:** 29/10/2026. **Môi trường:** StudyOnline local, Gemini `gemini-3.1-flash-lite`.  
**Cách thử:** đăng nhập 5 nick mẫu, mỗi nick 10 câu mới; dùng Python, JavaScript, MySQL và Hệ điều hành. Ba câu đầu của mỗi nick là một hội thoại nối tiếp, các câu còn lại mở hội thoại riêng. Chạy tối đa 2 nick song song, không sửa prompt, tài liệu hay cấu hình AI. Lượt này dùng API có xác thực, không thao tác UI.

## Kết luận

AI hiểu được nhiều cách hỏi thân mật/gõ sai, đặc biệt các câu JavaScript. Nhưng khả năng hỗ trợ học viên trong tình huống thực tế **chưa ổn định**: từ chối nhiều yêu cầu debug, lập lịch học, hỏi thiếu ngữ cảnh và xã giao; lúc LLM gián đoạn, phần trích xuất dự phòng có thể không giải quyết đúng câu hỏi.

**HTTP 200 cả 50 lượt không đồng nghĩa trả lời tốt cả 50 lượt.** Đánh giá thủ công theo yêu cầu cụ thể cho kết quả:

| Phản hồi | Số lượt |
|---|---:|
| Đáp ứng rõ yêu cầu | {counts['useful']} |
| Hỗ trợ một phần | {counts['partial']} |
| Từ chối bằng câu mẫu | {counts['refusal']} |
| Dự phòng nhưng không giải quyết yêu cầu | {counts['fallback_unhelpful']} |
| Chỉ trả thông báo lỗi kỹ thuật LLM | {counts['llm_error']} |

Trong **{len(academic)} câu gắn với nhu cầu học tập**: {Counter(x['assessment']for x in academic)['useful']} câu đáp ứng rõ yêu cầu, {Counter(x['assessment']for x in academic)['refusal']} câu bị từ chối và {Counter(x['assessment']for x in academic)['fallback_unhelpful']} câu dự phòng không giải quyết yêu cầu. Đây là chấm **mức đáp ứng**, không phải tỷ lệ đúng/sai kiến thức: không khẳng định tài liệu có đủ đáp án cho tất cả câu. Các câu ngoài phạm vi, đòi thao tác tài khoản hoặc hỏi thông tin chưa có được xem riêng.

## Một số câu trả lời đáng chú ý

| Câu hỏi thực tế | AI trả lời/ứng xử | Nhận xét |
|---|---|---|
| “list voi tupel khac nhau j v ban?” | list thay đổi được, tuple bất biến | Hiểu tốt gõ tắt và sai chính tả |
| “const rồi mà sao em vẫn push vào array được?” | const không cho gán lại tên biến, không đóng băng đối tượng | Đúng trọng tâm |
| “promsie la j, then catch de lam j v a?” | Giải thích Promise, ba trạng thái, then/catch | Hiểu tốt câu sai chính tả |
| “age = input(...); print(age + 1) ... bị lỗi?” | input trả chuỗi; cần int trước khi cộng | Hữu ích, nối tiếp còn sửa được đoạn code |
| “2 bạn học sinh có cùng id được không?” sau ví dụ khóa chính | “Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học.” | Mất cơ hội dùng ngữ cảnh; tài liệu #55 có quy tắc khóa chính duy nhất |
| `print("2" + 3)` báo lỗi, sửa giúp | Từ chối ở lần đầu | Chưa giải quyết yêu cầu debug |
| Đưa code if thiếu thụt lề, hỏi sửa | Dự phòng trích câu định nghĩa if rồi trộn ví dụ for/break/continue | Không sửa lỗi được hỏi |
| Tìm học viên chưa ghi danh bằng LEFT JOIN | Dự phòng trả ví dụ khóa học/chưa có học viên và đếm ghi danh | Đổi đối tượng truy vấn, không đáp ứng đề bài |
| “em thấy mình dốt quá, chắc bỏ thôi” | Dự phòng trả tiêu đề tài liệu và mục tiêu bài học | Không phản hồi nhu cầu hỗ trợ người học |
| “cái này sao nó không chạy?” | Từ chối bằng câu mẫu | Nên hỏi xin code và thông báo lỗi |
| “cảm ơn nha” / “chào bạn” | Từ chối bằng câu mẫu | Máy móc trong hội thoại |

Đầy đủ câu hỏi, câu trả lời **nguyên văn**, nguồn và thời gian nằm ở phụ lục và [CSV](ai-everyday-questions.csv).

## Kết quả theo nhóm

| Nhóm | Số câu | Đáp ứng rõ | Một phần | Từ chối | Dự phòng không hữu ích | Lỗi LLM |
|---|---:|---:|---:|---:|---:|---:|
'''
for k,name in category_names.items():
    a=summary['by_category'][k];c=a['assessments'];body+=f"| {name} | {a['total']} | {c.get('useful',0)} | {c.get('partial',0)} | {c.get('refusal',0)} | {c.get('fallback_unhelpful',0)} | {c.get('llm_error',0)} |\n"
body+=f'''
Các nick: `admin@gmail.com`, `an.nguyen@studyonline.vn`, `binh.tran@studyonline.vn`, `em.hoang@gmail.com`, `phuong.vu@gmail.com`. Câu hỏi giả lập học viên được gửi từ cả tài khoản admin/giảng viên để thử cách ứng xử của cùng AI Tutor; không phải phản hồi của người dùng thật.

## Điều gì hoạt động tốt?

- Theo được chuỗi Python: giải thích vòng lặp → in 1..5 → giải thích vì sao `range(1,6)` có cận trên 6.
- Theo được chuỗi JavaScript: const/mảng → khi nào dùng let → ví dụ gán lại biến.
- Hiểu được 4/4 câu gõ sai/gõ tắt được thử: tupel, jion, promsie, deadlok.
- Sửa được tiền đề sai `==` và `===` như nhau; giải thích nối chuỗi JavaScript.
- Không tự xác nhận đã đổi mật khẩu, hoàn tiền hay kiểm tra giao dịch; không bịa hạn nộp bài, đề thi ngày mai hoặc số điện thoại riêng của giảng viên.

## Các vấn đề cần chú ý

### 1. Từ chối quá máy móc thay vì hỏi thêm

Ba ca thiếu ngữ cảnh đều nhận câu từ chối, không xin đoạn code hoặc xác định bài/chương. Ba ca xã giao cũng bị từ chối. Đây là giới hạn trải nghiệm hội thoại của RAG hiện tại, không nên thống kê thành AI bịa kiến thức.

Ví dụ cụ thể: sau khi AI vừa lấy ví dụ khóa chính trong bảng học viên, câu “2 bạn học sinh có cùng id được không?” lại bị từ chối. Nên cải thiện cách giữ/viết lại chủ đề và cách hỏi rõ khi chưa chắc người học đang nói tới trường nào.

### 2. Dự phòng có thể trả đoạn gần chủ đề nhưng lệch yêu cầu

Có **{summary['fallback_count']}/50 lượt** dùng thông báo “Trợ giảng AI đang tạm gián đoạn”. Cả ba trường hợp đều chưa giải quyết yêu cầu: sửa thụt lề, tìm học viên chưa ghi danh, hỗ trợ người học nản. Có nguồn và có thông báo dự phòng vẫn chưa đủ để coi câu trả lời hữu ích.

Đặc biệt, truy vấn LEFT JOIN cần phân biệt **học viên chưa có khóa** với **khóa chưa có học viên**; không nên lấy ví dụ tương tự rồi coi là đáp án cho bài toán khác.

### 3. Thiếu hỗ trợ lập lộ trình và phản hồi cảm xúc

Cả ba yêu cầu lập kế hoạch/chọn nội dung ôn đều bị từ chối. Với lời than nản, một ca trả đoạn trích không liên quan; ca còn lại đưa mẹo console.log/F12 nhưng chưa ghi nhận cảm xúc hoặc xin đoạn code/thông báo lỗi cụ thể. Nếu sản phẩm muốn làm trợ giảng hội thoại, cần xác định rõ được phép động viên, hỏi thêm và gợi ý bước học nhỏ trong giới hạn nào.

### 4. Tốc độ phản hồi biến động

| Chỉ số trên 50 lượt đầu | Thời gian |
|---|---:|
| Trung vị | {L['median']:.2f} giây |
| Trung bình | {L['mean']:.2f} giây |
| P95, nearest rank | {L['p95_nearest_rank']:.2f} giây |
| Lớn nhất | {L['max']:.2f} giây |
| Lượt trên 10 giây | {L['over_10s']}/50 |
| Lượt trên 30 giây | {L['over_30s']}/50 |

Đo trên local với tối đa hai tài khoản song song, có gọi nhà cung cấp LLM; không phải kiểm thử tải. Không đủ nhật ký để quy mọi lần chậm cho một nguyên nhân như rate limit, retry hoặc mạng.

Một lượt hỏi hoàn tiền nhận nguyên văn **`[Lỗi gọi LLM: ReadTimeout]`** sau khoảng 65,85 giây, dù HTTP vẫn là 200. Chat không hề thực hiện hoàn tiền. Cần thông báo rõ chat không xử lý nghiệp vụ này và dùng lỗi thân thiện, không coi response 200 là một câu trả lời AI thành công.

## Phân biệt từ chối đúng phạm vi với câu trả lời chưa hữu ích

- Chuyện ăn uống, thời tiết, kể chuyện cười và số điện thoại riêng không thuộc tài liệu: từ chối là phù hợp giới hạn trợ giảng.
- Chat RAG không có nghiệp vụ thực hiện hoàn tiền/đổi mật khẩu hoặc tự đọc dữ liệu giao dịch: không giả vờ đã làm là đúng. Tuy nhiên nên hướng người dùng tới luồng hỗ trợ thật thay vì chỉ lặp câu mẫu.
- Với bài tập/code cụ thể, cần thêm dữ liệu thì nên xin dữ liệu. Nếu tài liệu chưa có kiến thức cần thiết thì cần nói rõ giới hạn, thay vì coi mọi từ chối là lỗi kiến thức hoặc dùng đoạn gần chủ đề như đáp án.

## Đối chứng bổ sung — giữ riêng, không sửa kết quả 50 lượt đầu
'''
for x in summary['additional_controls']:
    body+=f"\n**{x['id']}** — {x['ms']/1000:.2f} giây\n\nHỏi: {x['question']}\n\nAI: {x.get('answer',x.get('error',''))}\n"
body+='''

Kết quả đối chứng: câu khóa chính hỏi tường minh trả lời đúng, trong khi cách hỏi nối tiếp đời thường trước đó bị từ chối. Quy tắc int()/str() được giải thích, nhưng hỏi lại nguyên văn lỗi print("2" + 3) vẫn bị từ chối. Câu hỏi tường minh về thụt lề cũng gặp gián đoạn LLM và dùng trích xuất dự phòng; phần trích xuất có quy tắc 4 dấu cách nhưng kèm mục tiêu bài học không cần thiết. Điều này cho thấy cả cách hiểu/truy hồi và tính ổn định dịch vụ đều cần được xem xét.

Đối chứng giúp phân biệt thay đổi cách hỏi, thiếu tài liệu và biến động dịch vụ. Đây là số lần thử nhỏ; không quy mọi từ chối cho một nguyên nhân duy nhất. Các lần thử lại không được dùng để xóa phản hồi kém ở lần đầu.

## Dữ liệu và giới hạn

50 câu mới được lưu vào 40 hội thoại test; mỗi câu có một tin hỏi và một tin đáp. Đã lưu bằng chứng rồi xóa lịch sử test. Không sửa ứng dụng, tài liệu, tài khoản hoặc cấu hình AI.

Bốn câu đối chứng được lưu riêng trong 4 hội thoại và cũng đã được dọn; snapshot trước/sau đối chứng khớp nhau. Vì vậy có 54 lượt hỏi mới tổng cộng, còn các bảng thống kê chính chỉ tính 50 lượt đầu.

'''
body+='| Dữ liệu | Trước | Sau |\n|---|---:|---:|\n'
for key,name in [('ai_conversations','Hội thoại'),('ai_messages','Tin nhắn'),('documents','Tài liệu'),('document_chunks','Đoạn tài liệu')]:body+=f"| {name} | {state['before_counts'][key]} | {state['after_counts'][key]} |\n"
body+='''
Đánh giá thủ công theo mức đáp ứng ý định, không phải benchmark chuẩn hóa hoặc kết luận AI luôn đúng/sai. Một số câu được chủ động đặt ngoài dữ liệu mà RAG được phép sử dụng. Đợt này không đo lại lỗi trích dẫn trang/Markdown từ báo cáo trước và không có thay đổi để sửa chúng.

Ưu tiên: cải thiện hỏi làm rõ và xã giao; giữ ngữ cảnh nối tiếp; kiểm tra đoạn trích dự phòng có giải quyết đúng bài toán; bổ sung ví dụ lỗi code trong tài liệu; log/giảm thời gian chờ LLM. Chưa triển khai các thay đổi này trong đợt test.

## Bằng chứng

- [50 câu hỏi/câu trả lời và nhận xét, mở bằng Excel](ai-everyday-questions.csv).
- [Số liệu và đánh giá từng câu](ai-everyday-summary.json).
- [Nhật ký đầy đủ của 50 lượt đầu](ai-everyday-results.json).
- [Đối chứng bổ sung](ai-everyday-controls.json), [trước/sau đối chứng](ai-everyday-controls-state.json).
- [Snapshot trước/sau đợt 50 câu](ai-everyday-state.json).

## Phụ lục — 50 câu trả lời nguyên văn
'''
for i,x in enumerate(questions,1):
    src='; '.join(s['document']+(f" — tr. {s['page']}"if s.get('page')else '')for s in x['sources'])or'Không có'
    body+=f"\n### {i:02}. {x['id']}\n\n**Nick:** `{state['accounts'][x['role']]}` · **Nhóm:** {category_names[x['expected_behavior']]} · **Thời gian:** {x['ms']/1000:.2f} giây\n\n**Hỏi:**\n\n{x['question']}\n\n**AI trả lời:**\n\n{x.get('answer',x.get('error',''))}\n\n**Nguồn:** {src}\n\n**Đánh giá:** {labels[x['assessment']]}. {x['review_note']}\n"
(D/'bao-cao-ai-cau-hoi-thuc-te-2026-10-29.md').write_text(body,encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items()if k not in ['reviewed_questions','additional_controls','accounts']},ensure_ascii=True))
assert summary['history_restored']
