"""Link có chữ ký cho file bài học (video / tài liệu) trong uploads/videos và uploads/documents.

Thẻ <video>/<iframe> không gửi được header Authorization, nên API trả về URL
/api/lessons/media?...&sig=... có hạn dùng; endpoint đó kiểm tra lại quyền trong DB
ở mỗi lần tải, nên người bị khóa / hoàn tiền / hủy ghi danh mất quyền ngay.
"""
import hashlib
import hmac
import os
import time
from urllib.parse import urlencode

from .config import settings

# Thư mục con cần bảo vệ (không phục vụ công khai) và thời hạn của link có chữ ký (6 giờ)
PROTECTED_DIRS = ("videos", "documents")
LINK_TTL_SEC = 6 * 3600


def resolve_upload_path(url: str | None) -> str | None:
    """Ánh xạ URL …/uploads/<sub>/<file> sang đường dẫn cục bộ; None nếu không phải file upload."""
    # Tìm phần "/uploads/" trong URL; không có -> không phải file do hệ thống upload
    marker = "/uploads/"
    idx = (url or "").find(marker)
    if idx == -1:
        return None
    # Lấy phần đường dẫn sau "/uploads/", bỏ query string (?...) và anchor (#...)
    rel = url[idx + len(marker):].split("?", 1)[0].split("#", 1)[0]
    upload_root = os.path.abspath(settings.upload_dir)
    path = os.path.abspath(os.path.join(upload_root, rel))
    if os.path.commonpath([upload_root, path]) != upload_root:
        return None  # chặn path traversal
    return path


# Trả về đường dẫn file nếu file nằm trong thư mục được bảo vệ (videos/documents), ngược lại None
def protected_path(url: str | None) -> str | None:
    path = resolve_upload_path(url)
    if not path:
        return None
    # Thư mục con cấp 1 bên trong uploads (vd "videos", "documents", "images")
    sub = os.path.relpath(path, os.path.abspath(settings.upload_dir)).split(os.sep)[0]
    return path if sub in PROTECTED_DIRS else None


# Tạo chữ ký HMAC-SHA256 cho bộ (user, bài học, loại file, hạn dùng) bằng khóa JWT_SECRET
def _sig(uid: int, lesson_id: int, kind: str, exp: int) -> str:
    msg = f"{uid}:{lesson_id}:{kind}:{exp}".encode()
    return hmac.new(settings.jwt_secret.encode(), msg, hashlib.sha256).hexdigest()


# Link hợp lệ khi chưa hết hạn và chữ ký khớp (compare_digest chống dò chữ ký theo thời gian so sánh)
def verify(uid: int, lesson_id: int, kind: str, exp: int, sig: str) -> bool:
    return exp >= int(time.time()) and hmac.compare_digest(_sig(uid, lesson_id, kind, exp), sig or "")


def signed_src(user: dict | None, lesson: dict, kind: str) -> str | None:
    """URL để trình duyệt tải file: link có chữ ký nếu là file được bảo vệ, còn lại (YouTube, CDN…) giữ nguyên."""
    # kind = "video" hoặc "document" -> đọc lesson["video_url"] / lesson["document_url"]
    url = lesson.get(f"{kind}_url")
    if not url:
        return None
    # Link ngoài (YouTube, Google Drive...) không cần ký
    if not protected_path(url):
        return url
    # Khách chưa đăng nhập không được cấp link file bảo vệ
    if not user:
        return None
    # Tạo link /api/lessons/media có hạn dùng 6 giờ, gắn với user đang xem
    exp = int(time.time()) + LINK_TTL_SEC
    query = urlencode(
        {"lesson_id": lesson["id"], "kind": kind, "uid": user["id"], "exp": exp,
         "sig": _sig(user["id"], lesson["id"], kind, exp)}
    )
    return f"{settings.public_base_url.rstrip('/')}/api/lessons/media?{query}"
