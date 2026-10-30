# Kiểm tra Quản lý giao dịch Admin — 30/10/2026

**Cập nhật:** đã sửa an toàn hoàn tiền, phạm vi đối soát, dữ liệu chi tiết và phản hồi chậm
trong [các mục 1–4](admin-fixes-1-4.md). Các lỗi và bằng chứng bên dưới là trạng thái trước sửa.

Đã kiểm tra danh sách thực tế trên localhost và dùng dữ liệu tạm/cổng VNPay giả lập cho các thao tác
đối soát, hoàn tiền. Xác nhận **6 vấn đề** dưới đây. Lượt này chỉ kiểm tra và ghi nhận, chưa sửa mã chức năng.

**Cập nhật sau kiểm tra:** theo yêu cầu chỉ dùng VNPay, danh sách `/manage` đã được giới hạn
VNPay mặc định, kể cả khi không truyền phương thức. Giao diện gửi rõ `method=vnpay`;
số tab, doanh thu và phân trang cùng phạm vi. Dữ liệu phương thức cũ giữ nguyên trong DB.
Kiểm thử hồi quy với dữ liệu trộn VNPay/card/bank_transfer/momo/zalopay đã đạt;
các vấn đề 1–6 bên dưới vẫn là các hạng mục riêng chưa sửa trong thay đổi này.

## 1. Cao — Hai yêu cầu hoàn tiền đồng thời đều gọi sang VNPay

Backend đọc trạng thái `completed`, gọi cổng thanh toán, rồi mới cập nhật có điều kiện.
Hai request chạy đồng thời cùng vượt qua bước đọc và cùng gửi yêu cầu hoàn tiền.
Tái hiện: **2 lần gọi cổng giả lập**, sau đó **1 HTTP 200 và 1 HTTP 409** ở ứng dụng.
Điều kiện SQL ngăn cập nhật DB lần hai nhưng không ngăn yêu cầu gửi ra ngoài lần hai.

Đây là bằng chứng gửi trùng yêu cầu; **chưa phải bằng chứng ngân hàng đã hoàn tiền hai lần**.
Cổng thật có thể từ chối yêu cầu trùng. Nên có trạng thái xử lý/idempotency bền vững trước khi gọi cổng,
và quy trình đối soát khi timeout, tránh tự gửi lại khi chưa biết kết quả.

Mã: [payments.py:579](../backend/app/routers/payments.py#L579),
[cập nhật sau lời gọi cổng](../backend/app/routers/payments.py#L597).

## 2. Cao — Cập nhật hoàn tiền và thu hồi quyền học không nguyên tử

Sau khi cập nhật `refunded`, helper `execute()` commit ngay. Bước xóa ghi danh chạy trong lần commit khác.
Giả lập lỗi DB ở bước xóa ghi danh: API trả **HTTP 500**, đơn đã **refunded** nhưng học viên **vẫn có quyền học**,
dù yêu cầu đã chọn thu hồi. Đây là tái hiện bằng chèn lỗi có kiểm soát, không phải khẳng định lỗi luôn xảy ra.

Nên cập nhật trạng thái đơn, thông tin hoàn tiền và quyền học trong một giao dịch DB; đồng thời lưu bền vững
kết quả cổng/nhu cầu sửa trạng thái nếu cổng đã hoàn tiền nhưng DB chưa hoàn tất.

Mã: [payments.py:597](../backend/app/routers/payments.py#L597),
[bước thu hồi riêng](../backend/app/routers/payments.py#L616).

## 3. Vừa — Nút đối soát hiển thị số theo bộ lọc nhưng xử lý toàn bộ đơn chờ

Giao diện hiện **“Đối soát 1 đơn đang chờ”** sau khi tìm một đơn. Request gửi đến
`POST /api/payments/reconcile-pending` không mang bộ lọc, và backend chọn toàn bộ đơn `pending`.
Trong kiểm tra đã giới hạn backend vào khóa học tạm để bảo vệ dữ liệu thật: chỉ hiện **1**, nhưng có **7** đơn tạm được hỏi cổng.

Nên cho Admin chọn rõ đối soát các đơn đang lọc hoặc toàn bộ hệ thống; số lượng và xác nhận phải khớp phạm vi thực tế.

Mã: [nhãn nút](../frontend/src/pages/admin/Payments.jsx#L232),
[request](../frontend/src/pages/admin/Payments.jsx#L134),
[phạm vi backend](../backend/app/routers/payments.py#L497).

## 4. Vừa — Mở lại đơn hoàn tiền bị thiếu thông tin lịch sử

API `/manage` không trả `refunded_at`, `refund_reason`, `refund_txn_no` dù các giá trị có trong DB.
Modal lấy thẳng dòng danh sách để hiển thị nên ngày, lý do và mã hoàn tiền thành dấu `—`.
Phản hồi ngay sau hoàn tiền có `p.*` nên có thể thấy đủ lúc vừa thao tác, nhưng thiếu khi tải lại/mở từ danh sách.

Nên bổ sung các trường hoặc có API chi tiết riêng.

Mã: [các cột trả về](../backend/app/routers/payments.py#L399),
[modal đọc dữ liệu hoàn tiền](../frontend/src/pages/admin/Payments.jsx#L377).

## 5. Vừa — Kết quả đối soát đơn cũ thay thế đơn đang xem

Tái hiện trên trình duyệt: mở đơn A → bắt đầu đối soát → đóng modal → mở đơn B → phản hồi A trả về.
Modal đang xem B bị thay thành **A** vì `setDetail(res.data.data)` không kiểm tra đơn hiện đang mở.
Hàm hoàn tiền cũng dùng cách cập nhật tương tự; lượt này tái hiện trực tiếp ở nhánh đối soát.

Nên gắn phản hồi với ID đơn và phiên modal hiện tại; thao tác đang chạy không được thay dữ liệu đơn khác.

Mã: [đối soát](../frontend/src/pages/admin/Payments.jsx#L149),
[hoàn tiền](../frontend/src/pages/admin/Payments.jsx#L183).

## 6. Thấp — Lỗi tải danh sách vẫn giữ tổng số và doanh thu cũ

Giả lập tải bộ lọc mới trả HTTP 500: có cảnh báo lỗi, bảng rỗng, nhưng trang vẫn hiện
**“Tìm thấy 40 giao dịch”** và doanh thu/số tab từ lượt tải thành công trước.
Các số đó không phản ánh bộ lọc hiện tại và có thể gây nhầm lẫn.

Nên ẩn số liệu khi chưa tải được bộ lọc hiện tại, hoặc đánh dấu rõ dữ liệu cũ và cho thử lại.

Mã: [nhánh lỗi chỉ xóa rows](../frontend/src/pages/admin/Payments.jsx#L109),
[tổng số hiển thị](../frontend/src/pages/admin/Payments.jsx#L277).

## Phần hoạt động trong phạm vi kiểm tra

- Danh sách Admin tải được: 20 dòng trên trang thực tế; mở chi tiết được.
- Bộ lọc trạng thái/khóa học/ngày, tìm mã đơn/mã VNPay, phân trang, số tab và doanh thu khớp dữ liệu tạm.
- API chặn khách chưa đăng nhập; Teacher/Student không được quản lý, đối soát hoặc hoàn tiền.
- Kiểm thử thanh toán cũ: **4/4 đạt**. Các kiểm thử này chưa phát hiện những tình huống cạnh tranh/lỗi nêu trên.
- Kiểm tra sâu: **28 phép kiểm tra API** và **18 phép kiểm tra trình duyệt**, gồm cả xác nhận lỗi.
  Không hiểu các con số này là chứng nhận chức năng không còn lỗi.
- Không có JavaScript exception; giao diện và modal ở 390px không tràn ngang.
- Không gọi cổng VNPay thật, không chuyển/hoàn tiền thật. Đã dọn tài khoản, khóa học và giao dịch tạm;
  kiểm tra cuối còn **0** bản ghi fixture.

Bằng chứng: [API](admin-payments-api-audit.json), [trình duyệt](admin-payments-browser-audit.json),
[4 kiểm thử cũ](admin-payments-existing-tests.xml), [modal bị thay đơn](admin-payments-stale-detail.png),
[số liệu cũ khi lỗi](admin-payments-stale-totals.png), [mobile](admin-payments-mobile.png).
Script tái hiện: [API](admin-payments-api-audit.py), [trình duyệt](admin-payments-browser-audit.cjs).
