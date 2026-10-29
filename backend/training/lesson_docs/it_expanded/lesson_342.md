## Mục tiêu
Mô hình hóa vòng đời nghiệp vụ và kiểm tra chuyển trạng thái hợp lệ, không hợp lệ.

## Kiến thức trọng tâm
Mô hình trạng thái gồm trạng thái, sự kiện và chuyển tiếp. Kết quả của một hành động có thể phụ thuộc trạng thái trước đó. Ví dụ quiz đang làm, đã nộp hoặc hết thời gian không nên xử lý thao tác nộp giống nhau trong mọi trường hợp.

Bảng chuyển tiếp mô tả trạng thái đầu, hành động, trạng thái cuối và phản hồi. Ngoài đường hợp lệ, kiểm tra chuyển tiếp bị cấm như sửa câu trả lời sau khi đã nộp. Bao phủ trạng thái không đồng nghĩa bao phủ mọi chuyển tiếp giữa chúng.

Một lần chạy cần điều kiện khởi tạo rõ ràng và khả năng khôi phục dữ liệu. Với tác vụ bất đồng bộ, trạng thái giao diện và trạng thái server có thể cập nhật ở các thời điểm khác nhau; cần kiểm tra trạng thái có thẩm quyền. Không coi một nút bị ẩn là bằng chứng server đã ngăn hành động trái phép.

## Ví dụ có hướng dẫn
Luồng quiz: chưa bắt đầu → đang làm → đã nộp. Nộp lại cùng attempt không được tạo thêm kết quả ngoài quy tắc. Trạng thái hết giờ có thể dẫn tới tự nộp hoặc chặn theo yêu cầu đã xác nhận.

## Bài tập thực hành
Vẽ trạng thái của đơn hàng pending, paid, cancelled theo hợp đồng hệ thống. Viết ba chuyển tiếp hợp lệ và hai chuyển tiếp bị cấm; không dùng thanh toán thật.

## Gợi ý tự kiểm tra
Nêu rõ sự kiện dẫn tới chuyển trạng thái và kiểm tra cả dữ liệu server. Yêu cầu nộp trùng cần có kết quả mong đợi cụ thể.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf