"""PHASE 4 — Learning Analytics.

Tính các chỉ số học tập từ dữ liệu thật: results / result_answers / lesson_progress.
Phân loại năng lực theo thang cố định (dùng lại ở Rule-based Recommendation, Phase 5).
"""
from sqlalchemy.orm import Session
import unicodedata

from app.core.database import q_all, q_one, q_scalar

MIN_TOPIC_QUESTIONS = 5
TOPIC_REVIEW_THRESHOLD = 70


def normalize_topic(value: str | None) -> str:
    """Merge Unicode, whitespace and case variants; never guess synonyms."""
    return ' '.join(unicodedata.normalize('NFC', value or '').split()).casefold()


def level_for(score: float | None) -> str:
    """<50 Weak · 50–70 Average · 70–85 Good · >=85 Excellent."""
    if score is None:
        return "Chưa có dữ liệu"
    if score < 50:
        return "Weak"
    if score < 70:
        return "Average"
    if score < 85:
        return "Good"
    return "Excellent"


# Bài kiểm tra chính thức = không phải bộ ôn tập chương / bài. Bộ ôn tập được làm lại không giới hạn
# nên không tính vào điểm trung bình, số lượt làm, tỷ lệ đạt.
def official(qz: str) -> str:
    return f"{qz}.chapter_id IS NULL AND {qz}.review_lesson_id IS NULL"


# Lượt được tính điểm của bài chính thức theo cách tính của quiz (khớp _graded ở routers/quizzes.py):
# trung bình -> mọi lượt; lần đầu / lần cuối -> 1 lượt; cao nhất (mặc định) -> lượt điểm cao nhất, bằng điểm lấy lượt sớm nhất
def counted_attempt(qz: str, r: str) -> str:
    same = f"rx.user_id = {r}.user_id AND rx.quiz_id = {r}.quiz_id"
    return f"""(
        {qz}.grading_method = 'average'
        OR ({qz}.grading_method = 'first' AND {r}.id = (SELECT MIN(rx.id) FROM results rx WHERE {same}))
        OR ({qz}.grading_method = 'latest' AND {r}.id = (SELECT MAX(rx.id) FROM results rx WHERE {same}))
        OR (COALESCE({qz}.grading_method, 'highest') NOT IN ('average', 'first', 'latest')
            AND {r}.id = (SELECT rx.id FROM results rx WHERE {same}
                          ORDER BY ROUND(rx.score * 100 / NULLIF(rx.total, 0)) DESC, rx.id ASC LIMIT 1))
    )"""


# Phạm vi tính điểm theo chủ đề: lượt được tính điểm của bài chính thức + CHỈ lượt gần nhất của mỗi bộ ôn tập
# (bài chính thức làm 20% rồi 100% với cách tính "cao nhất" thì chủ đề chỉ tính lượt 100%, giống điểm quiz;
# vẫn dùng dữ liệu ôn tập để phát hiện chủ đề yếu, nhưng làm lại nhiều lần không làm lệch kết quả)
def topic_scope(qz: str, r: str) -> str:
    return (
        f"(({official(qz)} AND {counted_attempt(qz, r)}) OR (NOT ({official(qz)}) AND {r}.id = "
        f"(SELECT MAX(rl.id) FROM results rl WHERE rl.user_id = {r}.user_id AND rl.quiz_id = {r}.quiz_id)))"
    )


# Điều kiện "đạt" của 1 lượt làm: theo điểm đạt của quiz LÚC NỘP BÀI (lưu ở results.passing_score), điểm % làm tròn
# như ở trang quiz. Quiz không đặt điểm đạt -> NULL (không có khái niệm đạt), giống nhãn Đạt / Chưa đạt ở trang quiz
def passed_expr(r: str) -> str:
    return (
        f"(CASE WHEN COALESCE({r}.passing_score, 0) = 0 THEN NULL "
        f"ELSE ROUND({r}.score * 100 / NULLIF({r}.total, 0)) >= {r}.passing_score END)"
    )


# Cách tính điểm khi làm nhiều lượt (quizzes.grading_method)
GRADING_METHODS = ("highest", "latest", "first", "average")


# Bảng tạm: 1 dòng cho mỗi (học viên, bài kiểm tra chính thức) với điểm % và trạng thái đạt được TÍNH
# theo cách tính của quiz: lượt cao nhất / lượt cuối / lượt đầu / trung bình các lượt.
# Dùng thay cho việc lấy trung bình mọi lượt (làm 20% -> 60% -> 100% không còn bị tính 60%).
def graded_sql() -> str:
    pct = "r.score * 100.0 / NULLIF(r.total, 0)"
    return f"""
        SELECT a.user_id, a.quiz_id, q.course_id, a.attempts,
            CASE q.grading_method
                WHEN 'average' THEN a.avg_pct
                WHEN 'first'   THEN rf.score * 100.0 / NULLIF(rf.total, 0)
                WHEN 'latest'  THEN rl.score * 100.0 / NULLIF(rl.total, 0)
                ELSE a.max_pct
            END AS pct,
            CASE q.grading_method
                WHEN 'average' THEN (CASE WHEN COALESCE(rl.passing_score, 0) = 0 THEN NULL
                                          ELSE ROUND(a.avg_pct) >= rl.passing_score END)
                WHEN 'first'   THEN {passed_expr("rf")}
                WHEN 'latest'  THEN {passed_expr("rl")}
                ELSE a.any_passed
            END AS passed
        FROM (
            SELECT r.user_id, r.quiz_id, COUNT(*) AS attempts, MIN(r.id) AS first_id, MAX(r.id) AS last_id,
                AVG({pct}) AS avg_pct, MAX({pct}) AS max_pct, MAX({passed_expr("r")}) AS any_passed
            FROM results r WHERE r.total > 0
            GROUP BY r.user_id, r.quiz_id
        ) a
        JOIN quizzes q  ON q.id = a.quiz_id
        JOIN results rf ON rf.id = a.first_id
        JOIN results rl ON rl.id = a.last_id
        WHERE {official("q")}
    """


# Tạo điều kiện lọc theo khóa học (nếu có course_id) để ghép vào các câu truy vấn quiz
def _course_filter(course_id: int | None) -> tuple[str, dict]:
    if course_id:
        return "AND q.course_id = :cid", {"cid": course_id}
    return "", {}


# Chỉ số tổng quan của 1 học viên (trong 1 khóa hoặc tất cả các khóa đã ghi danh)
def overview(db: Session, user_id: int, course_id: int | None = None) -> dict:
    cf, cp = _course_filter(course_id)
    p = {"uid": user_id, **cp}

    # Điểm quiz trung bình (%): mỗi bài kiểm tra chính thức lấy 1 điểm theo cách tính của quiz
    avg_score = q_scalar(
        db,
        f"""
        SELECT ROUND(AVG(q.pct), 1) FROM ({graded_sql()}) q
        WHERE q.user_id = :uid {cf}
        """,
        **p,
    )
    # Tổng số lượt làm bài kiểm tra chính thức
    quiz_attempts = int(
        q_scalar(
            db,
            f"SELECT COUNT(*) FROM results r JOIN quizzes q ON q.id = r.quiz_id "
            f"WHERE r.user_id = :uid AND {official('q')} {cf}",
            **p,
        )
        or 0
    )

    # Phạm vi bài học: 1 khóa cụ thể, hoặc mọi khóa học viên đã ghi danh
    if course_id:
        course_scope = "ch.course_id = :cid"
        lp = {"uid": user_id, "cid": course_id}
    else:
        course_scope = "ch.course_id IN (SELECT course_id FROM enrollments WHERE user_id = :uid)"
        lp = {"uid": user_id}

    # Đếm tổng số bài, số bài đã hoàn thành và tổng giây đã xem video
    lessons = q_one(
        db,
        f"""
        SELECT
            COUNT(DISTINCT l.id) AS total_lessons,
            COUNT(DISTINCT CASE WHEN lp.is_completed = 1 THEN l.id END) AS completed_lessons,
            COALESCE(SUM(lp.watched_sec), 0) AS total_time_sec
        FROM lessons l
        JOIN chapters ch ON ch.id = l.chapter_id
        LEFT JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.user_id = :uid
        WHERE {course_scope}
        """,
        **lp,
    ) or {}

    total_lessons = int(lessons.get("total_lessons") or 0)
    completed_lessons = int(lessons.get("completed_lessons") or 0)
    # % hoàn thành = số bài xong / tổng số bài (không có bài nào thì 0)
    completion_pct = round(completed_lessons * 100.0 / total_lessons, 1) if total_lessons else 0.0
    avg = float(avg_score) if avg_score is not None else None

    return {
        "avg_quiz_score": avg,
        "level": level_for(avg),
        "completion_pct": completion_pct,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "total_time_sec": int(lessons.get("total_time_sec") or 0),
        "quiz_attempts": quiz_attempts,
    }


# Điểm theo chủ đề: từ chi tiết từng câu trả lời (result_answers), nhóm theo topic của câu hỏi.
# Sắp xếp chủ đề yếu nhất lên đầu để bộ gợi ý dùng
def topics(db: Session, user_id: int, course_id: int | None = None, after_result_id: int | None = None) -> list[dict]:
    cf, cp = _course_filter(course_id)
    rows = q_all(
        db,
        f"""
        SELECT CASE WHEN ra.classification_version>0 THEN ra.topic_name ELSE q.topic END AS topic,
            CASE WHEN ra.classification_version>0 THEN ra.topic_id ELSE q.topic_id END AS topic_id,
            q.id AS question_id, ra.is_correct, qz.course_id,
            r.id AS result_id, r.submit_time, qz.id AS quiz_id,qz.title AS quiz_title,
            ra.classification_version,
            c.title AS course_title, COALESCE(qz.review_lesson_id, qz.lesson_id) AS lesson_id
        FROM result_answers ra
        JOIN results r   ON r.id = ra.result_id
        JOIN questions q ON q.id = ra.question_id
        JOIN quizzes qz  ON qz.id = r.quiz_id
        JOIN courses c ON c.id = qz.course_id
        WHERE r.user_id = :uid
        AND EXISTS (SELECT 1 FROM enrollments e WHERE e.user_id=:uid AND e.course_id=qz.course_id)
        AND r.id = (SELECT MAX(rl.id) FROM results rl WHERE rl.user_id=r.user_id AND rl.quiz_id=r.quiz_id)
        { cf.replace("q.course_id", "qz.course_id") }
        AND (:after_id IS NULL OR r.id>:after_id)
        ORDER BY qz.course_id, q.id
        """,
        uid=user_id, after_id=after_result_id,
        **cp,
    )
    return summarize_topics(rows)


def unclassified_answers(db: Session, user_id: int, course_id: int | None = None) -> int:
    cf, cp = _course_filter(course_id)
    return int(q_scalar(db, f"""
        SELECT COUNT(DISTINCT q.id) FROM result_answers ra
        JOIN results r ON r.id=ra.result_id JOIN questions q ON q.id=ra.question_id
        JOIN quizzes qz ON qz.id=r.quiz_id
        WHERE r.user_id=:uid AND (CASE WHEN ra.classification_version>0 THEN ra.topic_name ELSE q.topic END IS NULL OR TRIM(CASE WHEN ra.classification_version>0 THEN ra.topic_name ELSE q.topic END)='')
        AND EXISTS (SELECT 1 FROM enrollments e WHERE e.user_id=:uid AND e.course_id=qz.course_id)
        AND r.id=(SELECT MAX(rl.id) FROM results rl WHERE rl.user_id=r.user_id AND rl.quiz_id=r.quiz_id)
        {cf.replace('q.course_id','qz.course_id')}
    """, uid=user_id, **cp) or 0)


def summarize_topics(rows: list[dict]) -> list[dict]:
    """Content uses latest attempts, independently of the official grading policy."""
    groups = {}
    for r in rows:
        key = normalize_topic(r['topic'])
        if not key:
            continue
        g = groups.setdefault((r['course_id'], r.get('topic_id') or key), dict(topic=' '.join(r['topic'].split()), topic_id=r.get('topic_id'),
            course_id=r['course_id'], course_title=r['course_title'], answers={}, lesson_ids=set(), sources={}))
        g['answers'][r['question_id']] = int(r['is_correct'] or 0)
        if r.get('result_id'):
            source=g['sources'].setdefault(r['result_id'],dict(result_id=r['result_id'],quiz_id=r['quiz_id'],quiz_title=r['quiz_title'],topic_name=r['topic'],submitted_at=str(r['submit_time']),answers={},reconstructed=r.get('classification_version')==1))
            source['answers'][r['question_id']]=int(r['is_correct'] or 0)
        if r.get('lesson_id'):
            g['lesson_ids'].add(int(r['lesson_id']))
    out = []
    for g in groups.values():
        answers = g.pop('answers')
        n, correct = len(answers), sum(answers.values())
        score = round(correct * 100 / n, 1)
        for source in g['sources'].values():
            source_answers=source.pop('answers')
            source.update(answered=len(source_answers),correct=sum(source_answers.values()))
        g.update(answered=n, correct=correct, avg_score=score, question_ids=sorted(answers), sources=list(g['sources'].values()),
                 sufficient_data=n >= MIN_TOPIC_QUESTIONS,
                 status=level_for(score) if n >= MIN_TOPIC_QUESTIONS else 'Insufficient',
                 lesson_ids=sorted(g['lesson_ids']))
        out.append(g)
    return sorted(out, key=lambda t: (not t['sufficient_data'], t['avg_score'], -t['answered'], t['course_id'], t['topic']))


# Lịch sử các lần làm 1 quiz theo thời gian + mức tiến bộ (điểm lần cuối - điểm lần đầu)
def quiz_progress(db: Session, user_id: int, quiz_id: int) -> dict:
    attempts = q_all(
        db,
        """
        SELECT id, score, total,
            ROUND(score * 100.0 / NULLIF(total, 0)) AS percent,
            submit_time
        FROM results
        WHERE user_id = :uid AND quiz_id = :qid
        ORDER BY submit_time ASC
        """,
        uid=user_id,
        qid=quiz_id,
    )
    # Cần ít nhất 2 lần làm mới tính được tiến bộ
    improvement = None
    if len(attempts) >= 2:
        first = float(attempts[0]["percent"] or 0)
        last = float(attempts[-1]["percent"] or 0)
        improvement = round(last - first, 1)
    return {
        "quiz_id": quiz_id,
        "attempt_count": len(attempts),
        "attempts": attempts,
        "improvement": improvement,
    }
