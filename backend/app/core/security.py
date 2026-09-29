"""JWT HS256 + mật khẩu (tương đương app/Services/JwtService.php + User model của PHP).

- Giữ nguyên payload {id, fullname, email, role, iat, exp} và JWT_SECRET để
  token do bản PHP phát hành vẫn dùng được.
- verify_password chấp nhận cả plaintext (dữ liệu seed) lẫn bcrypt.
"""
import time
from typing import Any

import bcrypt
from jose import JWTError, jwt

from .config import settings

# Thuật toán ký token: HMAC-SHA256 với khóa bí mật JWT_SECRET
ALGORITHM = "HS256"


# Băm mật khẩu bằng bcrypt (có salt ngẫu nhiên) trước khi lưu vào DB
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# So khớp mật khẩu người dùng nhập với giá trị lưu trong DB
def verify_password(plain: str, stored: str) -> bool:
    if plain == stored:  # dữ liệu mẫu để mật khẩu thô "123456"
        return True
    # Mật khẩu đã băm bcrypt; chuỗi lưu không đúng định dạng bcrypt -> coi như sai
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# Tạo token đăng nhập chứa id, tên, email, vai trò; iat = thời điểm tạo, exp = thời điểm hết hạn
def create_token(user: dict) -> str:
    now = int(time.time())
    payload = {
        "id": user["id"],
        "fullname": user["fullname"],
        "email": user["email"],
        "role": user["role"],
        "iat": now,
        "exp": now + int(settings.jwt_expire),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


# Giải mã và kiểm tra token: sai chữ ký, hết hạn hoặc thiếu exp -> None
def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError:
        return None
    if "exp" not in payload:
        return None
    return payload
