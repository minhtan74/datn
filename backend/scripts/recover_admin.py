"""Server-only recovery. Run from backend: python scripts/recover_admin.py

No HTTP endpoint and no password command-line argument. Requires trusted server
access and the application's database credentials. Never creates/promotes users.
"""
import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal, q_one
from app.core.password_recovery import check_password, replace_password
from app.core.responses import ApiError


def recover(email, password, confirm):
    check_password(password, confirm)
    with SessionLocal() as db:
        user = q_one(db, "SELECT * FROM users WHERE email=:email FOR UPDATE", email=email)
        if not user or user["role"] != "admin":
            raise ApiError("Chỉ khôi phục tài khoản Admin đã tồn tại; không tạo tài khoản hoặc đổi vai trò.")
        if not user["is_active"]:
            raise ApiError("Admin đang bị khóa. Cần quy trình xử lý tài khoản bị khóa riêng.")
        replace_password(db, user["id"], password)
        db.commit()


def main():
    print("Khôi phục Admin — chỉ thực hiện trên máy chủ đáng tin cậy sau khi xác minh chủ tài khoản.")
    email = input("Email Admin: ").strip()
    if input("Nhập lại email để xác nhận thao tác: ").strip() != email:
        print("Không khớp. Đã hủy.")
        return 1
    password = getpass.getpass("Mật khẩu mới (ít nhất 6 ký tự): ")
    confirm = getpass.getpass("Xác nhận mật khẩu mới: ")
    try:
        recover(email, password, confirm)
    except ApiError as exc:
        print(exc.message)
        return 1
    except Exception:
        print("Không thể khôi phục. Kiểm tra kết nối/cấu hình DB và migration trên máy chủ.")
        return 1
    print("Đã đặt lại mật khẩu Admin và vô hiệu hóa phiên cũ. Vai trò, hồ sơ được giữ nguyên.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EOFError, KeyboardInterrupt):
        print("\nĐã hủy.")
        sys.exit(1)
