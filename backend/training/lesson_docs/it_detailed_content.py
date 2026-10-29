"""Lesson-specific original worked material for the new IT course PDFs.

The short descriptions remain intact; these additions supply worked procedures,
examples, implementation notes and exercises, not repeated page-filling text.
"""

DETAILS = {
'Mô hình TCP/IP và thiết bị mạng': '''## 1. Từ yêu cầu người dùng đến dữ liệu trên đường truyền
Giả sử học viên mở trang khóa học. Ứng dụng tạo yêu cầu HTTP; giao vận quản lý trao đổi giữa các tiến trình; tầng Internet xử lý địa chỉ và đường đi; tầng truy nhập mạng chuyển khung trên liên kết hiện tại. Khi nhận, máy đích xử lý theo chiều ngược lại. Đây là cách nhìn theo chức năng, không phải mỗi tầng luôn tương ứng một thiết bị riêng.
- Tầng ứng dụng: nội dung và quy tắc trao đổi của dịch vụ, ví dụ HTTP, DNS.
- Tầng giao vận: endpoint ứng dụng và cơ chế vận chuyển, ví dụ TCP, UDP.
- Tầng Internet: gói IP, địa chỉ nguồn/đích và chuyển tiếp qua mạng.
- Tầng truy nhập: khung Ethernet hoặc kết nối vô tuyến của chặng hiện tại.

## 2. Chọn thiết bị theo vai trò
Một switch lớp 2 chuyển khung trong LAN, router nối các mạng IP, AP cung cấp truy nhập Wi-Fi. Thiết bị tích hợp ở nhà có thể làm cả router, switch, AP, DHCP và NAT. Hãy gọi tên chức năng đang xét thay vì suy luận mọi hộp có anten đều chỉ là AP.

## 3. Truy vết có hướng dẫn
1. Máy học viên biết địa chỉ IP của máy chủ qua DNS hoặc bộ đệm.
2. Máy xác định đích cùng mạng hay cần gửi qua gateway.
3. Giao vận và IP đóng gói dữ liệu; liên kết tạo khung cho chặng kế tiếp.
4. Router kiểm tra địa chỉ đích, chuyển gói bằng liên kết thích hợp.
5. Máy chủ đưa dữ liệu lên ứng dụng và tạo phản hồi.
Không có yêu cầu rằng gói đi và gói về phải qua cùng một dãy router.

## 4. Bài tập phân tích và lời giải
Một máy vẫn liên lạc được máy in nội bộ nhưng không ra Internet. Có thể bỏ qua mọi lỗi LAN không? Không: kết quả chỉ chứng minh đường tới máy in hoạt động. Tiếp tục kiểm tra gateway, route, DNS và dịch vụ đích. Không thay ngay switch chỉ vì website không mở.
Hãy vẽ hai host, switch, router và server; ghi địa chỉ IP, MAC và cổng ở nơi chúng có ý nghĩa. Đạt yêu cầu khi giải thích được khác nhau giữa chuyển khung trong LAN và định tuyến IP.''',
'Địa chỉ IPv4 và mạng con': '''## 1. Đọc địa chỉ và tính phần mạng
Mỗi octet của IPv4 biểu diễn 8 bit. Ví dụ 192 = 128+64 nên ở dạng nhị phân là 11000000. Subnet mask có các bit mạng là 1, phần host là 0; phép AND giữa địa chỉ và mask cho địa chỉ mạng. Ký hiệu CIDR /p là số bit mạng, không phải số host.

## 2. Ví dụ chia /24 thành /26
Mạng 192.168.10.0/24 chia thành bốn mạng /26. Mỗi mạng có 64 địa chỉ vì còn 6 bit host. Các địa chỉ mạng là .0, .64, .128 và .192. Với mạng con thông thường, bỏ địa chỉ mạng và broadcast còn 62 host dùng được.
Với host 192.168.10.70/26: 70 thuộc khối 64–127; mạng là 192.168.10.64, broadcast .127, dải host .65–.126. Gateway có thể là một địa chỉ host được chọn trong dải; không bắt buộc phải .1 trên mọi mạng.
```text
Mạng /26       Host đầu      Host cuối     Broadcast
.0             .1            .62           .63
.64            .65           .126          .127
.128           .129          .190          .191
.192           .193          .254          .255
```

## 3. Quy trình tự giải bài subnet
1. Xác định số bit host bằng 32 trừ độ dài tiền tố.
2. Tính kích thước khối và tìm mạng chứa địa chỉ.
3. Xác định broadcast và dải host theo loại mạng con.
4. Kiểm tra hai host có cùng network ID với mask của chúng hay không.
5. Kiểm tra gateway có truy cập trực tiếp trên liên kết phù hợp không.
Quy tắc trừ hai địa chỉ không dùng máy móc cho /31 điểm-điểm hoặc /32.

## 4. Bài tập có đáp án
Host 10.1.2.140/27 thuộc khối nào? /27 còn 5 bit host, khối 32 địa chỉ. 140 thuộc 128–159: mạng .128, broadcast .159, host .129–.158. Hai host .140/27 và .170/27 khác mạng.
Thiết kế mạng cho 25 máy và một gateway: /27 có 30 host thông thường nên đủ nếu không có thêm nhu cầu vượt số còn lại. Ghi rõ dự phòng và địa chỉ dành riêng thay vì chỉ nêu tiền tố.''',
'DNS và phân giải tên miền': '''## 1. Các thành phần tham gia
Stub resolver trên máy người dùng gửi câu hỏi tới recursive resolver đã cấu hình. Khi chưa có đáp án trong cache, resolver có thể lần theo root, máy chủ miền cấp cao và máy chủ có thẩm quyền. Root thường chỉ dẫn bước tiếp theo, không phải nơi lưu mọi địa chỉ website.

## 2. Đọc bản ghi đúng ý nghĩa
- A: địa chỉ IPv4; AAAA: địa chỉ IPv6.
- CNAME: bí danh tới một tên khác; cần phân giải tiếp tên đích.
- MX: máy chủ nhận thư và giá trị ưu tiên trong miền.
- TXT: văn bản cho các mục đích xác minh hoặc chính sách ứng dụng.
- TTL: thời gian cache theo bản ghi, không phải thời hạn sở hữu miền.
Một tên có thể có nhiều bản ghi và nhiều địa chỉ. Ứng dụng không nên giả định một tên mãi mãi chỉ có một IP.

## 3. Thực hành đọc kết quả
```text
nslookup example.com
nslookup -type=AAAA example.com
nslookup -type=MX example.com
```
Các lệnh trên chỉ truy vấn DNS thông thường; đầu ra phụ thuộc thời điểm và resolver. Ghi lại tên truy vấn, resolver sử dụng, loại bản ghi và kết quả thay vì chép một IP cố định làm đáp án cho mọi lần học.

## 4. Tình huống chẩn đoán
Sau khi đổi A record, máy A thấy IP mới còn máy B thấy IP cũ. Cache và TTL là giả thuyết hợp lý. Cần xác định resolver của hai máy, thời điểm cập nhật và bản ghi có thẩm quyền; không kết luận ngay DNS server bị hỏng. NXDOMAIN khác timeout: một bên là phản hồi tên không tồn tại, bên kia chưa nhận được phản hồi trong thời hạn.

## 5. Bài tập và lời giải
Một host phân giải đúng tên nhưng nhận HTTP 500. DNS có chứng minh website tốt không? Không: bước tên miền đã hoàn tất nhưng server ứng dụng còn lỗi. Một CNAME trỏ tới tên không có bản ghi địa chỉ cần kiểm tra chuỗi phân giải. Hãy nộp bảng ba ca: thành công, tên không tồn tại, timeout, với bằng chứng phân biệt từng ca.''',
'HTTP và HTTPS': '''## 1. Cấu trúc trao đổi
Trong cách biểu diễn HTTP/1.1 để dễ học, request gồm dòng yêu cầu, header, dòng trống và body tùy phương thức. Response gồm dòng trạng thái, header và body nếu có. Các phiên bản HTTP khác có biểu diễn khung khác; mô hình request/response vẫn hữu ích.
```text
GET /courses/513 HTTP/1.1
Host: example.com
Accept: application/json

HTTP/1.1 200 OK
Content-Type: application/json

{"id": 513, "title": "Mạng máy tính cơ bản"}
```

## 2. Phương thức và trạng thái
GET thường lấy biểu diễn; POST thường yêu cầu xử lý dữ liệu; PUT thay thế biểu diễn tại tài nguyên theo hợp đồng; PATCH cập nhật một phần; DELETE yêu cầu xóa. Không đánh giá nghiệp vụ chỉ từ tên phương thức. Phương thức và endpoint phải được kiểm tra cùng quyền và đầu vào.
200 thường thành công có nội dung; 201 thường tài nguyên đã được tạo; 204 không có body; 400 yêu cầu không hợp lệ; 401 cần xác thực; 403 bị từ chối quyền; 404 không tìm thấy; 500 lỗi nội bộ. Ứng dụng cần hợp đồng cụ thể, không được tùy ý đổi mọi lỗi thành 200.

## 3. HTTPS bảo vệ những gì
TLS hỗ trợ bí mật đường truyền, toàn vẹn và xác thực máy chủ khi chứng thư được kiểm tra đúng. TLS không sửa lỗi phân quyền, không xác thực tính đúng đắn của nội dung bài học. Không đưa mật khẩu hay token vào URL vì có thể bị lưu trong lịch sử hoặc log.

## 4. Thực hành và lời giải
Quan sát tab Network của trình duyệt khi mở trang khóa học: ghi phương thức, URL, mã trạng thái, Content-Type và thời gian. Không chia sẻ header Authorization. Nếu HTML được trả khi client chờ JSON, cần kiểm tra tuyến, proxy hoặc lỗi server thay vì chỉ thử parse lại.
Với 404 kiểm tra tài nguyên và đường dẫn; với 500 thu thập mã yêu cầu và log server đã được phép xem. Cùng nhìn thấy màn hình trống không có nghĩa hai nguyên nhân giống nhau.''',
'Ethernet, địa chỉ MAC và ARP': '''## 1. Khung Ethernet và phạm vi địa chỉ
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
Trong sơ đồ hai LAN qua router, hãy ghi MAC nguồn/đích từng chặng và IP nguồn/đích. Nếu có NAT, phân tích thêm nơi IP có thể được chuyển đổi; không áp dụng nhận xét giữ IP khi thiết kế đã có NAT. Chỉ quan sát lưu lượng lab được cho phép.''',
'VLAN và kết nối Wi-Fi': '''## 1. Phân biệt access, trunk và inter-VLAN routing
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
Thiết kế hai SSID cho 20 học viên và nhóm khách. Nộp ánh xạ SSID/VLAN/subnet, vị trí AP dự kiến, luồng được phép và cách kiểm tra. Đáp án chấp nhận phải có dải không chồng lấn, đúng gateway, nhận DHCP và xác nhận Guest không mở được vùng quản trị. Không công bố mật khẩu trong báo cáo. Đổi một tham số mỗi lần và lưu bản cấu hình lab trước khi thử.''',
'DHCP và NAT trong mạng gia đình': '''## 1. Vòng đời thuê địa chỉ
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
Một /24 có gateway .1, máy chủ .10–.20 và DHCP .10–.200. Chỉ ra xung đột thiết kế rồi đề xuất pool .50–.200 hoặc cơ chế loại trừ tương ứng. NAT có tạo quyền truy cập vào ứng dụng không? Không: vẫn cần xác thực và phân quyền. Nộp bảng cấu hình, bằng chứng cấp mới và phân tích đường về của một phiên PAT.''',
'Định tuyến cơ bản và làm quen IPv6': '''## 1. Thực hành longest-prefix match
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
Chọn tuyến cho bốn đích từ bảng; ghi tiền tố khớp và lý do bỏ các tuyến còn lại. Giải thích vì sao 2001:db8::1::2 không hợp lệ: hai dấu rút gọn khiến không xác định được số nhóm 0 ở mỗi vị trí. Với host dual stack, lập checklist IPv4 và IPv6 riêng thay vì kết luận chỉ từ một lệnh ping.''',
'Cổng, socket và vòng đời kết nối TCP': '''## 1. Nhận diện phiên trao đổi
Endpoint giao vận gồm địa chỉ và cổng trong ngữ cảnh giao thức. Hai kết nối tới cùng web server được phân biệt bằng các endpoint nguồn/đích. Cổng 443 là quy ước phổ biến cho HTTPS, không phải bằng chứng tự thân về TLS; kiểm tra giao thức thực tế và cấu hình dịch vụ.

## 2. Trình tự mở và đóng
Client gửi SYN với số thứ tự ban đầu; server phản hồi SYN-ACK; client ACK. Mỗi bên quản lý số thứ tự và xác nhận. Mất gói có thể dẫn tới truyền lại; dữ liệu nhận có thể được sắp lại trước khi ứng dụng đọc. Đóng có trật tự có thể trao đổi FIN/ACK, còn RST biểu thị kết thúc đột ngột trong những tình huống thích hợp.

## 3. Bài toán ranh giới thông điệp
```text
Ứng dụng gửi hai lần: "HELLO" rồi "WORLD"
Ứng dụng nhận có thể đọc: "HEL" và "LOWORLD"
Hoặc đọc một lần: "HELLOWORLD"
```
Không coi mỗi recv tương ứng đúng một send. Một giao thức ứng dụng có thể dùng độ dài đầu thông điệp hoặc dấu phân cách có quy tắc escape. Cần xử lý đọc thiếu, hết kết nối và timeout.

## 4. Lập luận xử lý lỗi
Connection refused có thể do không có listener hoặc thiết bị chủ động từ chối. Timeout có nhiều nguyên nhân như mất gói, lọc hoặc đường đi lỗi. Cả hai khác lỗi xác thực HTTP sau khi kết nối đã mở.
Tự luyện: vẽ hai client cùng dùng nguồn 51000 nhưng IP khác, kết nối server:443; chỉ ra vì sao không trùng phiên. Nộp thiết kế tách thông điệp dạng độ dài và ví dụ nhận thành ba mảnh. Đáp án cần giữ bộ đệm tới khi đủ độ dài, không parse ngay mảnh đầu.''',
'Tường lửa và phân vùng truy cập': '''## 1. Chuyển yêu cầu thành chính sách
Lập danh sách tài sản, vùng, người dùng và luồng nghiệp vụ trước. Mỗi quy tắc cần nguồn, đích, giao thức, cổng hoặc dịch vụ, hành động và lý do. Thứ tự xử lý và mặc định phụ thuộc nền tảng; phải hiểu cơ chế đang dùng thay vì chép cấu hình từ thiết bị khác.

## 2. Ví dụ ma trận truy cập
```text
Nguồn       Đích                 Nhu cầu              Quyết định
Student     LMS                  HTTPS                Cho phép
Guest       Vùng quản trị        Mọi dịch vụ           Từ chối
Admin       Máy lab quản trị     Kênh quản trị chọn    Cho phép có giới hạn
Student     DNS resolver nội bộ  DNS                  Theo thiết kế
```
Ma trận là mô hình lab. Không mặc định nó đã bao phủ mọi lưu lượng cần cho một hệ thống thật. Nêu DNS, đồng bộ giờ và các phụ thuộc nếu ứng dụng yêu cầu.

## 3. Thực thi và kiểm chứng
Sao lưu cấu hình; có đường khôi phục; áp dụng thay đổi nhỏ; kiểm tra luồng được phép và luồng bị cấm; so sánh log với nguồn/đích thực tế. Lọc theo hướng sai hoặc gắn sai interface có thể khiến quy tắc đúng trên giấy nhưng không có hiệu lực.
Stateful firewall theo dõi phiên để xử lý lưu lượng liên quan, nhưng không tự hiểu đúng mọi yêu cầu nghiệp vụ. WAF, firewall mạng và phân quyền ứng dụng giải quyết các phạm vi khác nhau.

## 4. Bài tập có tiêu chí chấm
Viết sáu quy tắc cho mạng lớp học và giải thích từng quy tắc. Chọn một thay đổi có thể khóa quản trị từ xa, mô tả cách hoàn nguyên không phụ thuộc phiên đang bị ảnh hưởng. Đáp án đạt cần tối thiểu quyền, không để mật khẩu trong log và có ca thử âm; chỉ nói ping được chưa đủ.''',
'Chẩn đoán lỗi mạng theo từng lớp': '''## 1. Quy trình thu thập bằng chứng
Tạo hồ sơ sự cố gồm thời điểm, phạm vi, thông báo, trạng thái trước đó và thay đổi gần nhất. Nếu nhiều máy cùng lỗi, so sánh điểm chung; nếu một máy lỗi, so sánh với máy tốt cùng mạng nhưng không tự sao chép IP của máy tốt.

## 2. Checklist có thứ tự
1. Liên kết: cáp, Wi-Fi, interface đang bật và trạng thái kết nối.
2. Địa chỉ: IP/mask, gateway, DNS; tìm dấu hiệu tự gán hoặc xung đột.
3. Đường đi: route tới đích, gateway và chính sách liên quan.
4. Tên miền: resolver, kết quả A/AAAA, cache và TTL.
5. Dịch vụ: cổng, TLS, mã HTTP và nội dung phản hồi.
6. Ghi lại giả thuyết, thay đổi nhỏ, đo lại và quyết định giữ hay hoàn nguyên.

## 3. Phân biệt ba ca lỗi
```text
Hiện tượng                     Giả thuyết cần kiểm tra
LAN được, ngoài LAN không      Gateway/route/chính sách đường ra
Kết nối IP được, tên lỗi       DNS hoặc đường truy cập resolver
DNS đúng, HTTP trả 500         Ứng dụng hoặc phụ thuộc server
```
Đây là định hướng, không phải bảng kết luận tuyệt đối. Ví dụ truy cập bằng IP có thể khác virtual host hoặc TLS hostname, nên phải hiểu phép thử thực sự đang so sánh gì.

## 4. Bài tập và đáp án mẫu
Một học viên không mở LMS, người khác mở được. Thu IP/mask/gateway/DNS của hai máy, kiểm tra phân giải cùng tên, thử dịch vụ với đúng hostname, thu mã HTTP. Nếu chỉ xóa cache rồi lỗi biến mất, ghi đây là thay đổi tương quan chứ chưa chứng minh mọi sự cố trước đó đều do cache.
Báo cáo cần giả thuyết ban đầu, bằng chứng phản bác hoặc hỗ trợ, nguyên nhân xác nhận được, cách sửa và kiểm tra sau sửa. Không ghi “đã reset và thấy ổn” như một lời giải đầy đủ.''',
'Dự án nhỏ: thiết kế mạng cho phòng học': '''## 1. Đề bài và phạm vi sản phẩm
Thiết kế mạng lab có 20 máy học viên, 2 máy giảng viên, một máy chủ học tập và tối đa 10 khách không dây. Học viên cần LMS và Internet; khách không được vào vùng quản trị. Ghi các giả định như thiết bị hỗ trợ VLAN, có kết nối Internet mô phỏng hoặc đường ra được phép.

## 2. Một phương án địa chỉ minh họa
```text
Vùng       Mạng                 Gateway         Địa chỉ dành riêng
Student    192.168.10.0/24      .1              .2-.20
Teacher    192.168.20.0/24      .1              .2-.20
Guest      192.168.30.0/24      .1              .2-.20
```
Đây là phương án dễ quản lý cho lab, không tối ưu tiết kiệm địa chỉ. Có thể đề xuất subnet nhỏ hơn nếu giải thích đủ số host và dự phòng. Pool .50–.200 chỉ là lựa chọn minh họa trong từng mạng, không cấp chung một pool cho cả ba VLAN.

## 3. Hồ sơ phải nộp
1. Sơ đồ vật lý và logic, đánh dấu AP, access, trunk và gateway.
2. Bảng địa chỉ, DHCP, DNS, route và quyền truy cập.
3. Kế hoạch cấu hình từng bước cùng cách hoàn nguyên.
4. Ít nhất sáu ca nghiệm thu có kết quả mong đợi, thực tế và bằng chứng.
5. Nhật ký một lỗi được đưa vào lab có kiểm soát và quá trình chẩn đoán.

## 4. Tiêu chí tự đánh giá
Chấm theo bốn nhóm: thiết kế đáp ứng yêu cầu; địa chỉ và dịch vụ nhất quán; phân vùng được kiểm chứng; hồ sơ tái hiện được. Không coi đạt quiz là hoàn thành cấu hình. Lời giải tốt có cả ca Student vào LMS thành công và Guest vào quản trị bị chặn; nếu dùng giả lập phải ghi giới hạn so với thiết bị thật. Ghi rõ phần chưa kiểm tra thay vì tự điền kết quả thành công.''',
}

DETAILS.update({
'Mục tiêu và các mức kiểm thử': '''## 1. Chất lượng, lỗi và bằng chứng
Một sai sót của con người có thể tạo khuyết tật trong tài liệu hoặc mã; khuyết tật khi được kích hoạt có thể gây thất bại quan sát được. Không phải mọi khuyết tật đều biểu hiện trong mọi lần chạy. Kiểm thử cần mô tả điều kiện kích hoạt và kết quả thay vì chỉ ghi “có lỗi”.
Verification thường xem sản phẩm công việc có đáp ứng yêu cầu đã chỉ định; validation xem giải pháp có phù hợp nhu cầu sử dụng trong ngữ cảnh. Hai góc nhìn bổ sung nhau. Số lỗi tìm được không trực tiếp đo năng lực tester hoặc chất lượng toàn hệ thống.

## 2. Phân biệt mức và loại
```text
Mức kiểm thử        Ví dụ LMS
Unit                Hàm tính phần trăm và xử lý tổng câu bằng 0
Integration         Service ghi danh phối hợp database và kiểm tra quyền
System              Luồng đăng ký -> mở bài -> nộp quiz trên hệ thống
Acceptance          Đối chiếu tiêu chí học viên bắt đầu học sau ghi danh
```
Functional/non-functional là cách phân loại mục tiêu, không phải thay thế các mức trên. Một integration test vẫn có thể đo thuộc tính phi chức năng.

## 3. Thiết kế phép kiểm tra có ý nghĩa
Với tỷ lệ đúng, test cần đầu vào và kỳ vọng: 2/5 thành 40%; tổng 0 phải theo hợp đồng. Không tự chọn 0% nếu yêu cầu muốn “chưa có dữ liệu”. Ví dụ này cho thấy test phải bám ý nghĩa sản phẩm, không chỉ biểu thức toán.

## 4. Bài tập và lời giải
Viết bốn test ở bốn mức cho nộp quiz. Unit kiểm tra chấm một câu; integration kiểm tra lưu kết quả và câu trả lời cùng giao dịch; system kiểm tra hiển thị sau nộp; acceptance kiểm tra học viên nhận được hướng ôn theo tiêu chí. Nêu cách dùng dữ liệu lab và không tự tạo điểm cho học viên thật.''',
'Thiết kế test case': '''## 1. Mẫu test case có thể thực hiện
```text
ID: ENR-001
Mục tiêu: ghi danh khóa miễn phí một lần
Điều kiện trước: tài khoản lab hoạt động, khóa published, chưa ghi danh
Dữ liệu: user U1, course C1, price=0
Bước 1: mở danh sách khóa, chọn C1
Bước 2: bấm Đăng ký, chờ request hoàn tất
Kỳ vọng: một phản hồi thành công, một ghi danh, khóa có trong Khóa học của tôi
Sau test: chỉ dọn dữ liệu do ca này tạo trong database test
```
Kết quả thực tế và bằng chứng chỉ điền sau khi chạy. Không điền “pass” sẵn trong mẫu để minh họa như một kết quả thật.

## 2. Bao phủ tình huống thay vì nhân bản thao tác
Test dương kiểm tra đăng ký hợp lệ. Test âm kiểm tra khóa không tồn tại, chưa xác thực, khóa không cho đăng ký hoặc đầu vào sai kiểu theo hợp đồng. Test lặp/đồng thời kiểm tra tính duy nhất. Một bộ test chỉ đổi tên tài khoản nhưng đi cùng đường thành công không bao phủ các rủi ro này.

## 3. Kết quả mong đợi đủ cụ thể
“Đăng ký tốt” không kiểm chứng rõ. “API phản hồi thành công theo hợp đồng; bảng ghi danh tăng đúng một bản ghi U1–C1; không phát sinh thanh toán cho khóa miễn phí” là các quan sát cụ thể. Nếu không có quyền xem database, dùng API kiểm tra hoặc cơ chế bằng chứng được nhóm cho phép, không bỏ qua xác minh.

## 4. Bài tập có đáp án định hướng
Viết ENR-002 cho bấm lặp và ENR-003 cho không đủ quyền. Phân biệt luồng bấm ở UI với hai request thật: khóa nút chỉ là một lớp chống lặp. Đáp án cần kiểm tra ràng buộc server và không tạo bản ghi thứ hai. Ghi rõ mã lỗi dự kiến theo hợp đồng hiện tại, không đoán mọi dự án đều trả 409.''',
'Phân vùng tương đương và giá trị biên': '''## 1. Bắt đầu từ miền đầu vào
Giả sử tuổi bắt buộc là số nguyên, hợp lệ 18–60 bao gồm hai đầu. Chia miền số nguyên thành dưới 18, 18–60, trên 60; xét thêm dữ liệu thiếu, chuỗi không chuyển được hoặc số thập phân theo API. Không dùng kỹ thuật biên để né việc làm rõ kiểu dữ liệu.

## 2. Ví dụ dữ liệu và kỳ vọng
```text
Giá trị    Phân loại             Kỳ vọng theo giả định
17         Ngay dưới biên dưới  Từ chối
18         Tại biên dưới        Chấp nhận
19         Ngay trên biên dưới  Chấp nhận
59         Ngay dưới biên trên  Chấp nhận
60         Tại biên trên        Chấp nhận
61         Ngay trên biên trên  Từ chối
```
Đây là lựa chọn ba điểm quanh mỗi biên cho dữ liệu rời rạc. Tài liệu và tiêu chuẩn có thể định nghĩa các biến thể bao phủ khác; luôn ghi biến thể đang dùng. Với số thực không có “số kế tiếp” giống số nguyên nếu chưa quy định độ chính xác và bước dữ liệu.

## 3. Sai lầm thường gặp
Chỉ thử 30 rồi kết luận 18 và 60 đúng; chỉ thử giá trị hợp lệ; tự chấp nhận chuỗi “18” dù hợp đồng yêu cầu JSON number; đưa null và chuỗi rỗng vào cùng vùng dù server xử lý khác. Những quyết định này có thể làm mất ca quan trọng.

## 4. Bài tập và lời giải
Điểm quiz là số nguyên 0–100: thử -1,0,1,99,100,101, cùng trường thiếu và sai kiểu theo yêu cầu. Nếu số lượt tối đa là 3, kiểm tra trước lượt 3, sau lượt 3 và trường hợp lượt cuối đang làm: đây còn là bài toán trạng thái, không chỉ biên số. Nêu giới hạn của kỹ thuật thay vì tuyên bố sáu giá trị đã bao phủ mọi lỗi.''',
'Báo cáo lỗi và kiểm thử hồi quy': '''## 1. Mẫu báo lỗi có bằng chứng
```text
ID: BUG-LAB-01 (tình huống minh họa)
Tiêu đề: Hai yêu cầu ghi danh cùng khóa tạo hai bản ghi
Môi trường: database test, phiên bản được ghi cụ thể
Điều kiện: U1 chưa ghi danh C1
Bước tái hiện: gửi hai yêu cầu đồng thời với dữ liệu test hợp lệ
Thực tế: mô tả quan sát sau khi chạy, không điền trước
Mong đợi: chỉ một ghi danh theo quy tắc duy nhất
Bằng chứng: ID request, trạng thái, ảnh/query đã che bí mật
```
Một mô tả “bấm thấy sai” thiếu thời điểm, dữ liệu và kết quả nên khó tái hiện. Báo cáo cần đủ chi tiết nhưng không đưa token, mật khẩu hoặc dữ liệu cá nhân không cần thiết.

## 2. Severity và priority
Severity đánh giá ảnh hưởng kỹ thuật/nghiệp vụ; priority là mức ưu tiên xử lý trong bối cảnh phát hành. Lỗi giao diện nhỏ có thể được ưu tiên cao do trang sắp ra mắt; không đồng nhất hai trường. Dùng thang và quy ước của nhóm thay vì tự gắn mọi lỗi là nghiêm trọng nhất.

## 3. Kiểm tra sau sửa
Confirmation testing thực hiện lại điều kiện gây lỗi để xác nhận bản sửa. Regression testing mở rộng sang các hành vi có nguy cơ bị ảnh hưởng: đăng ký lần đầu, trùng, khóa có phí, quyền mở bài và danh sách khóa. Chọn phạm vi theo thay đổi, không mặc định chạy mọi test vô hạn.

## 4. Bài tập có lời giải định hướng
Bản sửa thêm unique constraint nhưng UI báo lỗi thô khi request thứ hai tới. Cần báo vấn đề xử lý phản hồi riêng, không kết luận sửa database thất bại nếu tính duy nhất đã đúng. Nộp một bug report, một ca xác nhận và ít nhất bốn ca hồi quy có lý do lựa chọn; không dùng dữ liệu thật để cố tình gây lỗi.''',
'SDLC, Agile và chiến lược kiểm thử': '''## 1. Từ yêu cầu tới vận hành
Các hoạt động hiểu nhu cầu, thiết kế, triển khai, kiểm thử và vận hành không nhất thiết diễn ra một lần theo đường thẳng. Trong vòng lặp, thông tin phản hồi cập nhật sản phẩm và bộ test. Kiểm thử sớm có thể là review mô tả nghiệp vụ trước khi có giao diện.

## 2. Ví dụ kế hoạch cho một vòng phát triển
```text
Yêu cầu: khóa miễn phí chỉ ghi danh một lần
Trước code: review quyền, trạng thái khóa và thông báo lỗi
Trong code: unit cho quy tắc; integration cho lưu và chống trùng
Sau tích hợp: UI cho trạng thái chờ, lỗi, thành công và màn hình hẹp
Trước phát hành: hồi quy theo tác động, báo cáo giới hạn và rủi ro
```
Acceptance criteria mô tả điều kiện riêng của yêu cầu. Definition of Done là thỏa thuận chung về mức hoàn tất. Một câu chuyện có tiêu chí đạt nhưng chưa hoàn tất các yêu cầu chất lượng chung vẫn có thể chưa “done”.

## 3. Chọn phạm vi theo rủi ro
Ước lượng khả năng sai và tác động, xác định vùng ưu tiên, liên kết từng vùng tới test. Điểm số rủi ro chỉ là công cụ thảo luận; không tạo cảm giác chính xác tuyệt đối nếu đầu vào chỉ là đánh giá sơ bộ. Dành thời gian cho lỗi đã thấy và các ràng buộc quyền/dữ liệu quan trọng.

## 4. Bài tập và đáp án
Trong hai ngày, nhóm sửa luồng nộp quiz và đổi màu tiêu đề. Ưu tiên tính điểm, lưu kết quả và lượt làm trước phần màu vì ảnh hưởng cao hơn; vẫn kiểm tra hiển thị cơ bản. Nộp kế hoạch ai làm gì, dữ liệu nào, tiêu chí vào/ra và phần chưa thể kiểm tra. Không gọi kế hoạch là bằng chứng đã chạy test.''',
'Review yêu cầu và truy vết kiểm thử': '''## 1. Checklist review yêu cầu
- Rõ chủ thể, hành động và tài nguyên không?
- Có điều kiện trước, biên và trường hợp lỗi không?
- Thuật ngữ có nhất quán với màn hình và API không?
- Có thể quan sát kết quả bằng quyền và công cụ hiện có không?
- Có xung đột giữa hai yêu cầu hoặc thiếu quyết định nghiệp vụ không?
Ví dụ “người dùng xem được kết quả” cần làm rõ kết quả của ai, vai trò nào, thời điểm nào và có che đáp án trước lượt cuối không.

## 2. Ma trận truy vết tối thiểu
```text
Yêu cầu   Test                Mục tiêu                 Kết quả/Lỗi
REQ-01    RES-OWN             Xem bài của chính mình   Điền sau chạy
REQ-01    RES-OTHER           Chặn bài người khác      Điền sau chạy
REQ-02    RES-HIDE            Che đáp án khi còn lượt  Điền sau chạy
```
Không lấy việc một ô đã có tên test làm chứng cứ test đầy đủ. Kiểm tra xem kỳ vọng có thực sự bám điều kiện của yêu cầu hay chỉ gắn mã để hoàn thành bảng.

## 3. Xử lý yêu cầu đổi
Nếu đổi quy tắc hiện đáp án, tìm test liên quan lịch sử, nộp bài và quyền giảng viên. Cập nhật kỳ vọng có chủ ý và giữ lịch sử phiên bản. Không chỉnh test chỉ để khớp hành vi hiện tại khi hành vi đó chưa được xác nhận đúng.

## 4. Bài tập và lời giải
Viết lại “gợi ý phải chính xác” thành tiêu chí quan sát: đúng phần kiến thức, số câu đúng/tổng, ngưỡng, thiếu dữ liệu và link hợp lệ. Chọn một tiêu chí còn mơ hồ để ghi câu hỏi cho người phụ trách. Đáp án phải nêu được đầu vào minh họa, kỳ vọng cụ thể và giới hạn, ví dụ chưa đủ 5 câu không kết luận yếu.''',
'Bảng quyết định và tổ hợp điều kiện': '''## 1. Xác định điều kiện độc lập
Giả định bài miễn phí được xem không cần ghi danh; bài giới hạn cần ghi danh hợp lệ. Trong phạm vi tài khoản được phép dùng hệ thống, hai điều kiện Free và Enrolled cho bảng dưới. Nếu tài khoản bị khóa có quy tắc riêng, phải thêm hoặc làm rõ trước, không âm thầm áp bảng cho mọi vai trò.
```text
Quy tắc       Free       Enrolled       Cho xem
R1            Có         Có             Có
R2            Có         Không          Có
R3            Không      Có             Có
R4            Không      Không          Không
```
Có thể gộp R1 và R2 khi Enrolled không ảnh hưởng kết quả trong trường hợp Free; việc rút gọn cần giữ ý nghĩa điều kiện và khả năng truy vết.

## 2. Từ quy tắc sang test
Mỗi test tạo đúng trạng thái, gọi thao tác và xác minh quyền thật. Nếu UI ẩn nút, vẫn phải kiểm tra API trong môi trường được phép. Dữ liệu không hợp lệ như khóa đã gỡ không chỉ là một giá trị Free=false thông thường; nó có thể thuộc quy tắc tồn tại tài nguyên riêng.

## 3. Giảm tổ hợp có trách nhiệm
Ba điều kiện nhị phân tạo tối đa tám tổ hợp, trước khi loại các trường hợp bất khả thi. Pairwise nhắm tương tác từng cặp, không chứng minh bao phủ lỗi cần ba điều kiện. Tài liệu cần nêu cách chọn và phần bỏ lại.

## 4. Bài tập có đáp án
Giảm giá khi mã hợp lệ và tổng tiền ít nhất 500: cả hai đúng mới giảm. Tại biên 499/500/501, bổ sung kiểm tra giá trị biên bên cạnh bảng quyết định. Đừng tự dùng 499,99 nếu hợp đồng đang quy định đơn vị nguyên; xác nhận đơn vị tiền và cách làm tròn trước.''',
'Kiểm thử chuyển trạng thái': '''## 1. Mô hình hóa một lượt quiz
```text
Chưa bắt đầu --mở hợp lệ--> Đang làm --nộp hợp lệ--> Đã nộp
Đang làm --hết thời gian--> Trạng thái theo quy tắc hệ thống
Đã nộp --sửa câu trả lời--> Từ chối, không đổi kết quả đã lưu
```
Không tự chọn “hết giờ luôn tự nộp” nếu chưa có yêu cầu. Phải xác nhận cách server xử lý và chỉ rõ người có thẩm quyền tính thời gian.

## 2. Trạng thái khác với nhãn giao diện
Một nút có chữ “đã nộp” không chứng minh dữ liệu đã commit. Test phải quan sát trạng thái được server xác nhận, kết quả và các tác dụng phụ. Cần xử lý mạng mất phản hồi sau khi server đã lưu: gửi lại có thể không được tạo kết quả thứ hai theo hợp đồng.

## 3. Bao phủ và chuỗi sự kiện
Test từng chuyển tiếp hợp lệ, chuyển tiếp bị cấm và chuỗi có ý nghĩa. Bao phủ mọi trạng thái chỉ cho biết đã tới các nút, không bảo đảm đã đi qua mọi cạnh. Thêm điều kiện dữ liệu như hết lượt, lượt đang làm hoặc quá giờ để phân biệt quy tắc.

## 4. Mẫu test và lời giải
Tạo attempt lab đang làm, nộp thành công, giữ result_id, gửi sửa câu trả lời sau nộp. Mong đợi từ chối theo API và hash kết quả cũ không đổi. Test khác mô phỏng request nộp lặp, xác nhận số kết quả theo hợp đồng. Không chỉnh đồng hồ hệ thống thật để thử hết giờ; dùng cơ chế thời gian kiểm soát được trong test.
Nộp bảng trạng thái đầu, sự kiện, guard, trạng thái cuối và dữ liệu cần giữ. Đánh dấu trạng thái chưa thử thay vì ghi pass theo sơ đồ.''',
'Kiểm thử API và phân quyền': '''## 1. Hợp đồng request và response
Ghi method, path, headers cần thiết, schema body, trạng thái và schema response. Test API không chỉ kiểm tra “có JSON”: một JSON trả danh sách tài nguyên của người khác vẫn là sai quyền. Không ghi token vào fixture công khai hoặc ảnh minh chứng.

## 2. Mẫu yêu cầu minh họa
```text
POST /api/enrollments
Authorization: Bearer <TOKEN_TEST_KHÔNG_CÔNG_KHAI>
Content-Type: application/json

{"course_id": 513}
```
Đây là mẫu minh họa; trước khi chạy phải đối chiếu endpoint và trường thực tế của môi trường thử. Không tự gửi hàng loạt tới production vì thấy một URL trong tài liệu.

## 3. Ma trận tài khoản và tài nguyên
```text
Người gọi       Tài nguyên                  Kỳ vọng
Chưa xác thực   Bài làm riêng               Từ chối theo hợp đồng
U1              Bài làm U1                  Cho phép
U1              Bài làm U2                  Từ chối, không lộ nội dung
Giảng viên      Bài làm khóa mình phụ trách Theo quy tắc vai trò
```
Kiểm tra cả mã phản hồi lẫn nội dung bị rò rỉ. Trường hợp tài nguyên không tồn tại khác tài nguyên tồn tại nhưng không được phép, dù ứng dụng có thể cố ý dùng cùng phản hồi để giảm tiết lộ thông tin.

## 4. Bài tập và lời giải
Với API tạo ghi danh, viết test thiếu trường, chuỗi sai kiểu, khóa không tồn tại, lặp và đồng thời. Xác minh không tạo thanh toán với khóa miễn phí, không tạo dữ liệu khi bị từ chối. Hợp đồng có thể chấp nhận một số phép chuyển kiểu nên không tự coi mọi chuỗi số là lỗi nếu chưa xác nhận yêu cầu.''',
'Kiểm thử cơ sở dữ liệu và tính toàn vẹn': '''## 1. Bằng chứng dữ liệu cần kiểm tra
Đếm bản ghi chỉ là một phần. Xác minh đúng user_id, course_id, trạng thái và trường thời gian nếu liên quan. Một bản ghi tồn tại nhưng gắn sai người dùng là lỗi dù COUNT tăng đúng một. Không lấy nội dung toast làm bằng chứng duy nhất cho commit.

## 2. Schema lab minh họa
```sql
CREATE TABLE lab_enrollments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    UNIQUE (user_id, course_id)
);
```
Chỉ tạo bảng này trong database test. Cú pháp ID tự tăng và khóa ngoại phụ thuộc hệ quản trị; ví dụ tối thiểu không đại diện toàn schema của ứng dụng. Ghi lại ràng buộc thực tế trước khi viết kỳ vọng.

## 3. Test giao dịch nhiều bước
Tạo bản ghi cha, tạo bản ghi liên quan, gây lỗi có kiểm soát trước commit rồi kiểm tra rollback. Một thư viện có thể tự commit từng helper nên việc đặt hai lời gọi cạnh nhau không bảo đảm chúng nằm trong một transaction. Phải kiểm tra ranh giới giao dịch thật.

## 4. Đồng thời và dọn dữ liệu
Hai request đều kiểm tra “chưa có” trước khi insert có thể cùng vượt bước kiểm tra. Ràng buộc unique ở database là lớp bảo vệ cuối, còn server cần xử lý lỗi để trả phản hồi có nghĩa. Dọn test theo ID đã tạo, không DELETE toàn bảng hoặc quét theo tên người dùng thật.

## 5. Bài tập có tiêu chí
Thiết kế test trùng, NULL, khóa ngoại sai và rollback; nêu môi trường test, dữ liệu trước/sau và phép query đọc để xác nhận. Đạt khi bằng chứng phân biệt “request lỗi nhưng đã ghi một phần” với “giao dịch được hoàn tác đúng”.''',
'Hiệu năng, khả dụng và tương thích': '''## 1. Viết mục tiêu đo được
Thay “trang nhanh” bằng một tiêu chí ví dụ: trên môi trường lab đã nêu, dữ liệu 100 khóa, dưới mô hình tải được phép, đo p95 thời gian API và tỉ lệ lỗi theo ngưỡng nhóm thống nhất. Đây là mẫu đặc tả, không phải kết quả website hiện tại hay ngưỡng chuẩn cho mọi hệ thống.

## 2. Đọc số liệu có ngữ cảnh
Ghi thời gian làm nóng, số mẫu, phân bố độ trễ và tỉ lệ lỗi. Không so phiên bản A trên máy rảnh với B trên máy đang bận rồi quy mọi khác biệt cho mã nguồn. Timeout và lỗi HTTP cần được tính, không loại khỏi báo cáo để làm trung bình đẹp hơn.

## 3. Checklist thao tác giao diện
- Dùng Tab tới nút đăng ký, có focus rõ và kích hoạt bằng bàn phím.
- Thông báo đọc được, có văn bản chứ không chỉ màu; có nút đóng.
- Tên khóa dài không che số liệu hoặc đẩy nút ra ngoài màn hình.
- Ở màn hình hẹp và khi phóng to, không mất nội dung quan trọng.
- Mạng chậm có trạng thái chờ và ngăn bấm lặp phù hợp.
- Lỗi API không hiển thị như chưa có dữ liệu.
Một checklist thủ công hữu ích nhưng không tự chứng nhận đạt toàn bộ tiêu chuẩn tiếp cận.

## 4. Bài tập và đáp án định hướng
Soạn ma trận ba kích thước khung và hai trình duyệt được hỗ trợ. Chọn một luồng chính kiểm thử ở cả sáu tổ hợp, ghi môi trường. Tạo tên dài và thông báo lỗi dài trong dữ liệu lab. Đáp án cần có ảnh và nhận xét cụ thể, không chỉ “đẹp”; ghi giới hạn khi chưa có thiết bị thật hoặc công nghệ hỗ trợ để thử.''',
'Dự án nhỏ: kế hoạch kiểm thử và tự động hóa': '''## 1. Phạm vi gói bàn giao
Chọn đăng ký khóa miễn phí làm tính năng mục tiêu. Tài liệu cần mục tiêu, phạm vi không làm, rủi ro, môi trường, dữ liệu, trách nhiệm, điều kiện bắt đầu/kết thúc và cách báo cáo. Chỉ tự động hóa các kiểm tra có kỳ vọng rõ, không tạo assertion theo dữ liệu đang trả về để test luôn xanh.

## 2. Ví dụ test độc lập không gọi hệ thống thật
```python
def can_open_lesson(is_free, enrolled):
    return is_free or enrolled

def test_guest_cannot_open_restricted_lesson():
    assert can_open_lesson(False, False) is False

def test_enrolled_can_open_restricted_lesson():
    assert can_open_lesson(False, True) is True

def test_free_lesson_is_open():
    assert can_open_lesson(True, False) is True
```
Đây là mô hình luật đơn giản phục vụ học cách viết test, không phải toàn bộ hàm phân quyền của LMS. Trong dự án thật còn trạng thái khóa, tài khoản và vai trò; cần test implementation thật qua interface phù hợp.

## 3. Từ ví dụ tới kiểm tra tích hợp
Tạo user/course lab trong fixture, gọi API thực ở môi trường test, xác nhận phản hồi và dữ liệu. Mỗi test phải tự có điều kiện trước và dọn dữ liệu của nó. Test UI chờ điều kiện quan sát được thay vì sleep cố định dài. Khi flaky, thu trace và sửa nguyên nhân, không chỉ tăng timeout vô hạn.

## 4. Rubric tự đánh giá
Chấm yêu cầu có truy vết, bao phủ rủi ro, dữ liệu cô lập, assertions đúng, khả năng chạy lại và báo cáo trung thực. Nộp 12 test thiết kế, ba test tự động, kết quả thực chạy và hai báo cáo lỗi nếu tìm thấy; nếu dùng lỗi giả định phải gắn nhãn giả định. Không bịa lỗi hay kết quả chỉ để đủ số lượng bài nộp.''',
})

DETAILS.update({
'Mảng và danh sách liên kết': '''## 1. Mô hình lưu trữ và giới hạn giả định
Trong mô hình mảng cơ bản, phần tử có chỉ số và truy cập trực tiếp. Python list là mảng động các tham chiếu, không hoàn toàn giống mảng số nguyên tĩnh trong C. Vì vậy cần nêu ngôn ngữ và cấu trúc cụ thể khi bàn về bộ nhớ. append của list có thời gian phân bổ bình quân O(1), không có nghĩa mọi lần mở rộng đều hằng số.
Danh sách đơn lưu liên kết next. Biết một nút không đồng nghĩa biết ngay nút trước nó; thao tác xóa cần xét vị trí và mô hình nút. Không khẳng định mọi chèn/xóa danh sách đều O(1) nếu còn phải tìm vị trí.

## 2. Mô phỏng cập nhật
```text
Mảng trước: [A,B,C,D]; chèn X ở chỉ số 2
Dịch D sang phải -> dịch C sang phải -> đặt X
Mảng sau: [A,B,X,C,D]

Danh sách: A -> B -> C -> D
new.next = B.next
B.next = new
Kết quả: A -> B -> X -> C -> D
```
Thứ tự cập nhật liên kết quan trọng: nếu ghi đè B.next mà chưa giữ đường tới C, có thể làm mất phần đuôi khỏi chuỗi truy cập.

## 3. Ví dụ thực thi Python
```python
def insert_copy(values, index, item):
    if not 0 <= index <= len(values):
        raise IndexError("invalid insertion index")
    return values[:index] + [item] + values[index:]

assert insert_copy([1, 3], 1, 2) == [1, 2, 3]
assert insert_copy([], 0, 8) == [8]
```
Hàm tạo bản sao, vì vậy O(n) cả thời gian và bộ nhớ phụ; không nhầm với cập nhật tại chỗ.

## 4. Bài tập và lời giải
Chọn cấu trúc cho đọc phần tử thứ k rất thường xuyên: mảng là ứng viên hợp lý. Với nối nút khi đã có vị trí, danh sách có lợi thế nhưng vẫn cần quản lý bộ nhớ và liên kết. Nộp bảng truy cập, tìm kiếm, chèn giữa, xóa, kèm giả định; trường hợp rỗng và chỉ một phần tử phải được thử riêng.''',
'Ngăn xếp và hàng đợi': '''## 1. Giao diện trừu tượng trước triển khai
Stack có push, pop, peek, is_empty; queue có enqueue, dequeue, peek. Quy định rõ thao tác trên cấu trúc rỗng: báo lỗi, trả sentinel hoặc một kiểu kết quả riêng. Không dùng None làm dấu lỗi nếu None cũng là dữ liệu hợp lệ mà không có cách phân biệt.
Queue cài bằng list và pop(0) trong Python thường phải dịch phần tử. deque hỗ trợ thao tác ở hai đầu phù hợp hơn cho queue. Đây là lựa chọn triển khai, không thay đổi quy tắc FIFO.

## 2. Truy vết hai cấu trúc
```text
Thao tác        Stack trả      Queue trả
Thêm A          -              -
Thêm B          -              -
Lấy một         B              A
Thêm C          -              -
Lấy một         C              B
```
Hãy tự ghi phần tử còn lại sau từng dòng. Mô phỏng trên giấy giúp phân biệt quy tắc trước khi viết mã.

## 3. Kiểm tra dấu ngoặc bằng stack
```python
def balanced(text):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for char in text:
        if char in '([{':
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
    return not stack

assert balanced('([])')
assert not balanced('([)]')
assert not balanced('(')
```
Đây là ví dụ kiểm tra chuỗi dấu ngoặc, không phải bộ phân tích cú pháp Python: ngoặc trong chuỗi ký tự hoặc comment chưa được xử lý theo ngữ pháp ngôn ngữ.

## 4. Bài tập và lời giải
Thêm test chuỗi rỗng, dấu đóng ở đầu, ba loại ngoặc lồng nhau. Với n ký tự, mỗi ký tự xử lý một lần: thời gian O(n), bộ nhớ tối đa O(n). Đối với hàng đợi công việc, nêu cách ứng xử khi đầy và khi rỗng; không suy ra FIFO đồng nghĩa mọi công việc hoàn tất theo thứ tự nếu nhiều worker chạy đồng thời.''',
'Tìm kiếm tuyến tính và nhị phân': '''## 1. Hợp đồng hàm tìm kiếm
Quy định trả chỉ số hay giá trị, và trả gì khi không tìm thấy. Nếu dữ liệu có phần tử trùng, yêu cầu có thể là một vị trí bất kỳ, vị trí đầu hoặc cuối; đó là ba hợp đồng khác nhau. Tìm nhị phân cần mảng đã sắp theo cùng phép so sánh đang dùng.

## 2. Cài đặt có biên rõ ràng
```python
def binary_search(values, target):
    left, right = 0, len(values) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

assert binary_search([], 3) == -1
assert binary_search([2, 5, 8, 13, 21], 13) == 3
assert binary_search([2, 5, 8, 13, 21], 7) == -1
```
Bất biến: nếu target tồn tại ở phần chưa loại thì nó nằm trong khoảng đóng left..right. mid±1 bảo đảm khoảng giảm. Không trộn công thức biên đóng này với thuật toán khoảng nửa mở mà không sửa điều kiện tương ứng.

## 3. Truy vết và phân tích
Trong [2,5,8,13,21], tìm 13: mid=2 có 8 nên left=3; mid=3 có 13 nên trả 3. Khoảng giảm một nửa nên O(log n) lần so sánh trên mảng truy cập O(1). Nếu phải sắp xếp đầu vào cho chỉ một lần tìm, cần tính thêm chi phí sắp xếp.

## 4. Bài tập mở rộng có đáp án định hướng
Sửa hàm để trả vị trí đầu của 5 trong [1,5,5,5,9]. Khi gặp bằng, lưu ứng viên và tiếp tục tìm bên trái; không trả ngay. Kiểm thử đầu, cuối, rỗng, một phần tử và tất cả bằng nhau. Giải thích vì sao đổi left=mid có thể làm lặp vô hạn khi left sát right.''',
'Sắp xếp và độ phức tạp': '''## 1. Đặt tiêu chí trước khi chọn thuật toán
Đầu ra tăng hay giảm, có giữ phần tử bằng nhau theo thứ tự cũ không, có sửa đầu vào không, giới hạn bộ nhớ bao nhiêu? Một thuật toán tại chỗ và một thuật toán ổn định có thể phù hợp các nhu cầu khác nhau. So sánh chi phí phải cùng mô hình dữ liệu.

## 2. Merge sort đầy đủ cho danh sách số
```python
def merge_sort(values):
    if len(values) <= 1:
        return values[:]
    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    output = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            output.append(left[i]); i += 1
        else:
            output.append(right[j]); j += 1
    return output + left[i:] + right[j:]

assert merge_sort([4, 2, 5, 1]) == [1, 2, 4, 5]
assert merge_sort([2, 2, -1]) == [-1, 2, 2]
```
Chọn bên trái khi khóa bằng giúp giữ ổn định nếu phép so sánh theo khóa nhất quán. Bản ví dụ dùng slicing và danh sách phụ để dễ hiểu, không phải bản tối ưu bộ nhớ.

## 3. Vì sao O(n log n)
Chia đôi tạo khoảng log n mức; công việc trộn trên mỗi mức là O(n). Không ghi riêng một lần trộn rồi kết luận toàn thuật toán O(n). Với bản cài thông thường, bộ nhớ phụ cực đại là O(n) cộng ngăn xếp O(log n), vẫn O(n).

## 4. Bài tập và lời giải
Trộn [1,4,7] với [2,3,8] thu [1,2,3,4,7,8]; ở mỗi bước chọn đầu nhỏ hơn chưa dùng. Kiểm tra đầu ra vừa có thứ tự vừa giữ số lần xuất hiện từng phần tử. Một chương trình trả [] có thứ tự nhưng đã mất dữ liệu, nên chỉ kiểm tra tăng dần là chưa đủ.''',
'Big-O, bất biến và kiểm tra thuật toán': '''## 1. Đếm trước khi rút gọn
```text
for i in range(n): pass         -> n bước
Hai vòng trên nối tiếp          -> 2n bước -> O(n)
Hai vòng n bước lồng nhau       -> n*n bước -> O(n²)
while n > 1: n //= 2            -> khoảng log2(n) bước
```
Nếu vòng trong không chạy n lần mà phụ thuộc i, phải viết tổng thực tế. Với j từ 0 tới i-1, số bước là n(n-1)/2, vẫn O(n²). Không suy ra cứ thấy hai vòng là chắc O(n²).

## 2. Lập luận bằng bất biến
```python
def maximum(values):
    if not values:
        raise ValueError('empty input')
    best = values[0]
    for item in values[1:]:
        if item > best:
            best = item
    return best

assert maximum([-9, -2, -5]) == -2
assert maximum([7]) == 7
```
Khởi tạo: best đúng cho tiền tố dài một. Duy trì: so sánh phần tử mới giữ max của tiền tố đã xét. Kết thúc: tiền tố là toàn mảng. Bản dùng slicing ở ví dụ tạo danh sách phụ; nếu phân tích bộ nhớ phải tính chi phí này hoặc chuyển sang lặp chỉ số.

## 3. Thiết kế test theo đặc tính
Kết quả max phải thuộc dữ liệu và không nhỏ hơn mọi phần tử. Các đặc tính giúp chọn test rỗng, âm, lặp, tăng và giảm. Test chạy qua không thay thế chứng minh; chứng minh cũng không bảo đảm cài đặt không có lỗi gõ.

## 4. Bài tập và đáp án
Tính tổng từ i=0 đến n-1 của i: n(n-1)/2. Giải thích khác nhau giữa O(n), Θ(n) và một phép đo giây: chặn trên, chặn khít tiệm cận và kết quả thực nghiệm. Nếu chỉ biết thuật toán O(n²), không tự kết luận đó là chặn khít tốt nhất.''',
'Đệ quy và ngăn xếp lời gọi': '''## 1. Ba câu hỏi bắt buộc
Đầu vào nào hợp lệ? Khi nào giải trực tiếp? Mỗi lời gọi tiến gần cơ sở bằng cách nào? Thiếu một câu trả lời có thể gây không kết thúc hoặc xử lý sai biên. Không đặt cơ sở theo cảm tính chỉ để chương trình dừng.

## 2. Giai thừa và điều kiện miền
```python
def factorial(n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError('n must be a non-negative integer')
    def solve(k):
        if k == 0:
            return 1
        return k * solve(k - 1)
    return solve(n)

assert factorial(0) == 1
assert factorial(5) == 120
```
Ví dụ dùng số nhỏ để học; Python giới hạn độ sâu đệ quy. Với dữ liệu lớn nên lựa chọn cách lặp hoặc hàm thư viện phù hợp, không tự tăng giới hạn ngăn xếp để che thiết kế.

## 3. Truy vết thời gian và bộ nhớ
factorial(3) tạo các lời gọi 3,2,1,0 rồi trả ngược. Số phép nhân là ba, ngăn xếp sâu tuyến tính. Với Fibonacci trực tiếp, cây lời gọi có các nhánh lặp; độ sâu không bằng tổng số nút trong cây. Memoization giảm tính lại bằng bộ nhớ lưu kết quả.

## 4. Bài tập có hướng giải
Viết tổng danh sách bằng đệ quy với chỉ số thay vì cắt danh sách ở mỗi bước. Cơ sở index==len(values) trả 0; bước tiếp cộng values[index]. Phân tích O(n) thời gian và O(n) ngăn xếp trong mô hình phép cộng hằng số. Kiểm thử danh sách rỗng, âm và một phần tử; ghi rõ giả định về kích thước số nguyên nếu phân tích chi phí bit.''',
'Bảng băm, tập hợp và ánh xạ': '''## 1. Từ khóa tới vị trí lưu
Hàm băm và số ô bảng quyết định vị trí khởi đầu của khóa. Va chạm không có nghĩa hai khóa bằng nhau. Cấu trúc vẫn cần phép so sánh khóa đúng. Hệ số tải là số phần tử chia số ô theo mô hình bảng; khi tăng quá mức có thể cần mở rộng và băm lại tùy triển khai.

## 2. Bộ đếm có quy tắc đầu vào rõ
```python
def frequencies(words, ignore_case=False):
    result = {}
    for word in words:
        key = word.casefold() if ignore_case else word
        result[key] = result.get(key, 0) + 1
    return result

assert frequencies(['An', 'an']) == {'An': 1, 'an': 1}
assert frequencies(['An', 'an'], True) == {'an': 2}
```
casefold là một lựa chọn xử lý chữ hoa/thường, không tự giải quyết mọi khác biệt biểu diễn Unicode. Nếu ứng dụng cần chuẩn hóa NFC, phải nêu thêm bước đó và viết test tương ứng.

## 3. Độ phức tạp và giới hạn
Trong điều kiện băm tốt, n cập nhật có thời gian kỳ vọng O(n), bộ nhớ O(k) cho k khóa khác nhau, chưa tính độ dài khóa và chi phí băm chuỗi. Không khẳng định chuỗi rất dài luôn được xử lý cùng chi phí như một ký tự.
Set có thể kiểm tra trùng, nhưng sau khi loại bản sao cần quyết định thứ tự đầu ra. Không dựa vào một lần chạy để suy ra set có thứ tự sắp xếp.

## 4. Bài tập và đáp án
Với An,Bình,An,an và ignore_case=True, kết quả là an:3,bình:1. Hãy thêm báo cáo giảm dần theo tần suất rồi tăng theo tên khi hòa; bước sắp xếp k khóa có chi phí thêm O(k log k). Đối chiếu tổng đếm với bốn đầu vào để phát hiện mất hoặc nhân đôi dữ liệu.''',
'Cây nhị phân và cây tìm kiếm nhị phân': '''## 1. Các khái niệm cần thống nhất
Gốc không có cha; lá không có con. Chiều cao có thể tính bằng số cạnh hoặc số nút tùy tài liệu; phải ghi quy ước. Bài này dùng chiều cao theo số cạnh khi mô tả sơ đồ, còn phân tích O(h) không thay đổi ý nghĩa tiệm cận.

## 2. Tìm kiếm BST không dùng đệ quy
```python
class Node:
    def __init__(self, key, left=None, right=None):
        self.key, self.left, self.right = key, left, right

def contains(root, target):
    node = root
    while node is not None:
        if target == node.key:
            return True
        node = node.left if target < node.key else node.right
    return False

root = Node(4, Node(2, Node(1), Node(3)), Node(6))
assert contains(root, 3)
assert not contains(root, 5)
```
Thuật toán dùng bộ nhớ phụ O(1) cho tìm kiếm lặp; chi phí thời gian phụ thuộc chiều cao. Không lấy chiều cao của một hình cân đối để kết luận mọi cây đều log n.

## 3. Kiểm tra thứ tự toàn cây
Gốc 10, con trái 5, nhưng trong cây con trái có 12: mỗi cặp cha-con cục bộ có thể trông hợp lý ở một số cạnh nhưng 12 vẫn vi phạm ràng buộc nhỏ hơn 10. Kiểm tra hợp lệ cần truyền khoảng cho toàn cây con hoặc xem inorder theo chính sách khóa trùng.

## 4. Bài tập có hướng giải
Thêm thao tác chèn không cho khóa trùng; khi gặp bằng thì giữ nguyên hoặc báo lỗi theo hợp đồng. Viết test cây rỗng, khóa ở gốc, hai nhánh và chuỗi lệch. So sánh thứ tự chèn tăng dần với thứ tự tạo cây cân đối; không thay đổi bộ dữ liệu giữa hai phép so sánh.''',
'Heap và hàng đợi ưu tiên': '''## 1. Bất biến và chỉ số
Min-heap yêu cầu cha không lớn hơn các con, không yêu cầu toàn nhánh trái nhỏ hơn toàn nhánh phải như BST. Hình dạng hoàn chỉnh giúp biểu diễn bằng mảng. Với i>0, cha ở (i-1)//2; con ở 2*i+1 và 2*i+2 nếu các chỉ số còn trong mảng.

## 2. Cài đặt sử dụng thư viện chuẩn
```python
import heapq

heap = []
for value in [5, 2, 8, 1]:
    heapq.heappush(heap, value)
output = [heapq.heappop(heap) for _ in range(len(heap))]
assert output == [1, 2, 5, 8]
```
Đây là minh họa API min-heap đã có từ lâu, không phụ thuộc các hàm max-heap mới. Không gọi heappop trên heap rỗng nếu chưa quy định xử lý lỗi.

## 3. Truy vết thao tác và độ phức tạp
Thêm 1 vào [2,5,8] đặt ở cuối rồi đổi với cha 5, sau đó với cha 2. Lấy min thay gốc bằng phần tử cuối, đưa xuống qua con nhỏ hơn để khôi phục bất biến. Chiều cao là O(log n). heapify cả mảng có thể O(n); không nhân n với log n nếu đang phân tích thuật toán heapify tuyến tính.

## 4. Ưu tiên bằng nhau và ứng dụng
Lưu tuple (priority, sequence, task) để giữ thứ tự đến khi priority bằng nhau và tránh so sánh trực tiếp task không có thứ tự. Cần nêu quy ước số nhỏ là ưu tiên cao hay ngược lại.
Thực hành: thêm ba việc có ưu tiên 2,1,2; mong đợi việc ưu tiên 1 trước rồi hai việc ưu tiên 2 theo sequence. Giải thích tại sao heap không tối ưu mọi yêu cầu tìm theo mã task tùy ý.''',
'Đồ thị, BFS và DFS': '''## 1. Đọc đồ thị từ dữ liệu
Đồ thị có hướng cần ghi cạnh theo chiều; vô hướng thường thêm quan hệ hai chiều vào danh sách kề. Số đỉnh V và cạnh E cần nhất quán với cách lưu. Khi có self-loop hoặc cạnh trùng, quy định có giữ hay loại thay vì đếm tùy ý.

## 2. BFS trả khoảng cách ít cạnh nhất
```python
from collections import deque

def bfs_distances(graph, start):
    distance = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt not in distance:
                distance[nxt] = distance[node] + 1
                queue.append(nxt)
    return distance

g = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []}
assert bfs_distances(g, 'A')['D'] == 2
```
Đánh dấu khi phát hiện giúp một đỉnh không bị thêm lặp nhiều lần. Hàm chỉ trả các đỉnh đến được từ start.

## 3. DFS và lựa chọn chiến lược
DFS có thể ghi thời điểm vào/ra để hỗ trợ nhiều bài toán, nhưng một lần DFS không tự cho đường ít cạnh nhất. Đệ quy có thể vượt độ sâu khi đồ thị lớn; stack tường minh là một lựa chọn. Nếu cần đường theo trọng số, phải dùng thuật toán phù hợp điều kiện trọng số, không áp BFS thường cho mọi trường hợp.

## 4. Bài tập và đáp án
Thêm E cô lập: BFS từ A không có E trong kết quả. Thêm D→A tạo chu trình: hàm vẫn kết thúc vì đã có distance. Đổi thứ tự kề có thể đổi thứ tự khám phá nhưng không đổi khoảng cách ít cạnh nhất. Nộp bảng queue qua từng bước và đường đi lấy qua mảng cha được bổ sung.''',
'Chia để trị và quy hoạch động nhập môn': '''## 1. Từ lời giải trực tiếp tới trạng thái
Xác định thông tin tối thiểu để mô tả bài toán con. Với số cách lên cầu thang, trạng thái chỉ cần số bậc còn lại khi bước cho phép luôn là 1 hoặc 2. Nếu luật thay đổi theo bước trước, trạng thái phải chứa thêm thông tin; không tái sử dụng công thức cũ một cách máy móc.

## 2. Cài đặt bottom-up có kiểm tra biên
```python
def stair_ways(n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError('invalid n')
    previous, current = 1, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous

assert stair_ways(0) == 1
assert stair_ways(4) == 5
assert stair_ways(6) == 13
```
Theo mô hình phép toán số học hằng số: O(n) thời gian, O(1) số biến phụ. Với số nguyên rất lớn, chi phí bit và bộ nhớ số nguyên tăng theo kích thước giá trị, nên mô hình này là một giả định phân tích.

## 3. Phân biệt kỹ thuật
Chia để trị nhấn mạnh chia, giải và kết hợp; quy hoạch động lưu lời giải bài toán con hữu ích để tránh tính lại. Tham lam cần tính chất bảo đảm quyết định cục bộ dẫn tới tối ưu. Với mệnh giá 1,3,4 và tiền 6, lấy 4 trước cho ba đồng, còn 3+3 chỉ hai đồng.

## 4. Bài tập có lời giải định hướng
Lập bảng số đồng ít nhất cho tiền từ 0 tới 6 với các mệnh giá trên. Đặt dp[0]=0; trạng thái chưa đạt dùng vô cực; xét mọi đồng không vượt số tiền và lấy min(dp[s-coin]+1). Kết quả cho 6 là 2. Kiểm tra riêng trường hợp không tạo được số tiền nếu bỏ mệnh giá 1.''',
'Dự án nhỏ: bộ tra cứu và thống kê dữ liệu': '''## 1. Đặc tả sản phẩm
Đầu vào là danh sách tên; đầu ra gồm số bản ghi, số tên phân biệt, tần suất và báo cáo có thứ tự. Chọn chính sách bỏ khoảng trắng đầu/cuối và gộp hoa/thường rõ ràng. Nếu giữ nguyên tên để hiển thị, có thể lưu riêng khóa chuẩn hóa và nhãn hiển thị.

## 2. Chương trình mẫu có thể chạy
```python
def build_report(names):
    counts = {}
    for name in names:
        key = name.strip().casefold()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))

assert build_report(['An', ' Bình ', 'an', '']) == [('an', 2), ('bình', 1)]
assert build_report([]) == []
```
Theo hợp đồng mẫu, chuỗi rỗng bị bỏ qua nên tổng tần suất bằng số mục hợp lệ, không phải số mục thô. Nếu đề bài muốn giữ mục rỗng phải thay cả cài đặt và test.

## 3. Phân tích và nâng cấp
Với n mục và k khóa khác nhau, đếm thường O(n) kỳ vọng theo mô hình băm; sắp xếp O(k log k), chưa tính độ dài chuỗi. Giữ dữ liệu nguồn nếu cần truy vết lỗi chuẩn hóa. Nếu báo cáo lấy top k liên tục trên luồng lớn, đề xuất heap và so sánh với sắp xếp toàn bộ.

## 4. Hồ sơ nghiệm thu
Nộp mã nguồn, cách chạy, hợp đồng chuẩn hóa, tối thiểu sáu test và phân tích Big-O. Test gồm rỗng, tất cả trùng, khoảng trắng, chữ hoa/thường, Unicode và hòa tần suất. Giữ thứ tự thứ hai theo tên để báo cáo xác định. Không chứng minh đúng bằng một ảnh chụp đầu ra; phải có đầu vào và kỳ vọng đối chiếu.''',
})
