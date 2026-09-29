"""/api/courses — port của app/Controllers/CourseController.php."""
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import execute, get_db, q_all, q_one
from app.core.dependencies import get_viewer, require_roles
from app.core.responses import ApiError, ok

from ._common import assert_owns_course, iv, sv

router = APIRouter(prefix="/api/courses", tags=["courses"])

# Câu SELECT gốc: lấy khóa học kèm tên giảng viên phụ trách
_SELECT = (
    "SELECT c.*, u.fullname AS teacher_name "
    "FROM courses c LEFT JOIN users u ON c.teacher_id = u.id"
)

# Trạng thái khóa học: bản nháp / đã xuất bản / lưu trữ
STATUSES = ("draft", "published", "archived")


def _visibility(user: dict | None) -> tuple[str, dict]:
    """Admin thấy tất cả; giảng viên thấy thêm khóa của mình; học viên thấy thêm khóa đã ghi danh;
    còn lại chỉ thấy khóa đã xuất bản."""
    # Trả về (điều kiện WHERE, tham số) để ghép vào câu truy vấn danh sách khóa học
    if user and user["role"] == "admin":
        return "1=1", {}
    if not user:
        return "c.status = 'published'", {}
    return (
        "(c.status = 'published' OR c.teacher_id = :uid "
        "OR EXISTS (SELECT 1 FROM enrollments e WHERE e.course_id = c.id AND e.user_id = :uid))",
        {"uid": user["id"]},
    )


def _price_status(body: dict) -> dict:
    """Chỉ trả về các trường có trong body, để form không gửi price/status (vd form Admin) không ghi đè."""
    out = {}
    # Giá: phải là số và không âm (0 = miễn phí)
    if "price" in body:
        try:
            price = float(body.get("price") or 0)
        except (TypeError, ValueError):
            raise ApiError("Giá không hợp lệ.")
        if price < 0:
            raise ApiError("Giá không được âm.")
        out["price"] = price
    # Trạng thái: giá trị cũ "active" của frontend được hiểu là "published"
    if "status" in body:
        status = sv(body, "status")
        status = "published" if status == "active" else status
        if status not in STATUSES:
            raise ApiError("Trạng thái không hợp lệ.")
        out["status"] = status
    return out


def _teacher_id(db: Session, user: dict, body: dict) -> int | None:
    """Chỉ admin được chỉ định giảng viên phụ trách; người được chọn phải là giảng viên đang hoạt động."""
    if user["role"] != "admin" or not body.get("teacher_id"):
        return None
    tid = iv(body, "teacher_id")
    target = q_one(db, "SELECT role, is_active FROM users WHERE id = :id", id=tid)
    if not target or target["role"] not in ("teacher", "admin") or not target["is_active"]:
        raise ApiError("Giảng viên phụ trách không hợp lệ.")
    return tid


# GET /api/courses — danh sách khóa học (lọc theo quyền xem); ?id=X — chi tiết 1 khóa
@router.get("")
def index(
    id: int | None = Query(default=None),
    user: dict | None = Depends(get_viewer),
    db: Session = Depends(get_db),
):
    # Điều kiện hiển thị theo vai trò người xem (khách chỉ thấy khóa đã xuất bản)
    cond, params = _visibility(user)
    if id:
        course = q_one(db, f"{_SELECT} WHERE c.id = :id AND {cond}", id=id, **params)
        if not course:
            raise ApiError("Không tìm thấy khóa học.", 404)
        return ok(data=course)
    return ok(data=q_all(db, f"{_SELECT} WHERE {cond} ORDER BY c.id DESC", **params))


# POST /api/courses — giảng viên/admin tạo khóa học mới
@router.post("")
def create(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    title = sv(body, "title")
    description = sv(body, "description")
    thumbnail = sv(body, "thumbnail")
    if not title:
        raise ApiError("Tiêu đề không được trống.")
    # Mặc định miễn phí + đã xuất bản nếu client không gửi price/status
    extra = {"price": 0, "status": "published", **_price_status(body)}
    # Người phụ trách: admin có thể chọn giảng viên khác, còn lại là người tạo
    teacher_id = _teacher_id(db, user, body) or user["id"]

    res = execute(
        db,
        "INSERT INTO courses (teacher_id, title, description, thumbnail, price, status) "
        "VALUES (:tid, :title, :description, :thumbnail, :price, :status)",
        tid=teacher_id,
        title=title,
        description=description,
        thumbnail=thumbnail,
        **extra,
    )
    # Trả id khóa vừa tạo để frontend dùng tiếp
    return ok("Tạo thành công", id=res.lastrowid)


# PUT /api/courses — sửa khóa học (giảng viên chỉ sửa khóa của mình)
@router.put("")
def update(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    cid = iv(body, "id")
    title = sv(body, "title")
    description = sv(body, "description")
    thumbnail = sv(body, "thumbnail")
    if not cid or not title:
        raise ApiError("Dữ liệu không hợp lệ.")
    assert_owns_course(db, user, cid)

    # Ghép các trường cần cập nhật: thumbnail rỗng thì giữ ảnh cũ; teacher_id chỉ khi admin đổi người phụ trách
    fields = {"title": title, "description": description, **_price_status(body)}
    if thumbnail:
        fields["thumbnail"] = thumbnail
    teacher_id = _teacher_id(db, user, body)
    if teacher_id:
        fields["teacher_id"] = teacher_id
    sets = ", ".join(f"{k} = :{k}" for k in fields)
    execute(db, f"UPDATE courses SET {sets} WHERE id = :id", id=cid, **fields)
    return ok("Cập nhật thành công")


# DELETE /api/courses?id=X — xóa khóa học chưa có học viên / giao dịch
@router.delete("")
def delete(
    id: int = Query(default=0),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    if not id:
        raise ApiError("Thiếu ID.")
    assert_owns_course(db, user, id)

    # Xóa khóa học sẽ CASCADE xóa đăng ký + thanh toán -> học viên mất khóa đã mua, mất doanh thu.
    usage = q_one(
        db,
        "SELECT (SELECT COUNT(*) FROM enrollments WHERE course_id = :id) AS enrollments, "
        "(SELECT COUNT(*) FROM payments WHERE course_id = :id) AS payments",
        id=id,
    )
    if usage and (usage["enrollments"] or usage["payments"]):
        raise ApiError(
            f"Khóa học đã có {usage['enrollments']} học viên / {usage['payments']} giao dịch nên không thể xóa. "
            "Hãy chuyển trạng thái sang \"Lưu trữ\" để ngừng nhận học viên mới.",
            409,
        )

    execute(db, "DELETE FROM courses WHERE id = :id", id=id)
    return ok("Xóa thành công")
