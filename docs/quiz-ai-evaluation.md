# Kiểm tra giới hạn và chất lượng sinh quiz — 12/10/2026

## Giới hạn hiện tại

- Một mức: từ 1 đến 20 câu, đầu vào ngoài khoảng bị giới hạn lại trong bộ sinh.
- Phân bổ nhiều mức: mỗi mức 0–20 câu, tổng tối đa 30 câu mỗi request.
- Giao diện đề cuối khóa: tối đa 60 câu, gọi lần lượt từng chương. Giao diện chưa kiểm tra tổng số câu mỗi chương <=30, nên có thể cho phép cấu hình mà backend từ chối.
- Ngân sách output mỗi lô sinh: min(8192, 300 + 300 × số câu). Với giới hạn 20 câu, tối đa thực tế 6300 token.
- Lượt giải lại: min(8192, 300 + 450 × số câu), tối đa 8192 token.
- Mỗi mức thường gọi một lượt sinh và một lượt thẩm định. Nếu chưa nhận được câu hợp lệ, thử sinh lần hai. Ba mức thường cần 6 lượt gọi LLM; lỗi tạm thời HTTP có thể làm phát sinh request retry.
- Gemini: timeout cấu hình 60 giây cho mỗi request HTTP, không phải giới hạn tổng thời gian sinh toàn đề. Retry HTTP tối đa 3 lần cho các lỗi được hỗ trợ; không retry ReadTimeout tại lớp HTTP.
- Chưa có hạn mức số lần sinh theo giảng viên/ngày tại ứng dụng. Hạn mức phía Gemini phụ thuộc project/model/tier, xem [tài liệu Google](https://ai.google.dev/gemini-api/docs/rate-limits).
- Offline chỉ sinh câu dễ; số lượng thực trả có thể ít hơn yêu cầu vì thiếu ngữ liệu hoặc phương án hợp lệ.

## Phép thử thực tế

Gọi pipeline đang dùng với Gemini `gemini-3.1-flash-lite`, bài 5 “Vòng lặp for, while”, yêu cầu 2 dễ + 2 trung bình + 2 khó. Chỉ sinh bản nháp, không lưu quiz. Trước đó gọi trong sandbox lỗi ConnectError; phép thử có kết quả được chạy lại ngoài sandbox.

- Trả đủ 6/6 câu, đúng cấu trúc và nhãn phân bổ.
- Thời gian toàn bộ: 210,31 giây.
- Log ghi nhận hai ReadTimeout. Chỉ 2/6 câu có kết quả AI giải lại xác nhận; bốn câu không có xác nhận, không nên coi là đã kiểm chứng.
- Cả 6 câu được hệ thống đánh dấu grounded. Điều này chỉ có nghĩa căn cứ vượt ngưỡng từ trùng, không bảo đảm đúng đáp án hoặc đúng giải thích.

## Chấm nội dung độc lập

| Câu | Mức yêu cầu | Nhận xét |
|---|---|---|
| 1 | Dễ | Đáp án while phù hợp nội dung; lựa chọn range/list là tên không phải loại vòng lặp, nên nhiễu khá dễ loại. |
| 2 | Dễ | Đáp án continue đúng; hỏi nhận biết trực tiếp. |
| 3 | Trung bình | Đáp án đúng, nhưng gần trùng ý câu 1; chỉ chọn lại mô tả while, chưa thể hiện vận dụng rõ. |
| 4 | Trung bình | Đáp án đúng, gần trùng ý câu 2; lượt thẩm định cũng đề xuất mức easy. |
| 5 | Khó | Đáp án count=4 đúng khi chạy Python, nhưng giải thích sai bước: i=6 phải continue trước, i=7 mới break. Cần sửa giải thích. |
| 6 | Khó | Không dùng được nguyên trạng: các lựa chọn viết compound statement sau dấu chấm phẩy nên không biên dịch được thành Python. Giải thích A “thiếu tăng n dẫn đến vô hạn” sai: khi n=1, tong tăng mỗi vòng và vượt 50 sau 51 vòng. Cần viết lại câu, mã nhiều dòng và kiểm định đáp án. |

Theo tiêu chí nội dung câu và lời giải: 4/6 câu không phát hiện lỗi kiến thức trực tiếp, 1/6 cần sửa giải thích, 1/6 cần viết lại. Nếu xét thêm độ khó, trùng ý và chất lượng nhiễu, bốn câu đầu vẫn cần biên tập; tỷ lệ 4/6 không phải tỷ lệ có thể đưa ngay vào đề thi.

Không suy rộng kết quả từ một bài và một lần sinh thành “độ chính xác 66,7%” của toàn model. Kết quả này là bằng chứng cụ thể về các lỗi có thể lọt qua pipeline, không phải benchmark đại diện 7 khóa.

## Các giới hạn của kiểm định hiện tại

- Ngưỡng 85% trong `_grounded` là tỷ lệ từ của căn cứ có trong tập từ ngữ liệu, không phải độ chính xác model. Không kiểm tra thứ tự từ hoặc quan hệ lập luận.
- Cùng model sinh và giải lại có thể cùng mắc lỗi. Khi timeout, lượt thẩm định bị bỏ qua nhưng câu vẫn được trả.
- Loại trùng dựa trên văn bản chuẩn hóa, nên câu diễn đạt lại cùng ý vẫn lọt.
- Chưa biên dịch/chạy mã minh họa; chưa kiểm định một đáp án đúng duy nhất; nhãn độ khó được gán theo yêu cầu, cảnh báo chưa chặn duyệt.
- Script `training/evaluate.py` đo chủ yếu định dạng, không đo đúng kiến thức. Dataset test hiện có 36/36 câu hỏi khác nhau cũng xuất hiện trong train, nên không chứng minh khả năng tổng quát hóa của fine-tuning.

## Bằng chứng

- [Kết quả gốc](../backend/training/quiz_eval/pilot_20261012.json)
- [Kết quả kiểm tra độc lập](../backend/training/quiz_eval/pilot_20261012_review.json)

Ưu tiên tiếp theo: kiểm định mã Python bằng môi trường giới hạn, phát hiện trùng ý, phân biệt đã/ chưa thẩm định trên giao diện và chặn hoặc yêu cầu xử lý câu có lỗi trước khi duyệt. Muốn đo độ chính xác đại diện cần bộ tài liệu giữ riêng và giảng viên chấm nhiều lần sinh trên đủ khóa/mức tư duy.

## Đánh giá lại — 13/10/2026

Chưa có lần sinh mới: cơ chế duyệt tự động chặn gọi Gemini vì cần xác nhận việc gửi nội dung bài học sang dịch vụ ngoài. Phần dưới là thẩm định lại bộ câu đã lưu, không phải đo độ ổn định qua hai lần sinh.

- Câu 1 và 2 phù hợp để luyện nhận biết; câu 1 có nhiễu yếu, nên cải thiện nếu dùng trong đề kiểm tra.
- Câu 3 chưa đủ bằng chứng cho vận dụng: không có tình huống cụ thể, gần lặp lại định nghĩa và câu 1. Xếp dễ hoặc viết lại thành tình huống áp dụng. Đây là nhận xét giáo viên, khác với lượt model tự đánh giá medium.
- Câu 4 phải chuyển sang dễ hoặc viết lại; cùng ý câu 2 và model cũng cảnh báo easy.
- Câu 5 kết hợp range, continue, break và biến đếm; có yêu cầu theo dõi nhiều điều kiện. Chấp nhận nhãn khó dự kiến theo rubric hiện tại, nhưng độ khó thực tế phụ thuộc mức luyện trước đó. Python xác nhận i=6 continue, i=7 break, count=4; phải sửa lời giải.
- Câu 6 cần viết lại toàn bộ mã và câu dẫn. Nếu hiểu mã A thành nhiều dòng, nó dừng sau 51 vòng với tổng 51; mã B tương ứng dừng với tổng 55, n=11. Do đó giải thích A lặp vô hạn là sai, ngay cả khi bỏ qua lỗi cú pháp gốc. Phải ghi rõ yêu cầu cộng dãy 1+2+3+... thay vì diễn đạt tổng không rõ ràng.

Kết luận chính xác hơn: đủ định dạng không đồng nghĩa dùng được ngay. Có 5 câu xác định được đáp án phù hợp (câu 1–5), nhưng câu 5 có giải thích sai; câu 6 không hợp lệ nguyên trạng. Không nên giữ nguyên bộ đề 2 dễ/2 trung bình/2 khó này: hai câu trung bình không đạt mục đích phân hóa rõ và lặp nội dung với nhóm dễ. Chưa có cơ sở công bố độ chính xác chung hoặc kết luận model ổn định.
