"""Chapter/lesson evidence shared by exams, chapter reviews and lesson practice."""
import re

from app.core.database import q_all, q_one
from app.core.responses import ApiError
from app.services.analytics_service import MIN_TOPIC_QUESTIONS, TOPIC_REVIEW_THRESHOLD, normalize_topic


def outline(db, course_id):
    chapters = q_all(db, 'SELECT id,chapter_name,order_index FROM chapters WHERE course_id=:c ORDER BY order_index,id', c=course_id)
    lessons = q_all(db, '''SELECT l.id,l.title,l.chapter_id,l.order_index FROM lessons l
        JOIN chapters ch ON ch.id=l.chapter_id WHERE ch.course_id=:c ORDER BY ch.order_index,ch.id,l.order_index,l.id''', c=course_id)
    return {'chapters': chapters, 'lessons': lessons}


def _id(value):
    if value in (None, '', 0):
        return None
    try:
        result = int(value)
        if isinstance(value, bool) or str(result) != str(value).strip() or result <= 0:
            raise ValueError
        return result
    except (ValueError, TypeError):
        raise ApiError('Chương hoặc bài học không hợp lệ.')


def lesson_title_key(value):
    # Only remove the structural lesson number; do not guess synonyms by keywords.
    return re.sub(r'^bài\s+\d+\s*[:.\-–]\s*', '', normalize_topic(value))


def resolve(db, course_id, body, quiz=None, structure=None):
    """Validate explicit IDs; otherwise use the quiz scope or an unambiguous title."""
    data = structure or outline(db, course_id)
    quiz = quiz or {}
    explicit = 'knowledge_chapter_id' in body or 'knowledge_lesson_id' in body
    chapter_id = _id(body.get('knowledge_chapter_id'))
    lesson_id = _id(body.get('knowledge_lesson_id'))
    locked_lesson = _id(quiz.get('review_lesson_id') or quiz.get('lesson_id'))
    locked_chapter = _id(quiz.get('chapter_id'))
    if not explicit:
        lesson_id = locked_lesson
        chapter_id = locked_chapter
        if not lesson_id:
            candidates = [l for l in data['lessons'] if lesson_title_key(l['title']) == lesson_title_key(body.get('topic'))
                          and (not chapter_id or l['chapter_id'] == chapter_id)]
            if len(candidates) == 1:
                lesson_id = candidates[0]['id']
        if not chapter_id and not lesson_id:
            candidates = [ch for ch in data['chapters'] if normalize_topic(ch['chapter_name']) == normalize_topic(body.get('topic'))]
            if len(candidates) == 1:
                chapter_id = candidates[0]['id']
    lesson = next((l for l in data['lessons'] if l['id'] == lesson_id), None)
    if lesson_id and not lesson:
        raise ApiError('Bài học không thuộc khóa học này.')
    if lesson:
        if chapter_id and lesson['chapter_id'] != chapter_id:
            raise ApiError('Bài học không thuộc chương đã chọn.')
        chapter_id = lesson['chapter_id']
    if chapter_id and not any(ch['id'] == chapter_id for ch in data['chapters']):
        raise ApiError('Chương không thuộc khóa học này.')
    if locked_lesson and lesson_id != locked_lesson:
        raise ApiError('Câu hỏi phải thuộc bài học của bộ ôn tập.')
    if locked_chapter and chapter_id != locked_chapter:
        raise ApiError('Câu hỏi phải thuộc chương của bộ ôn tập.')
    return {'knowledge_chapter_id': chapter_id, 'knowledge_lesson_id': lesson_id}


def snapshot(db, question, structure=None):
    ch_id, lesson_id = question.get('knowledge_chapter_id'), question.get('knowledge_lesson_id')
    data = structure or outline(db, question['course_id'])
    chapter = next((ch for ch in data['chapters'] if ch['id'] == ch_id), None)
    lesson = next((l for l in data['lessons'] if l['id'] == lesson_id), None)
    return dict(knowledge_chapter_id=ch_id, knowledge_lesson_id=lesson_id,
                knowledge_chapter_name=chapter['chapter_name'] if chapter else None,
                knowledge_lesson_name=lesson['title'] if lesson else None)


def rows(db, user_id, course_id=None, result_id=None):
    return q_all(db, '''SELECT ra.question_id,ra.is_correct,ra.knowledge_chapter_id AS chapter_id,
        ra.knowledge_lesson_id AS lesson_id,ra.knowledge_chapter_name AS chapter_name,
        ra.knowledge_lesson_name AS lesson_name,ra.knowledge_version,
        CASE WHEN live_ch.id IS NOT NULL THEN 1 ELSE 0 END AS chapter_available,
        CASE WHEN live_l.id IS NOT NULL AND lesson_ch.course_id=qz.course_id THEN 1 ELSE 0 END AS lesson_available,
        r.id AS result_id,r.submit_time,qz.id AS quiz_id,qz.title AS quiz_title,
        qz.course_id,c.title AS course_title,
        CASE WHEN qz.review_lesson_id IS NOT NULL OR qz.lesson_id IS NOT NULL THEN 'lesson'
             WHEN qz.chapter_id IS NOT NULL THEN 'chapter' ELSE 'course' END AS assessment_scope
        FROM result_answers ra JOIN results r ON r.id=ra.result_id
        JOIN quizzes qz ON qz.id=r.quiz_id JOIN courses c ON c.id=qz.course_id
        LEFT JOIN chapters live_ch ON live_ch.id=ra.knowledge_chapter_id AND live_ch.course_id=qz.course_id
        LEFT JOIN lessons live_l ON live_l.id=ra.knowledge_lesson_id
        LEFT JOIN chapters lesson_ch ON lesson_ch.id=live_l.chapter_id
        WHERE r.user_id=:u AND (:c IS NULL OR qz.course_id=:c) AND (:r IS NULL OR r.id=:r)
        AND EXISTS (SELECT 1 FROM enrollments e WHERE e.user_id=:u AND e.course_id=qz.course_id)
        ORDER BY r.id,ra.question_id''', u=user_id, c=course_id, r=result_id)


def summarize(evidence, latest=True):
    # A newer result replaces evidence for the same lesson across all quiz types.
    # Keep the other lessons of a broad exam until those are assessed again.
    selected = {}
    latest_question = {}
    if latest:
        for row in evidence:
            key = (row['course_id'], row['question_id'])
            latest_question[key] = max(row['result_id'], latest_question.get(key, 0))
    for row in evidence:
        if latest and row['result_id'] != latest_question[(row['course_id'], row['question_id'])]:
            continue
        if not row['chapter_id']:
            continue
        key = (row['course_id'], row['chapter_id'], row['lesson_id'])
        if key not in selected or (latest and row['result_id'] > selected[key][0]['result_id']):
            selected[key] = [row]
        elif not latest or row['result_id'] == selected[key][0]['result_id']:
            selected[key].append(row)
    groups = {}
    for bucket in selected.values():
        for row in bucket:
            for kind, unit_id, title in [('chapter', row['chapter_id'], row['chapter_name']),
                                         ('lesson', row['lesson_id'], row['lesson_name'])]:
                if not unit_id:
                    continue
                key = (row['course_id'], kind, unit_id)
                group = groups.setdefault(key, dict(kind=kind, id=unit_id, title=title,
                    course_id=row['course_id'], course_title=row['course_title'], chapter_id=row['chapter_id'],
                    chapter_name=row['chapter_name'], answers={}, sources={}, reconstructed=False,
                    available=bool(row.get(f'{kind}_available', True))))
                group['answers'][row['question_id']] = int(row['is_correct'])
                group['reconstructed'] |= row.get('knowledge_version') == 1
                source = group['sources'].setdefault(row['result_id'], dict(result_id=row['result_id'],
                    quiz_id=row['quiz_id'], quiz_title=row['quiz_title'], submitted_at=str(row['submit_time']),
                    scope=row['assessment_scope'], answered=0, correct=0))
                source['answered'] += 1
                source['correct'] += int(row['is_correct'])
    out = []
    for group in groups.values():
        answers = group.pop('answers')
        n, correct = len(answers), sum(answers.values())
        sufficient = n >= MIN_TOPIC_QUESTIONS
        score = round(100 * correct / n, 1)
        group.update(answered=n, correct=correct, avg_score=score, sufficient_data=sufficient, question_ids=sorted(answers),
                     needs_review=sufficient and score < TOPIC_REVIEW_THRESHOLD,
                     status='Insufficient' if not sufficient else 'Review' if score < TOPIC_REVIEW_THRESHOLD else 'Good',
                     sources=list(group['sources'].values()), latest_result_id=max(group['sources']))
        out.append(group)
    return sorted(out, key=lambda g: (not g['needs_review'], g['avg_score'], -g['answered'], g['course_id'], g['id']))


def current(db, user_id, course_id=None):
    evidence = rows(db, user_id, course_id)
    latest = {}
    for row in evidence:
        latest[row['quiz_id']] = max(row['result_id'], latest.get(row['quiz_id'], 0))
    return {'units': summarize(evidence), 'unmapped_answers': sum(not r['chapter_id'] and r['result_id'] == latest[r['quiz_id']] for r in evidence)}


def assessment(db, user_id, result_id):
    evidence = rows(db, user_id, result_id=result_id)
    return {'units': summarize(evidence, latest=False), 'unmapped_answers': sum(not r['chapter_id'] for r in evidence),
            'min_questions': MIN_TOPIC_QUESTIONS, 'review_threshold': TOPIC_REVIEW_THRESHOLD}


def available_practice(db, user_id, course_id, kind, unit_id):
    from app.routers.quizzes import _attempts_used, _expired
    scope = '(q.review_lesson_id=:unit OR q.lesson_id=:unit)' if kind == 'lesson' else 'q.chapter_id=:unit'
    candidates = q_all(db, f'''SELECT q.* FROM quizzes q JOIN enrollments e ON e.course_id=q.course_id
        WHERE e.user_id=:u AND q.course_id=:c AND {scope}
        AND EXISTS (SELECT 1 FROM questions x WHERE x.quiz_id=q.id) ORDER BY q.id''', u=user_id, c=course_id, unit=unit_id)
    for quiz in candidates:
        active = q_one(db, '''SELECT id,started_ts FROM quiz_attempts WHERE user_id=:u AND quiz_id=:q
            AND finished_ts IS NULL ORDER BY id DESC LIMIT 1''', u=user_id, q=quiz['id'])
        resumable = active and not _expired(quiz, active)
        if quiz.get('max_attempts') and _attempts_used(db, user_id, quiz['id']) >= quiz['max_attempts'] and not resumable:
            continue
        return {'practice_url': f"/quiz-show?id={quiz['id']}", 'practice_label': 'Tiếp tục bài luyện' if resumable else 'Làm bài luyện'}
    return {}


def suggestions(db, user_id, units):
    items = []
    # Prefer specific lessons; a chapter covers only the remaining weak/uncertain parts.
    targets = [u for u in units if u.get('available', True)
               and (u['needs_review'] or (not u['sufficient_data'] and u['correct'] < u['answered']))]
    targets.sort(key=lambda u: (not u['needs_review'], u['kind'] != 'lesson', u['avg_score'], -u['latest_result_id']))
    lesson_chapters = {(u['course_id'], u['chapter_id']) for u in targets if u['kind'] == 'lesson' and u['needs_review']}
    weak_chapters = {(u['course_id'], u['id']) for u in targets if u['kind'] == 'chapter' and u['needs_review']}
    for unit in targets:
        if unit['kind'] == 'chapter' and (unit['course_id'], unit['id']) in lesson_chapters:
            # Keep chapter totals in the assessment table; one actionable lesson card avoids duplication.
            continue
        if unit['kind'] == 'lesson' and not unit['sufficient_data'] and (unit['course_id'], unit['chapter_id']) in weak_chapters:
            continue
        text = f"{unit['title']}: đúng {unit['correct']}/{unit['answered']} câu ({unit['avg_score']}%) trong khóa {unit['course_title']}. "
        text += 'Nên ôn lại phần kiến thức này.' if unit['needs_review'] else 'Số câu còn ít; hãy luyện thêm để kiểm tra kiến thức.'
        action = f"/lesson?id={unit['id']}" if unit['kind'] == 'lesson' else f"/chapters?course_id={unit['course_id']}&chapter_id={unit['id']}"
        practice = available_practice(db, user_id, unit['course_id'], unit['kind'], unit['id'])
        if not practice and unit['kind'] == 'lesson':
            practice = available_practice(db, user_id, unit['course_id'], 'chapter', unit['chapter_id'])
            if practice:
                practice['practice_label'] = 'Luyện cả chương'
        items.append(dict(type='review_knowledge', text=text, knowledge_evidence=unit,
            action_url=action, action_label='Ôn bài học' if unit['kind'] == 'lesson' else 'Xem chương',
            **practice))
        if len(items) == 3:
            break
    return items
