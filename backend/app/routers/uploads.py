"""/api/upload — port của app/Controllers/UploadController.php."""
import os
import secrets
import time

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.config import settings
from app.core.dependencies import require_roles
from app.core.responses import ApiError, ok

router = APIRouter(prefix="/api", tags=["upload"])

# Cấu hình cho từng loại file: (MIME cho phép, đuôi cho phép, dung lượng tối đa, thư mục con, nhãn dung lượng)
ALLOWED = {
    "video": (
        {"video/mp4", "video/webm", "video/ogg", "video/quicktime", "video/x-matroska"},
        {".mp4", ".webm", ".ogg", ".ogv", ".mov", ".mkv"},
        500 * 1024 * 1024,
        "videos",
        "500MB",
    ),
    "image": (
        {"image/jpeg", "image/png", "image/gif", "image/webp"},
        {".jpg", ".jpeg", ".png", ".gif", ".webp"},
        5 * 1024 * 1024,
        "images",
        "5MB",
    ),
    "document": (
        {"application/pdf"},
        {".pdf"},
        20 * 1024 * 1024,
        "documents",
        "20MB",
    ),
}


# POST /api/upload — giảng viên/admin tải file (video / ảnh / PDF) lên server
@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    type: str = Form(default="document"),
    _: dict = Depends(require_roles("teacher", "admin")),
):
    # Loại không hợp lệ thì coi như "document"; lấy cấu hình tương ứng
    kind = type if type in ALLOWED else "document"
    mimes, exts, max_bytes, subdir, limit_label = ALLOWED[kind]

    ext = os.path.splitext(file.filename or "")[1].lower()
    ctype = (file.content_type or "").lower()
    # Đuôi file quyết định cách /uploads phục vụ file -> bắt buộc nằm trong danh sách cho phép
    # (trước đây chỉ cần MIME khớp là file .html/.svg vẫn được lưu và phát công khai).
    if ext not in exts or (ctype and ctype != "application/octet-stream" and ctype not in mimes):
        label = {
            "video": "file video (mp4, webm, ogg, mov, mkv)",
            "image": "file ảnh (JPEG, PNG, GIF, WebP)",
            "document": "file PDF",
        }[kind]
        raise ApiError(f"Chỉ chấp nhận {label}.", 400)

    # Tạo thư mục đích nếu chưa có (uploads/videos, uploads/images, uploads/documents)
    upload_dir = os.path.join(settings.upload_dir, subdir)
    os.makedirs(upload_dir, exist_ok=True)

    # Đặt tên file mới = thời gian + chuỗi ngẫu nhiên (tránh trùng tên và không dùng tên gốc của người dùng)
    filename = f"{int(time.time())}_{secrets.token_hex(6)}{ext}"
    dest = os.path.join(upload_dir, filename)

    # Ghi file theo từng khối 1MB; vượt dung lượng cho phép thì xóa file dở và báo lỗi
    size = 0
    with open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                out.close()
                os.remove(dest)
                raise ApiError(f"File quá lớn. Giới hạn: {limit_label}.", 400)
            out.write(chunk)

    # Trả về URL công khai của file để lưu vào bài học / khóa học
    url = f"{settings.public_base_url.rstrip('/')}/uploads/{subdir}/{filename}"
    return ok("Upload thành công.", url=url)
