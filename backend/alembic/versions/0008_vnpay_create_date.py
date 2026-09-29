"""PHASE 10b — payments: lưu vnp_CreateDate đã gửi VNPay (cần cho API truy vấn querydr khi đối soát)

Revision ID: 0008_vnpay_create_date
Revises: 0007_vnpay_payments
Create Date: 2026-09-28

Additive. Đơn cũ không có giá trị -> đối soát dùng created_at thay thế.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0008_vnpay_create_date"
down_revision: Union[str, None] = "0007_vnpay_payments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE payments ADD COLUMN vnp_create_date CHAR(14) NULL "
        "COMMENT 'vnp_CreateDate (yyyyMMddHHmmss, GMT+7) đã gửi VNPay' AFTER response_code"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE payments DROP COLUMN vnp_create_date")
