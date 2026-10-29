## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 1: Nền tảng kết nối mạng.
- Các bài trong chương: Mô hình TCP/IP và thiết bị mạng; Địa chỉ IPv4 và mạng con.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Phân biệt chức năng các tầng và thiết bị mạng cơ bản.

## Kiến thức nền
Mạng máy tính cho phép các thiết bị trao đổi dữ liệu theo giao thức chung. Mô hình TCP/IP thường được trình bày với bốn tầng: ứng dụng, giao vận, Internet và truy nhập mạng. HTTP và DNS thuộc tầng ứng dụng; TCP và UDP thuộc tầng giao vận; IP thực hiện địa chỉ hóa và chuyển gói ở tầng Internet.

Switch chuyển tiếp khung trong mạng LAN dựa trên địa chỉ MAC. Router chuyển tiếp gói giữa các mạng IP dựa trên bảng định tuyến. Điểm truy cập không dây kết nối thiết bị Wi-Fi vào mạng; không nên đồng nhất mọi điểm truy cập với router dù thiết bị gia đình thường tích hợp nhiều chức năng.

TCP cung cấp luồng byte có thứ tự và cơ chế truyền lại. UDP gửi datagram, không tự bảo đảm giao hàng hoặc thứ tự. Ứng dụng chọn giao thức theo nhu cầu; không thể kết luận UDP luôn tốt hơn TCP.

## 1. Từ yêu cầu người dùng đến dữ liệu trên đường truyền
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
Hãy vẽ hai host, switch, router và server; ghi địa chỉ IP, MAC và cổng ở nơi chúng có ý nghĩa. Đạt yêu cầu khi giải thích được khác nhau giữa chuyển khung trong LAN và định tuyến IP.

## Bài tập vận dụng bổ sung
vẽ đường đi từ máy tính qua switch và router tới máy chủ; ghi giao thức ứng dụng và giao vận tại mỗi đầu.

## Câu hỏi tự kiểm tra
1. HTTP thuộc tầng nào của mô hình TCP/IP?
2. Thiết bị nào thường chuyển tiếp gói giữa hai mạng IP?
3. Switch lớp 2 thường chuyển tiếp khung dựa trên thông tin nào?
4. Đặc điểm nào do TCP cung cấp?
5. Phát biểu nào đúng về UDP?

## Gợi ý đáp án và điểm cần nhớ
- Ứng dụng. HTTP quy định trao đổi thông điệp giữa ứng dụng khách và máy chủ.
- Router. Router dùng địa chỉ IP và bảng định tuyến để chuyển gói giữa các mạng.
- Địa chỉ MAC. Switch học địa chỉ MAC và cổng tương ứng trong LAN.
- Luồng byte có thứ tự và truyền lại khi cần. TCP hỗ trợ thứ tự và độ tin cậy; bản thân TCP không mã hóa dữ liệu.
- Không tự bảo đảm giao hàng và thứ tự datagram. Ứng dụng sử dụng UDP phải tự xử lý các bảo đảm bổ sung nếu cần.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
