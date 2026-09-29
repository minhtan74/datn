"""PHASE 4 — Learning Analytics.

Tính các chỉ số học tập từ dữ liệu thật: results / result_answers / lesson_progress.
Phân loại năng lực theo thang cố định (dùng lại ở Rule-based Recommendation, Phase 5).
"""
from sqlalchemy.orm import Session

from app.core.database import q_all, q_one, q_scalar


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


# Phạm vi tính điểm theo chủ đề: mọi lượt của bài chính thức + CHỈ lượt gần nhất của mỗi bộ ôn tập
# (vẫn dùng dữ liệu ôn tập để phát hiện chủ đề yếu, nhưng làm lại nhiều lần không làm lệch kết quả)
def topic_scope(qz: str, r: str) -> str:
    return (
        f"({official(qz)} OR {r}.id = (SELECT MAX(rl.id) FROM results rl "
        f"WHERE rl.user_id = {r}.user_id AND rl.quiz_id = {r}.quiz_id))"
    )


# Điều kiện "đạt" của 1 lượt làm: theo điểm đạt của quiz LÚC NỘP BÀI (lưu ở results.passing_score),
# quiz không đặt điểm đạt thì lấy 50% — đổi điểm đạt của quiz về sau không làm đổi kết quả cũ
def passed_expr(r: str) -> str:
    return f"({r}.score * 100 >= COALESCE({r}.passing_score, 50) * {r}.total)"


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
                WHEN 'average' THEN a.avg_pct >= COALESCE(rl.passing_score, 50)
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
def topics(db: Session, user_id: int, course_id: int | None = None) -> list[dict]:
    cf, cp = _course_filter(course_id)
    rows = q_all(
        db,
        f"""
        SELECT q.topic,
            COUNT(*)                                   AS answered,
            SUM(ra.is_correct)                         AS correct,
            ROUND(SUM(ra.is_correct) * 100.0 / COUNT(*), 1) AS avg_score
        FROM result_answers ra
        JOIN results r   ON r.id = ra.result_id
        JOIN questions q ON q.id = ra.question_id
        JOIN quizzes qz  ON qz.id = r.quiz_id
        WHERE r.user_id = :uid AND q.topic IS NOT NULL AND {topic_scope("qz", "r")}
        { cf.replace("q.course_id", "qz.course_id") }
        GROUP BY q.topic
        ORDER BY avg_score ASC, answered DESC
        """,
        uid=user_id,
        **cp,
    )
    # Gắn mức năng lực (Weak/Average/Good/Excellent) cho từng chủ đề
    out = []
    for r in rows:
        score = float(r["avg_score"]) if r["avg_score"] is not None else 0.0
        out.append(
            {
                "topic": r["topic"],
                "answered": int(r["answered"]),
                "correct": int(r["correct"] or 0),
                "avg_score": score,
                "status": level_for(score),
            }
        )
    return out


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
