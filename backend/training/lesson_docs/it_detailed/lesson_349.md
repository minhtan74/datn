## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 4: Cấp phát địa chỉ và chuyển tiếp.
- Các bài trong chương: DHCP và NAT trong mạng gia đình; Định tuyến cơ bản và làm quen IPv6.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Mô tả cấp phát cấu hình tự động và phân biệt với chuyển đổi địa chỉ.

## Kiến thức nền
DHCPv4 cấp cấu hình IP theo thời hạn thuê. Trong luồng cấp mới điển hình, client gửi Discover, server Offer, client Request rồi server Acknowledge. Cấu hình có thể gồm địa chỉ IP, subnet mask, gateway và DNS. DHCP không phải dịch vụ phân giải tên.

NAT chuyển đổi địa chỉ khi gói đi qua thiết bị biên. PAT thường cho nhiều host dùng chung một IPv4 công khai bằng cách phân biệt thêm cổng giao vận. Router duy trì trạng thái ánh xạ cho lưu lượng phản hồi. NAT không đồng nghĩa với tường lửa và không thay thế kiểm soát truy cập.

Nếu một máy không lấy được cấu hình, cần kiểm tra liên kết, DHCP server, phạm vi cấp phát và xung đột. Địa chỉ 169.254.x.x có thể là địa chỉ link-local tự gán, không mặc nhiên là cấu hình Internet hoạt động. Trước khi đổi cấu hình, ghi nhận giá trị hiện tại để có thể khôi phục.

## 1. Vòng đời thuê địa chỉ
DORA mô tả cấp mới điển hình, còn gia hạn có thể không phát lại đủ bốn bước theo đúng hình thức ban đầu. Lease có thời hạn; client cố gia hạn theo quy trình giao thức. Khi không có cấu hình hợp lệ, lỗi cần được phân tích theo client, server, relay và phạm vi mạng.
DHCP pool nên loại địa chỉ gateway và địa chỉ đã cấp tĩnh. Reservation gắn cấu hình dự kiến cho một định danh client theo triển khai, khác việc tự gõ địa chỉ tĩnh trên máy. Nếu DHCP ở mạng khác, có thể cần relay phù hợp.

## 2. Theo dõi bảng PAT
```text
Nguồn bên trong        Nguồn sau PAT            Đích
192.168.1.10:51000     198.51.100.5:40001        203.0.113.8:443
192.168.1.20:51000     198.51.100.5:40002        203.0.113.8:443
```
Các địa chỉ 198.51.100.0/24 và 203.0.113.0/24 ở đây dùng minh họa, không phải dịch vụ lab công khai để truy cập. Bảng ánh xạ giúp đưa lưu lượng trả về đúng phiên nội bộ. Hai máy có thể dùng cùng cổng nguồn nội bộ mà vẫn được phân biệt sau PAT.

## 3. Những lỗi dễ gặp
IP tĩnh nằm trong pool có thể xung đột; gateway sai làm truy cập LAN được nhưng ra ngoài lỗi; DNS sai ảnh hưởng tên miền; pool hết địa chỉ làm máy mới không nhận lease. Không reset toàn mạng chỉ vì một máy chưa cấp IP.

## 4. Bài tập và đáp án
Một /24 có gateway .1, máy chủ .10–.20 và DHCP .10–.200. Chỉ ra xung đột thiết kế rồi đề xuất pool .50–.200 hoặc cơ chế loại trừ tương ứng. NAT có tạo quyền truy cập vào ứng dụng không? Không: vẫn cần xác thực và phân quyền. Nộp bảng cấu hình, bằng chứng cấp mới và phân tích đường về của một phiên PAT.

## Bài tập vận dụng bổ sung
Trên mạng lab, liệt kê địa chỉ IP, mask, gateway, DNS và thời hạn thuê. Vẽ hai máy truy cập cùng một web server qua PAT, đánh dấu cổng nguồn khác nhau.

## Hướng giải bài tập bổ sung
Không dùng IP riêng làm bằng chứng về địa chỉ công khai. Hai máy có thể chia sẻ IP công khai nhưng có các ánh xạ cổng riêng.

## Câu hỏi tự kiểm tra
1. Chuỗi cấp mới DHCPv4 điển hình là gì?
2. DHCP có thể cung cấp thông tin nào?
3. PAT phân biệt nhiều kết nối chung IP công khai bằng gì?
4. NAT có thay thế tường lửa không?
5. Máy chỉ có 169.254.x.x sau khi không nhận DHCP cần kiểm tra gì?

## Gợi ý đáp án và điểm cần nhớ
- Discover, Offer, Request, Acknowledge. DORA mô tả luồng cấp mới DHCP phổ biến.
- IP, mask, gateway và DNS. DHCP phân phối các tùy chọn cấu hình mạng.
- Cổng giao vận trong ánh xạ. PAT sử dụng thông tin cổng cùng địa chỉ để phân biệt luồng.
- Không. Chuyển đổi địa chỉ khác với chính sách lọc truy cập.
- Liên kết và khả năng cấp cấu hình DHCP. Link-local không chứng minh đã nhận được cấu hình ra Internet.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
