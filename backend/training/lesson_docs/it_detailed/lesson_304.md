## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 1: Nền tảng kết nối mạng.
- Các bài trong chương: Mô hình TCP/IP và thiết bị mạng; Địa chỉ IPv4 và mạng con.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Đọc địa chỉ IPv4, ký hiệu CIDR và xác định mạng con đơn giản.

## Kiến thức nền
IPv4 dùng địa chỉ 32 bit, thường viết thành bốn số thập phân từ 0 đến 255. Ký hiệu /24 cho biết 24 bit đầu là phần mạng; mặt nạ tương ứng là 255.255.255.0. Với mạng thông thường 192.168.1.0/24, địa chỉ mạng là 192.168.1.0, broadcast là 192.168.1.255 và các địa chỉ host thông thường là .1 đến .254.

Hai host 192.168.1.10/24 và 192.168.1.20/24 cùng mạng con. Host 192.168.2.10/24 nằm ở mạng khác. Khi đích ngoài mạng con, máy thường gửi gói đến default gateway để chuyển tiếp; gateway không phải máy chủ DNS.

Các dải riêng gồm 10.0.0.0/8, 172.16.0.0/12 và 192.168.0.0/16. Chúng không được định tuyến công khai trên Internet. Không suy ra mọi địa chỉ bắt đầu bằng 172 đều là địa chỉ riêng.

## 1. Đọc địa chỉ và tính phần mạng
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
Thiết kế mạng cho 25 máy và một gateway: /27 có 30 host thông thường nên đủ nếu không có thêm nhu cầu vượt số còn lại. Ghi rõ dự phòng và địa chỉ dành riêng thay vì chỉ nêu tiền tố.

## Bài tập vận dụng bổ sung
với 10.0.5.0/24, tìm địa chỉ mạng, broadcast và hai địa chỉ host hợp lệ. Quy tắc trừ hai địa chỉ chỉ áp dụng mạng con thông thường; /31 và /32 có cách sử dụng riêng.

## Câu hỏi tự kiểm tra
1. Địa chỉ IPv4 có bao nhiêu bit?
2. Mặt nạ nào tương ứng với /24?
3. Host nào cùng mạng con với 192.168.1.10/24?
4. Broadcast của mạng thông thường 192.168.1.0/24 là gì?
5. Default gateway thường được dùng khi nào?

## Gợi ý đáp án và điểm cần nhớ
- 32. IPv4 có 32 bit; IPv6 có 128 bit.
- 255.255.255.0. /24 đặt 24 bit đầu của mặt nạ thành 1.
- 192.168.1.20/24. Với /24, hai host có cùng ba octet đầu thuộc cùng mạng con.
- 192.168.1.255. Địa chỉ broadcast đặt toàn bộ 8 bit host thành 1.
- Gửi gói tới đích ngoài mạng con. Gateway là bước chuyển tiếp ra khỏi mạng con hiện tại.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
