Mục tiêu: đọc địa chỉ IPv4, ký hiệu CIDR và xác định mạng con đơn giản.

IPv4 dùng địa chỉ 32 bit, thường viết thành bốn số thập phân từ 0 đến 255. Ký hiệu /24 cho biết 24 bit đầu là phần mạng; mặt nạ tương ứng là 255.255.255.0. Với mạng thông thường 192.168.1.0/24, địa chỉ mạng là 192.168.1.0, broadcast là 192.168.1.255 và các địa chỉ host thông thường là .1 đến .254.

Hai host 192.168.1.10/24 và 192.168.1.20/24 cùng mạng con. Host 192.168.2.10/24 nằm ở mạng khác. Khi đích ngoài mạng con, máy thường gửi gói đến default gateway để chuyển tiếp; gateway không phải máy chủ DNS.

Các dải riêng gồm 10.0.0.0/8, 172.16.0.0/12 và 192.168.0.0/16. Chúng không được định tuyến công khai trên Internet. Không suy ra mọi địa chỉ bắt đầu bằng 172 đều là địa chỉ riêng.

Tự luyện: với 10.0.5.0/24, tìm địa chỉ mạng, broadcast và hai địa chỉ host hợp lệ. Quy tắc trừ hai địa chỉ chỉ áp dụng mạng con thông thường; /31 và /32 có cách sử dụng riêng.

Video tham khảo (tiếng Anh): What is Subnetting? - Subnetting Mastery - Part 1 of 7 — Practical Networking.
Nguồn gốc: https://www.youtube.com/watch?v=BWZ-MHIhqjM
Video minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên.