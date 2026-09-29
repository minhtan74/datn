"""PHASE 9 — quizzes: thêm lesson_id (quiz theo bài học) + source (manual/ai)

Revision ID: 0006_quiz_source_lesson
Revises: 0005_rag_tables
Create Date: 2026-09-06

Additive. `source='ai'` đánh dấu quiz do AI sinh (đã qua giảng viên duyệt).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006_quiz_source_lesson"
down_revision: Union[str, None] = "0005_rag_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE quizzes "
        "ADD COLUMN lesson_id INT NULL AFTER course_id, "
        "ADD COLUMN source ENUM('manual','ai') NOT NULL DEFAULT 'manual' AFTER description, "
        "ADD CONSTRAINT fk_quiz_lesson FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE quizzes DROP FOREIGN KEY fk_quiz_lesson")
    op.execute("ALTER TABLE quizzes DROP COLUMN lesson_id, DROP COLUMN source")
