# Đánh giá độ chính xác AI Tutor — 30/10/2026

**Kết quả chính: 45/50 câu kiến thức được trả lời đúng và đủ = 90%.**
Đây là tỷ lệ đáp ứng đầu cuối trên bộ câu hỏi này; không phải cam kết đúng cho mọi câu hỏi.

## Cách đo

- Gọi API thật trên localhost bằng 5 tài khoản mẫu: Em, Phương, An, Bình và Admin; model `gemini / gemini-3.1-flash-lite`.
- 50 câu kiến thức, chia đều 5 câu cho mỗi khóa trong 10 khóa: 40 câu cố định từ lần đo trước và 10 câu mới được đóng băng rubric trước khi gửi.
- Thêm 10 ca ngoài phạm vi và 8 ca thiếu thông tin, báo riêng, không cộng các ca dễ từ chối/hỏi lại vào tỷ lệ kiến thức.
- Chỉ lấy câu trả lời đầu tiên; không sửa prompt, mã AI, ngưỡng truy hồi hoặc tài liệu trong lúc đo. Mã nguồn được kiểm tra SHA-256 trước/sau cả ba phase.
- Điểm 2: đúng và đủ yêu cầu chính; 1: thiếu ý trọng yếu; 0: sai/lạc đề/không trả lời/hỏi lại thừa/lỗi dịch vụ. Không buộc câu trả lời phải nói thêm các chi tiết không được câu hỏi yêu cầu.
- Chấm nội dung và hỗ trợ nguồn theo từng câu bởi trợ lý AI, có rà soát độc lập; chưa có giảng viên kiểm định độc lập.

## Kết quả

| Chỉ số | Kết quả |
|---|---:|
| Đúng và đủ trên toàn bộ câu kiến thức | **45/50 = 90%** |
| Đúng và đủ trên 40 câu cố định | 36/40 |
| Đúng và đủ trên 10 câu mới | 9/10 |
| Hỏi lại thừa khi câu kiến thức đã rõ | 3/50 |
| Không trả lời câu kiến thức (từ chối) | 2/50 |
| Có khẳng định kiến thức sai trọng yếu được phát hiện | 0 trong 45 câu có trả lời nội dung |
| Câu đúng và ý chính có chứng cứ trong trang được trích | 44/50 = 88% |
| Từ chối phù hợp khi ngoài phạm vi | 10/10 |
| Hỏi lại đúng khi thật sự thiếu thông tin | 8/8 |

Không trình bày tỷ lệ đúng trong riêng các câu có nội dung trả lời làm kết quả chính: loại bỏ 5 câu không được trả lời sẽ làm số đẹp hơn và che mất thất bại đầu cuối.

## Những câu chưa đạt

| ID | Câu hỏi | Kết quả |
|---|---|---|
| student_em-accuracy-01 | Muốn phép tính print("4" + 2) cho ra số 6 thì sửa thế nào? Vì sao code cũ lỗi? | Từ chối câu hỏi đã rõ về cộng str/int; không giải thích lỗi hoặc đưa phép chuyển kiểu để ra 6. Từ chối không phải khẳng định bịa. |
| student_phuong-accuracy-07 | Máy một lõi có làm đồng thời nhiều việc được không, điều đó có phải song song thật trên lõi đó không? | Hỏi lại tên chủ đề dù câu đã nêu rõ đồng thời và song song trên máy một lõi. Không trả lời kiến thức được yêu cầu; đây là hỏi lại nhầm, không phải khẳng định bịa. |
| teacher_an-accuracy-03 | HashMap.put cùng một khóa hai lần có tự báo lỗi trùng không? Nếu cần từ chối trùng nên làm gì? | Câu hỏi đã nêu rõ HashMap.put, khóa trùng và mục tiêu từ chối trùng, nhưng AI yêu cầu code/thông báo lỗi thay vì trả lời hành vi put và cách kiểm tra/putIfAbsent. Hỏi lại thừa, không phải bịa một sự thật kỹ thuật. |
| teacher_binh-accuracy-02 | Nút trong form chỉ mở hộp trợ giúp, không gửi form. Nên đặt type gì? | Từ chối câu kiến thức cần đáp type=button để không submit form. Không đưa khẳng định sai, nhưng không đáp ứng yêu cầu đầu cuối. |
| new-10 | Sau khi sửa lỗi ghi danh trùng, chạy lại đúng ca từng gây lỗi đã thay thế được kiểm thử hồi quy chưa? Phân biệt confirmation testing với regression testing. | Câu hỏi đã rõ, yêu cầu phân biệt confirmation testing và regression testing sau sửa lỗi; AI lại yêu cầu code, thông báo lỗi, ngôn ngữ/công cụ như một yêu cầu chẩn đoán bug chưa đủ dữ liệu. Không trả lời nội dung được hỏi. Đây là hỏi lại nhầm, không phải khẳng định bịa. |

Ba trường hợp hỏi lại nhầm cho thấy bước làm rõ hiện còn quá nhạy với từ như ‘nó’, ‘báo lỗi’, ‘sửa lỗi’, dù câu hỏi đã đủ chủ đề. Các ca này được chấm 0 trong lần đo và giữ nguyên mã AI, không sửa rồi đo lại để thay kết quả.

Ca Python có quy tắc chuyển kiểu/cộng chuỗi-số trong các chunk 1332, 2014, 2016 của khóa, nhưng lượt trả lời vẫn từ chối. Ca nút không submit chưa thấy quy tắc `type="button"` trong các chunk HTML đã kiểm tra: đây còn là giới hạn bao phủ tài liệu. Từ chối ở ca này phù hợp nguyên tắc không đoán khi thiếu nguồn, nhưng vẫn không đáp ứng nhu cầu kiến thức nên giữ điểm 0 đầu cuối theo rubric đã định trước.

## Nguồn trích dẫn và việc ‘bịa’

Có 130 lượt gắn nguồn; metadata tài liệu/khóa/trang đều hợp lệ. Tuy nhiên, metadata đúng không chứng minh câu trả lời được tài liệu đó hỗ trợ.
Câu chia nguyên/chia thực Java cho đúng 7 và 7.5, nhưng các trang gắn kèm chỉ nói Map, kiểu dữ liệu/ép kiểu, String; không chứng minh trực tiếp quy tắc chia. Câu này vẫn đúng về kiến thức nhưng không đạt tiêu chí ý chính được trang trích dẫn hỗ trợ.
Một số câu có nguồn phụ ít liên quan, ví dụ câu `None` kèm trang if/else, câu `==`/`===` kèm trang hàm/Promise; vẫn có nguồn khác trong cùng câu chứng minh ý chính. Một số ví dụ phụ trong câu mạng máy tính chưa được trang được chọn chứng minh đầy đủ. Không tuyên bố mọi ý/mọi nguồn gắn kèm đều chính xác.
Chưa phát hiện khẳng định kiến thức sai trọng yếu trong các câu có nội dung trả lời của mẫu này. Điều đó không đồng nghĩa tỷ lệ bịa luôn bằng 0%; đặc biệt, vấn đề nguồn chưa hỗ trợ đủ vẫn tồn tại.

## Theo khóa học

| Khóa | Đúng / tổng | Tỷ lệ |
|---|---:|---:|
| Python cơ bản | 4/5 | 80% |
| JavaScript | 5/5 | 100% |
| Java | 4/5 | 80% |
| HTML & CSS | 4/5 | 80% |
| ReactJS | 5/5 | 100% |
| MySQL | 5/5 | 100% |
| Nguyên lí hệ điều hành | 4/5 | 80% |
| Mạng máy tính | 5/5 | 100% |
| Cấu trúc dữ liệu và giải thuật | 5/5 | 100% |
| Kiểm thử phần mềm | 4/5 | 80% |

Mỗi khóa chỉ có 5 câu; không dùng bảng này để kết luận một khóa luôn chính xác ở mức đó.

## Thời gian và dữ liệu kiểm thử

68 lượt: trung vị 2.08s, trung bình 4.67s, P95 33.56s, chậm nhất 60.98s. Lỗi transport/LLM hiển thị: 0; câu dự phòng: 0.
Chỉ tạo hội thoại audit rỗng với mã duy nhất và xóa đúng các id đó sau từng lượt. Trước/sau vẫn là 4 hội thoại, 18 tin nhắn, 176 tài liệu, 2063 chunk; giữ nguyên lịch sử, tài liệu và tài khoản có sẵn.

## Giới hạn

Bộ câu hỏi được chọn có chủ đích và khá nhỏ; 40 câu đã được sử dụng trước đây, 10 câu mới vẫn dựa trên tài liệu hiện có. Đây là kiểm tra hồi quy và một mẫu mở rộng, không phải đánh giá ngẫu nhiên hay bộ kiểm định độc lập. Kết quả có thể đổi theo cách hỏi, tài liệu, model và tình trạng dịch vụ. Nên có giảng viên kiểm tra thêm trước khi dùng tỷ lệ này làm cam kết chất lượng.

## Tệp đối chiếu

- [Bảng điểm 68 câu, UTF-8 cho Excel](ai-accuracy-current-2026-10-30-scores.csv)
- [Tóm tắt số liệu](ai-accuracy-current-2026-10-30-summary.json)
- [Câu trả lời và đánh giá từng câu, kèm trang nguồn](ai-accuracy-current-2026-10-30-reviewed.json)
- [Runner giữ câu trả lời đầu tiên](ai-accuracy-current-run.py)
- [Đề 10 câu mới, rubric và chứng cứ đã đóng băng](ai-accuracy-current-2026-10-30-new-plan.json)
