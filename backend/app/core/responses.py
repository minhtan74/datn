"""Chuẩn hoá "phong bì" JSON giống app/Core/Response.php của bản PHP.

Thành công: {"success": true, "message"?: "...", ...data}
Lỗi:       {"success": false, "message": "..."}  (HTTP status = mã lỗi)

JSON: ensure_ascii=False (giữ tiếng Việt), Decimal -> chuỗi ("599000.00"),
datetime -> "Y-m-d H:i:s"  — khớp cách PDO của PHP trả về.
"""
import datetime as _dt
import json
from decimal import Decimal
from typing import Any

from fastapi.responses import JSONResponse


# Chuyển các kiểu dữ liệu MySQL mà json không tự hiểu sang dạng chuỗi/số
def _json_default(o: Any):
    # Tiền (DECIMAL) -> chuỗi, giữ nguyên độ chính xác
    if isinstance(o, Decimal):
        return str(o)
    # Ngày giờ -> "YYYY-MM-DD HH:MM:SS"
    if isinstance(o, _dt.datetime):
        return o.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(o, _dt.date):
        return o.strftime("%Y-%m-%d")
    # Khoảng thời gian -> số giây
    if isinstance(o, _dt.timedelta):
        return o.total_seconds()
    if isinstance(o, (bytes, bytearray)):
        return o.decode("utf-8", "replace")
    raise TypeError(f"Không serialize được kiểu {type(o).__name__}")


# Response JSON tùy biến: không escape tiếng Việt, dùng _json_default cho kiểu đặc biệt
class ApiJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            default=_json_default,
        ).encode("utf-8")


class ApiError(Exception):
    """Ném ra để trả lỗi dạng {"success": false, "message": ...} (giống Response::error)."""

    # message: thông báo hiển thị cho người dùng; status: mã HTTP (400 mặc định, 401/403/404/409...)
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def ok(_message: str = "", **data: Any) -> "ApiJSONResponse":
    """Trả Response trực tiếp (bỏ qua jsonable_encoder của FastAPI) để giữ đúng
    kiểu dữ liệu như PDO của PHP: Decimal -> "599000.00", datetime -> "Y-m-d H:i:s"."""
    # Luôn có success=true; message chỉ thêm khi có; các dữ liệu khác trải phẳng vào body
    body: dict[str, Any] = {"success": True}
    if _message:
        body["message"] = _message
    body.update(data)
    return ApiJSONResponse(body)
