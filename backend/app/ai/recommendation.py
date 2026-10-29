"""PHASE 5 — Rule-based Recommendation Engine (thuần Python, KHÔNG ML).

Đầu vào: kết quả từng câu ở lượt gần nhất, chủ đề và tiến độ học.
Đầu ra: căn cứ theo chủ đề và hành động ôn tập có thể giải thích.
"""
import json

from sqlalchemy.orm import Session

from app.core.database import execute, q_all, q_one
from app.services import analytics_service as an
from app.services import knowledge

def _focus_course(db: Session, user_id: int) -> dict | None:
    """Prefer an unfinished course with the most recent quiz submission."""
    return q_one(
        db,
        """
        SELECT c.id, c.title,
            COUNT(DISTINCT l.id) AS total_lessons,
            COUNT(DISTINCT CASE WHEN lp.is_completed = 1 THEN l.id END) AS done_lessons
        FROM enrollments e
        JOIN courses c   ON c.id = e.course_id
        JOIN chapters ch ON ch.course_id = c.id
        JOIN lessons l   ON l.chapter_id = ch.id
        LEFT JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.user_id = :uid
        WHERE e.user_id = :uid
        GROUP BY c.id, c.title
        HAVING total_lessons > 0 AND done_lessons < total_lessons
        ORDER BY (SELECT MAX(r.id) FROM results r JOIN quizzes q ON q.id=r.quiz_id
                  WHERE r.user_id=:uid AND q.course_id=c.id) DESC,
                 (done_lessons / total_lessons) ASC, c.id ASC
        LIMIT 1
        """,
        uid=user_id,
    )


# Bài học chưa hoàn thành đầu tiên của khóa, theo thứ tự chương rồi thứ tự bài
def _next_lesson(db: Session, user_id: int, course_id: int) -> dict | None:
    return q_one(
        db,
        """
        SELECT l.id, l.title, ch.course_id
        FROM lessons l
        JOIN chapters ch ON ch.id = l.chapter_id
        LEFT JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.user_id = :uid AND lp.is_completed = 1
        WHERE ch.course_id = :cid AND lp.id IS NULL
        ORDER BY ch.order_index ASC, ch.id ASC, l.order_index ASC, l.id ASC
        LIMIT 1
        """,
        uid=user_id,
        cid=course_id,
    )


# Retake follows the same score and attempt rules as the quiz screen.
def _weak_quiz(db: Session, user_id: int, course_id: int | None) -> dict | None:
    from app.routers.quizzes import _graded, _attempts_used
    params = {"uid": user_id}
    cf = "AND q.course_id=:cid" if course_id else ""
    if course_id:
        params["cid"] = course_id
    quizzes = q_all(db, f"SELECT q.* FROM quizzes q JOIN enrollments e ON e.course_id=q.course_id "
                    f"WHERE e.user_id=:uid {cf} AND EXISTS "
                    "(SELECT 1 FROM results r WHERE r.quiz_id=q.id AND r.user_id=:uid)", **params)
    candidates = []
    for quiz in quizzes:
        # First-attempt grading cannot improve the official score through a retake.
        if quiz.get('grading_method') == 'first':
            continue
        results = q_all(db, 'SELECT id,score,total,passing_score,submit_time FROM results WHERE user_id=:uid AND quiz_id=:qid ORDER BY id',
                        uid=user_id, qid=quiz['id'])
        score, passed, _ = _graded(quiz.get('grading_method'), results)
        if score is None or (passed is not False and score >= an.TOPIC_REVIEW_THRESHOLD):
            continue
        used = _attempts_used(db, user_id, quiz['id'])
        # A live attempt can be resumed, even if it has used the last allowed slot.
        active = q_one(db, 'SELECT id,started_ts FROM quiz_attempts WHERE user_id=:uid AND quiz_id=:qid AND finished_ts IS NULL ORDER BY id DESC LIMIT 1',
                       uid=user_id, qid=quiz['id'])
        from app.routers.quizzes import _expired
        resumable = bool(active and not _expired(quiz, active))
        if quiz.get('max_attempts') and used >= quiz['max_attempts'] and not resumable:
            continue
        candidates.append({**quiz, 'evaluated_score': score, 'passed': passed, 'resume': resumable, 'attempts_used':used, 'sources':[dict(result_id=r['id'],submitted_at=str(r.get('submit_time'))) for r in results],
                           'attempts_left': max(0, quiz['max_attempts']-used) if quiz.get('max_attempts') else None})
    return min(candidates, key=lambda q: (q['passed'] is not False, q['evaluated_score'], q['id'])) if candidates else None


def _topic_action(topic: dict, lessons: list[dict]) -> dict:
    if topic.get('confirmed') and topic.get('mapped_lesson_id'):
        match=next((l for l in lessons if l['id']==topic['mapped_lesson_id'] and l['course_id']==topic['course_id']),None)
        if match:
            return {'action_url':f"/lesson?id={match['id']}",'action_label':'Ôn bài học','lesson_title':match['title']}
    scoped = [l for l in lessons if l['course_id'] == topic['course_id']]
    # Use an explicit source lesson, or an unambiguous exact normalized title.
    matches = [l for l in scoped if l['id'] in topic['lesson_ids']]
    if not matches:
        matches = [l for l in scoped if knowledge.lesson_title_key(l['title']) == knowledge.lesson_title_key(topic['topic'])]
    if len(matches) == 1:
        lesson = matches[0]
        return {'action_url': f"/lesson?id={lesson['id']}", 'action_label': 'Ôn bài học', 'lesson_title': lesson['title']}
    return {'action_url': f"/chapters?course_id={topic['course_id']}", 'action_label': 'Xem bài học'}


def build(db: Session, user_id: int, course_id: int | None = None) -> dict:
    ov = an.overview(db, user_id, course_id)
    topics = an.topics(db, user_id, course_id)
    unclassified = an.unclassified_answers(db, user_id, course_id)
    lessons = q_all(db, 'SELECT l.id,l.title,ch.course_id FROM lessons l JOIN chapters ch ON ch.id=l.chapter_id '
                    'JOIN enrollments e ON e.course_id=ch.course_id WHERE e.user_id=:uid', uid=user_id)
    catalog=q_all(db,'SELECT t.* FROM course_topics t JOIN enrollments e ON e.course_id=t.course_id WHERE e.user_id=:uid',uid=user_id)
    for t in topics:
        meta=next((x for x in catalog if x['id']==t.get('topic_id') and x['course_id']==t['course_id']),None)
        if meta:
            t.update(catalog_name=meta['name'],confirmed=bool(meta['confirmed']),mapped_lesson_id=meta['lesson_id'],practice_quiz_id=meta['practice_quiz_id'])
            if an.normalize_topic(t['topic'])==an.normalize_topic(meta['name']):
                t['topic']=meta['name']
    weak = [t for t in topics if t['sufficient_data'] and t['avg_score'] < an.TOPIC_REVIEW_THRESHOLD]
    uncertain = [t for t in topics if not t['sufficient_data']]
    sufficient = [t for t in topics if t['sufficient_data']]
    level = 'ContentBased' if sufficient else 'Insufficient'
    knowledge_data = knowledge.current(db, user_id, course_id)
    items = knowledge.suggestions(db, user_id, knowledge_data['units'])
    covered_lessons = {u['id'] for u in knowledge_data['units'] if u['kind'] == 'lesson'}
    covered_chapters = {i['knowledge_evidence']['id'] for i in items if i['knowledge_evidence']['kind'] == 'chapter'}
    def covered_topic(topic):
        action = _topic_action(topic, lessons)
        return (any(action['action_url'] == f'/lesson?id={lid}' for lid in covered_lessons)
                or any(u['kind'] == 'chapter' and u['course_id'] == topic['course_id']
                       and an.normalize_topic(u['title']) == an.normalize_topic(topic['topic']) for u in knowledge_data['units'])
                or any(u['kind'] == 'chapter' and u['id'] in covered_chapters and u['course_id'] == topic['course_id']
                       for u in knowledge_data['units']))
    uncovered_weak = [t for t in weak if not covered_topic(t)]
    for t in uncovered_weak[:3]:
        action = _topic_action(t, lessons)
        text = f"Bạn trả lời đúng {t['correct']}/{t['answered']} câu về \"{t['topic']}\" ({t['avg_score']}%) trong khóa {t['course_title']}."
        text += f" Ôn bài \"{action['lesson_title']}\"." if action.get('lesson_title') else ' Hãy ôn nội dung này trong khóa học.'
        items.append({'type': 'review_topic', 'topic': t['topic'], 'topic_id':t.get('topic_id'),'evidence':t, 'text': text, **action})
    wq = _weak_quiz(db, user_id, course_id)
    if wq and not any(i.get('practice_url') == f"/quiz-show?id={wq['id']}" for i in items):
        method = {'highest':'cao nhất','latest':'lần cuối','average':'trung bình'}.get(wq.get('grading_method'), 'cao nhất')
        reason = 'chưa đạt yêu cầu đề' if wq['passed'] is False else 'cần luyện thêm'
        items.append({'type': 'retake_quiz', 'text': f"{wq['title']}: điểm {method} {wq['evaluated_score']}% — {reason}.",
                      'grade_evidence':dict(score=wq['evaluated_score'],method=method,passed=wq['passed'],attempts_used=wq['attempts_used'],attempts_left=wq['attempts_left'],sources=wq['sources']),
                      'action_url': f"/quiz-show?id={wq['id']}", 'action_label': 'Tiếp tục bài' if wq['resume'] else 'Làm lại quiz'})
    for t in [t for t in uncertain if not covered_topic(t)][:2]:
        items.append({'type':'practice_topic', 'topic': t['topic'], 'topic_id':t.get('topic_id'),'evidence':t,
                      'text': f"Chưa đủ dữ liệu về \"{t['topic']}\" trong khóa {t['course_title']}: đúng {t['correct']}/{t['answered']} câu. Hãy luyện thêm để kiểm tra kiến thức.",
                      **_topic_action(t, lessons)})
    if not topics and not knowledge_data['units']:
        items.append({'type':'advice', 'text':'Chưa đủ dữ liệu theo chủ đề. Hãy làm bài kiểm tra có phân loại nội dung để nhận gợi ý ôn tập.'})
    if unclassified and not knowledge_data['units']:
        items.append({'type':'advice', 'text':f'{unclassified} câu ở các lượt gần nhất chưa được gắn chủ đề. Các câu này vẫn tính điểm tổng nhưng chưa dùng để gợi ý theo nội dung.'})
    focus = _focus_course(db, user_id) if course_id is None else q_one(db,
        'SELECT c.id,c.title FROM courses c JOIN enrollments e ON e.course_id=c.id WHERE c.id=:cid AND e.user_id=:uid',
        cid=course_id, uid=user_id)
    if focus:
        nxt = _next_lesson(db, user_id, int(focus['id']))
        if nxt and not any(i.get('action_url') == f"/lesson?id={nxt['id']}" for i in items):
            items.append({'type':'next_lesson', 'text': f"Bài chưa hoàn thành tiếp theo: \"{nxt['title']}\" (khóa {focus['title']}).",
                          'action_url':f"/lesson?id={nxt['id']}", 'action_label':'Học tiếp'})
    knowledge_weak = any(u['needs_review'] for u in knowledge_data['units'])
    knowledge_sufficient = any(u['sufficient_data'] for u in knowledge_data['units'])
    if sufficient and not weak and not knowledge_weak:
        items.append({'type':'advice','text':'Các chủ đề có đủ dữ liệu đều đạt từ 70% câu đúng. Tiếp tục luyện tập các nội dung khác để mở rộng phạm vi đánh giá.'})
    for item in items:
        evidence=item.get('evidence')
        if evidence and evidence.get('confirmed') and evidence.get('practice_quiz_id'):
            item['practice_url']=practice_url(db,user_id,evidence['course_id'],evidence['practice_quiz_id'],evidence['topic_id'])
    if knowledge_sufficient:
        level = 'ContentBased'
    summary = ('Ưu tiên ôn các nội dung cần củng cố' if uncovered_weak or knowledge_weak else
               'Tiếp tục luyện tập và học nội dung tiếp theo' if sufficient or knowledge_sufficient else 'Chưa đủ dữ liệu để đánh giá theo nội dung')
    based_on = {**ov, 'assessment_method':'latest_attempt_by_topic', 'min_topic_questions':an.MIN_TOPIC_QUESTIONS,
                'topic_review_threshold':an.TOPIC_REVIEW_THRESHOLD, 'unclassified_answers':unclassified,
                'weakest_topic':weak[0]['topic'] if weak else None,
                'weak_topics':[t['topic'] for t in weak],
                'strong_topics':[t['topic'] for t in sufficient if t['status']=='Excellent'],
                'insufficient_topics':[t['topic'] for t in uncertain], 'topic_evidence':topics}
    based_on['knowledge'] = knowledge_data
    based_on['knowledge_assessment_method'] = 'latest_submission_per_lesson'
    return {'level':level, 'summary':summary, 'items':items, 'based_on':based_on, 'topics':topics}


def practice_url(db,user_id,course_id,quiz_id,topic_id):
    from app.routers.quizzes import _attempts_used,_expired
    if not q_one(db,'SELECT id FROM enrollments WHERE user_id=:u AND course_id=:c',u=user_id,c=course_id):
        return None
    quiz=q_one(db,'SELECT * FROM quizzes WHERE id=:id AND course_id=:c AND (chapter_id IS NOT NULL OR review_lesson_id IS NOT NULL)',id=quiz_id,c=course_id)
    if not quiz or not q_one(db,'SELECT id FROM questions WHERE quiz_id=:q AND topic_id=:t LIMIT 1',q=quiz_id,t=topic_id):
        return None
    active=q_one(db,'SELECT id,started_ts FROM quiz_attempts WHERE user_id=:u AND quiz_id=:q AND finished_ts IS NULL ORDER BY id DESC LIMIT 1',u=user_id,q=quiz_id)
    if quiz.get('max_attempts') and _attempts_used(db,user_id,quiz_id)>=quiz['max_attempts'] and not (active and not _expired(quiz,active)):
        return None
    return f'/quiz-show?id={quiz_id}'


def save(db: Session, user_id: int, course_id: int | None, rec: dict) -> dict:
    """Ghi 1 dòng recommendations + cập nhật snapshot learning_analytics."""
    # Lưu 1 dòng lịch sử gợi ý (items, based_on lưu dạng JSON)
    res = execute(
        db,
        "INSERT INTO recommendations (user_id, course_id, level, summary, items, based_on) "
        "VALUES (:u, :c, :lvl, :s, :items, :bo)",
        u=user_id,
        c=course_id,
        lvl=rec["level"],
        s=rec["summary"],
        items=json.dumps(rec["items"], ensure_ascii=False),
        bo=json.dumps(rec["based_on"], ensure_ascii=False),
    )
    bo = rec["based_on"]
    # Gợi ý theo 1 khóa cụ thể -> cập nhật bản chụp số liệu học tập (mỗi học viên + khóa 1 dòng, có thì ghi đè)
    if course_id:
        execute(
            db,
            """
            INSERT INTO learning_analytics
                (user_id, course_id, avg_quiz_score, completion_pct, completed_lessons,
                 total_lessons, total_time_sec, quiz_attempts, weak_topics, strong_topics)
            VALUES (:u, :c, :avg, :cp, :cl, :tl, :tt, :qa, :wt, :st)
            ON DUPLICATE KEY UPDATE
                avg_quiz_score=VALUES(avg_quiz_score), completion_pct=VALUES(completion_pct),
                completed_lessons=VALUES(completed_lessons), total_lessons=VALUES(total_lessons),
                total_time_sec=VALUES(total_time_sec), quiz_attempts=VALUES(quiz_attempts),
                weak_topics=VALUES(weak_topics), strong_topics=VALUES(strong_topics)
            """,
            u=user_id,
            c=course_id,
            avg=bo["avg_quiz_score"],
            cp=bo["completion_pct"],
            cl=bo["completed_lessons"],
            tl=bo["total_lessons"],
            tt=bo["total_time_sec"],
            qa=bo["quiz_attempts"],
            wt=json.dumps(bo["weak_topics"], ensure_ascii=False),
            st=json.dumps(bo["strong_topics"], ensure_ascii=False),
        )
    # Đọc lại dòng vừa lưu để trả về cho frontend
    saved = q_one(db, "SELECT * FROM recommendations WHERE id = :id", id=res.lastrowid)
    return _row(saved)


# Lịch sử các lần gợi ý đã lưu của học viên, mới nhất trước
def history(db: Session, user_id: int, limit: int = 10) -> list[dict]:
    rows = q_all(
        db,
        f"SELECT * FROM recommendations WHERE user_id = :uid ORDER BY created_at DESC, id DESC LIMIT {int(limit)}",
        uid=user_id,
    )
    return [_row(r) for r in rows]


# Chuyển các cột JSON (items, based_on) từ chuỗi về dict/list
def _row(r: dict | None) -> dict | None:
    if not r:
        return None
    out = dict(r)
    for k in ("items", "based_on"):
        v = out.get(k)
        if isinstance(v, str):
            try:
                out[k] = json.loads(v)
            except ValueError:
                out[k] = None
    return out
