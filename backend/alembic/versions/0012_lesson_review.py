"""PHASE 12c — quizzes.review_lesson_id: bộ câu hỏi ôn tập theo kiến thức của từng bài học

Revision ID: 0012_lesson_review
Revises: 0011_quiz_settings
Create Date: 2026-09-29

Additive. Khác quizzes.lesson_id (quiz AI sinh từ bài, có thể nhiều quiz / bài):
review_lesson_id UNIQUE -> mỗi bài học tối đa 1 bộ ôn tập.
Xóa bài học -> SET NULL: bộ ôn tập đã có lượt làm được giữ lại thành quiz thường.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0012_lesson_review"
down_revision: Union[str, None] = "0011_quiz_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE quizzes "
        "ADD COLUMN review_lesson_id INT NULL COMMENT 'Bộ câu hỏi ôn tập của bài học' AFTER chapter_id, "
        "ADD CONSTRAINT uq_quiz_review_lesson UNIQUE (review_lesson_id), "
        "ADD CONSTRAINT fk_quiz_review_lesson FOREIGN KEY (review_lesson_id) REFERENCES lessons(id) ON DELETE SET NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE quizzes DROP FOREIGN KEY fk_quiz_review_lesson")
    op.execute("ALTER TABLE quizzes DROP INDEX uq_quiz_review_lesson, DROP COLUMN review_lesson_id")
