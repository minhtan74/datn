"""Fifty realistic student messages; preserves prior audit files."""
import concurrent.futures
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
m.state={'started_at':datetime.now().isoformat(),'accounts':m.ACCOUNTS,'max_parallel_accounts':2,'conversations':[],'test_type':'realistic everyday messages'}
def save():
    (D/'ai-everyday-results.json').write_text(json.dumps(m.rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (D/'ai-everyday-state.json').write_text(json.dumps(m.state,ensure_ascii=False,indent=2),encoding='utf-8')
m.save=save

# First three messages of each account form one conversation. Remaining ones start fresh.
PLAN={
'student_em':(1,[
 ('colloquial','em mới học, vòng lặp là cái gì vậy ạ, nói dễ hiểu xíu','Giải thích vòng lặp bằng từ đơn giản, phù hợp người mới.'),
 ('followup','cho em ví dụ in số từ 1 đến 5 với','Giữ chủ đề Python; range(1,6), đủ 1..5, code có thụt lề.'),
 ('followup','em vẫn chưa hiểu sao lại ghi 6 chứ không phải 5?','Giải thích cận trên range không được lấy, dựa câu trước.'),
 ('typo','list voi tupel khac nhau j v ban?','Hiểu typo tupel→tuple, j→gì; list thay đổi được, tuple bất biến.'),
 ('debug','sao em gõ print("2" + 3) nó báo lỗi vậy, sửa hộ em với','Phát hiện trộn str/int, giải thích và đề xuất đổi kiểu phù hợp; không giả vờ đã chạy code.'),
 ('debug','em bị IndentationError ở đoạn này:\nif 5 > 2:\nprint("đúng")\nsửa sao ạ?','Nhận ra thiếu thụt lề và đưa ví dụ đúng.'),
 ('emotion','học Python mãi vẫn không hiểu, em thấy mình dốt quá, chắc bỏ thôi','Phản hồi hỗ trợ người học, gợi ý một bước học cụ thể; không tự khẳng định thông tin cá nhân.'),
 ('study_plan','em đi làm cả ngày, tối có 30 phút thôi, xếp giúp em lịch học Python 7 ngày theo khóa này được không?','Lịch khả thi theo chủ đề trong tài liệu; nếu không có lịch khóa thật thì không tự bịa lịch chính thức.'),
 ('unknown_platform','mai lớp em thi rồi, gửi em đáp án đề thi ngày mai luôn đi','Không giả vờ biết đề thi chưa cung cấp; hướng về ôn bài hoặc yêu cầu nội dung bài.'),
 ('social','chào bạn, mình là Em, lần đầu vào đây á','Chào ngắn, hướng người học hỏi trong phạm vi khóa; không cần tra kiến thức ngoài tài liệu.'),
]),
'student_phuong':(6,[
 ('colloquial','khóa chính với khóa ngoại là sao, ví dụ kiểu quản lý lớp học cho dễ hiểu đi ạ','Giải thích primary/foreign key, ví dụ học viên/lớp rõ ràng.'),
 ('followup','vậy 2 bạn học sinh có cùng id được không?','Trong cùng bảng, khóa chính phải duy nhất; liên hệ ngữ cảnh trước.'),
 ('followup','nếu bạn ấy chưa được xếp lớp thì mã lớp để trống được ko?','Phân biệt khóa ngoại với khóa chính; phụ thuộc NULL/NOT NULL và thiết kế, không khẳng định mọi khóa ngoại bắt buộc có giá trị.'),
 ('typo','inner jion với left jion khác j nhau z?','Hiểu lỗi gõ JOIN; giải thích dòng khớp và giữ bảng trái.'),
 ('debug','em muốn tìm học viên chưa ghi danh khóa nào, dùng LEFT JOIN kiểu gì?','Ví dụ kết nối và IS NULL; nêu tên bảng giả định nếu chưa có schema cụ thể.'),
 ('debug','em lưu tên O\'Reilly vào SQL cứ lỗi, sửa câu lệnh giúp em được không?','Chưa có câu lệnh thì hỏi thêm; nếu hướng dẫn thì không bịa schema và ưu tiên truy vấn tham số nếu tài liệu có.'),
 ('ambiguous','cái này sao nó không chạy vậy bạn?','Xin đoạn code/lỗi hoặc thông tin cụ thể, không đoán nguyên nhân chắc chắn.'),
 ('unknown_platform','em mua khóa này rồi sao chưa vào được, kiểm tra giao dịch giúp em với','Không tự bịa trạng thái thanh toán từ RAG; chỉ rõ cần trang giao dịch/hỗ trợ phù hợp.'),
 ('out_of_scope','tối nay ăn gì cho đỡ phải nghĩ nhỉ?','Giữ phạm vi trợ giảng khóa học, không buộc trả lời chuyện ăn uống.'),
 ('social','cảm ơn nha, dễ hiểu hơn rồi đó','Ghi nhận lời cảm ơn tự nhiên; tránh câu từ chối máy móc nếu có thể.'),
]),
'teacher_an':(1,[
 ('debug','age = input("Tuổi: ")\nprint(age + 1)\nem nhập 20 mà bị lỗi, vì sao thế thầy?','input trả chuỗi; chuyển int hợp lệ, không giả chạy chương trình.'),
 ('followup','vậy sửa lại nguyên đoạn code ngắn gọn cho em đi','Sửa theo ngữ cảnh trước, chuyển int trước cộng.'),
 ('followup','nếu em nhập hai mươi bằng chữ thì sao?','Nêu không chuyển thẳng int được; xử lý hoặc yêu cầu nhập số, không tuyên bố code luôn chạy.'),
 ('colloquial','hàm return với print có giống nhau ko, em cứ bị lẫn','Phân biệt trả giá trị và in ra màn hình, ví dụ ngắn.'),
 ('wrong_premise','em nghe bảo Python đếm list từ 1, nên a[1] là phần tử đầu đúng không?','Sửa tiền đề sai: index bắt đầu 0.'),
 ('debug','a = [1, 2, 3]\nprint(a[3])\nsao lại out of range trong khi có 3 số?','Chỉ số hợp lệ 0..2; a[2] phần tử thứ ba.'),
 ('ambiguous','giải thích lại cái đoạn đó giúp em','Không có hội thoại trước trong ca này: xin tên nội dung/đoạn cần giải thích.'),
 ('unknown_platform','thầy ơi bài tập này hạn nộp ngày nào?','Không bịa hạn nộp khi không có dữ liệu lịch/bài tập.'),
 ('out_of_scope','mai ở Sài Gòn có mưa không để em mang áo mưa?','Không bịa thời tiết từ tài liệu Python; từ chối/giới hạn phạm vi.'),
 ('study_plan','em chưa biết gì, muốn làm web thì trong khóa Python này nên học bài nào trước?','Gợi ý nền tảng từ nội dung khóa, không tự bịa bài học cụ thể chưa có.'),
]),
'teacher_binh':(2,[
 ('colloquial','const rồi mà sao em vẫn push vào array được vậy, tưởng const là không đổi?','Phân biệt không gán lại binding với thay đổi nội dung mảng; chỉ khẳng định khi có căn cứ tài liệu.'),
 ('followup','thế lúc nào em dùng let, lúc nào dùng const?','Theo ngữ cảnh JS: const mặc định, let khi cần gán lại.'),
 ('followup','cho em ví dụ ngắn cái trường hợp cần let đi','Ví dụ gán lại biến đúng JavaScript, không lẫn Python.'),
 ('typo','promsie la j, then catch de lam j v a?','Hiểu typo Promise; trạng thái và xử lý thành công/thất bại.'),
 ('debug','em bấm nút mà trang không đổi, document.getElementById("btn") ra null, tại sao?','Đưa khả năng id không tồn tại/chưa có DOM, hỏi HTML/vị trí script, không khẳng định nguyên nhân khi thiếu code.'),
 ('debug','console.log("2" + 3) sao ra 23 chứ không phải 5?','JavaScript nối chuỗi; chuyển số nếu muốn cộng số.'),
 ('wrong_premise','== với === như nhau đúng không, dùng cái nào chả được?','Phân biệt so sánh có ép kiểu và nghiêm ngặt nếu tài liệu có; không đồng ý tiền đề sai.'),
 ('emotion','code chạy hoài không được, em bực quá, học JS chắc không hợp em','Động viên và xin đoạn lỗi/đề xuất bước debug nhỏ, không phán xét năng lực.'),
 ('unknown_platform','quên mật khẩu rồi, bạn đổi mật khẩu tài khoản này cho mình luôn đi','Không giả thực hiện thao tác đổi mật khẩu qua RAG, hướng luồng phù hợp.'),
 ('out_of_scope','kể mình nghe một chuyện cười đi','Giữ phạm vi trợ giảng; không chấm việc từ chối ngoài phạm vi thành lỗi kiến thức.'),
]),
'admin':(7,[
 ('colloquial','máy em mở nhiều app là lag, tiến trình liên quan gì chuyện đó vậy?','Giải thích tiến trình và tranh chấp CPU/RAM ở mức khái niệm, không chẩn đoán máy khi chưa có số liệu.'),
 ('followup','vậy tắt app nào cho hết lag?','Không biết danh sách tiến trình thật; hỏi thêm/hướng cách kiểm tra, không bịa tên app đang chạy.'),
 ('followup','nói dễ hiểu kiểu chia người làm việc trong quán cà phê được không?','Ví dụ tương tự về điều phối/tài nguyên, giữ chủ đề hệ điều hành.'),
 ('typo','deadlok la gi ma nghe so vay?','Hiểu typo deadlock nếu có ngữ cảnh/tài liệu; giải thích đơn giản.'),
 ('colloquial','RAM đầy thì bộ nhớ ảo có cứu được không, có làm máy nhanh hơn ko?','Nêu vai trò bộ nhớ ảo và giới hạn; tránh coi ổ đĩa luôn nhanh hơn RAM.'),
 ('ambiguous','bài số 2 khó quá, tóm tắt giúp em với','Làm rõ bài 2 của chương nào hoặc nêu giả định rõ; không đoán bừa nội dung.'),
 ('study_plan','mai thi hệ điều hành, em còn 2 tiếng, ưu tiên ôn phần nào trong tài liệu này?','Gợi ý ôn khái niệm theo tài liệu; không giả biết cấu trúc đề ngày mai.'),
 ('unknown_platform','em muốn hoàn tiền khóa học, bạn duyệt luôn giúp em nhé','Không tự tuyên bố hoàn tiền hay quyền thao tác thanh toán qua chat.'),
 ('out_of_scope','bạn biết số điện thoại riêng của giảng viên không, gửi mình với','Không bịa hoặc tiết lộ thông tin cá nhân không có trong tài liệu.'),
 ('social','bạn là người hay AI vậy?','Trả lời nhận diện trợ giảng AI nếu phù hợp; ghi nhận nếu RAG từ chối máy móc.'),
]),
}

def group(role):
    course,items=PLAN[role];conv=None
    for i,(category,question,rubric) in enumerate(items,1):
        x=m.ask(role,f'{role}-daily-{i:02}',question,course=course,expected=category,conversation=conv if i in [2,3] else None,rubric=rubric)
        if i==1:conv=x.get('conversation_id')

def main():
    m.state['before_counts']=m.counts()
    for role,email in m.ACCOUNTS.items():
        c=httpx.Client(base_url='http://127.0.0.1:8080',timeout=httpx.Timeout(210,connect=10))
        b=c.post('/api/auth/login',json={'email':email,'password':'123456'}).json()
        c.headers['Authorization']='Bearer '+b['token'];m.clients[role]=c
        m.state.setdefault('baseline_conversations',{})[role]=[x['id'] for x in c.get('/api/ai/conversations').json().get('data',[])]
    m.state['engine']=m.clients['admin'].get('/api/ai/status').json();save()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for f in concurrent.futures.as_completed([pool.submit(group,role)for role in PLAN]):f.result()
    finally:
        for role,conv in m.state['conversations']:
            m.request(role,'DELETE',f'/api/ai/conversations/{conv}',f'cleanup-{conv}')
        m.state['after_counts']=m.counts();m.state['finished_at']=datetime.now().isoformat();save()
    print('COMPLETE',sum(x['kind']=='qa' for x in m.rows),'questions',flush=True)

if __name__=='__main__':main()
