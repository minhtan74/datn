"""Observed changes after opening a study suggestion; no causal claims."""
import json
from app.core.database import q_all,q_one,q_scalar,execute
from app.core.responses import ApiError
from app.services import analytics_service as an


def start(db,user_id,topic_id):
    topic=q_one(db,'SELECT t.* FROM course_topics t JOIN enrollments e ON e.course_id=t.course_id WHERE t.id=:t AND e.user_id=:u',t=topic_id,u=user_id)
    if not topic:
        raise ApiError('Không có quyền học chủ đề này.',403)
    evidence=next((t for t in an.topics(db,user_id,topic['course_id']) if t.get('topic_id')==topic_id),None)
    if not evidence:
        raise ApiError('Chưa có kết quả làm căn cứ cho mốc ôn tập.')
    last=int(q_scalar(db,'SELECT MAX(id) FROM results WHERE user_id=:u',u=user_id) or 0)
    # Repeated clicks without a new submission do not reset the baseline.
    previous=q_one(db,'SELECT id FROM study_checkpoints WHERE user_id=:u AND topic_id=:t AND baseline_result_id=:r ORDER BY id DESC LIMIT 1',u=user_id,t=topic_id,r=last)
    if previous:
        return previous
    result=execute(db,'INSERT INTO study_checkpoints (user_id,topic_id,baseline,baseline_result_id) VALUES (:u,:t,:b,:r)',
                   u=user_id,t=topic_id,b=json.dumps(evidence,ensure_ascii=False,default=str),r=last)
    return {'id':result.lastrowid}


def comparison(before,after):
    if not after:
        return {'state':'waiting','difference_pct':None,'same_questions':False,'sufficient_data':False}
    same=set(before.get('question_ids',[]))==set(after.get('question_ids',[]))
    sufficient=before['answered']>=an.MIN_TOPIC_QUESTIONS and after['answered']>=an.MIN_TOPIC_QUESTIONS
    return {'state':'compared','difference_pct':round(after['avg_score']-before['avg_score'],1),
            'same_questions':same,'sufficient_data':sufficient,
            'note':'Đây là thay đổi tỷ lệ đúng sau khi mở gợi ý ôn. Không chứng minh việc ôn gây ra cải thiện. '
                   + ('Cùng bộ câu hỏi nên có thể chịu ảnh hưởng của việc nhớ đáp án.' if same else 'Bộ câu hỏi khác nhau nên độ khó có thể khác.')}


def start_knowledge(db, user_id, course_id, kind, unit_id):
    from app.services import knowledge
    if kind not in ('chapter', 'lesson') or not q_one(db, 'SELECT id FROM enrollments WHERE user_id=:u AND course_id=:c', u=user_id, c=course_id):
        raise ApiError('Không có quyền ôn phần kiến thức này.', 403)
    evidence = next((u for u in knowledge.current(db, user_id, course_id)['units'] if u['kind'] == kind and u['id'] == unit_id), None)
    if not evidence or not evidence.get('available', True):
        raise ApiError('Chưa có kết quả làm căn cứ cho mốc ôn tập.')
    last = int(q_scalar(db, 'SELECT MAX(id) FROM results WHERE user_id=:u', u=user_id) or 0)
    previous = q_one(db, '''SELECT id FROM knowledge_study_checkpoints WHERE user_id=:u AND course_id=:c
        AND unit_kind=:k AND unit_id=:i AND baseline_result_id=:r ORDER BY id DESC LIMIT 1''', u=user_id, c=course_id, k=kind, i=unit_id, r=last)
    if previous:
        return previous
    saved = execute(db, '''INSERT INTO knowledge_study_checkpoints (user_id,course_id,unit_kind,unit_id,baseline,baseline_result_id)
        VALUES (:u,:c,:k,:i,:b,:r)''', u=user_id, c=course_id, k=kind, i=unit_id, b=json.dumps(evidence, ensure_ascii=False), r=last)
    return {'id': saved.lastrowid}


def history(db,user_id,course_id=None):
    checkpoints=q_all(db,'''SELECT s.*,t.name AS topic,t.course_id,c.title AS course_title
        FROM study_checkpoints s JOIN course_topics t ON t.id=s.topic_id
        JOIN courses c ON c.id=t.course_id JOIN enrollments e ON e.course_id=t.course_id AND e.user_id=s.user_id
        WHERE s.user_id=:u AND (:cid IS NULL OR t.course_id=:cid) ORDER BY s.id DESC LIMIT 10''',u=user_id,cid=course_id)
    for entry in checkpoints:
        before=json.loads(entry['baseline']) if isinstance(entry['baseline'],str) else entry['baseline']
        after=next((t for t in an.topics(db,user_id,entry['course_id'],after_result_id=entry['baseline_result_id']) if t.get('topic_id')==entry['topic_id']),None)
        entry.update(before=before,after=after,**comparison(before,after))
        entry.pop('baseline')
        entry['checkpoint_kind'] = 'topic'
    from app.services import knowledge
    entries = q_all(db, '''SELECT s.*,c.title AS course_title FROM knowledge_study_checkpoints s
        JOIN courses c ON c.id=s.course_id JOIN enrollments e ON e.course_id=s.course_id AND e.user_id=s.user_id
        WHERE s.user_id=:u AND (:cid IS NULL OR s.course_id=:cid) ORDER BY s.id DESC LIMIT 10''', u=user_id, cid=course_id)
    for entry in entries:
        before = json.loads(entry['baseline']) if isinstance(entry['baseline'], str) else entry['baseline']
        new_rows = [r for r in knowledge.rows(db, user_id, entry['course_id']) if r['result_id'] > entry['baseline_result_id']]
        after = next((u for u in knowledge.summarize(new_rows) if u['kind'] == entry['unit_kind'] and u['id'] == entry['unit_id']), None)
        entry.update(checkpoint_kind='knowledge', topic=before['title'], before=before, after=after, **comparison(before, after))
        entry.pop('baseline')
    return sorted(checkpoints + entries, key=lambda e: str(e.get('started_at') or ''), reverse=True)[:10]
