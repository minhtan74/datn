"""PHASE 4 — Learning Analytics

Revision ID: 0002_analytics
Revises: 0001_baseline
Create Date: 2026-09-06

Additive: thêm cột topic/difficulty/explanation cho `questions`, tạo bảng
`learning_analytics`, và backfill topic/difficulty cho 30 câu hỏi mẫu.
Không sửa/xoá cột hay dữ liệu sẵn có.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_analytics"
down_revision: Union[str, None] = "0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (question_id -> (topic, difficulty)) — bám theo nội dung seed hiện có
BACKFILL = {
    1: ("Hàm (Functions)", "easy"),
    2: ("Kiểu dữ liệu (Data Types)", "easy"),
    3: ("Toán tử (Operators)", "easy"),
    4: ("Vòng lặp (Loops)", "easy"),
    5: ("Kiểu dữ liệu (Data Types)", "medium"),
    6: ("Biến & ES6", "easy"),
    7: ("DOM", "easy"),
    8: ("Kiểu dữ liệu (Data Types)", "medium"),
    9: ("Hàm (Functions)", "medium"),
    10: ("Bất đồng bộ (Async)", "medium"),
    11: ("Kế thừa (Inheritance)", "easy"),
    12: ("Kế thừa (Inheritance)", "medium"),
    13: ("Xử lý ngoại lệ (Exceptions)", "easy"),
    14: ("Collection Framework", "easy"),
    15: ("OOP cơ bản", "medium"),
    16: ("HTML cơ bản", "easy"),
    17: ("CSS cơ bản", "easy"),
    18: ("Flexbox & Layout", "medium"),
    19: ("Responsive Design", "medium"),
    20: ("HTML ngữ nghĩa (Semantic)", "medium"),
    21: ("Hooks", "easy"),
    22: ("Props & State", "easy"),
    23: ("Hooks", "medium"),
    24: ("JSX", "easy"),
    25: ("Routing", "medium"),
    26: ("Truy vấn SQL (SQL Queries)", "easy"),
    27: ("JOIN", "medium"),
    28: ("Thiết kế CSDL (DB Design)", "medium"),
    29: ("Hàm tổng hợp (Aggregate)", "easy"),
    30: ("Chuẩn hoá (Normalization)", "hard"),
}


def upgrade() -> None:
    op.execute(
        "ALTER TABLE questions "
        "ADD COLUMN topic VARCHAR(100) NULL AFTER correct_answer, "
        "ADD COLUMN difficulty ENUM('easy','medium','hard') NULL AFTER topic, "
        "ADD COLUMN explanation TEXT NULL AFTER difficulty"
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS learning_analytics (
            id                INT AUTO_INCREMENT PRIMARY KEY,
            user_id           INT NOT NULL,
            course_id         INT NOT NULL,
            avg_quiz_score    DECIMAL(5,2) NOT NULL DEFAULT 0,
            completion_pct    DECIMAL(5,2) NOT NULL DEFAULT 0,
            completed_lessons INT NOT NULL DEFAULT 0,
            total_lessons     INT NOT NULL DEFAULT 0,
            total_time_sec    INT NOT NULL DEFAULT 0,
            quiz_attempts     INT NOT NULL DEFAULT 0,
            weak_topics       JSON NULL,
            strong_topics     JSON NULL,
            computed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_la_user   FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
            CONSTRAINT fk_la_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE KEY uq_la (user_id, course_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    for qid, (topic, diff) in BACKFILL.items():
        op.execute(
            f"UPDATE questions SET topic = {_q(topic)}, difficulty = {_q(diff)} "
            f"WHERE id = {qid} AND topic IS NULL"
        )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS learning_analytics")
    op.execute(
        "ALTER TABLE questions DROP COLUMN topic, DROP COLUMN difficulty, DROP COLUMN explanation"
    )


def _q(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"
