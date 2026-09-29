"""/api/progress — port của app/Controllers/ProgressController.php + LessonProgress model."""
import datetime as dt

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import execute, get_db, q_all, q_one, q_scalar
from app.core.dependencies import get_current_user
from app.core.responses import ApiError, ok
from app.routers.enrollments import _enroll

from ._common import can_access_course, iv

router = APIRouter(prefix="/api/progress", tags=["progress"])


# GET /api/progress — tiến độ học của user hiện tại; chế độ trả về tùy tham số
@router.get("")
def index(
    course_id: int | None = Query(default=None),
    weekly: str | None = Query(default=None),
    recent: str | None = Query(default=None),
    limit: int = Query(default=10),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = user["id"]

    # Tiến độ trong 1 khóa cụ thể -> danh sách lesson_id đã hoàn thành
    # ?course_id=X: trả danh sách id bài đã hoàn thành trong khóa (để tick ✓ trên danh sách bài)
    if course_id:
        rows = q_all(
            db,
            "SELECT lp.lesson_id FROM lesson_progress lp "
            "JOIN lessons l ON l.id = lp.lesson_id "
            "JOIN chapters ch ON ch.id = l.chapter_id "
            "WHERE lp.user_id = :u AND ch.course_id = :c AND lp.is_completed = 1",
            u=uid,
            c=course_id,
        )
        return ok(data=[r["lesson_id"] for r in rows])

    # Biểu đồ theo tuần (7 ngày)
    # ?weekly=1: số bài hoàn thành mỗi ngày trong 7 ngày gần nhất; ngày không học vẫn trả count = 0
    if weekly:
        rows = q_all(
            db,
            "SELECT DATE(completed_at) AS day, COUNT(*) AS cnt FROM lesson_progress "
            "WHERE user_id = :u AND is_completed = 1 "
            "AND completed_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY) "
            "GROUP BY DATE(completed_at)",
            u=uid,
        )
        cnt_map = {str(r["day"]): int(r["cnt"]) for r in rows}
        today = dt.date.today()
        result = []
        for i in range(6, -1, -1):
            d = today - dt.timedelta(days=i)
            result.append(
                {"date": d.isoformat(), "label": d.strftime("%d/%m"), "count": cnt_map.get(d.isoformat(), 0)}
            )
        return ok(data=result)

    # Hoạt động gần đây
    # ?recent=1: các bài hoàn thành gần đây nhất (mục "Hoạt động gần đây" trên dashboard)
    if recent:
        lim = max(1, int(limit or 10))
        rows = q_all(
            db,
            "SELECT lp.lesson_id, lp.completed_at, l.title AS lesson_title, "
            "c.title AS course_title, c.id AS course_id FROM lesson_progress lp "
            "JOIN lessons l ON l.id = lp.lesson_id "
            "JOIN chapters ch ON ch.id = l.chapter_id "
            "JOIN courses c ON c.id = ch.course_id "
            "WHERE lp.user_id = :u AND lp.is_completed = 1 AND lp.completed_at IS NOT NULL "
            f"ORDER BY lp.completed_at DESC LIMIT {lim}",
            u=uid,
        )
        return ok(data=rows)

    # Tổng hợp theo từng khóa học
    # Lấy các khóa đã ghi danh (hoặc đã từng học bài thử), kèm tổng số bài, số bài xong, tổng giây đã xem
    by_course = q_all(
        db,
        """
        SELECT c.id AS course_id, c.title AS course_title, c.thumbnail,
            COUNT(DISTINCT l.id) AS total_lessons,
            COUNT(DISTINCT CASE WHEN lp.is_completed = 1 THEN l.id END) AS done_lessons,
            COALESCE(SUM(lp.watched_sec), 0) AS watched_sec_total
        FROM courses c
        JOIN chapters ch ON ch.course_id = c.id
        JOIN lessons l ON l.chapter_id = ch.id
        LEFT JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.user_id = :u
        WHERE c.id IN (
            SELECT course_id FROM enrollments WHERE user_id = :u
            UNION
            SELECT ch2.course_id FROM lesson_progress lp2
            JOIN lessons l2 ON l2.id = lp2.lesson_id
            JOIN chapters ch2 ON ch2.id = l2.chapter_id
            WHERE lp2.user_id = :u
        )
        GROUP BY c.id, c.title, c.thumbnail
        ORDER BY done_lessons DESC
        """,
        u=uid,
    )
    # Tổng thời gian xem video của user trên mọi bài học
    total_sec = int(
        q_scalar(
            db,
            "SELECT COALESCE(SUM(watched_sec), 0) FROM lesson_progress WHERE user_id = :u",
            u=uid,
        )
        or 0
    )
    # Cộng dồn số bài của tất cả khóa để ra tiến độ chung
    total_lessons = sum(int(c["total_lessons"]) for c in by_course)
    done_lessons = sum(int(c["done_lessons"]) for c in by_course)

    return ok(
        data={
            "courses": by_course,
            "total_lessons": total_lessons,
            "done_lessons": done_lessons,
            "total_watched_sec": total_sec,
        }
    )


# POST /api/progress — lưu tiến độ xem video / đánh dấu hoàn thành một bài học
@router.post("")
def update(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesson_id = iv(body, "lesson_id")
    watched_sec = iv(body, "watched_sec")
    is_completed = iv(body, "is_completed")

    if not lesson_id:
        raise ApiError("Thiếu lesson_id.")

    # Lấy bài học kèm thông tin khóa (giá, trạng thái) để kiểm tra quyền
    lesson = q_one(
        db,
        "SELECT l.is_free, c.id AS course_id, c.price, c.status FROM lessons l "
        "JOIN chapters ch ON ch.id = l.chapter_id JOIN courses c ON c.id = ch.course_id "
        "WHERE l.id = :id",
        id=lesson_id,
    )
    if not lesson:
        raise ApiError("Không tìm thấy bài học.", 404)

    course_id = int(lesson["course_id"])
    # Chưa ghi danh: khóa miễn phí thì tự ghi danh; khóa có phí chỉ được lưu tiến độ của bài học thử
    if not can_access_course(db, user, course_id):
        # Chỉ tự ghi danh với khóa miễn phí đã xuất bản (giống /api/enrollments);
        # khóa trả phí phải qua /api/payments.
        if float(lesson["price"] or 0) <= 0 and lesson["status"] == "published":
            _enroll(db, user["id"], course_id)
        elif not lesson["is_free"]:
            raise ApiError("Bạn cần đăng ký khóa học để lưu tiến độ bài học này.", 403)

    # Ghi/cập nhật tiến độ: GREATEST() để số giây đã xem và trạng thái hoàn thành chỉ tăng, không giảm;
    # completed_at chỉ ghi ở lần hoàn thành đầu tiên
    completed_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if is_completed else None
    execute(
        db,
        """
        INSERT INTO lesson_progress (user_id, lesson_id, is_completed, watched_sec, completed_at)
        VALUES (:u, :l, :ic, :ws, :ca)
        ON DUPLICATE KEY UPDATE
            watched_sec  = GREATEST(watched_sec, VALUES(watched_sec)),
            is_completed = GREATEST(is_completed, VALUES(is_completed)),
            completed_at = CASE
                WHEN VALUES(is_completed) = 1 AND completed_at IS NULL THEN VALUES(completed_at)
                ELSE completed_at END,
            updated_at   = CURRENT_TIMESTAMP
        """,
        u=user["id"],
        l=lesson_id,
        ic=is_completed,
        ws=watched_sec,
        ca=completed_at,
    )

    msg = "Đã đánh dấu hoàn thành bài học." if is_completed else "Đã lưu tiến độ."
    return ok(msg)
