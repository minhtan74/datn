"""PHASE 12f — quizzes.grading_method: cách tính điểm khi học viên làm nhiều lượt

Revision ID: 0015_quiz_grading_method
Revises: 0014_quiz_attempts
Create Date: 2026-09-29

highest = lượt cao nhất (mặc định), latest = lượt cuối, first = lượt đầu, average = trung bình các lượt.
Điểm trung bình / tỷ lệ đạt trong thống kê lấy 1 điểm cho mỗi (học viên, quiz) theo cách tính này,
thay vì cộng dồn mọi lượt như trước.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0015_quiz_grading_method"
down_revision: Union[str, None] = "0014_quiz_attempts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE quizzes ADD COLUMN grading_method VARCHAR(10) NOT NULL DEFAULT 'highest' "
        "COMMENT 'Cách tính điểm nhiều lượt: highest / latest / first / average' AFTER max_attempts"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE quizzes DROP COLUMN grading_method")
