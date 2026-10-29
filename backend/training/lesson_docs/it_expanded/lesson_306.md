Mục tiêu: nhận biết request, response, phương thức và nhóm mã trạng thái.

HTTP tổ chức trao đổi yêu cầu và phản hồi. Request có phương thức, đường dẫn, header và có thể có body; response có mã trạng thái, header và có thể có body. GET thường dùng để lấy biểu diễn tài nguyên; POST thường gửi dữ liệu để máy chủ xử lý. Không đặt dữ liệu bí mật vào URL chỉ vì đang dùng HTTPS, vì URL có thể xuất hiện trong lịch sử và nhật ký.

Nhóm 2xx báo thành công, 3xx chuyển hướng, 4xx lỗi phía yêu cầu và 5xx lỗi máy chủ. 404 nghĩa là không tìm thấy tài nguyên theo yêu cầu; 500 là lỗi nội bộ máy chủ. Cần đọc cả phản hồi và ngữ cảnh để chẩn đoán.

HTTPS là HTTP được bảo vệ bằng TLS: hỗ trợ bảo mật đường truyền, toàn vẹn và xác thực máy chủ theo chứng thư hợp lệ. HTTPS không bảo đảm nội dung website đáng tin hoặc ứng dụng không có lỗ hổng.

Tự luyện: mô tả một request GET lấy trang khóa học; nêu cách xử lý khác nhau khi nhận 404 và 500.

Video tham khảo (tiếng Anh): SSL, TLS, HTTP, HTTPS Explained — PowerCert Animated Videos.
Nguồn gốc: https://www.youtube.com/watch?v=hExRDVZHhig
Video minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên.