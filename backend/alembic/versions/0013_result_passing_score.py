"""PHASE 12d — results.passing_score: lưu điểm đạt của quiz tại thời điểm nộp bài

Revision ID: 0013_result_passing_score
Revises: 0012_lesson_review
Create Date: 2026-09-29

Additive. Trước đây trạng thái đạt / chưa đạt tính theo quizzes.passing_score hiện tại,
nên giảng viên đổi điểm đạt là kết quả cũ đổi theo. Lượt cũ được điền điểm đạt hiện tại của quiz.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0013_result_passing_score"
down_revision: Union[str, None] = "0012_lesson_review"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE results ADD COLUMN passing_score INT NULL "
        "COMMENT 'Điểm đạt (%) của quiz lúc nộp bài, NULL = quiz không đặt điểm đạt' AFTER total"
    )
    op.execute(
        "UPDATE results r JOIN quizzes q ON q.id = r.quiz_id SET r.passing_score = q.passing_score"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE results DROP COLUMN passing_score")
