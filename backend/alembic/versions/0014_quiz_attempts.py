"""PHASE 12e — quiz_attempts: lượt làm bài bắt đầu từ lúc mở đề

Revision ID: 0014_quiz_attempts
Revises: 0013_result_passing_score
Create Date: 2026-09-29

Additive. Chỉ dùng cho đề có giới hạn thời gian / số lượt: mở đề là tạo 1 lượt (lưu giờ bắt đầu),
mở lại thì tiếp tục đúng lượt đó -> không reset được đồng hồ, xem đề rồi bỏ cũng tính là đã dùng lượt.
Lượt đã nộp trỏ tới results.id; lượt bỏ dở / quá giờ có finished_ts nhưng result_id NULL.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0014_quiz_attempts"
down_revision: Union[str, None] = "0013_result_passing_score"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE quiz_attempts (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            user_id     INT NOT NULL,
            quiz_id     INT NOT NULL,
            started_ts  INT NOT NULL COMMENT 'Giờ mở đề (unix giây)',
            finished_ts INT NULL COMMENT 'Giờ nộp / hết hạn (unix giây), NULL = đang làm',
            result_id   INT NULL COMMENT 'Kết quả của lượt này, NULL = chưa nộp / bỏ dở',
            CONSTRAINT fk_attempt_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            CONSTRAINT fk_attempt_quiz FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
            CONSTRAINT fk_attempt_result FOREIGN KEY (result_id) REFERENCES results(id) ON DELETE SET NULL,
            INDEX idx_attempt_user_quiz (user_id, quiz_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE quiz_attempts")
