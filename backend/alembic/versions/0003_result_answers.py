"""PHASE 4 — bảng result_answers (chi tiết từng câu trả lời mỗi lần nộp quiz)

Revision ID: 0003_result_answers
Revises: 0002_analytics
Create Date: 2026-09-06

Cần cho phân tích theo topic (điểm mạnh/yếu) và vòng lặp cá nhân hoá:
`results` cũ chỉ lưu score/total, không lưu đúng/sai từng câu.
Additive — không đụng dữ liệu cũ. Các bản ghi `results` cũ (seed) sẽ không có
dòng result_answers cho tới khi học viên làm lại quiz.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003_result_answers"
down_revision: Union[str, None] = "0002_analytics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS result_answers (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            result_id   INT NOT NULL,
            question_id INT NOT NULL,
            chosen      VARCHAR(1) NULL,
            is_correct  TINYINT(1) NOT NULL DEFAULT 0,
            CONSTRAINT fk_ra_result   FOREIGN KEY (result_id)   REFERENCES results(id)   ON DELETE CASCADE,
            CONSTRAINT fk_ra_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
            INDEX ix_ra_result (result_id),
            INDEX ix_ra_question (question_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS result_answers")
