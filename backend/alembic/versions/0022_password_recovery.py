"""Single-use password recovery and session revocation."""
from alembic import op
import sqlalchemy as sa

revision = "0022_password_recovery"
down_revision = "0021_knowledge_scope"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))
    op.create_table("password_reset_tokens",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.BigInteger(), nullable=False),
        sa.Column("used_at", sa.BigInteger(), nullable=True),
    )
    op.create_index("ix_password_reset_user", "password_reset_tokens", ["user_id"])
    op.create_table("password_reset_limits",
        sa.Column("key_hash", sa.String(64), primary_key=True),
        sa.Column("window_start", sa.BigInteger(), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("last_request", sa.BigInteger(), nullable=False),
    )


def downgrade():
    op.drop_table("password_reset_limits")
    op.drop_table("password_reset_tokens")
    op.drop_column("users", "token_version")
