"""baseline — schema studyonline_db hiện có (studyonline_db.sql + migration_add_payments.sql)

Revision ID: 0001_baseline
Revises:
Create Date: 2026-09-06

Không tạo bảng ở đây: database đã tồn tại sẵn với 10 bảng.
Chạy `alembic stamp 0001_baseline` để đánh dấu điểm khởi đầu, rồi các migration
sau (bảng AI, cột topic...) mới thêm nội dung thật.
"""
from typing import Sequence, Union

revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
