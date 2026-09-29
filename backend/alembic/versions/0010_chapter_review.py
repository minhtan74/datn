"""PHASE 12 — quizzes.chapter_id: bộ câu hỏi ôn tập của từng chương

Revision ID: 0010_chapter_review
Revises: 0009_payment_refund
Create Date: 2026-09-29

Additive. Quiz có chapter_id là bộ ôn tập của chương đó (UNIQUE -> mỗi chương 1 bộ).
Xóa chương -> SET NULL: bộ ôn tập thành quiz thường, giữ lại điểm của học viên.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0010_chapter_review"
down_revision: Union[str, None] = "0009_payment_refund"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE quizzes "
        "ADD COLUMN chapter_id INT NULL COMMENT 'Bộ câu hỏi ôn tập của chương' AFTER lesson_id, "
        "ADD CONSTRAINT uq_quiz_chapter UNIQUE (chapter_id), "
        "ADD CONSTRAINT fk_quiz_chapter FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE quizzes DROP FOREIGN KEY fk_quiz_chapter")
    op.execute("ALTER TABLE quizzes DROP INDEX uq_quiz_chapter, DROP COLUMN chapter_id")
