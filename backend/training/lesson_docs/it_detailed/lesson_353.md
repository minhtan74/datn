## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 6: Chẩn đoán và bài thực hành tổng hợp.
- Các bài trong chương: Chẩn đoán lỗi mạng theo từng lớp; Dự án nhỏ: thiết kế mạng cho phòng học.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Tạo giả thuyết và thu thập bằng chứng thay vì thay đổi cấu hình ngẫu nhiên.

## Kiến thức nền
Chẩn đoán bắt đầu bằng phạm vi: chỉ một máy hay nhiều máy, chỉ một dịch vụ hay toàn bộ kết nối, lỗi liên tục hay theo thời điểm. Ghi thông báo lỗi, thời gian và thay đổi gần nhất trước khi thử sửa.

Kiểm tra lần lượt liên kết, cấu hình địa chỉ và gateway, đường đi IP, phân giải DNS, kết nối cổng và phản hồi ứng dụng. ping dùng ICMP nên thất bại có thể do bị lọc, không đủ để khẳng định host tắt. nslookup giúp khảo sát DNS; curl có thể quan sát phản hồi HTTP. Tên và tùy chọn lệnh phụ thuộc hệ điều hành.

Chỉ đổi một yếu tố mỗi lần, đo lại rồi ghi kết quả. Nếu truy cập IP được nhưng tên miền không phân giải, DNS là giả thuyết hợp lý, chưa phải kết luận cuối cùng cho mọi lỗi trình duyệt. Không xóa dữ liệu hoặc thay đổi hàng loạt chỉ để thử vận may.

## 1. Quy trình thu thập bằng chứng
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
Báo cáo cần giả thuyết ban đầu, bằng chứng phản bác hoặc hỗ trợ, nguyên nhân xác nhận được, cách sửa và kiểm tra sau sửa. Không ghi “đã reset và thấy ổn” như một lời giải đầy đủ.

## Bài tập vận dụng bổ sung
Lập checklist cho ba lỗi lab: sai gateway, sai DNS và server HTTP ngừng chạy. Với mỗi lỗi, dự đoán phép thử nào phân biệt được nó với hai lỗi còn lại.

## Hướng giải bài tập bổ sung
Sai DNS có thể vẫn kết nối được IP; server dừng có thể DNS vẫn trả lời. ping không thay thế kiểm tra cổng và HTTP.

## Câu hỏi tự kiểm tra
1. Bước đầu khi chẩn đoán nên là gì?
2. ping thất bại có chắc host đã tắt không?
3. Công cụ nào phù hợp khảo sát phân giải tên?
4. DNS trả lời đúng nhưng web không mở, cần kiểm tra thêm gì?
5. Vì sao chỉ thay một yếu tố mỗi lần?

## Gợi ý đáp án và điểm cần nhớ
- Xác định phạm vi và ghi nhận hiện tượng. Xác định phạm vi giúp thu hẹp nguyên nhân.
- Không, ICMP có thể bị lọc. Một phép thử ICMP không đủ kết luận trạng thái mọi dịch vụ.
- nslookup. nslookup hỏi dịch vụ DNS.
- Kết nối cổng và phản hồi ứng dụng. DNS chỉ là một bước trong chuỗi truy cập dịch vụ.
- Giúp xác định tác động của thay đổi. Thay đổi có kiểm soát giữ khả năng so sánh trước và sau.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
