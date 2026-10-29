"""Course topic catalog, immutable answer classification and study checkpoints."""
import unicodedata
from alembic import op
import sqlalchemy as sa

revision = '0020_topic_catalog'
down_revision = '0019_content_recommendations'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''CREATE TABLE course_topics (
        id INT AUTO_INCREMENT PRIMARY KEY, course_id INT NOT NULL,
        name VARCHAR(100) NOT NULL, normalized_name VARCHAR(200) NOT NULL,
        lesson_id INT NULL, practice_quiz_id INT NULL, confirmed TINYINT NOT NULL DEFAULT 0,
        UNIQUE KEY uq_course_topic (course_id,normalized_name),
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
        FOREIGN KEY (practice_quiz_id) REFERENCES quizzes(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin''')
    op.add_column('questions', sa.Column('topic_id',sa.Integer(),nullable=True))
    op.create_foreign_key('fk_question_topic','questions','course_topics',['topic_id'],['id'],ondelete='SET NULL')
    op.add_column('result_answers',sa.Column('topic_id',sa.Integer(),nullable=True))
    op.add_column('result_answers',sa.Column('topic_name',sa.String(100),nullable=True))
    op.add_column('result_answers',sa.Column('classification_version',sa.Integer(),nullable=False,server_default='0'))
    op.execute('''CREATE TABLE study_checkpoints (
        id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, topic_id INT NOT NULL,
        baseline JSON NOT NULL, baseline_result_id INT NOT NULL,
        started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES course_topics(id) ON DELETE CASCADE,
        INDEX ix_study_user (user_id,started_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')
    conn=op.get_bind()
    rows=conn.execute(sa.text('SELECT q.id,q.topic,qz.course_id FROM questions q JOIN quizzes qz ON qz.id=q.quiz_id WHERE q.topic IS NOT NULL')).mappings()
    ids={}
    for row in list(rows):
        name=' '.join(unicodedata.normalize('NFC',row['topic']).split())[:100]
        if not name:
            continue
        key=(row['course_id'],name.casefold())
        if key not in ids:
            result=conn.execute(sa.text('INSERT INTO course_topics (course_id,name,normalized_name) VALUES (:c,:n,:k)'),dict(c=key[0],n=name,k=key[1]))
            ids[key]=result.lastrowid
        conn.execute(sa.text('UPDATE questions SET topic_id=:t WHERE id=:q'),dict(t=ids[key],q=row['id']))
    # Existing answers can only be reconstructed from the current question metadata.
    op.execute('UPDATE result_answers ra JOIN questions q ON q.id=ra.question_id SET ra.topic_id=q.topic_id,ra.topic_name=q.topic,ra.classification_version=1')


def downgrade():
    op.drop_table('study_checkpoints')
    for col in ['classification_version','topic_name','topic_id']:
        op.drop_column('result_answers',col)
    op.drop_constraint('fk_question_topic','questions',type_='foreignkey')
    op.drop_column('questions','topic_id')
    op.drop_table('course_topics')
