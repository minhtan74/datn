"""Admin-assisted credential recovery; public email/token recovery is disabled."""
import time
from sqlalchemy import text
from .responses import ApiError
from .security import hash_password


def check_password(password, confirm):
    if not isinstance(password, str) or len(password) < 6:
        raise ApiError("Mật khẩu phải có ít nhất 6 ký tự.")
    if len(password.encode("utf-8")) > 72:
        raise ApiError("Mật khẩu quá dài. Vui lòng dùng mật khẩu ngắn hơn.")
    if password != password.strip():
        raise ApiError("Mật khẩu không được bắt đầu hoặc kết thúc bằng khoảng trắng.")
    if password != confirm:
        raise ApiError("Mật khẩu xác nhận không khớp.")



def replace_password(db, user_id, password):
    """Caller holds the user row lock; credentials and revocation commit atomically."""
    db.execute(text("UPDATE users SET password=:pw, token_version=token_version+1 WHERE id=:id"),
               {"pw": hash_password(password), "id": user_id})
    db.execute(text("UPDATE password_reset_tokens SET used_at=:now WHERE user_id=:id AND used_at IS NULL"),
               {"now": int(time.time()), "id": user_id})
