"""/api/enrollments — port của app/Controllers/EnrollmentController.php."""
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import execute, get_db, q_all, q_one
from app.core.dependencies import get_current_user
from app.core.responses import ApiError, ok

from app.services.analytics_service import graded_sql

from ._common import iv

router = APIRouter(prefix="/api/enrollments", tags=["enrollments"])

# Câu truy vấn mẫu cho admin/giảng viên: mỗi lượt ghi danh kèm tên học viên, tên khóa,
# tổng số bài, số bài đã hoàn thành và điểm quiz trung bình của học viên trong khóa đó.
# {extra} = cột bổ sung, {where} = điều kiện lọc (ghép vào tùy vai trò)
_ENROLL_AGG = """
    SELECT e.*, u.fullname AS user_name, u.email AS user_email, c.title AS course_title,
        {extra}
        c.thumbnail, c.price,
        (SELECT COUNT(*) FROM lessons l JOIN chapters ch ON l.chapter_id = ch.id
         WHERE ch.course_id = c.id) AS total_lessons,
        (SELECT COUNT(*) FROM lesson_progress lp JOIN lessons l ON lp.lesson_id = l.id
         JOIN chapters ch ON l.chapter_id = ch.id
         WHERE ch.course_id = c.id AND lp.user_id = e.user_id AND lp.is_completed = 1)
            AS completed_lessons,
        (SELECT ROUND(AVG(g.pct)) FROM ({graded}) g
         WHERE g.course_id = c.id AND g.user_id = e.user_id) AS avg_quiz_score
    FROM enrollments e
    JOIN users u ON u.id = e.user_id
    JOIN courses c ON c.id = e.course_id
    {where}
    ORDER BY e.enroll_date DESC
"""


# Kiểm tra user đã ghi danh khóa học chưa
def _is_enrolled(db: Session, user_id: int, course_id: int) -> bool:
    return (
        q_one(
            db,
            "SELECT id FROM enrollments WHERE user_id = :u AND course_id = :c",
            u=user_id,
            c=course_id,
        )
        is not None
    )


# Ghi danh user vào khóa học; INSERT IGNORE để gọi lại nhiều lần không bị lỗi trùng
def _enroll(db: Session, user_id: int, course_id: int):
    execute(
        db,
        "INSERT IGNORE INTO enrollments (user_id, course_id) VALUES (:u, :c)",
        u=user_id,
        c=course_id,
    )


# GET /api/enrollments — tra cứu ghi danh (nhiều chế độ tùy tham số và vai trò)
@router.get("")
def index(
    course_id: int | None = Query(default=None),
    ids_only: str | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ?course_id=X -> chỉ trả về user hiện tại đã ghi danh khóa X hay chưa
    if course_id:
        return ok(enrolled=_is_enrolled(db, user["id"], course_id))
    # ?ids_only=1 -> danh sách id các khóa user đã ghi danh (frontend dùng để đánh dấu nút "Đã đăng ký")
    if ids_only:
        rows = q_all(
            db, "SELECT course_id FROM enrollments WHERE user_id = :u", u=user["id"]
        )
        return ok(data=[r["course_id"] for r in rows])

    # Admin: toàn bộ lượt ghi danh kèm thống kê tiến độ
    if user["role"] == "admin":
        data = q_all(db, _ENROLL_AGG.format(graded=graded_sql(), extra="c.teacher_id,", where=""))
    # Giảng viên: chỉ học viên của các khóa mình phụ trách
    elif user["role"] == "teacher":
        data = q_all(
            db,
            _ENROLL_AGG.format(graded=graded_sql(), extra="", where="WHERE c.teacher_id = :tid"),
            tid=user["id"],
        )
    # Học viên: các khóa mình đã ghi danh (trang "Khóa học của tôi")
    else:
        data = q_all(
            db,
            "SELECT e.*, c.title, c.description, c.price, c.level, c.thumbnail, c.slug "
            "FROM enrollments e JOIN courses c ON c.id = e.course_id "
            "WHERE e.user_id = :u ORDER BY e.enroll_date DESC",
            u=user["id"],
        )
    return ok(data=data)


# POST /api/enrollments — ghi danh khóa học (khóa có phí phải thanh toán trước)
@router.post("")
def create(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course_id = iv(body, "course_id")
    if not course_id:
        raise ApiError("Thiếu course_id.")
    # Khóa học phải tồn tại, chưa ghi danh, và (với học viên) phải đang mở bán
    course = q_one(db, "SELECT price, status FROM courses WHERE id = :id", id=course_id)
    if not course:
        raise ApiError("Khóa học không tồn tại.", 404)
    if _is_enrolled(db, user["id"], course_id):
        raise ApiError("Bạn đã đăng ký khóa học này rồi.", 409)
    if user["role"] == "student" and course["status"] != "published":
        raise ApiError("Khóa học này chưa mở đăng ký.", 403)

    # Khóa có phí chỉ được ghi danh qua /api/payments; ở đây chỉ chấp nhận khi đã có thanh toán thành công.
    if user["role"] == "student" and float(course["price"] or 0) > 0:
        paid = q_one(
            db,
            "SELECT id FROM payments WHERE user_id = :u AND course_id = :c AND status = 'completed'",
            u=user["id"],
            c=course_id,
        )
        if not paid:
            raise ApiError("Khóa học này có phí. Vui lòng thanh toán để đăng ký.", 402)

    _enroll(db, user["id"], course_id)
    return ok("Đăng ký khóa học thành công!")


# DELETE /api/enrollments?course_id=X — user tự hủy ghi danh khóa học của mình
@router.delete("")
def delete(
    course_id: int = Query(default=0),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not course_id:
        raise ApiError("Thiếu course_id.")
    execute(
        db,
        "DELETE FROM enrollments WHERE user_id = :u AND course_id = :c",
        u=user["id"],
        c=course_id,
    )
    return ok("Đã hủy đăng ký.")
