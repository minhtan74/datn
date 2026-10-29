## Mục tiêu
Tạo giả thuyết và thu thập bằng chứng thay vì thay đổi cấu hình ngẫu nhiên.

## Kiến thức trọng tâm
Chẩn đoán bắt đầu bằng phạm vi: chỉ một máy hay nhiều máy, chỉ một dịch vụ hay toàn bộ kết nối, lỗi liên tục hay theo thời điểm. Ghi thông báo lỗi, thời gian và thay đổi gần nhất trước khi thử sửa.

Kiểm tra lần lượt liên kết, cấu hình địa chỉ và gateway, đường đi IP, phân giải DNS, kết nối cổng và phản hồi ứng dụng. ping dùng ICMP nên thất bại có thể do bị lọc, không đủ để khẳng định host tắt. nslookup giúp khảo sát DNS; curl có thể quan sát phản hồi HTTP. Tên và tùy chọn lệnh phụ thuộc hệ điều hành.

Chỉ đổi một yếu tố mỗi lần, đo lại rồi ghi kết quả. Nếu truy cập IP được nhưng tên miền không phân giải, DNS là giả thuyết hợp lý, chưa phải kết luận cuối cùng cho mọi lỗi trình duyệt. Không xóa dữ liệu hoặc thay đổi hàng loạt chỉ để thử vận may.

## Ví dụ có hướng dẫn
Một máy không vào được website nhưng máy bên cạnh được. So sánh IP/mask/gateway/DNS, kiểm tra resolver và kết nối tới dịch vụ. Ghi rõ bước nào thành công trước khi thay DNS.

## Bài tập thực hành
Lập checklist cho ba lỗi lab: sai gateway, sai DNS và server HTTP ngừng chạy. Với mỗi lỗi, dự đoán phép thử nào phân biệt được nó với hai lỗi còn lại.

## Gợi ý tự kiểm tra
Sai DNS có thể vẫn kết nối được IP; server dừng có thể DNS vẫn trả lời. ping không thay thế kiểm tra cổng và HTTP.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://www.netacad.com/courses/networking-basics
https://developer.mozilla.org/en-US/docs/Web/HTTP