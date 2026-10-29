## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 3: Ethernet và mạng cục bộ.
- Các bài trong chương: Ethernet, địa chỉ MAC và ARP; VLAN và kết nối Wi-Fi.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Giải thích phân đoạn LAN bằng VLAN và lựa chọn cấu hình Wi-Fi cơ bản.

## Kiến thức nền
VLAN chia hạ tầng switch thành các miền broadcast logic. Hai cổng access thuộc hai VLAN khác nhau không tự trao đổi như cùng một LAN chỉ vì nối chung switch. Muốn liên lạc giữa VLAN thường cần định tuyến và chính sách cho phép. Trunk có thể mang nhiều VLAN với cơ chế gắn thẻ như IEEE 802.1Q.

Wi-Fi là kết nối vô tuyến qua điểm truy cập. SSID là tên mạng được công bố, không phải mật khẩu. Nhiễu, vật cản, số thiết bị và vị trí AP đều ảnh hưởng chất lượng. Băng 5 GHz thường có nhiều lựa chọn kênh hơn 2,4 GHz nhưng không bảo đảm xuyên vật cản tốt hơn.

Dùng cơ chế bảo vệ được thiết bị hỗ trợ như WPA2 hoặc WPA3, mật khẩu riêng đủ mạnh và firmware được cập nhật. Không coi ẩn SSID là thay thế mã hóa. VLAN là phân đoạn logic, không tự mã hóa nội dung; quyền truy cập giữa các vùng vẫn cần được thiết kế.

## 1. Phân biệt access, trunk và inter-VLAN routing
Access port phục vụ thiết bị cuối trong một VLAN theo cấu hình. Trunk mang nhiều VLAN qua liên kết giữa các thiết bị hỗ trợ. Một VLAN ID giống nhau trên hai switch chưa đủ bảo đảm thông nếu trunk không mang VLAN đó hoặc đường nối bị lỗi. Tra cứu cấu hình và trạng thái trước khi thay đổi.
Định tuyến giữa VLAN có thể dùng router hoặc switch lớp 3. Cần địa chỉ gateway cho từng mạng con và chính sách cho phép các luồng mong muốn. VLAN 10 và VLAN 20 không tự trở thành một mạng chỉ vì đặt cùng subnet IP; cách cấu hình chồng lấn này còn gây khó chẩn đoán.

## 2. Thiết kế Wi-Fi theo nhu cầu
Khảo sát vùng phủ, số người đồng thời, vật cản và nhiễu. Dải 2,4 GHz và 5 GHz có đặc điểm truyền khác nhau; tốc độ công bố không phải tốc độ thực của mọi người dùng. Nhiều client chia sẻ môi trường vô tuyến. Kết nối Wi-Fi mạnh không chứng minh đường Internet hoặc DNS tốt.

## 3. Ví dụ tách mạng khách
```text
SSID Student -> VLAN 10 -> DHCP pool Student -> Internet, máy chủ học tập
SSID Guest   -> VLAN 20 -> DHCP pool Guest   -> chỉ Internet theo chính sách
```
SSID là nhãn, VLAN là phân đoạn, DHCP là cấu hình, firewall là quyền truy cập. Cần kiểm tra tất cả các thành phần thay vì đồng nhất chúng.

## 4. Bài thực hành có tiêu chí
Thiết kế hai SSID cho 20 học viên và nhóm khách. Nộp ánh xạ SSID/VLAN/subnet, vị trí AP dự kiến, luồng được phép và cách kiểm tra. Đáp án chấp nhận phải có dải không chồng lấn, đúng gateway, nhận DHCP và xác nhận Guest không mở được vùng quản trị. Không công bố mật khẩu trong báo cáo. Đổi một tham số mỗi lần và lưu bản cấu hình lab trước khi thử.

## Bài tập vận dụng bổ sung
Vẽ sơ đồ hai nhóm người dùng trên hai switch. Chỉ ra cổng access, trunk, thiết bị định tuyến và chính sách cần kiểm tra khi mạng khách không được truy cập máy chủ nội bộ.

## Hướng giải bài tập bổ sung
Cùng VLAN có thể trải trên nhiều switch qua trunk. Khác VLAN cần đường định tuyến phù hợp; đặt tên SSID khác nhau chưa tự chứng minh đã cách ly mạng.

## Câu hỏi tự kiểm tra
1. VLAN chủ yếu dùng để làm gì?
2. Cổng trunk thường có nhiệm vụ gì?
3. SSID là gì?
4. Hai VLAN khác nhau thường cần gì để trao đổi IP?
5. Ẩn SSID có thay thế mã hóa Wi-Fi không?

## Gợi ý đáp án và điểm cần nhớ
- Chia miền broadcast logic. VLAN phân đoạn lớp liên kết thành các miền logic.
- Mang lưu lượng nhiều VLAN. Trunk cho phép nhiều VLAN dùng chung liên kết.
- Tên mạng Wi-Fi. SSID nhận diện mạng không dây.
- Định tuyến giữa VLAN và chính sách cho phép. Phân đoạn VLAN cần lớp định tuyến để trao đổi giữa các mạng.
- Không. Ẩn tên mạng không cung cấp bảo đảm mã hóa.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
