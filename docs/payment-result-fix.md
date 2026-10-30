# Sửa vấn đề số 1: thông báo kết quả thanh toán

Trang kết quả từng gộp đơn đang chờ và lỗi mạng vào nhánh thất bại, đồng thời khẳng định
người học chưa bị trừ tiền. Đã tách kết quả theo trạng thái đơn lấy từ API:

| Tình trạng | Hiển thị và hành động |
|---|---|
| `completed`, có quyền học | Thành công, liên kết Vào học ngay |
| `completed`, chưa xác nhận quyền học | Thành công, hướng dẫn kiểm tra lại quyền truy cập/liên hệ Admin |
| `pending` | Đang chờ xác nhận, nút Kiểm tra lại trạng thái |
| `failed` | Không thành công, hướng dẫn kiểm tra lịch sử ngân hàng trước khi thanh toán lại |
| `refunded` | Đã hoàn tiền, thông báo thời điểm tiền về phụ thuộc ngân hàng |
| Mất mạng, timeout, lỗi API, không tìm thấy đơn, phản hồi sai/thiếu hoặc trạng thái lạ | Chưa xác minh được thanh toán, cho kiểm tra lại nếu có mã đơn |
| Thiếu mã đơn | Chưa xác minh được, hướng dẫn kiểm tra liên kết/liên hệ Admin; không gọi API thiếu mã |

Không suy ra số dư ngân hàng từ trạng thái trang. `status`/`reason` trên URL không quyết định
kết quả hiển thị. Chỉ dùng phản hồi thành công đúng mã đơn; không hiển thị thông tin đơn khác.
Yêu cầu đọc trạng thái có thời gian chờ 15 giây, hủy khi rời trang/đổi mã đơn, bỏ qua kết quả cũ trả muộn.
Nút kiểm tra lại chỉ đọc trạng thái đơn hiện tại; không tạo đơn mới hoặc gọi thanh toán.

## Kiểm chứng trên localhost — 30/10/2026

- **46/46 kiểm tra trình duyệt đạt**, 0 JavaScript exception, 0 request ghi thanh toán.
- Kiểm tra đủ các trạng thái, mất mạng rồi khôi phục, timeout, HTTP 404/500, phản hồi sai,
  sửa tham số URL, thanh toán thành công nhưng chưa có quyền học, thiếu mã và đổi mã khi request cũ chưa xong.
- Kiểm tra mobile 390px không tràn ngang.
- Build production thành công; còn cảnh báo font/CSS và bundle lớn đã có trước.
- Trạng thái thanh toán được giả lập có kiểm soát; không tạo đơn, chuyển tiền hay hoàn tiền thật.

Bằng chứng: [kết quả kiểm tra](payment-result-browser-results.json),
[đơn đang chờ](payment-result-pending.png), [lỗi mạng trên mobile](payment-result-network-mobile.png).
Script tái kiểm tra: [payment-result-browser.cjs](payment-result-browser.cjs).

Mã sửa: [PaymentResult.jsx](../frontend/src/pages/student/PaymentResult.jsx),
[paymentService.js](../frontend/src/services/paymentService.js).
