## Mục tiêu
Mô tả cấp phát cấu hình tự động và phân biệt với chuyển đổi địa chỉ.

## Kiến thức trọng tâm
DHCPv4 cấp cấu hình IP theo thời hạn thuê. Trong luồng cấp mới điển hình, client gửi Discover, server Offer, client Request rồi server Acknowledge. Cấu hình có thể gồm địa chỉ IP, subnet mask, gateway và DNS. DHCP không phải dịch vụ phân giải tên.

NAT chuyển đổi địa chỉ khi gói đi qua thiết bị biên. PAT thường cho nhiều host dùng chung một IPv4 công khai bằng cách phân biệt thêm cổng giao vận. Router duy trì trạng thái ánh xạ cho lưu lượng phản hồi. NAT không đồng nghĩa với tường lửa và không thay thế kiểm soát truy cập.

Nếu một máy không lấy được cấu hình, cần kiểm tra liên kết, DHCP server, phạm vi cấp phát và xung đột. Địa chỉ 169.254.x.x có thể là địa chỉ link-local tự gán, không mặc nhiên là cấu hình Internet hoạt động. Trước khi đổi cấu hình, ghi nhận giá trị hiện tại để có thể khôi phục.

## Ví dụ có hướng dẫn
Laptop nhận 192.168.1.20/24, gateway 192.168.1.1 từ DHCP. Khi truy cập web, router dùng NAT/PAT ánh xạ phiên của laptop ra địa chỉ công khai. Một việc cấp cấu hình, một việc chuyển đổi lưu lượng.

## Bài tập thực hành
Trên mạng lab, liệt kê địa chỉ IP, mask, gateway, DNS và thời hạn thuê. Vẽ hai máy truy cập cùng một web server qua PAT, đánh dấu cổng nguồn khác nhau.

## Gợi ý tự kiểm tra
Không dùng IP riêng làm bằng chứng về địa chỉ công khai. Hai máy có thể chia sẻ IP công khai nhưng có các ánh xạ cổng riêng.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP