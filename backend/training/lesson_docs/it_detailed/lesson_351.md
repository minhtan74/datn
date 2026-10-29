## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 5: Giao vận và vận hành an toàn.
- Các bài trong chương: Cổng, socket và vòng đời kết nối TCP; Tường lửa và phân vùng truy cập.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Phân biệt cổng dịch vụ với địa chỉ IP; mô tả bắt tay TCP.

## Kiến thức nền
Địa chỉ IP nhận diện giao diện ở tầng mạng; cổng giúp phân biệt ứng dụng ở tầng giao vận. Một dịch vụ lắng nghe tại địa chỉ và cổng, còn client thường dùng cổng nguồn tạm thời. Cùng số cổng nhưng TCP và UDP là hai không gian khác nhau.

TCP mở kết nối điển hình bằng SYN, SYN-ACK, ACK. Số thứ tự và xác nhận hỗ trợ truyền luồng byte có thứ tự. TCP không giữ ranh giới thông điệp ứng dụng; chương trình cần tự xác định độ dài hoặc ký hiệu kết thúc thông điệp. Đóng kết nối và timeout cũng cần được xử lý.

Một phiên TCP thường được nhận diện bằng cặp IP/cổng hai đầu trong ngữ cảnh giao thức. Không thể kết luận dịch vụ an toàn chỉ vì dùng cổng quen thuộc. Khi kiểm tra kết nối, phân biệt không tới được host, không có dịch vụ lắng nghe, bị lọc và sai giao thức ứng dụng.

## 1. Nhận diện phiên trao đổi
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
Tự luyện: vẽ hai client cùng dùng nguồn 51000 nhưng IP khác, kết nối server:443; chỉ ra vì sao không trùng phiên. Nộp thiết kế tách thông điệp dạng độ dài và ví dụ nhận thành ba mảnh. Đáp án cần giữ bộ đệm tới khi đủ độ dài, không parse ngay mảnh đầu.

## Bài tập vận dụng bổ sung
Vẽ ba bước bắt tay. Giải thích tại sao hai lần ghi dữ liệu ở ứng dụng không bảo đảm bên nhận có đúng hai lần đọc tương ứng. Chỉ thử kết nối tới dịch vụ lab bạn được phép dùng.

## Hướng giải bài tập bổ sung
TCP là luồng byte; ứng dụng phải đóng khung thông điệp. Bắt tay thành công chưa chứng minh đăng nhập hoặc nghiệp vụ thành công.

## Câu hỏi tự kiểm tra
1. Cổng ở tầng giao vận giúp phân biệt điều gì?
2. Bắt tay TCP điển hình có thứ tự nào?
3. TCP cung cấp kiểu dữ liệu trao đổi nào?
4. Hai client cùng truy cập cổng 443 có thể được phân biệt nhờ gì?
5. Kết nối TCP thành công chứng minh điều gì?

## Gợi ý đáp án và điểm cần nhớ
- Ứng dụng hoặc dịch vụ. Cổng tách các endpoint ứng dụng trên host.
- SYN, SYN-ACK, ACK. Ba bước đồng bộ và xác nhận mở kết nối.
- Luồng byte có thứ tự. TCP không bảo toàn ranh giới thông điệp ứng dụng.
- IP và cổng hai đầu kết nối. Các endpoint phân biệt từng kết nối TCP.
- Đã thiết lập kết nối giao vận tới endpoint. Giao vận thành công không đồng nghĩa nghiệp vụ thành công.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
