## Mục tiêu
Đề xuất chính sách truy cập tối thiểu trong một mạng lab.

## Kiến thức trọng tâm
Tường lửa cho phép hoặc chặn lưu lượng theo chính sách như IP, cổng, giao thức và trạng thái kết nối. Chính sách nên xuất phát từ luồng nghiệp vụ cần thiết thay vì mở mọi cổng để thử. Stateful firewall theo dõi trạng thái để xử lý lưu lượng phản hồi phù hợp.

Phân vùng đặt thiết bị có nhu cầu và mức tin cậy khác nhau vào vùng riêng. Mạng khách thường chỉ cần Internet, không cần truy cập máy chủ quản trị nội bộ. Quyền tối thiểu nghĩa là chỉ cấp truy cập cần cho công việc, rồi kiểm tra cả luồng được phép và luồng phải bị chặn.

Ghi log có ích nhưng phải tránh lưu mật khẩu và token. Thay đổi chính sách cần kế hoạch khôi phục, đặc biệt nếu đang quản trị từ xa. HTTPS bảo vệ đường truyền, tường lửa kiểm soát luồng; hai công cụ không thay thế nhau. Không tiến hành quét hoặc thử vượt quyền trên mạng bên ngoài phạm vi được cho phép.

## Ví dụ có hướng dẫn
Mạng Guest được phép DNS tới resolver chỉ định và web ra Internet; bị chặn truy cập vùng quản trị. Kiểm tra từ thiết bị Guest và thiết bị quản trị để tránh một chính sách nhầm ảnh hưởng cả hai.

## Bài tập thực hành
Viết bảng nguồn, đích, giao thức/cổng và quyết định cho ba luồng: học viên mở web, khách vào trang quản trị nội bộ, quản trị viên kết nối máy lab. Ghi cách kiểm tra và hoàn nguyên.

## Gợi ý tự kiểm tra
Không chỉ kiểm tra có thể truy cập web; cần xác nhận khách bị chặn đúng vùng. Không dùng việc NAT hoạt động để kết luận chính sách đã an toàn.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP