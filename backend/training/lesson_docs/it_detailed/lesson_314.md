## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 2: Kỹ thuật kiểm thử và xử lý lỗi.
- Các bài trong chương: Phân vùng tương đương và giá trị biên; Báo cáo lỗi và kiểm thử hồi quy.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Báo lỗi đủ thông tin và xác nhận bản sửa một cách có căn cứ.

## Kiến thức nền
Báo cáo lỗi nên có tiêu đề ngắn, môi trường, điều kiện trước, bước tái hiện, kết quả thực tế, kết quả mong đợi và bằng chứng liên quan. Không đưa mật khẩu hoặc token vào ảnh chụp và nhật ký chia sẻ.

Severity mô tả mức độ ảnh hưởng của lỗi; priority mô tả thứ tự cần xử lý theo quyết định của nhóm. Hai yếu tố liên quan nhưng không đồng nhất: một lỗi giao diện nhỏ trên trang chiến dịch sắp ra mắt có thể được ưu tiên sớm.

Sau sửa lỗi, confirmation testing kiểm tra lại lỗi cụ thể đã được sửa. Regression testing kiểm tra các hành vi liên quan để tìm tác động phụ ngoài ý muốn. Test tự động có ích cho tình huống lặp lại nhưng vẫn cần dữ liệu và kết quả mong đợi đúng.

## 1. Mẫu báo lỗi có bằng chứng
```text
ID: BUG-LAB-01 (tình huống minh họa)
Tiêu đề: Hai yêu cầu ghi danh cùng khóa tạo hai bản ghi
Môi trường: database test, phiên bản được ghi cụ thể
Điều kiện: U1 chưa ghi danh C1
Bước tái hiện: gửi hai yêu cầu đồng thời với dữ liệu test hợp lệ
Thực tế: mô tả quan sát sau khi chạy, không điền trước
Mong đợi: chỉ một ghi danh theo quy tắc duy nhất
Bằng chứng: ID request, trạng thái, ảnh/query đã che bí mật
```
Một mô tả “bấm thấy sai” thiếu thời điểm, dữ liệu và kết quả nên khó tái hiện. Báo cáo cần đủ chi tiết nhưng không đưa token, mật khẩu hoặc dữ liệu cá nhân không cần thiết.

## 2. Severity và priority
Severity đánh giá ảnh hưởng kỹ thuật/nghiệp vụ; priority là mức ưu tiên xử lý trong bối cảnh phát hành. Lỗi giao diện nhỏ có thể được ưu tiên cao do trang sắp ra mắt; không đồng nhất hai trường. Dùng thang và quy ước của nhóm thay vì tự gắn mọi lỗi là nghiêm trọng nhất.

## 3. Kiểm tra sau sửa
Confirmation testing thực hiện lại điều kiện gây lỗi để xác nhận bản sửa. Regression testing mở rộng sang các hành vi có nguy cơ bị ảnh hưởng: đăng ký lần đầu, trùng, khóa có phí, quyền mở bài và danh sách khóa. Chọn phạm vi theo thay đổi, không mặc định chạy mọi test vô hạn.

## 4. Bài tập có lời giải định hướng
Bản sửa thêm unique constraint nhưng UI báo lỗi thô khi request thứ hai tới. Cần báo vấn đề xử lý phản hồi riêng, không kết luận sửa database thất bại nếu tính duy nhất đã đúng. Nộp một bug report, một ca xác nhận và ít nhất bốn ca hồi quy có lý do lựa chọn; không dùng dữ liệu thật để cố tình gây lỗi.

## Bài tập vận dụng bổ sung
báo lỗi “học viên hết lượt vẫn mở được quiz”. Viết bước tái hiện, kiểm tra trạng thái dữ liệu và đề xuất các test hồi quy cho trường hợp còn lượt và tiếp tục lượt đang làm.

## Câu hỏi tự kiểm tra
1. Báo cáo lỗi cần thông tin nào để tái hiện?
2. Severity thường thể hiện điều gì?
3. Kiểm tra lại chính lỗi vừa sửa gọi là gì?
4. Kiểm thử hồi quy nhằm mục đích gì?
5. Thông tin nào nên che khi chia sẻ bằng chứng lỗi?

## Gợi ý đáp án và điểm cần nhớ
- Điều kiện trước và các bước thực hiện. Các bước và điều kiện trước giúp người khác tái hiện lỗi.
- Mức độ ảnh hưởng của lỗi. Severity đánh giá ảnh hưởng; priority đánh giá mức ưu tiên xử lý.
- Confirmation testing. Confirmation testing xác nhận lỗi cụ thể được khắc phục.
- Phát hiện tác động phụ tới hành vi đã hoạt động. Thay đổi có thể ảnh hưởng chức năng khác nên cần kiểm tra hồi quy phù hợp.
- Mật khẩu và token truy cập. Thông tin xác thực không được đưa vào bằng chứng chia sẻ.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
