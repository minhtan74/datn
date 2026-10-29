## Mục tiêu
Phân biệt cổng dịch vụ với địa chỉ IP; mô tả bắt tay TCP.

## Kiến thức trọng tâm
Địa chỉ IP nhận diện giao diện ở tầng mạng; cổng giúp phân biệt ứng dụng ở tầng giao vận. Một dịch vụ lắng nghe tại địa chỉ và cổng, còn client thường dùng cổng nguồn tạm thời. Cùng số cổng nhưng TCP và UDP là hai không gian khác nhau.

TCP mở kết nối điển hình bằng SYN, SYN-ACK, ACK. Số thứ tự và xác nhận hỗ trợ truyền luồng byte có thứ tự. TCP không giữ ranh giới thông điệp ứng dụng; chương trình cần tự xác định độ dài hoặc ký hiệu kết thúc thông điệp. Đóng kết nối và timeout cũng cần được xử lý.

Một phiên TCP thường được nhận diện bằng cặp IP/cổng hai đầu trong ngữ cảnh giao thức. Không thể kết luận dịch vụ an toàn chỉ vì dùng cổng quen thuộc. Khi kiểm tra kết nối, phân biệt không tới được host, không có dịch vụ lắng nghe, bị lọc và sai giao thức ứng dụng.

## Ví dụ có hướng dẫn
Client 192.168.1.20:51000 kết nối server:443 bằng TCP. Một client khác có thể cùng truy cập server:443 nhưng có địa chỉ hoặc cổng nguồn khác; server không nhầm hai phiên.

## Bài tập thực hành
Vẽ ba bước bắt tay. Giải thích tại sao hai lần ghi dữ liệu ở ứng dụng không bảo đảm bên nhận có đúng hai lần đọc tương ứng. Chỉ thử kết nối tới dịch vụ lab bạn được phép dùng.

## Gợi ý tự kiểm tra
TCP là luồng byte; ứng dụng phải đóng khung thông điệp. Bắt tay thành công chưa chứng minh đăng nhập hoặc nghiệp vụ thành công.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP