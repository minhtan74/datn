"""/api/users — port của app/Controllers/UserController.php."""
import re

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import execute, get_db, q_one
from app.core.dependencies import get_current_user, require_roles
from app.core.responses import ApiError, ok

from ._common import sv

router = APIRouter(prefix="/api/users", tags=["users"])

# Các vai trò hợp lệ và mẫu kiểm tra định dạng email (có @ và có dấu chấm ở phần tên miền)
ROLES = ("admin", "teacher", "student")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# Kiểm tra email đúng định dạng và không quá 100 ký tự (giới hạn cột users.email)
def _check_email(email: str) -> None:
    if not _EMAIL_RE.match(email) or len(email) > 100:
        raise ApiError("Email không hợp lệ.")


# Kiểm tra mật khẩu tối thiểu 6 ký tự
def _check_password(password: str) -> None:
    if len(password) < 6:
        raise ApiError("Mật khẩu phải có ít nhất 6 ký tự.")


# GET /api/users — admin: danh sách mọi user; GET /api/users?id=X — xem 1 user (admin, hoặc chính mình)
@router.get("")
def index(
    id: int | None = Query(default=None),
    current=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    # Xem 1 user: giảng viên chỉ được xem thông tin của chính mình
    if id:
        if current["role"] != "admin" and current["id"] != id:
            raise ApiError("Bạn không có quyền xem thông tin người dùng này.", 403)
        user = q_one(
            db,
            "SELECT id, fullname, email, role, bio, created_at FROM users WHERE id = :id",
            id=id,
        )
        if not user:
            raise ApiError("Không tìm thấy người dùng.", 404)
        return ok(data=user)

    # Danh sách toàn bộ user (có email) chỉ dành cho admin
    if current["role"] != "admin":
        raise ApiError("Chỉ Admin mới xem được danh sách người dùng.", 403)

    from app.core.database import q_all

    rows = q_all(
        db,
        "SELECT id, fullname, email, role, is_active, created_at FROM users ORDER BY id DESC",
    )
    return ok(data=rows)


# POST /api/users — admin tạo tài khoản mới (chọn được vai trò)
@router.post("")
def create(
    body: dict = Body(default={}),
    _=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    fullname = sv(body, "fullname")
    email = sv(body, "email")
    password = sv(body, "password")
    role = sv(body, "role", "student") or "student"

    # Kiểm tra dữ liệu đầu vào và email chưa bị dùng
    if not fullname or not email or not password:
        raise ApiError("Vui lòng nhập đầy đủ thông tin.")
    _check_email(email)
    _check_password(password)
    if role not in ROLES:
        raise ApiError("Vai trò không hợp lệ.")
    if q_one(db, "SELECT id FROM users WHERE email = :email LIMIT 1", email=email):
        raise ApiError("Email này đã tồn tại.", 409)

    from app.core.security import hash_password

    # Lưu user với mật khẩu đã băm
    execute(
        db,
        "INSERT INTO users (fullname, email, password, role) "
        "VALUES (:fullname, :email, :password, :role)",
        fullname=fullname,
        email=email,
        password=hash_password(password),
        role=role,
    )
    return ok("Tạo người dùng thành công")


# PUT /api/users — cập nhật user: admin sửa được mọi người; user khác chỉ sửa được hồ sơ của mình
@router.put("")
def update(
    body: dict = Body(default={}),
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from ._common import iv

    uid = iv(body, "id")
    fullname = sv(body, "fullname")
    email = sv(body, "email")
    role = sv(body, "role")

    if not uid or not fullname or not email or not role:
        raise ApiError("Dữ liệu không hợp lệ.")
    _check_email(email)
    # Có gửi mật khẩu mới -> chức năng "đặt lại mật khẩu" chỉ admin được dùng
    new_password = sv(body, "password")
    if new_password:
        if current["role"] != "admin":
            raise ApiError("Hãy dùng chức năng Đổi mật khẩu để đổi mật khẩu của bạn.", 403)
        _check_password(new_password)

    # Người không phải admin: chỉ sửa chính mình và không được tự đổi vai trò
    if current["role"] != "admin":
        if current["id"] != uid:
            raise ApiError("Bạn không có quyền cập nhật người dùng này.", 403)
        if role != current["role"]:
            raise ApiError("Bạn không có quyền thay đổi vai trò của chính mình.", 403)

    if role not in ROLES:
        raise ApiError("Vai trò không hợp lệ.")

    # Lấy vai trò hiện tại của người được sửa
    target = q_one(db, "SELECT role FROM users WHERE id = :id", id=uid)
    if not target:
        raise ApiError("Không tìm thấy người dùng.", 404)

    # Hạ quyền một admin: không được tự hạ mình và hệ thống phải còn ít nhất 1 admin hoạt động
    if target["role"] == "admin" and role != "admin":
        if current["id"] == uid:
            raise ApiError("Bạn không thể tự hạ quyền Admin của chính mình.", 403)
        admin_count = q_one(
            db, "SELECT COUNT(*) AS n FROM users WHERE role = 'admin' AND is_active = 1"
        )["n"]
        if admin_count <= 1:
            raise ApiError("Hệ thống phải còn ít nhất một Admin đang hoạt động.", 403)

    # Hạ giảng viên thành học viên: không cho nếu họ còn phụ trách khóa học (tránh khóa học "mồ côi")
    if role == "student" and target["role"] != "student":
        owned = q_one(db, "SELECT COUNT(*) AS n FROM courses WHERE teacher_id = :id", id=uid)["n"]
        if owned:
            raise ApiError(
                f"Người này đang phụ trách {owned} khóa học. Hãy chuyển các khóa học sang giảng viên khác "
                "(Quản lý Khóa học → Sửa) trước khi đổi vai trò thành Học viên.",
                409,
            )

    # Email mới không được trùng với tài khoản khác
    if q_one(
        db,
        "SELECT id FROM users WHERE email = :email AND id <> :id LIMIT 1",
        email=email,
        id=uid,
    ):
        raise ApiError("Email này đã được sử dụng bởi tài khoản khác.", 409)

    # Ghép câu UPDATE động: chỉ cập nhật bio khi client có gửi trường bio
    fields = {"fullname": fullname, "email": email, "role": role}
    if "bio" in body:
        fields["bio"] = sv(body, "bio")[:2000] or None
    sets = ", ".join(f"{k} = :{k}" for k in fields)
    execute(db, f"UPDATE users SET {sets} WHERE id = :id", id=uid, **fields)
    # Admin đặt lại mật khẩu cho user
    if new_password:
        from app.core.security import hash_password

        execute(db, "UPDATE users SET password = :pw WHERE id = :id", pw=hash_password(new_password), id=uid)
        return ok("Cập nhật người dùng và đặt lại mật khẩu thành công")
    return ok("Cập nhật người dùng thành công")


# DELETE /api/users?id=X — admin xóa vĩnh viễn một tài khoản chưa có dữ liệu
@router.delete("")
def delete(
    id: int = Query(default=0),
    current=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    if not id:
        raise ApiError("Thiếu ID.")
    if current["id"] == id:
        raise ApiError("Bạn không thể tự xóa tài khoản của chính mình.")
    if not q_one(db, "SELECT id FROM users WHERE id = :id", id=id):
        raise ApiError("Không tìm thấy người dùng.", 404)

    # Xóa user sẽ CASCADE xóa theo khóa học, đăng ký, thanh toán... -> chỉ cho xóa tài khoản trống.
    usage = q_one(
        db,
        """
        SELECT
            (SELECT COUNT(*) FROM courses     WHERE teacher_id = :id) AS courses,
            (SELECT COUNT(*) FROM enrollments WHERE user_id    = :id) AS enrollments,
            (SELECT COUNT(*) FROM payments    WHERE user_id    = :id) AS payments,
            (SELECT COUNT(*) FROM results     WHERE user_id    = :id) AS results
        """,
        id=id,
    )
    if any(usage.values()):
        raise ApiError(
            "Tài khoản này đã có dữ liệu (khóa học / đăng ký / thanh toán / bài làm) "
            "nên không thể xóa. Hãy dùng chức năng Khóa tài khoản.",
            409,
        )

    execute(db, "DELETE FROM users WHERE id = :id", id=id)
    return ok("Xóa người dùng thành công")


# PUT /api/users/status — admin khóa / mở khóa tài khoản (thay cho xóa khi user đã có dữ liệu)
@router.put("/status")
def set_status(
    body: dict = Body(default={}),
    current=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    from ._common import iv

    uid = iv(body, "id")
    # Chuẩn hóa is_active về 1 (mở khóa) hoặc 0 (khóa) dù client gửi true/"1"/"true"
    is_active = 1 if body.get("is_active") in (True, 1, "1", "true") else 0
    if not uid:
        raise ApiError("Thiếu ID.")
    if current["id"] == uid and not is_active:
        raise ApiError("Bạn không thể tự khóa tài khoản của chính mình.")

    target = q_one(db, "SELECT role FROM users WHERE id = :id", id=uid)
    if not target:
        raise ApiError("Không tìm thấy người dùng.", 404)
    # Khóa một admin: phải còn ít nhất 1 admin đang hoạt động
    if target["role"] == "admin" and not is_active:
        active_admins = q_one(
            db, "SELECT COUNT(*) AS n FROM users WHERE role = 'admin' AND is_active = 1"
        )["n"]
        if active_admins <= 1:
            raise ApiError("Hệ thống phải còn ít nhất một Admin đang hoạt động.", 403)

    # Cập nhật trạng thái; user bị khóa sẽ bị từ chối ngay ở request kế tiếp (get_current_user)
    execute(db, "UPDATE users SET is_active = :a WHERE id = :id", a=is_active, id=uid)
    return ok("Đã mở khóa tài khoản" if is_active else "Đã khóa tài khoản")
