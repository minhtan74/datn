"""Kết nối MySQL + helper truy vấn thô (tương đương app/Core/Database.php + Model.php)."""
from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings

# Engine kết nối MySQL: pool_pre_ping kiểm tra kết nối còn sống trước khi dùng,
# pool_recycle làm mới kết nối sau ~280 giây để tránh MySQL tự ngắt kết nối nhàn rỗi
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=280,
    future=True,
    echo=False,
)

# Nhà máy tạo phiên làm việc (session) với DB
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Lớp gốc cho các model SQLAlchemy (app/models) — dùng cho Alembic migration
Base = declarative_base()


# Dependency của FastAPI: mỗi request được cấp 1 session và session luôn được đóng khi request kết thúc
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Helper truy vấn thô: giữ SQL gần y hệt bản PHP để đảm bảo parity ──────────
# Tất cả dùng tham số đặt tên (:ten) nên an toàn trước SQL injection.

# Lấy nhiều dòng -> danh sách dict
def q_all(db: Session, sql: str, /, **params: Any) -> list[dict]:
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


# Lấy 1 dòng -> dict, hoặc None nếu không có
def q_one(db: Session, sql: str, /, **params: Any) -> dict | None:
    row = db.execute(text(sql), params).mappings().first()
    return dict(row) if row is not None else None


# Lấy 1 giá trị đơn (vd COUNT(*), SUM(...))
def q_scalar(db: Session, sql: str, /, **params: Any) -> Any:
    return db.execute(text(sql), params).scalar()


# Chạy câu lệnh ghi (INSERT/UPDATE/DELETE) và commit ngay; trả về kết quả để đọc lastrowid
def execute(db: Session, sql: str, /, **params: Any):
    res = db.execute(text(sql), params)
    db.commit()
    return res
