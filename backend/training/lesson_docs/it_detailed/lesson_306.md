## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 2: Dịch vụ và ứng dụng mạng.
- Các bài trong chương: DNS và phân giải tên miền; HTTP và HTTPS.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Nhận biết request, response, phương thức và nhóm mã trạng thái.

## Kiến thức nền
HTTP tổ chức trao đổi yêu cầu và phản hồi. Request có phương thức, đường dẫn, header và có thể có body; response có mã trạng thái, header và có thể có body. GET thường dùng để lấy biểu diễn tài nguyên; POST thường gửi dữ liệu để máy chủ xử lý. Không đặt dữ liệu bí mật vào URL chỉ vì đang dùng HTTPS, vì URL có thể xuất hiện trong lịch sử và nhật ký.

Nhóm 2xx báo thành công, 3xx chuyển hướng, 4xx lỗi phía yêu cầu và 5xx lỗi máy chủ. 404 nghĩa là không tìm thấy tài nguyên theo yêu cầu; 500 là lỗi nội bộ máy chủ. Cần đọc cả phản hồi và ngữ cảnh để chẩn đoán.

HTTPS là HTTP được bảo vệ bằng TLS: hỗ trợ bảo mật đường truyền, toàn vẹn và xác thực máy chủ theo chứng thư hợp lệ. HTTPS không bảo đảm nội dung website đáng tin hoặc ứng dụng không có lỗ hổng.

## 1. Cấu trúc trao đổi
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
Với 404 kiểm tra tài nguyên và đường dẫn; với 500 thu thập mã yêu cầu và log server đã được phép xem. Cùng nhìn thấy màn hình trống không có nghĩa hai nguyên nhân giống nhau.

## Bài tập vận dụng bổ sung
mô tả một request GET lấy trang khóa học; nêu cách xử lý khác nhau khi nhận 404 và 500.

## Câu hỏi tự kiểm tra
1. Phương thức HTTP nào thường dùng để lấy tài nguyên?
2. Mã 404 thường có ý nghĩa gì?
3. Mã 500 thuộc nhóm nào?
4. HTTPS bổ sung cơ chế nào cho HTTP?
5. Một HTTP response thường chứa thành phần nào?

## Gợi ý đáp án và điểm cần nhớ
- GET. GET được thiết kế để lấy biểu diễn của tài nguyên.
- Không tìm thấy tài nguyên được yêu cầu. 404 thuộc nhóm lỗi yêu cầu 4xx.
- Lỗi máy chủ. 500 là Internal Server Error thuộc nhóm 5xx.
- Bảo vệ đường truyền bằng TLS. TLS cung cấp các bảo đảm đường truyền, không thay thế bảo mật ứng dụng.
- Mã trạng thái và header. Response có mã trạng thái, header và có thể có body.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
