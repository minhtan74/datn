# Rà soát breadcrumb toàn website

Đã bỏ breadcrumb trong `AdminTopbar` và giữ breadcrumb phía dưới ở đầu nội dung từng trang.
Thay đổi áp dụng chung cho Dashboard, Quản lý người dùng (tất cả/Giảng viên/Học viên),
Quản lý khóa học, Quản lý giao dịch và Báo cáo. Thanh trên cùng tiếp tục có menu, lời chào và avatar.

Rà soát mã nguồn các layout và trang của Admin, Giảng viên, Học viên và khu vực công khai:
phần lặp đến từ topbar Admin; các layout còn lại không có breadcrumb thứ hai cần gỡ.

Kiểm chứng bằng Chromium trên localhost:

- **84 lượt xem**: 42 đường dẫn ở desktop 1440px và mobile 390px, gồm các đường dẫn chuyển hướng cũ.
- Bao phủ khu vực công khai, 7 trang Admin chính, các trang Giảng viên/Học viên,
  trang chương, bài học, giới thiệu quiz, kết quả quiz và câu hỏi quiz của Giảng viên.
- **0 trang có breadcrumb trùng**, 0 trang có JavaScript exception, 0 trang tràn ngang.
- Các trang Admin và đường dẫn chuyển hướng đều còn đúng 1 breadcrumb trong nội dung chính,
  không còn breadcrumb trong header.
- Build frontend thành công; còn cảnh báo font/CSS và bundle lớn có từ trước.
- Chặn các request ghi API từ trang trong lúc rà soát; không nộp quiz, cập nhật tiến độ,
  thanh toán hay chỉnh sửa dữ liệu thật.

Phạm vi là breadcrumb, tải trang và bố cục; không phải kiểm thử lại toàn bộ nghiệp vụ của website.

Bằng chứng: [kết quả 84 lượt xem](breadcrumb-site-audit.json),
[Admin desktop](breadcrumb-admin-desktop.png), [Admin mobile](breadcrumb-admin-mobile.png).
