"""PHASE 5 — bảng recommendations (lưu lịch sử gợi ý cá nhân hoá)

Revision ID: 0004_recommendations
Revises: 0003_result_answers
Create Date: 2026-09-06

Mỗi lần hệ thống tính lại gợi ý -> ghi 1 dòng => chứng minh recommendation
thay đổi theo dữ liệu học tập mới (vòng lặp cá nhân hoá, đề bài §16).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004_recommendations"
down_revision: Union[str, None] = "0003_result_answers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendations (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            user_id    INT NOT NULL,
            course_id  INT NULL,
            level      ENUM('Weak','Average','Good','Excellent') NOT NULL,
            summary    VARCHAR(255) NOT NULL,
            items      JSON NOT NULL,
            based_on   JSON NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_rec_user   FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
            CONSTRAINT fk_rec_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            INDEX ix_rec_user (user_id, created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS recommendations")
