"""/api/reports/summary — port của app/Controllers/ReportController.php (Admin dashboard)."""
import csv
import datetime as dt
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.ai.rag.rag_pipeline import NO_ANSWER
from app.core.database import get_db, q_all, q_one, q_scalar
from app.core.dependencies import get_current_user
from app.core.responses import ApiError, ok
from app.services.analytics_service import graded_sql, official, topic_scope

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _require_admin(user: dict) -> None:
    if user["role"] != "admin":
        raise ApiError("Chỉ Admin mới có thể xem báo cáo.", 403)


# Giới hạn số dòng (None = lấy toàn bộ, dùng khi xuất file)
def _limit(limit: int | None) -> str:
    return f" LIMIT {int(limit)}" if limit else ""


# Danh sách giao dịch, mới nhất lên đầu
def _payments(db: Session, limit: int | None = None) -> list[dict]:
    return q_all(
        db,
        "SELECT p.id, p.amount, p.method, p.status, p.created_at, p.paid_at, "
        "u.fullname AS user_name, u.email, c.title AS course_title FROM payments p "
        "JOIN users u ON u.id = p.user_id JOIN courses c ON c.id = p.course_id "
        "ORDER BY COALESCE(p.paid_at, p.created_at) DESC, p.id DESC" + _limit(limit),
    )


# Khóa học xếp theo doanh thu rồi theo số học viên
def _top_courses(db: Session, limit: int | None = None) -> list[dict]:
    return q_all(
        db,
        """
        SELECT c.id, c.title, c.thumbnail, c.price, u.fullname AS teacher_name,
            (SELECT COUNT(DISTINCT e.user_id) FROM enrollments e
             WHERE e.course_id = c.id) AS student_count,
            (SELECT COALESCE(SUM(p.amount), 0) FROM payments p
             WHERE p.course_id = c.id AND p.status = 'completed') AS revenue
        FROM courses c
        LEFT JOIN users u ON u.id = c.teacher_id
        ORDER BY revenue DESC, student_count DESC
        """ + _limit(limit),
    )


# Lượt ghi danh mới nhất, kèm tiến độ (số bài xong / tổng số bài) của học viên trong khóa
def _enrollments(db: Session, limit: int | None = None) -> list[dict]:
    return q_all(
        db,
        """
        SELECT e.id, e.enroll_date, u.fullname AS user_name, u.email,
            c.title AS course_title,
            (SELECT COUNT(*) FROM lessons l JOIN chapters ch ON l.chapter_id=ch.id
             WHERE ch.course_id=c.id) AS total_lessons,
            (SELECT COUNT(*) FROM lesson_progress lp2 JOIN lessons l2 ON lp2.lesson_id=l2.id
             JOIN chapters ch2 ON l2.chapter_id=ch2.id
             WHERE ch2.course_id=c.id AND lp2.user_id=e.user_id AND lp2.is_completed=1)
                AS done_lessons
        FROM enrollments e
        JOIN users u ON u.id = e.user_id
        JOIN courses c ON c.id = e.course_id
        ORDER BY e.enroll_date DESC, e.id DESC
        """ + _limit(limit),
    )


# Học tập theo từng khóa: số học viên, lượt làm bài kiểm tra chính thức, điểm TB,
# tỷ lệ đạt (theo điểm đạt của từng quiz; quiz không đặt điểm đạt không tính vào), % hoàn thành TB
def _learning_by_course(db: Session) -> list[dict]:
    rows = q_all(
        db,
        f"""
        SELECT c.id, c.title,
            (SELECT COUNT(*) FROM enrollments e WHERE e.course_id = c.id) AS students,
            (SELECT COUNT(*) FROM results r JOIN quizzes q ON q.id = r.quiz_id
             WHERE q.course_id = c.id AND {official("q")}) AS attempts,
            (SELECT ROUND(AVG(g.pct), 1) FROM ({graded_sql()}) g WHERE g.course_id = c.id) AS avg_score,
            (SELECT ROUND(AVG(g.passed) * 100, 1) FROM ({graded_sql()}) g WHERE g.course_id = c.id) AS pass_rate,
            (SELECT ROUND(AVG(CASE WHEN t.total > 0 THEN t.done * 100.0 / t.total ELSE 0 END), 1)
             FROM (SELECT e.course_id,
                     (SELECT COUNT(*) FROM lessons l JOIN chapters ch ON ch.id = l.chapter_id
                      WHERE ch.course_id = e.course_id) AS total,
                     (SELECT COUNT(*) FROM lesson_progress lp JOIN lessons l ON l.id = lp.lesson_id
                      JOIN chapters ch ON ch.id = l.chapter_id
                      WHERE ch.course_id = e.course_id AND lp.user_id = e.user_id
                        AND lp.is_completed = 1) AS done
                   FROM enrollments e) t
             WHERE t.course_id = c.id) AS avg_completion
        FROM courses c
        ORDER BY attempts DESC, c.id
        """,
    )
    for r in rows:
        for k in ("avg_score", "pass_rate", "avg_completion"):
            r[k] = float(r[k]) if r[k] is not None else None
    return rows


# Chủ đề yếu nhất toàn hệ thống (tỷ lệ đúng thấp nhất, chỉ xét chủ đề có >= 10 câu trả lời)
def _weak_topics(db: Session, limit: int | None = 10) -> list[dict]:
    rows = q_all(
        db,
        f"""
        SELECT q.topic, c.title AS course_title,
            COUNT(*) AS answered,
            SUM(ra.is_correct) AS correct,
            ROUND(SUM(ra.is_correct) * 100.0 / COUNT(*), 1) AS correct_pct,
            COUNT(DISTINCT r.user_id) AS students
        FROM result_answers ra
        JOIN results r   ON r.id = ra.result_id
        JOIN questions q ON q.id = ra.question_id
        JOIN quizzes qz  ON qz.id = q.quiz_id
        JOIN courses c   ON c.id = qz.course_id
        WHERE q.topic IS NOT NULL AND q.topic <> '' AND {topic_scope("qz", "r")}
        GROUP BY q.topic, c.id, c.title
        HAVING answered >= 10
        ORDER BY correct_pct ASC, answered DESC
        """ + _limit(limit),
    )
    for r in rows:
        r["correct_pct"] = float(r["correct_pct"] or 0)
        r["correct"] = int(r["correct"] or 0)
    return rows


# Mức dùng AI Tutor theo khóa: số hội thoại, số câu hỏi, số lần AI không tìm thấy thông tin
def _ai_by_course(db: Session) -> list[dict]:
    rows = q_all(
        db,
        """
        SELECT c.id, c.title,
            COUNT(DISTINCT cv.id) AS conversations,
            COUNT(DISTINCT cv.user_id) AS users,
            SUM(m.role = 'user') AS questions,
            SUM(m.role = 'assistant' AND m.content = :na) AS no_answer
        FROM ai_conversations cv
        JOIN courses c ON c.id = cv.course_id
        LEFT JOIN ai_messages m ON m.conversation_id = cv.id
        GROUP BY c.id, c.title
        ORDER BY questions DESC
        """,
        na=NO_ANSWER,
    )
    for r in rows:
        r["questions"] = int(r["questions"] or 0)
        r["no_answer"] = int(r["no_answer"] or 0)
    return rows


# GET /api/reports/learning — số liệu học tập toàn hệ thống: quiz, hoàn thành bài, chủ đề yếu, AI Tutor
@router.get("/learning")
def learning(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(user)
    # Số lượt làm / số người học đếm mọi lượt; điểm TB + tỷ lệ đạt lấy 1 điểm / (học viên, quiz)
    # theo cách tính của từng quiz
    quiz = q_one(
        db,
        f"""
        SELECT SUM(g.attempts) AS attempts,
            COUNT(DISTINCT g.user_id) AS learners,
            ROUND(AVG(g.pct), 1) AS avg_score,
            ROUND(AVG(g.passed) * 100, 1) AS pass_rate
        FROM ({graded_sql()}) g
        """,
    ) or {}
    ai_by_course = _ai_by_course(db)
    questions = sum(r["questions"] for r in ai_by_course)
    no_answer = sum(r["no_answer"] for r in ai_by_course)
    return ok(
        data={
            "overview": {
                "quiz_attempts": int(quiz.get("attempts") or 0),
                "active_learners": int(quiz.get("learners") or 0),
                "avg_quiz_score": float(quiz.get("avg_score") or 0),
                # Không quiz nào đặt điểm đạt -> None (giao diện hiện "—")
                "pass_rate": float(quiz["pass_rate"]) if quiz.get("pass_rate") is not None else None,
                "ai_questions": questions,
                "ai_no_answer_rate": round(no_answer * 100.0 / questions, 1) if questions else 0.0,
            },
            "by_course": _learning_by_course(db),
            "weak_topics": _weak_topics(db),
            "ai_by_course": ai_by_course,
        }
    )


# Cấu hình xuất CSV: tên file, hàm lấy dữ liệu (toàn bộ, không giới hạn), các cột (tiêu đề, key)
_EXPORTS = {
    "payments": ("giao-dich", lambda db: _payments(db), [
        ("Mã GD", "id"), ("Học viên", "user_name"), ("Email", "email"), ("Khóa học", "course_title"),
        ("Phương thức", "method"), ("Số tiền (VNĐ)", "amount"), ("Trạng thái", "status"),
        ("Ngày tạo đơn", "created_at"), ("Ngày thanh toán", "paid_at"),
    ]),
    "enrollments": ("dang-ky-hoc", lambda db: _enrollments(db), [
        ("Học viên", "user_name"), ("Email", "email"), ("Khóa học", "course_title"),
        ("Bài đã xong", "done_lessons"), ("Tổng số bài", "total_lessons"), ("Ngày đăng ký", "enroll_date"),
    ]),
    "courses": ("khoa-hoc", lambda db: _top_courses(db), [
        ("Mã khóa", "id"), ("Khóa học", "title"), ("Giảng viên", "teacher_name"), ("Giá (VNĐ)", "price"),
        ("Số học viên", "student_count"), ("Doanh thu (VNĐ)", "revenue"),
    ]),
    "learning": ("hoc-tap-theo-khoa", _learning_by_course, [
        ("Mã khóa", "id"), ("Khóa học", "title"), ("Số học viên", "students"), ("Lượt làm quiz", "attempts"),
        ("Điểm TB (%)", "avg_score"), ("Tỷ lệ đạt (%)", "pass_rate"), ("Hoàn thành TB (%)", "avg_completion"),
    ]),
    "topics": ("chu-de-yeu", lambda db: _weak_topics(db, limit=None), [
        ("Chủ đề", "topic"), ("Khóa học", "course_title"), ("Số câu đã làm", "answered"),
        ("Số câu đúng", "correct"), ("Tỷ lệ đúng (%)", "correct_pct"), ("Số học viên", "students"),
    ]),
}


# GET /api/reports/export?type=payments|enrollments|courses|learning|topics — tải CSV đầy đủ (mở được bằng Excel)
@router.get("/export")
def export(
    type: str = Query(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(user)
    if type not in _EXPORTS:
        raise ApiError("Loại báo cáo không hợp lệ.", 400)
    name, fetch, cols = _EXPORTS[type]

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([h for h, _ in cols])
    for row in fetch(db):
        out = []
        for _, k in cols:
            v = row.get(k)
            if isinstance(v, dt.datetime):
                v = v.strftime("%d/%m/%Y %H:%M")
            out.append("" if v is None else v)
        w.writerow(out)

    # BOM UTF-8 để Excel hiển thị đúng tiếng Việt
    filename = f"bao-cao-{name}-{dt.date.today().isoformat()}.csv"
    return Response(
        content="﻿" + buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# GET /api/reports/summary?range=7d — toàn bộ số liệu cho trang Báo cáo của admin
@router.get("/summary")
def summary(
    range: str = Query(default="7d"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(user)
    # Khoảng thời gian cho biểu đồ doanh thu: today / 7d / 30d / 1y (sai thì mặc định 7d)
    rng = range if range in ("today", "7d", "30d", "1y") else "7d"

    # Tổng hợp giao dịch: doanh thu và số đơn theo từng trạng thái (thành công / chờ / lỗi / hoàn tiền)
    rev = q_one(
        db,
        """
        SELECT
            COALESCE(SUM(CASE WHEN status='completed' THEN amount ELSE 0 END), 0) AS total_revenue,
            COUNT(CASE WHEN status='completed' THEN 1 END) AS total_orders,
            COUNT(CASE WHEN status='pending'   THEN 1 END) AS pending_orders,
            COUNT(CASE WHEN status='failed'    THEN 1 END) AS failed_orders,
            COUNT(CASE WHEN status='refunded'  THEN 1 END) AS refunded_orders,
            COALESCE(SUM(CASE WHEN status='refunded' THEN amount ELSE 0 END), 0) AS refunded_amount
        FROM payments
        """,
    ) or {}

    # Doanh thu theo phương thức thanh toán (chỉ tính giao dịch thành công)
    by_method = q_all(
        db,
        "SELECT method, SUM(amount) AS revenue, COUNT(*) AS cnt FROM payments "
        "WHERE status='completed' GROUP BY method ORDER BY revenue DESC",
    )

    # 20 giao dịch gần nhất
    recent_payments = _payments(db, limit=20)

    # Top 10 khóa học theo doanh thu, rồi theo số học viên
    top_courses = _top_courses(db, limit=10)

    # Số học viên mới đăng ký tài khoản trong 30 ngày qua
    new_students_30 = int(
        q_scalar(
            db,
            "SELECT COUNT(*) FROM users WHERE role='student' "
            "AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
        )
        or 0
    )
    # Tổng số học viên và tổng lượt ghi danh
    total_students = int(
        q_scalar(db, "SELECT COUNT(*) FROM users WHERE role='student'") or 0
    )

    total_enrollments = int(q_scalar(db, "SELECT COUNT(*) FROM enrollments") or 0)

    # 20 lượt ghi danh gần nhất, kèm tiến độ của học viên trong khóa
    recent_enrollments = _enrollments(db, limit=20)

    # Tỷ lệ hoàn thành trung bình: tính % hoàn thành cho từng lượt ghi danh rồi lấy trung bình
    completion = q_one(
        db,
        """
        SELECT AVG(CASE WHEN total_lessons > 0 THEN done_lessons * 100.0 / total_lessons ELSE 0 END) AS avg_pct
        FROM (
            SELECT e.user_id, e.course_id,
                (SELECT COUNT(*) FROM lessons l JOIN chapters ch ON l.chapter_id=ch.id
                 WHERE ch.course_id=e.course_id) AS total_lessons,
                (SELECT COUNT(*) FROM lesson_progress lp JOIN lessons l ON lp.lesson_id=l.id
                 JOIN chapters ch ON l.chapter_id=ch.id
                 WHERE ch.course_id=e.course_id AND lp.user_id=e.user_id AND lp.is_completed=1)
                    AS done_lessons
            FROM enrollments e
        ) sub
        """,
    ) or {}

    # Chuỗi doanh thu cho biểu đồ theo khoảng thời gian đã chọn
    weekly = _revenue_series(db, rng)

    return ok(
        data={
            "overview": {
                "total_revenue": float(rev.get("total_revenue") or 0),
                "total_orders": int(rev.get("total_orders") or 0),
                "pending_orders": int(rev.get("pending_orders") or 0),
                "failed_orders": int(rev.get("failed_orders") or 0),
                "refunded_orders": int(rev.get("refunded_orders") or 0),
                "refunded_amount": float(rev.get("refunded_amount") or 0),
                "total_students": total_students,
                "new_students_30d": new_students_30,
                "total_enrollments": total_enrollments,
                "avg_completion_pct": round(float(completion.get("avg_pct") or 0), 1),
            },
            "revenue_by_method": by_method,
            "revenue_weekly": weekly,
            "top_courses": top_courses,
            "recent_payments": recent_payments,
            "recent_enrollments": recent_enrollments,
        }
    )


# Tạo dữ liệu biểu đồ doanh thu: mỗi mốc thời gian 1 điểm, mốc không có giao dịch vẫn trả 0
def _revenue_series(db: Session, rng: str) -> list[dict]:
    # Hôm nay: 24 mốc theo giờ
    if rng == "today":
        rows = q_all(
            db,
            "SELECT HOUR(paid_at) AS slot, SUM(amount) AS revenue, COUNT(*) AS orders "
            "FROM payments WHERE status='completed' AND DATE(paid_at) = CURDATE() "
            "GROUP BY HOUR(paid_at) ORDER BY slot ASC",
        )
        m = {int(r["slot"]): r for r in rows}
        return [
            {
                "label": f"{h:02d}:00",
                "revenue": float(m[h]["revenue"]) if h in m else 0,
                "orders": int(m[h]["orders"]) if h in m else 0,
            }
            for h in range(24)
        ]

    # 30 ngày: mỗi ngày 1 mốc
    if rng == "30d":
        rows = q_all(
            db,
            "SELECT DATE(paid_at) AS day, SUM(amount) AS revenue, COUNT(*) AS orders "
            "FROM payments WHERE status='completed' "
            "AND paid_at >= DATE_SUB(CURDATE(), INTERVAL 29 DAY) "
            "GROUP BY DATE(paid_at) ORDER BY day ASC",
        )
        m = {str(r["day"]): r for r in rows}
        today = dt.date.today()
        out = []
        for i in range(29, -1, -1):
            d = today - dt.timedelta(days=i)
            r = m.get(d.isoformat())
            out.append(
                {
                    "label": d.strftime("%d/%m"),
                    "revenue": float(r["revenue"]) if r else 0,
                    "orders": int(r["orders"]) if r else 0,
                }
            )
        return out

    # 1 năm: 12 mốc theo tháng (tính lùi từ tháng hiện tại, xử lý lùi qua năm trước)
    if rng == "1y":
        rows = q_all(
            db,
            "SELECT DATE_FORMAT(paid_at, '%Y-%m') AS slot, SUM(amount) AS revenue, COUNT(*) AS orders "
            "FROM payments WHERE status='completed' "
            # Mốc bắt đầu là NGÀY 1 của tháng cách đây 11 tháng (lùi từ hôm nay sẽ cắt mất nửa đầu tháng đầu tiên)
            "AND paid_at >= DATE_SUB(DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL 11 MONTH) "
            "GROUP BY slot ORDER BY slot ASC",
        )
        m = {str(r["slot"]): r for r in rows}
        today = dt.date.today().replace(day=1)
        out = []
        for i in range(11, -1, -1):
            y = today.year
            mo = today.month - i
            while mo <= 0:
                mo += 12
                y -= 1
            slot = f"{y:04d}-{mo:02d}"
            r = m.get(slot)
            out.append(
                {
                    "label": f"{mo:02d}/{y:04d}",
                    "revenue": float(r["revenue"]) if r else 0,
                    "orders": int(r["orders"]) if r else 0,
                }
            )
        return out

    # Mặc định 7 ngày: mỗi ngày 1 mốc
    # 7d
    rows = q_all(
        db,
        "SELECT DATE(paid_at) AS day, SUM(amount) AS revenue, COUNT(*) AS orders "
        "FROM payments WHERE status='completed' "
        "AND paid_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY) "
        "GROUP BY DATE(paid_at) ORDER BY day ASC",
    )
    m = {str(r["day"]): r for r in rows}
    today = dt.date.today()
    out = []
    for i in range(6, -1, -1):
        d = today - dt.timedelta(days=i)
        r = m.get(d.isoformat())
        out.append(
            {
                "label": d.strftime("%d/%m"),
                "revenue": float(r["revenue"]) if r else 0,
                "orders": int(r["orders"]) if r else 0,
            }
        )
    return out
