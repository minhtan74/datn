"""Shared topic selection for manual, Word and approved AI questions."""
from app.core.database import q_one, q_all
from app.core.responses import ApiError
from app.services.analytics_service import normalize_topic
from sqlalchemy import text


def resolve_topic(db, course_id, topic_id=None, name=None):
    if not q_one(db,'SELECT id FROM courses WHERE id=:c',c=course_id):
        raise ApiError('Khóa học không tồn tại.',404)
    if topic_id:
        try:
            topic_id=int(topic_id)
        except (ValueError,TypeError):
            raise ApiError('Chủ đề không hợp lệ.')
        row=q_one(db,'SELECT * FROM course_topics WHERE id=:id AND course_id=:c',id=topic_id,c=course_id)
        if not row:
            raise ApiError('Chủ đề không thuộc khóa học này.')
        return row
    clean=' '.join((name or '').split())[:100]
    if not clean:
        return None
    key=normalize_topic(clean)
    row=q_one(db,'SELECT * FROM course_topics WHERE course_id=:c AND normalized_name=:k',c=course_id,k=key)
    if not row:
        # Part of the caller's transaction; a later validation failure does not commit.
        db.execute(text('INSERT INTO course_topics (course_id,name,normalized_name) VALUES (:c,:n,:k)'),dict(c=course_id,n=clean,k=key))
        row=q_one(db,'SELECT * FROM course_topics WHERE course_id=:c AND normalized_name=:k',c=course_id,k=key)
    return row


def catalog(db,course_id):
    return q_all(db,'''SELECT t.*, l.title AS lesson_title,q.title AS practice_title,
        (SELECT COUNT(*) FROM questions x WHERE x.topic_id=t.id) AS question_count
        FROM course_topics t LEFT JOIN lessons l ON l.id=t.lesson_id
        LEFT JOIN quizzes q ON q.id=t.practice_quiz_id WHERE t.course_id=:c ORDER BY t.name,t.id''',c=course_id)
