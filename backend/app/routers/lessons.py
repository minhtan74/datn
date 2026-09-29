"""/api/lessons — port của app/Controllers/LessonController.php."""
import os

from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import execute, get_db, q_all, q_one, q_scalar
from app.core.dependencies import get_viewer, require_roles
from app.core.media import protected_path, signed_src, verify
from app.core.responses import ApiError, ok

from ._common import assert_owns_course, can_access_course, course_id_of, iv, sv

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


# Ẩn link video/tài liệu của bài học bị khóa (người xem chưa ghi danh)
def _hide_content(lesson: dict) -> dict:
    # Người chưa ghi danh vẫn xem được đề cương (tiêu đề, mô tả) nhưng không có link video/tài liệu.
    return {**lesson, "video_url": None, "document_url": None,
            "video_src": None, "document_src": None, "locked": True}


def _lesson_extras(body: dict) -> dict:
    """Chỉ lấy các trường có trong body để client cũ (không gửi) không ghi đè giá trị hiện có."""
    out = {}
    if "is_free" in body:
        out["is_free"] = 1 if body.get("is_free") in (True, 1, "1", "true") else 0
    if "order_index" in body:
        out["order_index"] = max(0, iv(body, "order_index"))
    if "duration" in body:
        out["duration"] = max(0, iv(body, "duration"))
    return out


# Gắn thêm link phát/tải (video_src, document_src) cho bài học
def _with_src(user: dict | None, lesson: dict) -> dict:
    # *_url giữ giá trị gốc (form sửa bài học lưu lại nó); *_src là link để trình duyệt phát/tải.
    return {**lesson, "video_src": signed_src(user, lesson, "video"),
            "document_src": signed_src(user, lesson, "document")}


# Cột chung khi đọc bài học: kèm id bộ ôn tập của bài (nếu có) và số câu hỏi ôn tập
_LESSON_SELECT = (
    "SELECT l.*, rq.id AS review_quiz_id, "
    "(SELECT COUNT(*) FROM questions WHERE quiz_id = rq.id) AS review_question_count "
    "FROM lessons l LEFT JOIN quizzes rq ON rq.review_lesson_id = l.id "
)


# GET /api/lessons — ?id=X: chi tiết 1 bài học; ?chapter_id=X: danh sách bài học của chương
@router.get("")
def index(
    id: int | None = Query(default=None),
    chapter_id: int | None = Query(default=None),
    user: dict | None = Depends(get_viewer),
    db: Session = Depends(get_db),
):
    # Chi tiết 1 bài: bài không miễn phí thì phải có quyền vào khóa học
    if id:
        lesson = q_one(db, _LESSON_SELECT + "WHERE l.id = :id", id=id)
        if not lesson:
            raise ApiError("Không tìm thấy bài học.", 404)
        if not lesson.get("is_free") and not can_access_course(db, user, course_id_of(db, "lessons", id)):
            raise ApiError("Bạn cần đăng ký khóa học để xem bài học này.", 403)
        return ok(data=_with_src(user, lesson))
    # Danh sách bài của chương theo thứ tự; người chưa ghi danh chỉ thấy link của bài học thử (is_free)
    if chapter_id:
        lessons = q_all(
            db,
            _LESSON_SELECT + "WHERE l.chapter_id = :cid ORDER BY l.order_index ASC, l.id ASC",
            cid=chapter_id,
        )
        chapter = q_one(db, "SELECT course_id FROM chapters WHERE id = :id", id=chapter_id)
        allowed = not chapter or can_access_course(db, user, chapter["course_id"])
        lessons = [
            _with_src(user, l) if allowed or l.get("is_free") else _hide_content(l) for l in lessons
        ]
        return ok(data=lessons)
    raise ApiError("Cần truyền chapter_id hoặc id.")


# Lấy (hoặc tạo mới nếu chưa có) bộ câu hỏi ôn tập của bài học; trả về id quiz.
# INSERT IGNORE + UNIQUE(review_lesson_id) -> 2 request đồng thời cũng chỉ tạo ra 1 bộ.
def ensure_lesson_review_quiz(db: Session, lesson_id: int) -> int:
    lesson = q_one(
        db,
        "SELECT l.id, l.title, ch.course_id FROM lessons l JOIN chapters ch ON ch.id = l.chapter_id "
        "WHERE l.id = :id",
        id=lesson_id,
    )
    if not lesson:
        raise ApiError("Không tìm thấy bài học.", 404)
    quiz_id = q_scalar(db, "SELECT id FROM quizzes WHERE review_lesson_id = :l", l=lesson_id)
    if quiz_id:
        return int(quiz_id)
    execute(
        db,
        "INSERT IGNORE INTO quizzes (course_id, review_lesson_id, title, description) "
        "VALUES (:cid, :l, :title, :descr)",
        cid=lesson["course_id"],
        l=lesson_id,
        title=f"Ôn tập bài: {lesson['title']}"[:255],
        descr="Câu hỏi ôn tập kiến thức của bài học.",
    )
    return int(q_scalar(db, "SELECT id FROM quizzes WHERE review_lesson_id = :l", l=lesson_id))


# POST /api/lessons/review — giảng viên mở bộ câu hỏi ôn tập của bài học (chưa có thì tạo)
@router.post("/review")
def open_review(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    lesson_id = iv(body, "lesson_id")
    if not lesson_id:
        raise ApiError("Thiếu lesson_id.")
    assert_owns_course(db, user, course_id_of(db, "lessons", lesson_id))
    return ok(data={"quiz_id": ensure_lesson_review_quiz(db, lesson_id)})


# GET /api/lessons/media — phát file video/tài liệu qua link có chữ ký (thẻ <video> không gửi được JWT)
@router.get("/media")
def media(
    lesson_id: int = Query(...),
    kind: str = Query(...),
    uid: int = Query(...),
    exp: int = Query(...),
    sig: str = Query(...),
    db: Session = Depends(get_db),
):
    # Kiểm tra loại file và chữ ký HMAC + hạn dùng của link
    if kind not in ("video", "document") or not verify(uid, lesson_id, kind, exp, sig):
        raise ApiError("Link đã hết hạn hoặc không hợp lệ. Vui lòng tải lại trang bài học.", 403)

    # User trong link phải còn tồn tại và đang hoạt động (chưa bị khóa)
    user = q_one(db, "SELECT id, role, is_active FROM users WHERE id = :id", id=uid)
    lesson = q_one(db, "SELECT * FROM lessons WHERE id = :id", id=lesson_id)
    if not user or not user["is_active"] or not lesson:
        raise ApiError("Không có quyền truy cập tệp này.", 403)
    # Kiểm tra lại quyền ở mỗi lần tải: link đã phát ra vẫn mất hiệu lực khi bị hoàn tiền / hủy ghi danh.
    if not lesson.get("is_free") and not can_access_course(db, user, course_id_of(db, "lessons", lesson_id)):
        raise ApiError("Bạn cần đăng ký khóa học để xem bài học này.", 403)

    # Ánh xạ URL sang file thật trên đĩa rồi trả file (inline để trình duyệt phát trực tiếp, cache riêng 1 giờ)
    path = protected_path(lesson.get(f"{kind}_url"))
    if not path or not os.path.isfile(path):
        raise ApiError("Không tìm thấy tệp.", 404)
    return FileResponse(
        path,
        filename=os.path.basename(path),
        content_disposition_type="inline",
        headers={"Cache-Control": "private, max-age=3600"},
    )


# POST /api/lessons — thêm bài học vào chương
@router.post("")
def create(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    chapter_id = iv(body, "chapter_id")
    title = sv(body, "title")
    description = sv(body, "description")
    video_url = sv(body, "video_url")
    document_url = sv(body, "document_url")
    if not chapter_id or not title:
        raise ApiError("Dữ liệu không hợp lệ.")
    # Chỉ chủ khóa học (hoặc admin) được thêm; giá trị mặc định: không miễn phí, thứ tự 0, thời lượng 0
    assert_owns_course(db, user, course_id_of(db, "chapters", chapter_id))
    extra = {"is_free": 0, "order_index": 0, "duration": 0, **_lesson_extras(body)}
    res = execute(
        db,
        "INSERT INTO lessons (chapter_id, title, description, video_url, document_url, "
        "is_free, order_index, duration) "
        "VALUES (:cid, :title, :description, :video, :doc, :is_free, :order_index, :duration)",
        cid=chapter_id,
        title=title,
        description=description,
        video=video_url,
        doc=document_url,
        **extra,
    )
    return ok("Tạo thành công", id=res.lastrowid)


# PUT /api/lessons — sửa bài học
@router.put("")
def update(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    lid = iv(body, "id")
    title = sv(body, "title")
    description = sv(body, "description")
    video_url = sv(body, "video_url")
    document_url = sv(body, "document_url")
    if not lid or not title:
        raise ApiError("Dữ liệu không hợp lệ.")
    assert_owns_course(db, user, course_id_of(db, "lessons", lid))
    fields = {
        "title": title,
        "description": description,
        "video_url": video_url,
        "document_url": document_url,
        **_lesson_extras(body),
    }
    # Ghép câu UPDATE động theo các trường cần cập nhật
    sets = ", ".join(f"{k} = :{k}" for k in fields)
    execute(db, f"UPDATE lessons SET {sets} WHERE id = :id", id=lid, **fields)
    return ok("Cập nhật thành công")


# DELETE /api/lessons?id=X — chủ khóa học xóa bài học
@router.delete("")
def delete(
    id: int = Query(default=0),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    if not id:
        raise ApiError("Thiếu ID.")
    assert_owns_course(db, user, course_id_of(db, "lessons", id))
    # Bộ ôn tập chưa ai làm thì xóa theo bài; đã có lượt làm thì FK SET NULL giữ lại thành quiz thường
    execute(
        db,
        "DELETE FROM quizzes WHERE review_lesson_id = :id "
        "AND NOT EXISTS (SELECT 1 FROM results r WHERE r.quiz_id = quizzes.id)",
        id=id,
    )
    execute(db, "DELETE FROM lessons WHERE id = :id", id=id)
    return ok("Xóa thành công")
