Mục tiêu: giải thích vai trò DNS và đọc các loại bản ghi cơ bản.

DNS là hệ thống phân giải tên phân tán. Ứng dụng có thể hỏi resolver để tìm địa chỉ gắn với tên miền. Resolver tận dụng bộ nhớ đệm hoặc truy vấn các máy chủ thích hợp; không phải mọi yêu cầu đều đi lại toàn bộ chuỗi truy vấn.

Bản ghi A ánh xạ tên tới IPv4, AAAA tới IPv6. CNAME khai báo tên bí danh trỏ tới một tên khác. MX mô tả máy chủ nhận thư cho miền. TTL hướng dẫn thời gian lưu bộ nhớ đệm, không phải thời gian tải trang hay thời hạn đăng ký tên miền.

DNS thường sử dụng cổng 53 với UDP hoặc TCP. Phân giải tên thành công chỉ cho biết có câu trả lời DNS; không chứng minh máy chủ web đang hoạt động. Khi gỡ lỗi, tách kiểm tra DNS khỏi kiểm tra kết nối và HTTP.

Tự luyện: mô tả vì sao đổi bản ghi chưa chắc mọi người dùng thấy ngay. Nêu khác biệt giữa tên miền, địa chỉ IP và URL; URL còn có thể chứa giao thức, đường dẫn và tham số.

Video tham khảo (tiếng Anh): How a DNS Server (Domain Name System) works. — PowerCert Animated Videos.
Nguồn gốc: https://www.youtube.com/watch?v=mpQZVYPuDGU
Video minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên.