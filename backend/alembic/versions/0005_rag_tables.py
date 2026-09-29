"""PHASE 6 — RAG AI Tutor: documents, document_chunks, ai_conversations, ai_messages

Revision ID: 0005_rag_tables
Revises: 0004_recommendations
Create Date: 2026-09-06

Vector store = MySQL (cột embedding JSON) — không cần vector DB ngoài, dễ triển
khai & giải thích cho DATN. Additive hoàn toàn.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0005_rag_tables"
down_revision: Union[str, None] = "0004_recommendations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            course_id   INT NOT NULL,
            lesson_id   INT NULL,
            uploaded_by INT NULL,
            title       VARCHAR(255) NOT NULL,
            filename    VARCHAR(255) NOT NULL,
            file_path   VARCHAR(500) NOT NULL,
            file_type   ENUM('pdf','docx','txt') NOT NULL,
            status      ENUM('pending','indexed','failed') NOT NULL DEFAULT 'pending',
            pages       INT NULL,
            chunk_count INT NOT NULL DEFAULT 0,
            error       VARCHAR(500) NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_doc_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            CONSTRAINT fk_doc_lesson FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
            CONSTRAINT fk_doc_user   FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX ix_doc_course (course_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS document_chunks (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            document_id INT NOT NULL,
            course_id   INT NOT NULL,
            lesson_id   INT NULL,
            chunk_index INT NOT NULL,
            page        INT NULL,
            content     TEXT NOT NULL,
            embedding   JSON NOT NULL,
            token_count INT NOT NULL DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_chunk_doc    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
            CONSTRAINT fk_chunk_course FOREIGN KEY (course_id)   REFERENCES courses(id)   ON DELETE CASCADE,
            INDEX ix_chunk_course (course_id),
            INDEX ix_chunk_doc (document_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            user_id    INT NOT NULL,
            course_id  INT NULL,
            lesson_id  INT NULL,
            title      VARCHAR(255) NOT NULL DEFAULT 'Cuộc trò chuyện mới',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_conv_user   FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
            CONSTRAINT fk_conv_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            INDEX ix_conv_user (user_id, updated_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_messages (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            conversation_id INT NOT NULL,
            role            ENUM('user','assistant') NOT NULL,
            content         TEXT NOT NULL,
            sources         JSON NULL,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_msg_conv FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id) ON DELETE CASCADE,
            INDEX ix_msg_conv (conversation_id, id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )


def downgrade() -> None:
    for t in ("ai_messages", "ai_conversations", "document_chunks", "documents"):
        op.execute(f"DROP TABLE IF EXISTS {t}")
