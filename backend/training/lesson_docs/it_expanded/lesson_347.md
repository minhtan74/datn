## Mục tiêu
Theo dõi việc gửi một gói IPv4 trong LAN; phân biệt địa chỉ IP với MAC.

## Kiến thức trọng tâm
Ethernet truyền khung giữa các giao diện trong một mạng cục bộ. Khung có địa chỉ MAC nguồn và đích; gói IP nằm trong phần tải của khung. Switch học MAC nguồn và cổng nhận, sau đó dùng bảng MAC để quyết định cổng chuyển tiếp. Không nên nhầm bảng MAC với bảng định tuyến.

ARP giúp tìm địa chỉ MAC tương ứng một IPv4 trên liên kết cục bộ. Host phát ARP request dạng broadcast, thiết bị sở hữu IPv4 trả lời. Kết quả có thể được lưu tạm trong ARP cache. IPv6 dùng Neighbor Discovery thay cho ARP.

Nếu đích nằm ngoài mạng con, host tìm MAC của gateway, không ARP trực tiếp địa chỉ máy chủ xa. Khi qua router, khung lớp liên kết được tạo lại cho chặng tiếp theo; địa chỉ MAC không đi xuyên suốt Internet. Chỉ quan sát ARP trong mạng lab hoặc mạng bạn được phép quản lý.

## Ví dụ có hướng dẫn
A có IP 192.168.10.2/24, B có IP 192.168.10.3/24. A chưa biết MAC của B nên gửi ARP request. Khi gửi tới 8.8.8.8, A sử dụng MAC của default gateway trong khung Ethernet.

## Bài tập thực hành
Vẽ khung và gói khi A gửi tới B, rồi tới máy chủ ngoài LAN. Ghi MAC đích của khung trong từng trường hợp. Quan sát bảng ARP bằng arp -a trong máy lab.

## Gợi ý tự kiểm tra
Cùng mạng: MAC của B. Ngoài mạng: MAC gateway. Không kết luận rằng địa chỉ IP và MAC là hai cách viết của cùng một định danh.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP