"""Question chapter/lesson scope and immutable assessment evidence."""
from alembic import op
import sqlalchemy as sa

revision = '0021_knowledge_scope'
down_revision = '0020_topic_catalog'
branch_labels = None
depends_on = None


def upgrade():
    for column, table in [('knowledge_chapter_id', 'chapters'), ('knowledge_lesson_id', 'lessons')]:
        op.add_column('questions', sa.Column(column, sa.Integer(), nullable=True))
        op.create_foreign_key('fk_question_' + column, 'questions', table, [column], ['id'], ondelete='SET NULL')
    for column, type_ in [('knowledge_chapter_id', sa.Integer()), ('knowledge_lesson_id', sa.Integer()),
                           ('knowledge_chapter_name', sa.String(255)), ('knowledge_lesson_name', sa.String(255))]:
        op.add_column('result_answers', sa.Column(column, type_, nullable=True))
    op.add_column('result_answers', sa.Column('knowledge_version', sa.Integer(), nullable=False, server_default='0'))
    op.create_table('knowledge_study_checkpoints',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('unit_kind', sa.String(10), nullable=False), sa.Column('unit_id', sa.Integer(), nullable=False),
        sa.Column('baseline', sa.JSON(), nullable=False), sa.Column('baseline_result_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False))
    op.create_index('ix_knowledge_study_user', 'knowledge_study_checkpoints', ['user_id', 'id'])
    # Reconstruct only from explicit quiz scope or an unambiguous structural title.
    # Historical topic snapshots take precedence over today's edited question topic.
    from app.services.knowledge import outline, resolve, snapshot
    from sqlalchemy.orm import Session
    db = Session(bind=op.get_bind())
    structures = {}
    questions = db.execute(sa.text('SELECT q.id,q.topic,qz.course_id,qz.chapter_id,qz.lesson_id,qz.review_lesson_id FROM questions q JOIN quizzes qz ON qz.id=q.quiz_id')).mappings().all()
    for q in questions:
        if q['course_id'] not in structures:
            structures[q['course_id']] = outline(db, q['course_id'])
        data = structures[q['course_id']]
        scope = resolve(db, q['course_id'], {'topic': q['topic']}, q, data)
        db.execute(sa.text('UPDATE questions SET knowledge_chapter_id=:knowledge_chapter_id,knowledge_lesson_id=:knowledge_lesson_id WHERE id=:id'), dict(id=q['id'], **scope))
    answers = db.execute(sa.text('''SELECT ra.id,CASE WHEN ra.classification_version>0 THEN ra.topic_name ELSE q.topic END AS topic,
        qz.course_id,qz.chapter_id,qz.lesson_id,qz.review_lesson_id FROM result_answers ra
        JOIN questions q ON q.id=ra.question_id JOIN results r ON r.id=ra.result_id JOIN quizzes qz ON qz.id=r.quiz_id''')).mappings().all()
    for answer in answers:
        data = structures[answer['course_id']]
        scope = resolve(db, answer['course_id'], {'topic': answer['topic']}, answer, data)
        saved = snapshot(db, scope, data)
        db.execute(sa.text('''UPDATE result_answers SET knowledge_chapter_id=:knowledge_chapter_id,
            knowledge_lesson_id=:knowledge_lesson_id,knowledge_chapter_name=:knowledge_chapter_name,
            knowledge_lesson_name=:knowledge_lesson_name,knowledge_version=1 WHERE id=:id'''), dict(id=answer['id'], **saved))


def downgrade():
    op.drop_table('knowledge_study_checkpoints')
    for column in ['knowledge_version', 'knowledge_lesson_name', 'knowledge_chapter_name', 'knowledge_lesson_id', 'knowledge_chapter_id']:
        op.drop_column('result_answers', column)
    for column in ['knowledge_lesson_id', 'knowledge_chapter_id']:
        op.drop_constraint('fk_question_' + column, 'questions', type_='foreignkey')
        op.drop_column('questions', column)
