## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 1: Nền tảng kiểm thử.
- Các bài trong chương: Mục tiêu và các mức kiểm thử; Thiết kế test case.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Viết test case có thể lặp lại và đánh giá được.

## Kiến thức nền
Một test case nên có mục tiêu, điều kiện trước, dữ liệu đầu vào, các bước và kết quả mong đợi. Kết quả mong đợi cần cụ thể theo yêu cầu; câu như “hệ thống chạy tốt” không đủ để xác định pass hay fail.

Phân biệt kết quả mong đợi với kết quả thực tế. Khi chạy test, ghi môi trường và phiên bản để có thể tái hiện. Dữ liệu thử cần kiểm soát, không dùng tài khoản hoặc giao dịch thật nếu có môi trường kiểm thử riêng.

Bao phủ cả luồng hợp lệ và các tình huống không hợp lệ: thiếu trường bắt buộc, sai kiểu, không đủ quyền hoặc tài nguyên không tồn tại. Không chỉ kiểm tra giao diện báo thành công mà bỏ qua việc dữ liệu thực sự được lưu đúng.

## 1. Mẫu test case có thể thực hiện
```text
ID: ENR-001
Mục tiêu: ghi danh khóa miễn phí một lần
Điều kiện trước: tài khoản lab hoạt động, khóa published, chưa ghi danh
Dữ liệu: user U1, course C1, price=0
Bước 1: mở danh sách khóa, chọn C1
Bước 2: bấm Đăng ký, chờ request hoàn tất
Kỳ vọng: một phản hồi thành công, một ghi danh, khóa có trong Khóa học của tôi
Sau test: chỉ dọn dữ liệu do ca này tạo trong database test
```
Kết quả thực tế và bằng chứng chỉ điền sau khi chạy. Không điền “pass” sẵn trong mẫu để minh họa như một kết quả thật.

## 2. Bao phủ tình huống thay vì nhân bản thao tác
Test dương kiểm tra đăng ký hợp lệ. Test âm kiểm tra khóa không tồn tại, chưa xác thực, khóa không cho đăng ký hoặc đầu vào sai kiểu theo hợp đồng. Test lặp/đồng thời kiểm tra tính duy nhất. Một bộ test chỉ đổi tên tài khoản nhưng đi cùng đường thành công không bao phủ các rủi ro này.

## 3. Kết quả mong đợi đủ cụ thể
“Đăng ký tốt” không kiểm chứng rõ. “API phản hồi thành công theo hợp đồng; bảng ghi danh tăng đúng một bản ghi U1–C1; không phát sinh thanh toán cho khóa miễn phí” là các quan sát cụ thể. Nếu không có quyền xem database, dùng API kiểm tra hoặc cơ chế bằng chứng được nhóm cho phép, không bỏ qua xác minh.

## 4. Bài tập có đáp án định hướng
Viết ENR-002 cho bấm lặp và ENR-003 cho không đủ quyền. Phân biệt luồng bấm ở UI với hai request thật: khóa nút chỉ là một lớp chống lặp. Đáp án cần kiểm tra ràng buộc server và không tạo bản ghi thứ hai. Ghi rõ mã lỗi dự kiến theo hợp đồng hiện tại, không đoán mọi dự án đều trả 409.

## Bài tập vận dụng bổ sung
viết test case cho học viên chưa ghi danh mở bài có giới hạn. Ghi điều kiện trước, bước truy cập, kết quả về quyền và xác nhận không phát sinh tiến độ học trái phép.

## Câu hỏi tự kiểm tra
1. Thành phần nào giúp quyết định test pass hay fail?
2. Điều kiện trước mô tả điều gì?
3. Test đăng nhập chỉ dùng mật khẩu đúng đã đủ chưa?
4. Kết quả mong đợi nào kiểm chứng được rõ hơn?
5. Vì sao ghi phiên bản và môi trường khi chạy test?

## Gợi ý đáp án và điểm cần nhớ
- Kết quả mong đợi cụ thể. Cần đối chiếu kết quả thực tế với kết quả mong đợi.
- Trạng thái cần có trước khi thực hiện test. Ví dụ tài khoản đã ghi danh là một điều kiện trước.
- Chưa, cần tình huống sai và dữ liệu không hợp lệ phù hợp. Luồng không hợp lệ có thể bộc lộ lỗi xác thực và xử lý đầu vào.
- API trả 403 và không tạo bản ghi tiến độ. Mã phản hồi và trạng thái dữ liệu là các quan sát cụ thể.
- Giúp tái hiện và phân tích kết quả. Hành vi có thể khác theo cấu hình hoặc phiên bản.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
