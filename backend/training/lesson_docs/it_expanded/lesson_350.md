## Mục tiêu
Đọc tuyến mặc định, chọn tuyến theo tiền tố dài nhất và nhận diện IPv6.

## Kiến thức trọng tâm
Router chọn tuyến phù hợp địa chỉ đích; khi có nhiều tiền tố khớp, nguyên tắc tiền tố dài nhất giúp chọn tuyến cụ thể nhất. Tuyến mặc định IPv4 là 0.0.0.0/0, được dùng khi không có tuyến cụ thể hơn. Một tuyến mô tả mạng đích cùng next hop hoặc giao diện ra.

IPv6 có địa chỉ 128 bit, viết bằng các nhóm thập lục phân. Có thể bỏ số 0 đầu mỗi nhóm và rút gọn một chuỗi nhóm 0 bằng dấu :: một lần trong một địa chỉ. IPv6 không dùng broadcast như IPv4; multicast có vai trò quan trọng trong nhiều giao thức.

Địa chỉ link-local IPv6 dùng trên liên kết cục bộ. Host có thể chạy IPv4 và IPv6 đồng thời theo dual stack. Không chỉ kiểm tra có địa chỉ: muốn liên lạc còn cần tuyến, dịch vụ và chính sách phù hợp. Bài này chưa đi sâu OSPF, BGP hoặc cấu hình định tuyến động.

## Ví dụ có hướng dẫn
Bảng có 10.0.0.0/8 qua R1 và 10.1.0.0/16 qua R2. Gói tới 10.1.2.3 chọn tuyến /16. Nếu chỉ có default route cho một đích công khai, gói đi theo default route.

## Bài tập thực hành
Với các tuyến /0, 192.168.0.0/16 và 192.168.2.0/24, chọn tuyến cho 192.168.2.9. Rút gọn 2001:0db8:0000:0000:0000:0000:0000:0001.

## Gợi ý tự kiểm tra
Chọn /24 vì cụ thể nhất. IPv6 rút gọn thành 2001:db8::1; không dùng hai dấu :: trong cùng địa chỉ.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP