"""/api/chapters — port của app/Controllers/ChapterController.php."""
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import execute, get_db, q_all, q_one, q_scalar
from app.core.dependencies import require_roles
from app.core.responses import ApiError, ok

from ._common import assert_owns_course, course_id_of, iv, sv

router = APIRouter(prefix="/api/chapters", tags=["chapters"])


# Cột chung khi đọc chương: kèm id bộ ôn tập (nếu có) và số câu hỏi ôn tập của chương
_CHAPTER_SELECT = (
    "SELECT ch.*, rq.id AS review_quiz_id, "
    "(SELECT COUNT(*) FROM questions WHERE quiz_id = rq.id) AS review_question_count "
    "FROM chapters ch LEFT JOIN quizzes rq ON rq.chapter_id = ch.id "
)


# GET /api/chapters?course_id=X — danh sách chương của khóa (công khai, dùng làm đề cương); ?id=X — 1 chương
@router.get("")
def index(
    id: int | None = Query(default=None),
    course_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if id:
        chapter = q_one(db, _CHAPTER_SELECT + "WHERE ch.id = :id", id=id)
        if not chapter:
            raise ApiError("Không tìm thấy chương.", 404)
        return ok(data=chapter)
    # Sắp theo thứ tự giảng viên đặt (order_index), cùng thứ tự thì theo thứ tự tạo
    if course_id:
        return ok(
            data=q_all(
                db,
                _CHAPTER_SELECT + "WHERE ch.course_id = :cid ORDER BY ch.order_index ASC, ch.id ASC",
                cid=course_id,
            )
        )
    raise ApiError("Cần truyền course_id hoặc id.")


# Lấy (hoặc tạo mới nếu chưa có) bộ câu hỏi ôn tập của chương; trả về id quiz.
# INSERT IGNORE + UNIQUE(chapter_id) -> 2 request đồng thời cũng chỉ tạo ra 1 bộ.
def ensure_review_quiz(db: Session, chapter_id: int) -> int:
    chapter = q_one(db, "SELECT id, course_id, chapter_name FROM chapters WHERE id = :id", id=chapter_id)
    if not chapter:
        raise ApiError("Không tìm thấy chương.", 404)
    quiz_id = q_scalar(db, "SELECT id FROM quizzes WHERE chapter_id = :ch", ch=chapter_id)
    if quiz_id:
        return int(quiz_id)
    execute(
        db,
        "INSERT IGNORE INTO quizzes (course_id, chapter_id, title, description) "
        "VALUES (:cid, :ch, :title, :descr)",
        cid=chapter["course_id"],
        ch=chapter_id,
        title=f"Ôn tập: {chapter['chapter_name']}"[:255],
        descr="Câu hỏi ôn tập kiến thức của chương.",
    )
    return int(q_scalar(db, "SELECT id FROM quizzes WHERE chapter_id = :ch", ch=chapter_id))


# POST /api/chapters/review — giảng viên mở bộ câu hỏi ôn tập của chương (chưa có thì tạo)
@router.post("/review")
def open_review(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    chapter_id = iv(body, "chapter_id")
    if not chapter_id:
        raise ApiError("Thiếu chapter_id.")
    assert_owns_course(db, user, course_id_of(db, "chapters", chapter_id))
    return ok(data={"quiz_id": ensure_review_quiz(db, chapter_id)})


# POST /api/chapters — thêm chương vào khóa học của mình
@router.post("")
def create(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    course_id = iv(body, "course_id")
    name = sv(body, "chapter_name")
    if not course_id or not name:
        raise ApiError("Dữ liệu không hợp lệ.")
    assert_owns_course(db, user, course_id)
    # order_index âm được đưa về 0
    res = execute(
        db,
        "INSERT INTO chapters (course_id, chapter_name, order_index) VALUES (:cid, :name, :oi)",
        cid=course_id,
        name=name,
        oi=max(0, iv(body, "order_index")),
    )
    return ok("Tạo thành công", id=res.lastrowid)


# PUT /api/chapters — đổi tên / thứ tự chương
@router.put("")
def update(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    cid = iv(body, "id")
    name = sv(body, "chapter_name")
    if not cid or not name:
        raise ApiError("Dữ liệu không hợp lệ.")
    # Kiểm tra quyền theo khóa học chứa chương này
    assert_owns_course(db, user, course_id_of(db, "chapters", cid))
    # Chỉ cập nhật thứ tự khi client có gửi order_index
    fields = {"chapter_name": name}
    if "order_index" in body:
        fields["order_index"] = max(0, iv(body, "order_index"))
    sets = ", ".join(f"{k} = :{k}" for k in fields)
    execute(db, f"UPDATE chapters SET {sets} WHERE id = :id", id=cid, **fields)
    return ok("Cập nhật thành công")


# DELETE /api/chapters?id=X — xóa chương (các bài học bên trong bị xóa theo do CASCADE)
@router.delete("")
def delete(
    id: int = Query(default=0),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    if not id:
        raise ApiError("Thiếu ID.")
    assert_owns_course(db, user, course_id_of(db, "chapters", id))
    # Bộ ôn tập chưa ai làm thì xóa theo chương; đã có lượt làm thì FK SET NULL giữ lại thành quiz thường
    execute(
        db,
        "DELETE FROM quizzes WHERE (chapter_id = :id "
        "OR review_lesson_id IN (SELECT l.id FROM lessons l WHERE l.chapter_id = :id)) "
        "AND NOT EXISTS (SELECT 1 FROM results r WHERE r.quiz_id = quizzes.id)",
        id=id,
    )
    execute(db, "DELETE FROM chapters WHERE id = :id", id=id)
    return ok("Xóa thành công")
