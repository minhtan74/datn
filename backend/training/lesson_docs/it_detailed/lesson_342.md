## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 4: Thiết kế kiểm thử theo hành vi.
- Các bài trong chương: Bảng quyết định và tổ hợp điều kiện; Kiểm thử chuyển trạng thái.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Mô hình hóa vòng đời nghiệp vụ và kiểm tra chuyển trạng thái hợp lệ, không hợp lệ.

## Kiến thức nền
Mô hình trạng thái gồm trạng thái, sự kiện và chuyển tiếp. Kết quả của một hành động có thể phụ thuộc trạng thái trước đó. Ví dụ quiz đang làm, đã nộp hoặc hết thời gian không nên xử lý thao tác nộp giống nhau trong mọi trường hợp.

Bảng chuyển tiếp mô tả trạng thái đầu, hành động, trạng thái cuối và phản hồi. Ngoài đường hợp lệ, kiểm tra chuyển tiếp bị cấm như sửa câu trả lời sau khi đã nộp. Bao phủ trạng thái không đồng nghĩa bao phủ mọi chuyển tiếp giữa chúng.

Một lần chạy cần điều kiện khởi tạo rõ ràng và khả năng khôi phục dữ liệu. Với tác vụ bất đồng bộ, trạng thái giao diện và trạng thái server có thể cập nhật ở các thời điểm khác nhau; cần kiểm tra trạng thái có thẩm quyền. Không coi một nút bị ẩn là bằng chứng server đã ngăn hành động trái phép.

## 1. Mô hình hóa một lượt quiz
```text
Chưa bắt đầu --mở hợp lệ--> Đang làm --nộp hợp lệ--> Đã nộp
Đang làm --hết thời gian--> Trạng thái theo quy tắc hệ thống
Đã nộp --sửa câu trả lời--> Từ chối, không đổi kết quả đã lưu
```
Không tự chọn “hết giờ luôn tự nộp” nếu chưa có yêu cầu. Phải xác nhận cách server xử lý và chỉ rõ người có thẩm quyền tính thời gian.

## 2. Trạng thái khác với nhãn giao diện
Một nút có chữ “đã nộp” không chứng minh dữ liệu đã commit. Test phải quan sát trạng thái được server xác nhận, kết quả và các tác dụng phụ. Cần xử lý mạng mất phản hồi sau khi server đã lưu: gửi lại có thể không được tạo kết quả thứ hai theo hợp đồng.

## 3. Bao phủ và chuỗi sự kiện
Test từng chuyển tiếp hợp lệ, chuyển tiếp bị cấm và chuỗi có ý nghĩa. Bao phủ mọi trạng thái chỉ cho biết đã tới các nút, không bảo đảm đã đi qua mọi cạnh. Thêm điều kiện dữ liệu như hết lượt, lượt đang làm hoặc quá giờ để phân biệt quy tắc.

## 4. Mẫu test và lời giải
Tạo attempt lab đang làm, nộp thành công, giữ result_id, gửi sửa câu trả lời sau nộp. Mong đợi từ chối theo API và hash kết quả cũ không đổi. Test khác mô phỏng request nộp lặp, xác nhận số kết quả theo hợp đồng. Không chỉnh đồng hồ hệ thống thật để thử hết giờ; dùng cơ chế thời gian kiểm soát được trong test.
Nộp bảng trạng thái đầu, sự kiện, guard, trạng thái cuối và dữ liệu cần giữ. Đánh dấu trạng thái chưa thử thay vì ghi pass theo sơ đồ.

## Bài tập vận dụng bổ sung
Vẽ trạng thái của đơn hàng pending, paid, cancelled theo hợp đồng hệ thống. Viết ba chuyển tiếp hợp lệ và hai chuyển tiếp bị cấm; không dùng thanh toán thật.

## Hướng giải bài tập bổ sung
Nêu rõ sự kiện dẫn tới chuyển trạng thái và kiểm tra cả dữ liệu server. Yêu cầu nộp trùng cần có kết quả mong đợi cụ thể.

## Câu hỏi tự kiểm tra
1. Kết quả thao tác trong hệ thống có trạng thái phụ thuộc gì?
2. Bao phủ mọi trạng thái có bằng bao phủ mọi chuyển tiếp không?
3. Ẩn nút nộp sau hoàn tất đã chứng minh server chặn nộp lại chưa?
4. Test chuyển tiếp cần ghi thông tin nào?
5. Với chức năng bất đồng bộ nên đối chiếu thêm gì?

## Gợi ý đáp án và điểm cần nhớ
- Trạng thái trước và sự kiện. Cùng sự kiện có thể được xử lý khác ở mỗi trạng thái.
- Không. Các đường nối trạng thái là mục tiêu bao phủ riêng.
- Chưa. Phải kiểm tra quy tắc tại API hoặc server.
- Trạng thái đầu, sự kiện và kết quả mong đợi. Các thành phần mô tả được luồng cần xác minh.
- Trạng thái server có thẩm quyền. Giao diện có thể cập nhật trước hoặc sau dữ liệu thực.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
