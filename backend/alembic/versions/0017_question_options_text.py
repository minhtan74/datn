"""PHASE 12h — questions.option_a..d: VARCHAR(255) -> TEXT

Revision ID: 0017_question_options_text
Revises: 0016_quiz_source_word
Create Date: 2026-09-29

Phương án có thể chứa công thức (ký hiệu [[math:LaTeX]]) hoặc ảnh ([[img:url]]) khi nhập từ Word
-> dễ vượt 255 ký tự. Nới rộng cột, dữ liệu cũ giữ nguyên.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0017_question_options_text"
down_revision: Union[str, None] = "0016_quiz_source_word"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE questions "
        "MODIFY option_a TEXT NOT NULL, MODIFY option_b TEXT NOT NULL, "
        "MODIFY option_c TEXT NOT NULL, MODIFY option_d TEXT NOT NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE questions "
        "MODIFY option_a VARCHAR(255) NOT NULL, MODIFY option_b VARCHAR(255) NOT NULL, "
        "MODIFY option_c VARCHAR(255) NOT NULL, MODIFY option_d VARCHAR(255) NOT NULL"
    )
