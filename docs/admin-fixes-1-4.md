# Hoàn tất các mục 1–4

Giữ luồng Admin xử lý hoàn tiền hiện tại; không thêm lại chức năng Học viên gửi yêu cầu/xét duyệt.
Mục 4 đã đổi theo lựa chọn mới: **người quên mật khẩu liên hệ Admin**, không dùng Gmail/SMTP.

## 1. Hoàn tiền chống trùng và phục hồi nhất quán

- Thêm migration `0023_refund_safety`, hai bảng nhật ký thao tác/lịch sử theo đơn.
- Khóa dòng và lưu trạng thái cùng mã yêu cầu trước khi gọi VNPay; hai request đồng thời chỉ một request được gửi.
- `sending/pending/unknown`: chặn gửi lại; Admin dùng **Đối soát hoàn tiền**.
- Chỉ coi hoàn tiền cuối cùng khi phản hồi đã ký của VNPay khớp merchant, lệnh, mã đơn, số tiền,
  loại hoàn toàn phần và trạng thái thành công. Tiếp nhận/đang xử lý chưa đổi đơn sang `refunded`.
- Không dùng phản hồi thanh toán gốc làm bằng chứng hoàn tiền. Mã từ chối rõ ràng mới cho Admin chủ động gửi lại.
- Lưu xác nhận cổng bền vững trước khi hoàn tất DB. Cập nhật đơn, thu hồi quyền học và trạng thái hoàn tất
  cùng giao dịch: lỗi ở một bước thì cùng rollback.
- Nếu đã có xác nhận nhưng phần DB lỗi, nút đối soát chỉ chạy lại phần DB, không gửi tiền thêm lần nữa.
- Không thu hồi nếu Admin chọn giữ quyền học hoặc còn đơn thành công khác của cùng người/khóa.
- Không ghi nhận hoàn tiền thủ công cho đơn thiếu giao dịch VNPay hợp lệ; không đổi/xóa giao dịch cũ.

Nếu truy vấn vẫn chưa có kết quả cuối cùng, giữ trạng thái cần đối soát để Admin xác minh với VNPay;
không tự mở khóa gửi lại một giao dịch chưa rõ kết quả.

Nguồn tích hợp: [API querydr/refund chính thức của VNPay](https://sandbox.vnpayment.vn/apis/docs/truy-van-hoan-tien/querydr%26refund.html).
Đây là sửa an toàn kỹ thuật cho luồng Admin, không tự đặt một chính sách hoàn tiền khóa học mới.

## 2. Đối soát đúng bộ lọc

Nút đổi thành **Đối soát N đơn chờ trong bộ lọc**, có xác nhận trước thao tác.
Gửi cùng tìm kiếm, khóa học, từ ngày/đến ngày; backend dùng chung bộ lọc với danh sách,
chỉ chọn VNPay `pending`. Không gửi trạng thái tab vào bộ lọc này: số `pending` trên các tab
đã được tính độc lập tab, nhưng vẫn theo tìm kiếm/khóa/ngày.
API trả số đơn thực tế đã chọn để đối chiếu khi dữ liệu thay đổi giữa lúc xem và bấm.
Ngày sai, khoảng đảo hoặc ngày cuối vượt phạm vi được trả lỗi rõ ràng.

## 3. Chi tiết giao dịch, phản hồi chậm và lỗi danh sách

- API danh sách/chi tiết có ngày, người thực hiện, lý do và mã hoàn tiền.
- Mở modal lấy lại dữ liệu chi tiết; ID phiên modal chặn phản hồi cũ sau khi đóng/mở đơn khác hoặc rời trang.
- Kết quả đối soát và hoàn tiền không được ghi đè modal của đơn khác.
- Khi tải lỗi/đang tải, tổng số, doanh thu và số tab hiển thị dấu trống/chờ thay vì số cũ;
  xóa phân trang cũ và có nút **Thử tải lại**.
- Modal giới hạn chiều cao, cuộn được, hiển thị trên header/sidebar; kiểm tra đóng được ở mobile.

## 4. Quên mật khẩu qua Admin quản lý

`/forgot-password` hướng dẫn liên hệ Admin, cung cấp thông tin xác minh, nhận mật khẩu được cấp,
đăng nhập rồi đổi mật khẩu trong hồ sơ. Không còn form gửi email hay API public reset token.
`/reset-password` cũ hướng dẫn liên hệ Admin và bỏ fragment token.

Admin cấp lại Teacher/Student từ Quản lý người dùng; mật khẩu băm và thu hồi phiên cũ,
giữ hồ sơ/vai trò. Admin duy nhất vẫn dùng công cụ trên máy chủ sau xác minh.
Không cần Gmail/Mật khẩu ứng dụng. Xem [hướng dẫn](password-recovery.md).

## Kiểm chứng

- **39 kiểm thử backend đạt**: cấp lại qua Admin, quyền, gửi hoàn tiền đồng thời, timeout,
  phân biệt tiếp nhận/kết quả cuối, sai phản hồi, chữ ký, rollback/phục hồi, giữ quyền học,
  bộ lọc/phạm vi đối soát, hồi quy danh sách/báo cáo và thanh toán VNPay.
- **19 kiểm tra trình duyệt đạt**: danh sách thực tế đọc được; các lỗi/chậm/thao tác tài chính giả lập;
  phản hồi đơn cũ không ghi đè đơn mới, gửi đúng bộ lọc, thông tin hoàn tiền đầy đủ,
  không gửi lại khi pending, retry danh sách, modal mobile và quên mật khẩu liên hệ Admin.
- Build frontend thành công; còn các cảnh báo font/CSS và bundle lớn có trước.
- Migration đã áp dụng trên DB local. Không hoàn/chuyển tiền thật, không đổi mật khẩu tài khoản mẫu;
  dữ liệu kiểm thử được dọn theo tài khoản/khóa học tạm.
- Chưa nghiệm thu gửi/hoàn tiền với merchant VNPay production; các kiểm tra cổng trong lượt này là giả lập.

Bằng chứng: [JUnit](admin-fixes-1-4-tests.xml), [trình duyệt](admin-fixes-1-4-browser-results.json),
[hoàn tiền mobile](admin-fixes-refund-mobile.png), [khôi phục qua Admin](admin-assisted-recovery-mobile.png).
