"""PHASE 10 — payments: thêm phương thức 'vnpay' + các cột lưu kết quả từ cổng VNPay

Revision ID: 0007_vnpay_payments
Revises: 0006_quiz_source_lesson
Create Date: 2026-09-28

Additive. transaction_ref dùng làm vnp_TxnRef (duy nhất) nên thêm UNIQUE index.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0007_vnpay_payments"
down_revision: Union[str, None] = "0006_quiz_source_lesson"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE payments "
        "MODIFY COLUMN method ENUM('card','bank_transfer','momo','zalopay','vnpay') "
        "COLLATE utf8mb4_unicode_ci DEFAULT 'card', "
        "ADD COLUMN gateway_txn_no VARCHAR(50) NULL COMMENT 'Mã giao dịch phía VNPay (vnp_TransactionNo)' AFTER transaction_ref, "
        "ADD COLUMN bank_code VARCHAR(20) NULL COMMENT 'Ngân hàng thanh toán (vnp_BankCode)' AFTER gateway_txn_no, "
        "ADD COLUMN response_code VARCHAR(10) NULL COMMENT 'Mã phản hồi VNPay (vnp_ResponseCode)' AFTER bank_code, "
        "ADD UNIQUE KEY uq_payment_ref (transaction_ref)"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE payments DROP INDEX uq_payment_ref, "
        "DROP COLUMN gateway_txn_no, DROP COLUMN bank_code, DROP COLUMN response_code"
    )
    op.execute("UPDATE payments SET method='card' WHERE method='vnpay'")
    op.execute(
        "ALTER TABLE payments MODIFY COLUMN method ENUM('card','bank_transfer','momo','zalopay') "
        "COLLATE utf8mb4_unicode_ci DEFAULT 'card'"
    )
