## Mục tiêu
Chuyển quy tắc nghiệp vụ nhiều điều kiện thành các ca kiểm thử rõ ràng.

## Kiến thức trọng tâm
Bảng quyết định biểu diễn điều kiện và hành động theo từng quy tắc. Hữu ích khi kết quả phụ thuộc nhiều điều kiện kết hợp. Mỗi cột có thể mô tả một tổ hợp cùng hành vi mong đợi; cần phân biệt tổ hợp không thể xảy ra với tổ hợp chưa được kiểm tra.

Ví dụ quyền học phụ thuộc tài khoản hợp lệ, trạng thái ghi danh và nội dung miễn phí. Đặt giả định rõ trước khi lập bảng. Không mặc định mọi ứng dụng có cùng thứ tự ưu tiên giữa các điều kiện; cần hỏi hoặc xác nhận yêu cầu nếu quy tắc xung đột.

Khi số điều kiện tăng, số tổ hợp tăng nhanh. Có thể nhóm các quy tắc tương đương hoặc chọn kỹ thuật giảm tổ hợp theo rủi ro, nhưng phải ghi giới hạn. Pairwise không bảo đảm tìm mọi lỗi cần ba điều kiện tương tác. Dữ liệu test phải thực sự tạo được trạng thái đã mô tả.

## Ví dụ có hướng dẫn
Giả sử bài miễn phí cho phép xem không cần ghi danh; bài trả phí chỉ cho người đã ghi danh. Lập bốn tổ hợp free/enrolled và gắn kết quả cho phép hoặc chặn, trong phạm vi tài khoản hợp lệ.

## Bài tập thực hành
Lập bảng cho giảm giá chỉ khi có mã hợp lệ và tổng tiền đạt ngưỡng. Viết test cho bốn tổ hợp, thêm tình huống mã hết hạn theo yêu cầu cụ thể.

## Gợi ý tự kiểm tra
Hai điều kiện nhị phân có bốn tổ hợp trước khi rút gọn. Với phép AND, chỉ tổ hợp cả hai đúng được giảm giá.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf