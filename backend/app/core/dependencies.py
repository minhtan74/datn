"""Dependency xác thực — thay cho JwtMiddleware / RoleMiddleware của bản PHP."""
from typing import Any

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from .database import get_db, q_one
from .responses import ApiError
from .security import decode_token


# Bắt buộc đăng nhập: đọc token từ header "Authorization: Bearer <token>" và trả về thông tin user
def get_current_user(request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    # Không có header Authorization hợp lệ -> chưa đăng nhập (401)
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise ApiError("Chưa đăng nhập. Vui lòng cung cấp mã token hợp lệ.", 401)

    # Giải mã token (bỏ 7 ký tự "Bearer "); sai chữ ký hoặc hết hạn -> 401
    payload = decode_token(auth[7:])
    if not payload:
        raise ApiError("Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.", 401)

    # Đối chiếu DB để việc khóa / xóa / đổi quyền có hiệu lực ngay, không chờ token hết hạn.
    user = q_one(
        db,
        "SELECT id, fullname, email, role, is_active FROM users WHERE id = :id",
        id=payload.get("id"),
    )
    if not user:
        raise ApiError("Tài khoản không còn tồn tại. Vui lòng đăng nhập lại.", 401)
    if not user["is_active"]:
        raise ApiError("Tài khoản của bạn đã bị khóa.", 401)

    # Lấy tên, email, vai trò mới nhất từ DB (đè lên giá trị cũ lưu trong token)
    return {**payload, "fullname": user["fullname"], "email": user["email"], "role": user["role"]}


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> dict[str, Any] | None:
    """Như get_current_user, nhưng trả None khi không có token thay vì báo lỗi 401
    — dùng cho endpoint công khai có hành vi khác nhau tùy đã đăng nhập hay chưa."""
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return get_current_user(request, db)


def get_viewer(request: Request, db: Session = Depends(get_db)) -> dict[str, Any] | None:
    """Cho endpoint công khai: token hỏng/hết hạn thì coi như khách thay vì trả 401."""
    try:
        return get_current_user_optional(request, db)
    except ApiError:
        return None


# Giới hạn vai trò: dùng dạng Depends(require_roles("admin", "teacher")) trên endpoint
def require_roles(*roles: str):
    def _dep(user: dict = Depends(get_current_user)) -> dict[str, Any]:
        # Đã đăng nhập nhưng vai trò không nằm trong danh sách cho phép -> 403
        if user.get("role") not in roles:
            raise ApiError("Bạn không có quyền thực hiện thao tác này.", 403)
        return user

    return _dep
