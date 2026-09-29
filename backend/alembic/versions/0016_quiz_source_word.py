"""PHASE 12g — quizzes.source thêm 'word': quiz nhập từ file Word

Revision ID: 0016_quiz_source_word
Revises: 0015_quiz_grading_method
Create Date: 2026-09-29

Additive: mở rộng ENUM, dữ liệu cũ ('manual' / 'ai') giữ nguyên.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0016_quiz_source_word"
down_revision: Union[str, None] = "0015_quiz_grading_method"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE quizzes MODIFY COLUMN source ENUM('manual','ai','word') NOT NULL DEFAULT 'manual'")


def downgrade() -> None:
    op.execute("UPDATE quizzes SET source = 'manual' WHERE source = 'word'")
    op.execute("ALTER TABLE quizzes MODIFY COLUMN source ENUM('manual','ai') NOT NULL DEFAULT 'manual'")
