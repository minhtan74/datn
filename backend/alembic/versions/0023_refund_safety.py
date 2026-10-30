"""Admin refund operation ledger (no student request workflow)."""
from alembic import op
import sqlalchemy as sa

revision = "0023_refund_safety"
down_revision = "0022_password_recovery"
branch_labels = depends_on = None


def upgrade():
    op.create_table("payment_refund_operations",
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("request_id", sa.String(64), nullable=False),
        sa.Column("state", sa.String(30), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("revoke_access", sa.Boolean(), nullable=False),
        sa.Column("gateway_txn_no", sa.String(50)),
        sa.Column("gateway_code", sa.String(10)),
        sa.Column("message", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table("payment_refund_operation_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payment_refund_operations.payment_id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("state", sa.String(30), nullable=False),
        sa.Column("message", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("payment_refund_operation_events")
    op.drop_table("payment_refund_operations")
