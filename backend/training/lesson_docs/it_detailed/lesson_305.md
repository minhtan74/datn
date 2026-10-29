## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 2: Dịch vụ và ứng dụng mạng.
- Các bài trong chương: DNS và phân giải tên miền; HTTP và HTTPS.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Giải thích vai trò DNS và đọc các loại bản ghi cơ bản.

## Kiến thức nền
DNS là hệ thống phân giải tên phân tán. Ứng dụng có thể hỏi resolver để tìm địa chỉ gắn với tên miền. Resolver tận dụng bộ nhớ đệm hoặc truy vấn các máy chủ thích hợp; không phải mọi yêu cầu đều đi lại toàn bộ chuỗi truy vấn.

Bản ghi A ánh xạ tên tới IPv4, AAAA tới IPv6. CNAME khai báo tên bí danh trỏ tới một tên khác. MX mô tả máy chủ nhận thư cho miền. TTL hướng dẫn thời gian lưu bộ nhớ đệm, không phải thời gian tải trang hay thời hạn đăng ký tên miền.

DNS thường sử dụng cổng 53 với UDP hoặc TCP. Phân giải tên thành công chỉ cho biết có câu trả lời DNS; không chứng minh máy chủ web đang hoạt động. Khi gỡ lỗi, tách kiểm tra DNS khỏi kiểm tra kết nối và HTTP.

## 1. Các thành phần tham gia
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
Một host phân giải đúng tên nhưng nhận HTTP 500. DNS có chứng minh website tốt không? Không: bước tên miền đã hoàn tất nhưng server ứng dụng còn lỗi. Một CNAME trỏ tới tên không có bản ghi địa chỉ cần kiểm tra chuỗi phân giải. Hãy nộp bảng ba ca: thành công, tên không tồn tại, timeout, với bằng chứng phân biệt từng ca.

## Bài tập vận dụng bổ sung
mô tả vì sao đổi bản ghi chưa chắc mọi người dùng thấy ngay. Nêu khác biệt giữa tên miền, địa chỉ IP và URL; URL còn có thể chứa giao thức, đường dẫn và tham số.

## Câu hỏi tự kiểm tra
1. Vai trò chính của DNS là gì?
2. Bản ghi nào ánh xạ tên miền tới IPv4?
3. Bản ghi nào chứa địa chỉ IPv6?
4. TTL trong DNS liên quan tới điều gì?
5. DNS phân giải thành công có bảo đảm website hoạt động không?

## Gợi ý đáp án và điểm cần nhớ
- Phân giải tên miền thành thông tin như địa chỉ IP. DNS cung cấp bản ghi gắn với tên miền.
- A. Bản ghi A chứa địa chỉ IPv4.
- AAAA. AAAA là loại bản ghi dành cho địa chỉ IPv6.
- Thời gian lưu bản ghi trong bộ nhớ đệm. TTL giúp resolver xác định thời gian có thể tái sử dụng bản ghi.
- Không, dịch vụ web vẫn có thể gặp lỗi. DNS và dịch vụ HTTP là các bước khác nhau.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
