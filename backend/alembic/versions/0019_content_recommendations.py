"""Represent missing evidence and content-based recommendations explicitly."""
from alembic import op

revision = '0019_content_recommendations'
down_revision = '0018_attempt_shuffle'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE recommendations MODIFY level ENUM('Weak','Average','Good','Excellent','Insufficient','ContentBased') NOT NULL")
    op.execute('ALTER TABLE learning_analytics MODIFY avg_quiz_score DECIMAL(5,2) NULL')


def downgrade():
    op.execute("UPDATE recommendations SET level='Average' WHERE level IN ('Insufficient','ContentBased')")
    op.execute("ALTER TABLE recommendations MODIFY level ENUM('Weak','Average','Good','Excellent') NOT NULL")
    op.execute('UPDATE learning_analytics SET avg_quiz_score=0 WHERE avg_quiz_score IS NULL')
    op.execute('ALTER TABLE learning_analytics MODIFY avg_quiz_score DECIMAL(5,2) NOT NULL DEFAULT 0')
