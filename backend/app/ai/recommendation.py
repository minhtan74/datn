"""PHASE 5 — Rule-based Recommendation Engine (thuần Python, KHÔNG ML).

Đầu vào: chỉ số từ analytics_service (điểm quiz, tiến độ, thời gian, topic yếu).
Đầu ra: level (Weak/Average/Good/Excellent) + danh sách gợi ý cụ thể có link hành động.
"""
import json

from sqlalchemy.orm import Session

from app.core.database import execute, q_all, q_one
from app.services import analytics_service as an

# Lời khuyên chung theo từng mức năng lực (luôn là gợi ý cuối cùng)
_GENERIC = {
    "Weak": "Bạn đang gặp khó khăn — hãy học lại bài và làm quiz cơ bản để củng cố nền tảng.",
    "Average": "Kết quả ở mức trung bình — luyện thêm quiz để chắc kiến thức.",
    "Good": "Bạn đang học tốt — tiếp tục sang bài/chủ đề tiếp theo trong lộ trình.",
    "Excellent": "Xuất sắc! Hãy thử các nội dung nâng cao.",
}
# Câu tóm tắt ngắn hiển thị ở đầu thẻ gợi ý
_SUMMARY = {
    "Weak": "Cần củng cố nền tảng",
    "Average": "Luyện tập thêm để vững kiến thức",
    "Good": "Tiến độ tốt — học tiếp lộ trình",
    "Excellent": "Sẵn sàng cho nội dung nâng cao",
}


def _focus_course(db: Session, user_id: int) -> dict | None:
    """Khóa đang học dở có tỷ lệ hoàn thành thấp nhất (để gợi ý bài học cụ thể)."""
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
        HAVING total_lessons > 0
        ORDER BY (done_lessons / total_lessons) ASC, c.id ASC
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


# Quiz có điểm cao nhất dưới 70% (lấy quiz điểm thấp nhất) để gợi ý làm lại
def _weak_quiz(db: Session, user_id: int, course_id: int | None) -> dict | None:
    cf = "AND q.course_id = :cid" if course_id else ""
    params = {"uid": user_id}
    if course_id:
        params["cid"] = course_id
    return q_one(
        db,
        f"""
        SELECT q.id, q.title, MAX(ROUND(r.score * 100.0 / NULLIF(r.total, 0))) AS best
        FROM results r JOIN quizzes q ON q.id = r.quiz_id
        WHERE r.user_id = :uid {cf}
        GROUP BY q.id, q.title, q.max_attempts
        HAVING best < 70 AND (q.max_attempts IS NULL OR COUNT(*) < q.max_attempts)
        ORDER BY best ASC
        LIMIT 1
        """,
        **params,
    )


# Xây dựng gợi ý: lấy chỉ số học tập -> xác định mức năng lực -> áp lần lượt 5 luật bên dưới
def build(db: Session, user_id: int, course_id: int | None = None) -> dict:
    ov = an.overview(db, user_id, course_id)
    topics = an.topics(db, user_id, course_id)
    avg = ov["avg_quiz_score"]

    # Chưa làm quiz nào thì tạm xếp mức Average
    level = an.level_for(avg) if avg is not None else "Average"
    items: list[dict] = []

    # 1. Hoàn thành bài học nếu tiến độ thấp
    if ov["total_lessons"] and ov["completion_pct"] < 50:
        remaining = ov["total_lessons"] - ov["completed_lessons"]
        items.append(
            {
                "type": "finish_lessons",
                "text": f"Hoàn thành các bài học còn lại ({remaining} bài chưa xong).",
                "action_url": "/student/my-courses",
            }
        )

    # 2. Ôn lại chủ đề yếu nhất
    weak = [t for t in topics if t["status"] in ("Weak", "Average")]
    if weak:
        w = weak[0]
        items.append(
            {
                "type": "review_topic",
                "text": f"Ôn lại chủ đề \"{w['topic']}\" — điểm hiện tại {w['avg_score']}%.",
                "topic": w["topic"],
            }
        )

    # 3. Bài học tiếp theo cụ thể
    focus = _focus_course(db, user_id) if course_id is None else q_one(
        db, "SELECT id, title FROM courses WHERE id = :cid", cid=course_id
    )
    if focus:
        nxt = _next_lesson(db, user_id, int(focus["id"]))
        if nxt:
            items.append(
                {
                    "type": "next_lesson",
                    "text": f"Học bài tiếp theo: \"{nxt['title']}\" (khóa {focus['title']}).",
                    "action_url": f"/lesson?id={nxt['id']}",
                }
            )

    # 4. Làm lại quiz điểm thấp
    wq = _weak_quiz(db, user_id, course_id)
    if wq:
        items.append(
            {
                "type": "retake_quiz",
                "text": f"Làm lại quiz \"{wq['title']}\" (điểm cao nhất {int(wq['best'])}%).",
                "action_url": f"/quiz-show?id={wq['id']}",
            }
        )

    # 5. Lời khuyên theo mức năng lực
    items.append({"type": "advice", "text": _GENERIC[level]})

    # Lưu lại số liệu làm căn cứ cho gợi ý (hiển thị "vì sao có gợi ý này" và lưu lịch sử)
    based_on = {
        "avg_quiz_score": avg,
        "completion_pct": ov["completion_pct"],
        "completed_lessons": ov["completed_lessons"],
        "total_lessons": ov["total_lessons"],
        "quiz_attempts": ov["quiz_attempts"],
        "total_time_sec": ov["total_time_sec"],
        "weakest_topic": weak[0]["topic"] if weak else None,
        "weak_topics": [t["topic"] for t in weak],
        "strong_topics": [t["topic"] for t in topics if t["status"] == "Excellent"],
    }

    return {
        "level": level,
        "summary": _SUMMARY[level],
        "items": items,
        "based_on": based_on,
        "topics": topics,
    }


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
            avg=bo["avg_quiz_score"] or 0,
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
