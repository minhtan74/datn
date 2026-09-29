"""StudyOnline API — FastAPI (thay cho backend PHP).

Giữ nguyên "hợp đồng" HTTP của bản PHP: đường dẫn /api/..., tham số query,
phong bì JSON {success, message?, ...data} và thông điệp lỗi tiếng Việt.
"""
import datetime as dt
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.responses import ApiError, ApiJSONResponse
from app.routers import (
    ai,
    analytics,
    auth,
    chapters,
    courses,
    enrollments,
    lessons,
    payments,
    progress,
    quizzes,
    recommendations,
    reports,
    uploads,
    users,
)

# Cấu hình logger "rag" (AI Tutor): khi APP_DEBUG bật thì in log truy vấn RAG ra console
logging.getLogger("rag").setLevel(logging.INFO if settings.app_debug else logging.WARNING)
if not logging.getLogger("rag").handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S"))
    logging.getLogger("rag").addHandler(_h)
    logging.getLogger("rag").propagate = False

# Tạo ứng dụng FastAPI; mọi response mặc định dùng ApiJSONResponse (giữ tiếng Việt, định dạng ngày/tiền)
app = FastAPI(
    title="StudyOnline API",
    version="2.0.0",
    default_response_class=ApiJSONResponse,
)

# Cho phép frontend (khác domain/port) gọi API: nguồn được phép lấy từ FRONTEND_ORIGIN trong .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    # Cho frontend đọc tên file khi tải báo cáo CSV
    expose_headers=["Content-Disposition"],
)


# ── Exception handlers -> phong bì lỗi giống Response::error ──────────────────

# Lỗi nghiệp vụ do code tự ném (raise ApiError) -> {"success": false, "message": ...} kèm mã HTTP tương ứng
@app.exception_handler(ApiError)
async def _api_error_handler(_: Request, exc: ApiError):
    return ApiJSONResponse({"success": False, "message": exc.message}, status_code=exc.status)


# Dữ liệu gửi lên sai kiểu (FastAPI không parse được) -> trả 400 thay vì 422 mặc định
@app.exception_handler(RequestValidationError)
async def _validation_handler(_: Request, exc: RequestValidationError):
    return ApiJSONResponse({"success": False, "message": "Dữ liệu không hợp lệ."}, status_code=400)


# Lỗi HTTP chung (404 sai đường dẫn, 405 sai method...) -> thông điệp tiếng Việt
@app.exception_handler(StarletteHTTPException)
async def _http_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        msg = (
            f"Đường dẫn API '{request.url.path}' cho method "
            f"'{request.method}' không được tìm thấy."
        )
    elif exc.status_code == 405:
        msg = "Phương thức không được hỗ trợ cho đường dẫn này."
    else:
        msg = exc.detail if isinstance(exc.detail, str) else "Lỗi."
    return ApiJSONResponse({"success": False, "message": msg}, status_code=exc.status_code)


# Lỗi không lường trước (bug, mất kết nối DB...) -> 500; chỉ lộ chi tiết lỗi khi APP_DEBUG=true
@app.exception_handler(Exception)
async def _unhandled_handler(_: Request, exc: Exception):
    return ApiJSONResponse(
        {
            "success": False,
            "message": "Lỗi hệ thống nghiêm trọng",
            "error": str(exc) if settings.app_debug else "Internal Server Error",
        },
        status_code=500,
    )


# ── Static uploads (thay public/uploads + .htaccess của PHP) ─────────────────
import os

# Chỉ ảnh (thumbnail) được phục vụ công khai; video/tài liệu bài học đi qua
# /api/lessons/media (link có chữ ký + kiểm tra quyền).
_images_dir = os.path.join(settings.upload_dir, "images")
os.makedirs(_images_dir, exist_ok=True)
app.mount("/uploads/images", StaticFiles(directory=_images_dir), name="uploads-images")


# ── Routers ─────────────────────────────────────────────────────────────────
# Gắn toàn bộ nhóm API vào ứng dụng (mỗi file trong app/routers là một nhóm /api/...)
for r in (
    auth.router,
    users.router,
    courses.router,
    chapters.router,
    lessons.router,
    quizzes.router,
    enrollments.router,
    payments.router,
    progress.router,
    uploads.router,
    reports.router,
    analytics.router,
    recommendations.router,
    ai.router,
):
    app.include_router(r)


# Trang gốc: kiểm tra nhanh API đang chạy
@app.get("/")
def root():
    return {"success": True, "name": "StudyOnline API", "engine": "fastapi", "time": dt.datetime.now()}


# Health check (Docker / script khởi động dùng để biết backend đã sẵn sàng)
@app.get("/api/health")
def health():
    return {"success": True, "status": "ok"}


# Job nền: định kỳ đối soát các đơn VNPay "đang chờ" đã quá hạn (học viên trả tiền nhưng đóng tab
# trước khi quay về web -> hoàn tất + ghi danh; không thanh toán -> chuyển thất bại).
# PAYMENT_RECONCILE_INTERVAL (giây), 0 = tắt.
_reconcile_task = None


async def _reconcile_loop():
    import asyncio

    from app.core.database import SessionLocal

    log = logging.getLogger("uvicorn.error")
    while True:
        await asyncio.sleep(settings.payment_reconcile_interval)
        try:
            def run():
                db = SessionLocal()
                try:
                    return payments.reconcile_pending(db, only_expired=True)
                finally:
                    db.close()

            summary = await asyncio.to_thread(run)
            if any(summary.values()):
                log.info("[payments] đối soát định kỳ: %s", summary)
        except Exception as e:  # noqa: BLE001 — job nền không được làm sập server
            log.warning("[payments] đối soát định kỳ lỗi: %s", e)


@app.on_event("startup")
async def _start_reconcile_job():
    import asyncio

    global _reconcile_task
    if settings.payment_reconcile_interval > 0:
        _reconcile_task = asyncio.create_task(_reconcile_loop())


@app.on_event("shutdown")
async def _stop_reconcile_job():
    if _reconcile_task:
        _reconcile_task.cancel()
