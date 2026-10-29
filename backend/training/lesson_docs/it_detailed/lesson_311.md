## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 1: Nền tảng kiểm thử.
- Các bài trong chương: Mục tiêu và các mức kiểm thử; Thiết kế test case.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Giải thích giá trị kiểm thử và phân biệt các mức kiểm thử phổ biến.

## Kiến thức nền
Kiểm thử cung cấp thông tin về chất lượng và rủi ro của phần mềm. Nó có thể phát hiện lỗi nhưng một tập kiểm thử hữu hạn không chứng minh chương trình không còn lỗi. Kiểm thử nên bám yêu cầu, ngữ cảnh sử dụng và mức độ ảnh hưởng của sai sót.

Unit test tập trung vào đơn vị nhỏ như hàm hoặc lớp; integration test kiểm tra tương tác giữa các thành phần; system test kiểm tra hệ thống hoàn chỉnh; acceptance test đánh giá khả năng đáp ứng nhu cầu chấp nhận đã thống nhất. Ranh giới cụ thể phụ thuộc thiết kế hệ thống.

Kiểm thử tĩnh xem xét sản phẩm công việc mà không chạy phần mềm, như review yêu cầu hoặc mã nguồn. Kiểm thử động thực thi phần mềm và quan sát kết quả. Hai cách bổ sung cho nhau.

## 1. Chất lượng, lỗi và bằng chứng
Một sai sót của con người có thể tạo khuyết tật trong tài liệu hoặc mã; khuyết tật khi được kích hoạt có thể gây thất bại quan sát được. Không phải mọi khuyết tật đều biểu hiện trong mọi lần chạy. Kiểm thử cần mô tả điều kiện kích hoạt và kết quả thay vì chỉ ghi “có lỗi”.
Verification thường xem sản phẩm công việc có đáp ứng yêu cầu đã chỉ định; validation xem giải pháp có phù hợp nhu cầu sử dụng trong ngữ cảnh. Hai góc nhìn bổ sung nhau. Số lỗi tìm được không trực tiếp đo năng lực tester hoặc chất lượng toàn hệ thống.

## 2. Phân biệt mức và loại
```text
Mức kiểm thử        Ví dụ LMS
Unit                Hàm tính phần trăm và xử lý tổng câu bằng 0
Integration         Service ghi danh phối hợp database và kiểm tra quyền
System              Luồng đăng ký -> mở bài -> nộp quiz trên hệ thống
Acceptance          Đối chiếu tiêu chí học viên bắt đầu học sau ghi danh
```
Functional/non-functional là cách phân loại mục tiêu, không phải thay thế các mức trên. Một integration test vẫn có thể đo thuộc tính phi chức năng.

## 3. Thiết kế phép kiểm tra có ý nghĩa
Với tỷ lệ đúng, test cần đầu vào và kỳ vọng: 2/5 thành 40%; tổng 0 phải theo hợp đồng. Không tự chọn 0% nếu yêu cầu muốn “chưa có dữ liệu”. Ví dụ này cho thấy test phải bám ý nghĩa sản phẩm, không chỉ biểu thức toán.

## 4. Bài tập và lời giải
Viết bốn test ở bốn mức cho nộp quiz. Unit kiểm tra chấm một câu; integration kiểm tra lưu kết quả và câu trả lời cùng giao dịch; system kiểm tra hiển thị sau nộp; acceptance kiểm tra học viên nhận được hướng ôn theo tiêu chí. Nêu cách dùng dữ liệu lab và không tự tạo điểm cho học viên thật.

## Bài tập vận dụng bổ sung
với website học trực tuyến, đề xuất một unit test cho hàm tính điểm, một integration test giữa ghi danh và quyền học, một acceptance test cho quy trình học viên nộp quiz.

## Câu hỏi tự kiểm tra
1. Mục tiêu phù hợp của kiểm thử là gì?
2. Kiểm tra riêng một hàm tính điểm thường thuộc mức nào?
3. Kiểm tra tương tác giữa API và cơ sở dữ liệu thường là gì?
4. Acceptance test tập trung vào điều gì?
5. Review mã nguồn mà không chạy chương trình là gì?

## Gợi ý đáp án và điểm cần nhớ
- Cung cấp thông tin chất lượng và phát hiện vấn đề. Kiểm thử giảm bất định nhưng không chứng minh tuyệt đối phần mềm không có lỗi.
- Unit test. Unit test tập trung vào một đơn vị nhỏ.
- Integration test. Integration test kiểm tra sự phối hợp giữa các thành phần.
- Tiêu chí chấp nhận và nhu cầu đã thống nhất. Acceptance test đánh giá khả năng đáp ứng nhu cầu sử dụng theo tiêu chí chấp nhận.
- Kiểm thử tĩnh. Hoạt động tĩnh không yêu cầu thực thi phần mềm.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
