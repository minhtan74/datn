## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 3: Ethernet và mạng cục bộ.
- Các bài trong chương: Ethernet, địa chỉ MAC và ARP; VLAN và kết nối Wi-Fi.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Theo dõi việc gửi một gói IPv4 trong LAN; phân biệt địa chỉ IP với MAC.

## Kiến thức nền
Ethernet truyền khung giữa các giao diện trong một mạng cục bộ. Khung có địa chỉ MAC nguồn và đích; gói IP nằm trong phần tải của khung. Switch học MAC nguồn và cổng nhận, sau đó dùng bảng MAC để quyết định cổng chuyển tiếp. Không nên nhầm bảng MAC với bảng định tuyến.

ARP giúp tìm địa chỉ MAC tương ứng một IPv4 trên liên kết cục bộ. Host phát ARP request dạng broadcast, thiết bị sở hữu IPv4 trả lời. Kết quả có thể được lưu tạm trong ARP cache. IPv6 dùng Neighbor Discovery thay cho ARP.

Nếu đích nằm ngoài mạng con, host tìm MAC của gateway, không ARP trực tiếp địa chỉ máy chủ xa. Khi qua router, khung lớp liên kết được tạo lại cho chặng tiếp theo; địa chỉ MAC không đi xuyên suốt Internet. Chỉ quan sát ARP trong mạng lab hoặc mạng bạn được phép quản lý.

## 1. Khung Ethernet và phạm vi địa chỉ
Khung mang MAC nguồn/đích và trường nhận diện giao thức tải. MAC thường là định danh 48 bit của giao diện trong mô hình Ethernet thông dụng, nhưng không được dùng như danh tính xác thực con người. Switch có thể flood broadcast hoặc unknown unicast trong miền VLAN thích hợp.

## 2. Dựng bảng chuyển tiếp bằng ví dụ
Ban đầu switch chưa có bảng. Khung từ A vào cổng 1 làm switch học MAC_A→1. Khi B gửi từ cổng 2, switch học MAC_B→2. Sau khi biết đích B ở cổng 2, unicast A→B có thể được chuyển riêng tới cổng đó. Bảng có thời gian lão hóa và thay đổi theo hoạt động thực tế.

## 3. Truy vết ARP cùng mạng và khác mạng
Với A=192.168.1.10/24, B=.20 và gateway=.1, gửi tới B cần MAC_B; gửi tới máy chủ ở mạng khác cần MAC_gateway. Máy gửi dùng mask và bảng route để quyết định next hop trước khi cần MAC. ARP cache chưa có không có nghĩa DNS không hoạt động: đây là hai bảng và hai vai trò khác nhau.
```text
Đích IP         Next hop IP       MAC cần tra
192.168.1.20    192.168.1.20       MAC của B
203.0.113.10    192.168.1.1        MAC gateway
```

## 4. Bài tập kiểm tra hiểu biết
Xóa ARP cache có làm thay đổi IP của máy không? Không: đó là xóa ánh xạ tạm, máy có thể phân giải lại. Thay gateway có thể làm thay đổi next hop nên khung đầu tiên dùng MAC khác.
Trong sơ đồ hai LAN qua router, hãy ghi MAC nguồn/đích từng chặng và IP nguồn/đích. Nếu có NAT, phân tích thêm nơi IP có thể được chuyển đổi; không áp dụng nhận xét giữ IP khi thiết kế đã có NAT. Chỉ quan sát lưu lượng lab được cho phép.

## Bài tập vận dụng bổ sung
Vẽ khung và gói khi A gửi tới B, rồi tới máy chủ ngoài LAN. Ghi MAC đích của khung trong từng trường hợp. Quan sát bảng ARP bằng arp -a trong máy lab.

## Hướng giải bài tập bổ sung
Cùng mạng: MAC của B. Ngoài mạng: MAC gateway. Không kết luận rằng địa chỉ IP và MAC là hai cách viết của cùng một định danh.

## Câu hỏi tự kiểm tra
1. ARP dùng trong tình huống nào?
2. Host gửi gói tới mạng khác thường dùng MAC đích nào trong khung đầu tiên?
3. Switch lớp 2 học bảng MAC từ đâu?
4. IPv6 sử dụng cơ chế nào thay ARP?
5. Khi gói qua router, điều gì thường xảy ra với khung lớp liên kết?

## Gợi ý đáp án và điểm cần nhớ
- Tìm MAC ứng với IPv4 trên liên kết cục bộ. ARP ánh xạ IPv4 sang MAC trong LAN.
- MAC của gateway. Gateway là chặng tiếp theo trên liên kết cục bộ.
- MAC nguồn và cổng nhận khung. Switch học địa chỉ nguồn tại cổng nhận.
- Neighbor Discovery. IPv6 dùng Neighbor Discovery dựa trên ICMPv6.
- Được tạo lại cho liên kết tiếp theo. Router chuyển tiếp gói trong một khung phù hợp liên kết mới.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
