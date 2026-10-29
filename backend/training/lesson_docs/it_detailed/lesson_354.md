## Vị trí bài học trong khóa
- Khóa học: Mạng máy tính cơ bản.
- Chương 6: Chẩn đoán và bài thực hành tổng hợp.
- Các bài trong chương: Chẩn đoán lỗi mạng theo từng lớp; Dự án nhỏ: thiết kế mạng cho phòng học.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Tổng hợp địa chỉ, phân vùng, dịch vụ và kiểm tra nghiệm thu thành một phương án mạng.

## Kiến thức nền
Một thiết kế nhập môn cần danh sách thiết bị, nhóm người dùng, nhu cầu truy cập và sơ đồ logic. Tách yêu cầu khỏi giải pháp: số máy và nhu cầu của khách là yêu cầu; VLAN và dải IP là lựa chọn triển khai. Không cấp địa chỉ trước khi ước lượng số host cần dùng.

Chọn các mạng con không chồng lấn, địa chỉ gateway, vùng DHCP và địa chỉ dành riêng cho hạ tầng. Ghi resolver DNS, đường ra Internet và các luồng bị giới hạn. Đề xuất vị trí AP dựa trên khảo sát, không chỉ số lượng thiết bị.

Bàn giao gồm sơ đồ, bảng địa chỉ, chính sách, kế hoạch kiểm tra và cách khôi phục. Chất lượng được đánh giá bằng bằng chứng: máy học viên có cấu hình đúng, web hoạt động, khách bị cách ly và lỗi có thể được chẩn đoán. Quiz chỉ kiểm tra quyết định thiết kế, không tự chấm sản phẩm thực hành.

## 1. Đề bài và phạm vi sản phẩm
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
Chấm theo bốn nhóm: thiết kế đáp ứng yêu cầu; địa chỉ và dịch vụ nhất quán; phân vùng được kiểm chứng; hồ sơ tái hiện được. Không coi đạt quiz là hoàn thành cấu hình. Lời giải tốt có cả ca Student vào LMS thành công và Guest vào quản trị bị chặn; nếu dùng giả lập phải ghi giới hạn so với thiết bị thật. Ghi rõ phần chưa kiểm tra thay vì tự điền kết quả thành công.

## Bài tập vận dụng bổ sung
Nộp sơ đồ hai vùng, bảng IP/gateway/DHCP, ba quy tắc truy cập và năm ca nghiệm thu. Thực hiện bằng mô phỏng hoặc mạng lab được phép; ghi ảnh bằng chứng không chứa bí mật.

## Hướng giải bài tập bổ sung
Tiêu chí đạt: dải IP không trùng; gateway thuộc mạng host; DHCP không cấp địa chỉ dành riêng; có cả kiểm tra được phép, bị chặn và tình huống DNS lỗi.

## Câu hỏi tự kiểm tra
1. Trước khi chọn mạng con cần biết gì?
2. Hai mạng con dùng cho hai vùng nên có đặc điểm gì?
3. DHCP pool cần tránh cấp gì?
4. Nghiệm thu cách ly khách cần làm gì?
5. Quiz của dự án có tự chứng nhận cấu hình thực tế đúng không?

## Gợi ý đáp án và điểm cần nhớ
- Số host và nhu cầu kết nối. Yêu cầu dung lượng và luồng truy cập quyết định thiết kế.
- Không chồng lấn địa chỉ. Dải không chồng lấn giúp định tuyến và quản lý rõ ràng.
- Địa chỉ đã dành riêng cho hạ tầng. Tránh xung đột giữa cấp động và địa chỉ dành riêng.
- Thử cả truy cập Internet và truy cập nội bộ bị cấm. Cần chứng minh chức năng và ràng buộc đều hoạt động.
- Không, cần sản phẩm và bằng chứng thực hành. Câu hỏi lý thuyết không thay thế kiểm chứng triển khai.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://www.netacad.com/courses/networking-basics
- https://developer.mozilla.org/en-US/docs/Web/HTTP
