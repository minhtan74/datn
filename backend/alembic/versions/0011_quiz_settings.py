"""PHASE 12b — quizzes: thời gian làm bài, điểm đạt, số lần làm tối đa

Revision ID: 0011_quiz_settings
Revises: 0010_chapter_review
Create Date: 2026-09-29

Additive. NULL = không giới hạn / không xét đạt -> quiz cũ giữ nguyên hành vi.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0011_quiz_settings"
down_revision: Union[str, None] = "0010_chapter_review"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE quizzes "
        "ADD COLUMN duration INT NULL COMMENT 'Thời gian làm bài (phút), NULL = không giới hạn' AFTER source, "
        "ADD COLUMN passing_score INT NULL COMMENT 'Điểm đạt (%), NULL = không xét đạt' AFTER duration, "
        "ADD COLUMN max_attempts INT NULL COMMENT 'Số lần làm tối đa, NULL = không giới hạn' AFTER passing_score"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE quizzes DROP COLUMN duration, DROP COLUMN passing_score, DROP COLUMN max_attempts")
