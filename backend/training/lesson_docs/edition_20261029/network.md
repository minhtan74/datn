# Mạng máy tính — lab có phạm vi và chẩn đoán theo lớp

Chỉ kiểm tra thiết bị/mạng mình được phép sử dụng. Ghi sơ đồ, địa chỉ, thời điểm và kết quả; không quét mạng công cộng hoặc chia sẻ mật khẩu Wi-Fi. Ví dụ địa chỉ riêng phục vụ lab, không giả định cấu hình mạng thật của người học.

## Mô hình TCP/IP và thiết bị mạng
**Tình huống:** mở web lỗi nhưng chưa rõ mạng hay server. Tách đường đi ứng dụng → truyền tải → IP → liên kết. Switch thường chuyển frame trong mạng LAN; router chuyển gói giữa các mạng theo bảng định tuyến. Thiết bị thật có thể tích hợp nhiều vai trò.

**Tự luyện:** vẽ laptop → Wi-Fi/AP → router → Internet → server. **Hướng giải:** ghi việc nào thuộc phân giải tên, thiết lập kết nối và gửi HTTP; không gọi mọi lỗi web là lỗi TCP hoặc Wi-Fi. Kiểm tra giả thuyết từng bước, không thay đồng thời mọi cấu hình.

## Địa chỉ IPv4 và mạng con
**Tình huống:** hai máy cùng Wi-Fi nhưng không cùng mạng logic như dự đoán. Địa chỉ IP phải xét cùng prefix/mask và gateway; chỉ nhìn ba nhóm số đầu là không đủ trong mọi subnet.
```python
import ipaddress
network = ipaddress.ip_network("192.168.10.0/24")
assert ipaddress.ip_address("192.168.10.15") in network
assert ipaddress.ip_address("192.168.11.15") not in network
```
**Tự luyện:** chia /24 thành hai /25 bằng công cụ và vẽ dải địa chỉ. **Hướng giải:** một /25 có 128 địa chỉ tổng; số host thường dùng trong bài IPv4 thông thường cần trừ network/broadcast, không áp quy tắc đó máy móc cho mọi prefix đặc biệt.

## DNS và phân giải tên miền
**Tình huống:** vào được một dịch vụ bằng IP nhưng không bằng tên. Có thể DNS sai, nhưng HTTPS theo IP còn có vấn đề chứng chỉ/virtual host nên không kết luận chỉ từ một thao tác trình duyệt.

**Tự luyện:** dùng công cụ phân giải tên của hệ điều hành, ghi resolver, loại record và kết quả. **Hướng giải:** so tên gõ đúng, cache và record cần dùng; TTL không hứa mọi máy cập nhật ngay cùng thời điểm. Không thay DNS công cộng tùy tiện trong mạng doanh nghiệp có tên nội bộ.

## HTTP và HTTPS
**Tình huống:** nhận 401, 403, 404 hoặc 500. Đây là phản hồi tầng ứng dụng, khác mất kết nối. HTTPS bảo vệ kênh bằng TLS và xác thực danh tính theo chứng chỉ; không chứng minh ứng dụng không có lỗi phân quyền.

**Tự luyện:** đọc method, URL, status và content-type trong Network trên lab. **Hướng giải:** 200 có body lỗi nghiệp vụ vẫn cần kiểm tra hợp đồng API; không chỉ căn mã HTTP để kết luận đúng nội dung. Không đưa token/cookie vào ảnh báo cáo chia sẻ.

## Ethernet, địa chỉ MAC và ARP
**Tình huống:** nhầm MAC với địa chỉ dùng định tuyến toàn Internet. Frame mang địa chỉ lớp liên kết; IP phục vụ định tuyến. ARP trong IPv4 giúp tìm địa chỉ liên kết cho next hop trong miền liên kết tương ứng.

**Tự luyện:** xem bảng ARP/neighbor trên lab và phân biệt MAC gateway với IP server ngoài mạng. **Hướng giải:** gửi ra Internet thường cần frame tới gateway, không phải biết MAC của server ở xa. Không dùng việc nhìn thấy một MAC làm bằng chứng chắc chắn về danh tính một người dùng.

## VLAN và kết nối Wi-Fi
**Tình huống:** Wi-Fi có sóng không đồng nghĩa đã có Internet. Cần xét liên kết, cấp IP, gateway, DNS và chính sách truy cập. VLAN chia miền quảng bá logic; giao tiếp giữa VLAN cần định tuyến và chính sách phù hợp.

**Tự luyện:** thiết kế mạng học viên và mạng quản trị tách biệt trên sơ đồ lab. **Hướng giải:** ghi rõ luồng nào được phép qua; không coi ẩn SSID hoặc VLAN tự thân thay thế mã hóa, xác thực và firewall. Đo nhiều vị trí/thời điểm trước khi kết luận AP hỏng.

## DHCP và NAT trong mạng gia đình
**Tình huống:** máy có địa chỉ nhưng không đúng dải cấu hình. DHCP cấp thông số theo lease; cấu hình tĩnh sai hoặc trùng IP có thể gây lỗi. NAT dịch địa chỉ/port theo trạng thái triển khai, không thay thế kiểm soát truy cập toàn diện.

**Tự luyện:** mô tả địa chỉ riêng laptop và địa chỉ công cộng quan sát được từ dịch vụ lab. **Hướng giải:** ghi rõ điểm quan sát; port forwarding mở thêm đường vào mạng và chỉ nên cấu hình cho lab đã xác định. Không công khai dịch vụ quản trị chỉ để “thử cho nhanh”.

## Định tuyến cơ bản và làm quen IPv6
**Tình huống:** gói đi được trong LAN nhưng không tới mạng khác. Xem route đích, route mặc định và đường về; không chỉ nhìn gateway của máy gửi. Router chọn route theo prefix phù hợp trong mô hình cơ bản.

**Tự luyện:** vẽ hai LAN qua router và thêm route hai chiều. **Hướng giải:** phản hồi cần đường về; tường lửa cũng có thể chặn. IPv6 có địa chỉ 128 bit và cơ chế neighbor discovery; không chép nguyên mọi quy tắc ARP/broadcast của IPv4 sang IPv6.

## Cổng, socket và vòng đời kết nối TCP
**Tình huống:** server chạy nhưng client báo connection refused. Kiểm tra tiến trình có listen đúng địa chỉ và port không; bind loopback khác với bind cho truy cập từ mạng. Timeout và refused không phải cùng một lỗi.

**Tự luyện:** khởi động một server lab rồi dừng, so kết quả kết nối. **Hướng giải:** TCP cung cấp luồng byte, không giữ ranh giới thông điệp ứng dụng; cần giao thức đóng khung hoặc độ dài. Không giả định một lần send tương ứng một lần recv hoặc kết nối mở là nghiệp vụ đã hoàn thành.

## Tường lửa và phân vùng truy cập
**Tình huống:** muốn chỉ học viên truy cập web, không truy cập database. Xác định nguồn, đích, port và chiều kết nối; cho phép đúng luồng cần dùng. Backend truy cập DB theo quyền riêng, không mở DB cho mọi client.

**Tự luyện:** viết ma trận luồng học viên→web, web→API, API→DB. **Hướng giải:** kiểm tra cả luồng hợp lệ và luồng bị cấm trong lab. Không tắt toàn bộ firewall rồi coi lỗi đã được sửa; chính sách cần lưu và có cách hoàn tác.

## Chẩn đoán lỗi mạng theo từng lớp
**Quy trình thực hành:** ghi triệu chứng → kiểm tra liên kết → địa chỉ/gateway → phân giải tên → cổng dịch vụ → HTTP/ứng dụng. Mỗi bước ghi lệnh, thời điểm và đầu ra, không chỉ ảnh “đã kết nối”.

**Tự luyện:** chọn một lỗi lab: sai hostname hoặc sai port. **Hướng giải:** thay đúng một biến để kiểm chứng giả thuyết. Ping thất bại có thể do ICMP bị chặn; ping thành công không chứng minh HTTP hoạt động. Câu “máy em không vào mạng” cần thêm thiết bị, mạng, dịch vụ và lỗi cụ thể.

## Dự án nhỏ: thiết kế mạng cho phòng học
**Bài thực hành:** sơ đồ phòng 20 máy, vùng giảng viên, khách và thiết bị quản trị; kế hoạch địa chỉ, Wi-Fi, dịch vụ và phân vùng. Ghi rõ đây là thiết kế lab, chưa phải chứng nhận triển khai.

**Tự luyện:** lập 8 phép thử gồm cấp IP, DNS, truy cập web, chặn DB, mất AP và đường về. **Hướng giải:** mỗi phép thử có điều kiện đầu, luồng, tiêu chí và kết quả. Ước lượng băng thông dựa tải sử dụng và đo kiểm, không chỉ cộng tốc độ danh nghĩa của các card mạng.

# Tài liệu tham khảo
https://www.rfc-editor.org/rfc/rfc9293.html
