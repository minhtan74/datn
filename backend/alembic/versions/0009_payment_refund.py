"""PHASE 10c — payments: lưu thông tin hoàn tiền (thời điểm, người thực hiện, lý do, mã GD hoàn của VNPay)

Revision ID: 0009_payment_refund
Revises: 0008_vnpay_create_date
Create Date: 2026-09-28

Additive.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0009_payment_refund"
down_revision: Union[str, None] = "0008_vnpay_create_date"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE payments "
        "ADD COLUMN refunded_at TIMESTAMP NULL AFTER paid_at, "
        "ADD COLUMN refunded_by INT NULL COMMENT 'Admin thực hiện hoàn tiền' AFTER refunded_at, "
        "ADD COLUMN refund_reason VARCHAR(255) NULL AFTER refunded_by, "
        "ADD COLUMN refund_txn_no VARCHAR(50) NULL COMMENT 'Mã GD hoàn tiền phía VNPay' AFTER refund_reason, "
        "ADD CONSTRAINT fk_payment_refunded_by FOREIGN KEY (refunded_by) REFERENCES users(id) ON DELETE SET NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE payments DROP FOREIGN KEY fk_payment_refunded_by")
    op.execute(
        "ALTER TABLE payments DROP COLUMN refunded_at, DROP COLUMN refunded_by, "
        "DROP COLUMN refund_reason, DROP COLUMN refund_txn_no"
    )
