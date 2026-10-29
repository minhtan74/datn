## Mục tiêu
Tổng hợp địa chỉ, phân vùng, dịch vụ và kiểm tra nghiệm thu thành một phương án mạng.

## Kiến thức trọng tâm
Một thiết kế nhập môn cần danh sách thiết bị, nhóm người dùng, nhu cầu truy cập và sơ đồ logic. Tách yêu cầu khỏi giải pháp: số máy và nhu cầu của khách là yêu cầu; VLAN và dải IP là lựa chọn triển khai. Không cấp địa chỉ trước khi ước lượng số host cần dùng.

Chọn các mạng con không chồng lấn, địa chỉ gateway, vùng DHCP và địa chỉ dành riêng cho hạ tầng. Ghi resolver DNS, đường ra Internet và các luồng bị giới hạn. Đề xuất vị trí AP dựa trên khảo sát, không chỉ số lượng thiết bị.

Bàn giao gồm sơ đồ, bảng địa chỉ, chính sách, kế hoạch kiểm tra và cách khôi phục. Chất lượng được đánh giá bằng bằng chứng: máy học viên có cấu hình đúng, web hoạt động, khách bị cách ly và lỗi có thể được chẩn đoán. Quiz chỉ kiểm tra quyết định thiết kế, không tự chấm sản phẩm thực hành.

## Ví dụ có hướng dẫn
Một phòng có 20 máy học viên và một nhóm khách. Có thể dùng hai mạng /24 riêng trong lab để dễ quản lý, nhưng phải nêu đây là lựa chọn đơn giản hóa chứ không phải phương án tiết kiệm địa chỉ tối ưu.

## Bài tập thực hành
Nộp sơ đồ hai vùng, bảng IP/gateway/DHCP, ba quy tắc truy cập và năm ca nghiệm thu. Thực hiện bằng mô phỏng hoặc mạng lab được phép; ghi ảnh bằng chứng không chứa bí mật.

## Gợi ý tự kiểm tra
Tiêu chí đạt: dải IP không trùng; gateway thuộc mạng host; DHCP không cấp địa chỉ dành riêng; có cả kiểm tra được phép, bị chặn và tình huống DNS lỗi.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP