"""/api/auth/* — port của app/Controllers/AuthController.php."""
import re

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.core.database import execute, get_db, q_one
from app.core.dependencies import get_current_user
from app.core.responses import ApiError, ok
from app.core.security import create_token, hash_password, verify_password

from ._common import sv

router = APIRouter(prefix="/api/auth", tags=["auth"])


# Tìm user theo email (dùng khi đăng nhập và kiểm tra email trùng khi đăng ký)
def _find_by_email(db: Session, email: str) -> dict | None:
    return q_one(db, "SELECT * FROM users WHERE email = :email LIMIT 1", email=email)


# POST /api/auth/login — đăng nhập bằng email + mật khẩu, trả về token JWT và thông tin user
@router.post("/login")
def login(body: dict = Body(default={}), db: Session = Depends(get_db)):
    email = sv(body, "email")
    password = sv(body, "password")
    if not email or not password:
        raise ApiError("Email và mật khẩu không được để trống.")

    # Không tìm thấy email hoặc sai mật khẩu -> cùng một thông báo (không tiết lộ email có tồn tại hay không)
    user = _find_by_email(db, email)
    if not user or not verify_password(password, user["password"]):
        raise ApiError("Email hoặc mật khẩu không chính xác.", 401)
    # Tài khoản bị admin khóa thì không cho đăng nhập
    if not user["is_active"]:
        raise ApiError("Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.", 403)

    # Cấp token; frontend lưu token vào localStorage và gửi kèm mọi request sau
    token = create_token(user)
    return ok(
        token=token,
        user={
            "id": user["id"],
            "fullname": user["fullname"],
            "email": user["email"],
            "role": user["role"],
        },
    )


# POST /api/auth/register — đăng ký tài khoản mới (luôn là học viên)
@router.post("/register")
def register(body: dict = Body(default={}), db: Session = Depends(get_db)):
    fullname = sv(body, "fullname")
    email = sv(body, "email")
    password = sv(body, "password")
    confirm = sv(body, "confirm_password")

    # Kiểm tra dữ liệu: đủ trường, mật khẩu khớp, đủ độ dài, email đúng định dạng, email chưa bị dùng
    if not fullname or not email or not password or not confirm:
        raise ApiError("Vui lòng nhập đầy đủ thông tin.")
    if password != confirm:
        raise ApiError("Mật khẩu xác nhận không khớp.")
    if len(password) < 6:
        raise ApiError("Mật khẩu phải có ít nhất 6 ký tự.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ApiError("Email không hợp lệ.")
    if _find_by_email(db, email):
        raise ApiError("Email này đã được đăng ký.", 409)

    # Lưu user mới với mật khẩu đã băm bcrypt; vai trò cố định 'student' (không nhận role từ client)
    execute(
        db,
        "INSERT INTO users (fullname, email, password, role) "
        "VALUES (:fullname, :email, :password, 'student')",
        fullname=fullname,
        email=email,
        password=hash_password(password),
    )
    return ok("Đăng ký thành công! Hãy đăng nhập.")


# GET /api/auth/me — thông tin user đang đăng nhập (lấy mới từ DB qua get_current_user)
@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return ok(
        user={
            "id": user["id"],
            "fullname": user["fullname"],
            "email": user["email"],
            "role": user["role"],
        }
    )


# POST /api/auth/logout — JWT không lưu phía server nên chỉ trả thông báo; frontend tự xóa token
@router.post("/logout")
def logout():
    return ok("Đăng xuất thành công.")


# POST /api/auth/change-password — user tự đổi mật khẩu (phải nhập đúng mật khẩu cũ)
@router.post("/change-password")
def change_password(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    old_password = sv(body, "old_password")
    new_password = sv(body, "new_password")

    if not old_password or not new_password:
        raise ApiError("Vui lòng nhập đầy đủ mật khẩu cũ và mới.")
    if len(new_password) < 6:
        raise ApiError("Mật khẩu mới phải có ít nhất 6 ký tự.")

    # Xác minh mật khẩu cũ trước khi cho đổi
    row = q_one(db, "SELECT password FROM users WHERE id = :id", id=user["id"])
    if not row or not verify_password(old_password, row["password"]):
        raise ApiError("Mật khẩu hiện tại không đúng.", 400)

    # Lưu mật khẩu mới đã băm
    execute(
        db,
        "UPDATE users SET password = :pw WHERE id = :id",
        pw=hash_password(new_password),
        id=user["id"],
    )
    return ok("Đổi mật khẩu thành công!")
