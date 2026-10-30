# Quên mật khẩu: liên hệ Admin quản lý

Theo lựa chọn hiện tại, website không sử dụng SMTP hoặc liên kết đặt lại mật khẩu qua email.
Trang **Đăng nhập → Quên mật khẩu?** hướng dẫn người dùng liên hệ Admin và xác minh tài khoản.

## Giảng viên và Học viên

1. Liên hệ Admin quản lý đơn vị; cung cấp email đăng ký và thông tin xác minh theo hướng dẫn.
2. Admin xác minh trước khi cấp lại; không yêu cầu mật khẩu hiện tại hoặc OTP ngân hàng.
3. Admin vào **Quản lý người dùng → chọn tài khoản → Cập nhật → Đặt lại mật khẩu**.
4. Nhập mật khẩu mới và lưu; hệ thống băm bcrypt, thu hồi các phiên cũ, giữ vai trò và hồ sơ.
5. Admin chuyển mật khẩu mới qua kênh đã xác minh. Người dùng đăng nhập rồi đổi mật khẩu
   tại Hồ sơ cá nhân. Hiện đây là hướng dẫn thao tác, chưa có cơ chế bắt buộc đổi ngay ở lần đăng nhập kế tiếp.

Không cần cấu hình Gmail/SMTP hay tạo Mật khẩu ứng dụng Google cho luồng này.
Website chưa cung cấp hệ thống ticket hỗ trợ; dùng kênh liên hệ Admin của đơn vị.

## Admin duy nhất quên mật khẩu

Không cấp lại Admin qua màn hình Quản lý người dùng. Người vận hành xác minh chủ tài khoản,
truy cập terminal máy chủ đáng tin cậy, vào thư mục `backend` và chạy:

```powershell
.venv\Scripts\python.exe scripts/recover_admin.py
```

Docker: `docker compose exec backend python scripts/recover_admin.py`.
Nhập email hai lần, sau đó nhập mật khẩu mới và xác nhận (ẩn khi nhập).
Công cụ chỉ xử lý Admin đang hoạt động, đã tồn tại; không tạo Admin, không đổi vai trò hoặc mở khóa.
Không truyền mật khẩu bằng tham số dòng lệnh hay gửi vào chat/log.

## Các đường dẫn cũ

- `/forgot-password`: trang hướng dẫn liên hệ Admin.
- `/reset-password`: thông báo không còn dùng link email, hướng dẫn liên hệ Admin và bỏ token khỏi fragment.
- API công khai `POST /api/auth/forgot-password`, `/reset-password`, `/reset-password/validate` đã gỡ,
  trả HTTP 404. Link/token cũ không còn dùng được.
- Giữ metadata phiên đăng nhập và schema migration cũ để không phá dữ liệu/lịch sử migration;
  không còn mã tạo token hoặc gửi email công khai.

Kiểm thử: [backend cấp lại mật khẩu qua Admin](../backend/tests/test_password_recovery.py),
[giao diện và các mục 1–4](admin-fixes-1-4-browser-results.json).
Các ảnh/kết quả SMTP cũ trong `docs` là bằng chứng lịch sử trước quyết định này, không còn mô tả luồng hiện tại.
