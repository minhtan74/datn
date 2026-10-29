## Mục tiêu
Giải thích phân đoạn LAN bằng VLAN và lựa chọn cấu hình Wi-Fi cơ bản.

## Kiến thức trọng tâm
VLAN chia hạ tầng switch thành các miền broadcast logic. Hai cổng access thuộc hai VLAN khác nhau không tự trao đổi như cùng một LAN chỉ vì nối chung switch. Muốn liên lạc giữa VLAN thường cần định tuyến và chính sách cho phép. Trunk có thể mang nhiều VLAN với cơ chế gắn thẻ như IEEE 802.1Q.

Wi-Fi là kết nối vô tuyến qua điểm truy cập. SSID là tên mạng được công bố, không phải mật khẩu. Nhiễu, vật cản, số thiết bị và vị trí AP đều ảnh hưởng chất lượng. Băng 5 GHz thường có nhiều lựa chọn kênh hơn 2,4 GHz nhưng không bảo đảm xuyên vật cản tốt hơn.

Dùng cơ chế bảo vệ được thiết bị hỗ trợ như WPA2 hoặc WPA3, mật khẩu riêng đủ mạnh và firmware được cập nhật. Không coi ẩn SSID là thay thế mã hóa. VLAN là phân đoạn logic, không tự mã hóa nội dung; quyền truy cập giữa các vùng vẫn cần được thiết kế.

## Ví dụ có hướng dẫn
Phòng thực hành chia VLAN 10 cho học viên, VLAN 20 cho giảng viên. Một trunk nối hai switch mang cả hai VLAN. SSID Guest có thể gắn vào một vùng riêng với chính sách hạn chế truy cập nội bộ.

## Bài tập thực hành
Vẽ sơ đồ hai nhóm người dùng trên hai switch. Chỉ ra cổng access, trunk, thiết bị định tuyến và chính sách cần kiểm tra khi mạng khách không được truy cập máy chủ nội bộ.

## Gợi ý tự kiểm tra
Cùng VLAN có thể trải trên nhiều switch qua trunk. Khác VLAN cần đường định tuyến phù hợp; đặt tên SSID khác nhau chưa tự chứng minh đã cách ly mạng.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP