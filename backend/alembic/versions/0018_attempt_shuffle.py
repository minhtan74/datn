"""Lưu phiên bản đảo đề theo lượt làm."""
from alembic import op
import sqlalchemy as sa

revision = "0018_attempt_shuffle"
down_revision = "0017_question_options_text"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("quiz_attempts", sa.Column("shuffle_version", sa.Integer(), nullable=False, server_default="0"))


def downgrade():
    op.drop_column("quiz_attempts", "shuffle_version")
