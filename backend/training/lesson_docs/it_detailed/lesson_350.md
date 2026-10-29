## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 4: Cấp phát địa chỉ và chuyển tiếp.
- Các bài trong chương: DHCP và NAT trong mạng gia đình; Định tuyến cơ bản và làm quen IPv6.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Đọc tuyến mặc định, chọn tuyến theo tiền tố dài nhất và nhận diện IPv6.

## Kiến thức nền
Router chọn tuyến phù hợp địa chỉ đích; khi có nhiều tiền tố khớp, nguyên tắc tiền tố dài nhất giúp chọn tuyến cụ thể nhất. Tuyến mặc định IPv4 là 0.0.0.0/0, được dùng khi không có tuyến cụ thể hơn. Một tuyến mô tả mạng đích cùng next hop hoặc giao diện ra.

IPv6 có địa chỉ 128 bit, viết bằng các nhóm thập lục phân. Có thể bỏ số 0 đầu mỗi nhóm và rút gọn một chuỗi nhóm 0 bằng dấu :: một lần trong một địa chỉ. IPv6 không dùng broadcast như IPv4; multicast có vai trò quan trọng trong nhiều giao thức.

Địa chỉ link-local IPv6 dùng trên liên kết cục bộ. Host có thể chạy IPv4 và IPv6 đồng thời theo dual stack. Không chỉ kiểm tra có địa chỉ: muốn liên lạc còn cần tuyến, dịch vụ và chính sách phù hợp. Bài này chưa đi sâu OSPF, BGP hoặc cấu hình định tuyến động.

## 1. Thực hành longest-prefix match
```text
Đích tiền tố         Next hop
0.0.0.0/0            R0
10.0.0.0/8           R1
10.1.0.0/16          R2
10.1.2.0/24          R3
```
Đích 10.1.2.9 chọn R3; 10.1.8.9 chọn R2; 10.2.8.9 chọn R1; đích không có tuyến cụ thể hơn dùng R0 nếu tuyến hợp lệ. Nếu nhiều tuyến cùng tiền tố, các tiêu chí chọn tiếp phụ thuộc giao thức và nền tảng; không quyết định bằng vị trí dòng đầu theo bảng minh họa.

## 2. IPv6 từ cách viết tới phạm vi
Một địa chỉ đầy đủ có tám nhóm 16 bit. 2001:0db8:0000:0000:0000:0000:0000:0001 rút gọn thành 2001:db8::1. Dải 2001:db8::/32 dùng cho tài liệu minh họa. ::1 là loopback. Link-local thường nhận diện bằng tiền tố fe80::/10, dùng trong liên kết và có thể cần thông tin interface để xác định vùng.
IPv6 không dùng ARP; Neighbor Discovery xử lý các chức năng láng giềng. Không được chặn mọi ICMPv6 một cách tùy tiện vì nó tham gia các hoạt động thiết yếu của mạng IPv6.

## 3. Kết nối và chẩn đoán
Một host có IPv6 global chưa chắc có đường tới mọi dịch vụ; kiểm tra route, DNS AAAA, khả năng hỗ trợ của đích và chính sách. Dual stack có thể khiến một phần truy cập hoạt động qua một giao thức còn giao thức kia lỗi.

## 4. Bài tập có lời giải
Chọn tuyến cho bốn đích từ bảng; ghi tiền tố khớp và lý do bỏ các tuyến còn lại. Giải thích vì sao 2001:db8::1::2 không hợp lệ: hai dấu rút gọn khiến không xác định được số nhóm 0 ở mỗi vị trí. Với host dual stack, lập checklist IPv4 và IPv6 riêng thay vì kết luận chỉ từ một lệnh ping.

## Bài tập vận dụng bổ sung
Với các tuyến /0, 192.168.0.0/16 và 192.168.2.0/24, chọn tuyến cho 192.168.2.9. Rút gọn 2001:0db8:0000:0000:0000:0000:0000:0001.

## Hướng giải bài tập bổ sung
Chọn /24 vì cụ thể nhất. IPv6 rút gọn thành 2001:db8::1; không dùng hai dấu :: trong cùng địa chỉ.

## Câu hỏi tự kiểm tra
1. Khi nhiều tuyến đều khớp đích, ưu tiên thông thường là gì?
2. Tuyến mặc định IPv4 viết thế nào?
3. IPv6 có độ dài địa chỉ bao nhiêu?
4. Dấu :: có thể dùng tối đa mấy lần trong một địa chỉ IPv6?
5. Dual stack nghĩa là gì?

## Gợi ý đáp án và điểm cần nhớ
- Tiền tố dài nhất. Longest-prefix match chọn tuyến cụ thể nhất.
- 0.0.0.0/0. /0 khớp mọi địa chỉ khi không có tuyến cụ thể hơn.
- 128 bit. IPv6 dùng không gian địa chỉ 128 bit.
- Một lần. Chỉ một vị trí rút gọn để khôi phục số nhóm 0 một cách rõ ràng.
- Cùng hỗ trợ IPv4 và IPv6. Dual stack vận hành hai bộ giao thức IP song song.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
