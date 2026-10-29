## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 3: Kiểm thử trong vòng đời phát triển.
- Các bài trong chương: SDLC, Agile và chiến lược kiểm thử; Review yêu cầu và truy vết kiểm thử.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Chọn hoạt động kiểm thử phù hợp giai đoạn phát triển và rủi ro sản phẩm.

## Kiến thức nền
SDLC mô tả hoạt động phát triển từ hiểu nhu cầu tới vận hành. Kiểm thử nên tham gia sớm qua review yêu cầu và tiêu chí chấp nhận, không chờ mã nguồn hoàn thành mới bắt đầu. Phát hiện yêu cầu mơ hồ sớm có thể tránh xây sai chức năng.

Trong phát triển lặp, kiểm thử được thực hiện xuyên suốt từng vòng. Definition of Done là thỏa thuận về điều kiện hoàn tất, khác tiêu chí chấp nhận cụ thể cho từng câu chuyện. Chất lượng là trách nhiệm chung; có tester không có nghĩa lập trình viên không cần kiểm tra.

Chiến lược chọn phạm vi, mức kiểm thử và mức tự động hóa theo rủi ro. Luồng thanh toán hoặc phân quyền có tác động lớn nên cần được ưu tiên hợp lý. Không thể kiểm thử mọi kết hợp vô hạn; cần ghi giả định, phần đã kiểm tra và rủi ro còn lại. Mô hình phát triển ảnh hưởng cách tổ chức nhưng không xóa nhu cầu có kết quả mong đợi.

## 1. Từ yêu cầu tới vận hành
Các hoạt động hiểu nhu cầu, thiết kế, triển khai, kiểm thử và vận hành không nhất thiết diễn ra một lần theo đường thẳng. Trong vòng lặp, thông tin phản hồi cập nhật sản phẩm và bộ test. Kiểm thử sớm có thể là review mô tả nghiệp vụ trước khi có giao diện.

## 2. Ví dụ kế hoạch cho một vòng phát triển
```text
Yêu cầu: khóa miễn phí chỉ ghi danh một lần
Trước code: review quyền, trạng thái khóa và thông báo lỗi
Trong code: unit cho quy tắc; integration cho lưu và chống trùng
Sau tích hợp: UI cho trạng thái chờ, lỗi, thành công và màn hình hẹp
Trước phát hành: hồi quy theo tác động, báo cáo giới hạn và rủi ro
```
Acceptance criteria mô tả điều kiện riêng của yêu cầu. Definition of Done là thỏa thuận chung về mức hoàn tất. Một câu chuyện có tiêu chí đạt nhưng chưa hoàn tất các yêu cầu chất lượng chung vẫn có thể chưa “done”.

## 3. Chọn phạm vi theo rủi ro
Ước lượng khả năng sai và tác động, xác định vùng ưu tiên, liên kết từng vùng tới test. Điểm số rủi ro chỉ là công cụ thảo luận; không tạo cảm giác chính xác tuyệt đối nếu đầu vào chỉ là đánh giá sơ bộ. Dành thời gian cho lỗi đã thấy và các ràng buộc quyền/dữ liệu quan trọng.

## 4. Bài tập và đáp án
Trong hai ngày, nhóm sửa luồng nộp quiz và đổi màu tiêu đề. Ưu tiên tính điểm, lưu kết quả và lượt làm trước phần màu vì ảnh hưởng cao hơn; vẫn kiểm tra hiển thị cơ bản. Nộp kế hoạch ai làm gì, dữ liệu nào, tiêu chí vào/ra và phần chưa thể kiểm tra. Không gọi kế hoạch là bằng chứng đã chạy test.

## Bài tập vận dụng bổ sung
Viết tiêu chí chấp nhận cho đăng ký khóa, đề xuất hoạt động review, unit, integration và system trong một vòng phát triển. Nêu ba rủi ro cần ưu tiên.

## Hướng giải bài tập bổ sung
Phân biệt điều kiện hoàn tất chung với tiêu chí riêng của chức năng. Bao phủ tính đúng dữ liệu và quyền, không chỉ màu thông báo.

## Câu hỏi tự kiểm tra
1. Kiểm thử nên bắt đầu khi nào?
2. Trong Agile, trách nhiệm chất lượng thuộc về ai?
3. Tiêu chí chấp nhận mô tả điều gì?
4. Khi thời gian có hạn, nên ưu tiên test theo gì?
5. Có thể kiểm tra hết mọi kết hợp đầu vào của mọi hệ thống không?

## Gợi ý đáp án và điểm cần nhớ
- Từ sớm, gồm review yêu cầu. Review sớm giúp phát hiện vấn đề trước khi viết mã.
- Cả nhóm theo vai trò phối hợp. Chất lượng không được giao hoàn toàn cho một vai trò.
- Điều kiện cụ thể chức năng cần đáp ứng. Tiêu chí giúp đánh giá hành vi theo nhu cầu.
- Rủi ro và tác động nghiệp vụ. Ưu tiên dựa trên xác suất và ảnh hưởng sai sót.
- Thường không, cần chọn phạm vi có căn cứ. Kiểm thử toàn bộ thường không khả thi với hệ thống thực tế.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
