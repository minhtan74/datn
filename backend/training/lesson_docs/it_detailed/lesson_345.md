## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 6: Chất lượng và thực hành tổng hợp.
- Các bài trong chương: Hiệu năng, khả dụng và tương thích; Dự án nhỏ: kế hoạch kiểm thử và tự động hóa.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Viết tiêu chí đo chất lượng ngoài chức năng trong phạm vi lab.

## Kiến thức nền
Kiểm thử phi chức năng xem đặc tính như hiệu năng, khả dụng, khả năng tiếp cận và tương thích. Một chức năng đúng kết quả nhưng chậm hoặc không thao tác được bằng bàn phím vẫn có thể không đáp ứng nhu cầu người dùng.

Hiệu năng cần mô hình tải, dữ liệu, môi trường, thước đo và ngưỡng đã thống nhất. Thời gian phản hồi, thông lượng và tỉ lệ lỗi là các thước đo khác nhau. Percentile như p95 mô tả phần lớn mẫu tốt hơn một trung bình đơn lẻ khi có đuôi chậm. Đo tải chỉ trên hệ thống được phép và có giới hạn để tránh ảnh hưởng người dùng.

Kiểm tra giao diện với tên dài, màn hình hẹp, phóng to và thao tác bàn phím. Thông báo cần rõ, không chỉ dùng màu để truyền trạng thái. Kiểm tra tương thích theo tập trình duyệt/thiết bị được hỗ trợ; không tuyên bố đã thử mọi nền tảng nếu chỉ có một môi trường.

## 1. Viết mục tiêu đo được
Thay “trang nhanh” bằng một tiêu chí ví dụ: trên môi trường lab đã nêu, dữ liệu 100 khóa, dưới mô hình tải được phép, đo p95 thời gian API và tỉ lệ lỗi theo ngưỡng nhóm thống nhất. Đây là mẫu đặc tả, không phải kết quả website hiện tại hay ngưỡng chuẩn cho mọi hệ thống.

## 2. Đọc số liệu có ngữ cảnh
Ghi thời gian làm nóng, số mẫu, phân bố độ trễ và tỉ lệ lỗi. Không so phiên bản A trên máy rảnh với B trên máy đang bận rồi quy mọi khác biệt cho mã nguồn. Timeout và lỗi HTTP cần được tính, không loại khỏi báo cáo để làm trung bình đẹp hơn.

## 3. Checklist thao tác giao diện
- Dùng Tab tới nút đăng ký, có focus rõ và kích hoạt bằng bàn phím.
- Thông báo đọc được, có văn bản chứ không chỉ màu; có nút đóng.
- Tên khóa dài không che số liệu hoặc đẩy nút ra ngoài màn hình.
- Ở màn hình hẹp và khi phóng to, không mất nội dung quan trọng.
- Mạng chậm có trạng thái chờ và ngăn bấm lặp phù hợp.
- Lỗi API không hiển thị như chưa có dữ liệu.
Một checklist thủ công hữu ích nhưng không tự chứng nhận đạt toàn bộ tiêu chuẩn tiếp cận.

## 4. Bài tập và đáp án định hướng
Soạn ma trận ba kích thước khung và hai trình duyệt được hỗ trợ. Chọn một luồng chính kiểm thử ở cả sáu tổ hợp, ghi môi trường. Tạo tên dài và thông báo lỗi dài trong dữ liệu lab. Đáp án cần có ảnh và nhận xét cụ thể, không chỉ “đẹp”; ghi giới hạn khi chưa có thiết bị thật hoặc công nghệ hỗ trợ để thử.

## Bài tập vận dụng bổ sung
Viết checklist 8 mục cho trang khóa học: ít nhất hai mục về bàn phím, hai về màn hình hẹp, hai về nội dung dài và hai về hiệu năng có điều kiện đo.

## Hướng giải bài tập bổ sung
Ghi rõ môi trường và tiêu chí, không dùng câu “rất nhanh” hay “đẹp” làm kết quả mong đợi duy nhất. p95 không phải giá trị chậm nhất tuyệt đối.

## Câu hỏi tự kiểm tra
1. Kiểm thử phi chức năng xem xét gì?
2. Để tiêu chí hiệu năng kiểm chứng được cần gì?
3. p95 thời gian phản hồi thường diễn đạt điều gì?
4. Vì sao không nên chỉ dùng màu báo lỗi?
5. Test tải nên thực hiện ở đâu?

## Gợi ý đáp án và điểm cần nhớ
- Đặc tính chất lượng như hiệu năng và khả dụng. Phi chức năng đánh giá cách hệ thống đáp ứng ngoài kết quả nghiệp vụ.
- Tải, môi trường, thước đo và ngưỡng. Các điều kiện đo làm kết quả có ý nghĩa.
- Khoảng 95% mẫu không vượt ngưỡng đó. Percentile mô tả phân bố mẫu đo.
- Người dùng cần tín hiệu văn bản hoặc biểu tượng dễ hiểu. Trạng thái cần được truyền bằng nhiều dấu hiệu có thể tiếp cận.
- Hệ thống được phép với giới hạn đã xác định. Hoạt động tải cần phạm vi và kiểm soát tác động.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
