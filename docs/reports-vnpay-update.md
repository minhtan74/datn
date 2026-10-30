# Báo cáo VNPay — thay biểu đồ phương thức

Đã thay “Doanh thu theo phương thức” bằng **Tình trạng giao dịch VNPay** vì website chỉ sử dụng
một phương thức thanh toán. Biểu đồ đếm số đơn theo bốn trạng thái thành công, đang chờ,
thất bại, đã hoàn tiền; số lượng hiển thị bằng chữ bên dưới để đọc được cả trạng thái có 0 đơn.
Ghi rõ phạm vi toàn bộ thời gian, độc lập bộ chọn thời gian của biểu đồ doanh thu bên cạnh.
Khi chưa có giao dịch, hiển thị thông báo thay vì vẽ vòng tròn không có dữ liệu.

Đồng bộ phần tài chính của báo cáo về VNPay:

- Tổng doanh thu, số đơn, số tiền hoàn và thống kê trạng thái.
- Biểu đồ doanh thu hôm nay, 7 ngày, 30 ngày và 12 tháng.
- Doanh thu xếp hạng khóa học, danh sách giao dịch và CSV giao dịch/khóa học.

Doanh thu chỉ tính đơn VNPay đang ở trạng thái `completed`; đơn hoàn tiền không tính trong doanh thu này.
Giữ nguyên dữ liệu phương thức cũ trong DB. API `revenue_by_method` vẫn giữ để tương thích,
nhưng chỉ trả VNPay và giao diện không còn dùng nó để so sánh phương thức.
Các thống kê học tập, học viên và ghi danh tiếp tục tính toàn hệ thống.

Kiểm chứng localhost ngày 30/10/2026:

- 3 kiểm thử backend đạt, gồm kiểm tra danh sách và báo cáo với dữ liệu trộn VNPay/card/bank_transfer/momo/zalopay.
  Bao phủ KPI, bốn khoảng biểu đồ, doanh thu khóa học và CSV; dọn dữ liệu tạm sau kiểm tra.
- 19 kiểm tra trình duyệt đạt: khớp số lượng và doanh thu với Quản lý giao dịch,
  không còn biểu đồ/nhãn phương thức cũ, đổi khoảng thời gian, tải CSV, mobile,
  dữ liệu rỗng và chỉ có một trạng thái. Không có JavaScript exception.
- Build production thành công; còn cảnh báo font/CSS và kích thước bundle đã có trước.
- Không tạo hay thực hiện thanh toán/hoàn tiền thật.

Bằng chứng: [kết quả trình duyệt](reports-vnpay-browser-results.json),
[desktop](reports-vnpay-status.png), [mobile](reports-vnpay-status-mobile.png).
