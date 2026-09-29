"""Tiện ích dùng chung cho router — mô phỏng trim($data['x'] ?? '') / (int)$x của PHP."""
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import q_one
from app.core.responses import ApiError


def assert_owns_course(db: Session, user: dict, course_id: int) -> None:
    """Giáo viên chỉ được thao tác trên khóa học của chính mình; admin không bị giới hạn."""
    if user["role"] == "admin":
        return
    # Tìm giảng viên phụ trách khóa học; khóa không tồn tại -> 404
    course = q_one(db, "SELECT teacher_id FROM courses WHERE id = :id", id=course_id)
    if not course:
        raise ApiError("Khóa học không tồn tại.", 404)
    # Khóa của giảng viên khác -> 403
    if course["teacher_id"] != user["id"]:
        raise ApiError("Bạn không có quyền thao tác trên khóa học này.", 403)


def can_access_course(db: Session, user: dict | None, course_id: int) -> bool:
    """Xem nội dung học (bài học, câu hỏi, nộp quiz): admin/giảng viên, hoặc học viên đã ghi danh."""
    if not user:
        return False
    if user["role"] in ("admin", "teacher"):
        return True
    # Học viên: chỉ khi đã có dòng ghi danh (enrollment) cho khóa học này
    return (
        q_one(
            db,
            "SELECT id FROM enrollments WHERE user_id = :u AND course_id = :c",
            u=user["id"],
            c=course_id,
        )
        is not None
    )


# Giống assert_owns_course nhưng trả True/False thay vì ném lỗi (dùng để quyết định có hiện đáp án quiz không)
def owns_course(db: Session, user: dict | None, course_id: int) -> bool:
    if not user:
        return False
    if user["role"] == "admin":
        return True
    if user["role"] != "teacher":
        return False
    course = q_one(db, "SELECT teacher_id FROM courses WHERE id = :id", id=course_id)
    return bool(course) and course["teacher_id"] == user["id"]


def course_id_of(db: Session, table: str, row_id: int) -> int:
    """course_id của một chapter / lesson / quiz / question (đi ngược lên tới courses)."""
    # Mỗi bảng có đường JOIN khác nhau để tìm ra khóa học chứa nó
    sql = {
        "chapters": "SELECT course_id FROM chapters WHERE id = :id",
        "lessons": "SELECT ch.course_id FROM lessons l JOIN chapters ch ON ch.id = l.chapter_id WHERE l.id = :id",
        "quizzes": "SELECT course_id FROM quizzes WHERE id = :id",
        "questions": "SELECT qz.course_id FROM questions q JOIN quizzes qz ON qz.id = q.quiz_id WHERE q.id = :id",
    }[table]
    row = q_one(db, sql, id=row_id)
    if not row:
        raise ApiError("Không tìm thấy dữ liệu.", 404)
    return row["course_id"]


# Đọc giá trị chuỗi từ body JSON: thiếu hoặc null -> "", có thì cắt khoảng trắng hai đầu
def sv(body: dict, key: str, default: str = "") -> str:
    v = body.get(key, default)
    if v is None:
        return ""
    return str(v).strip()


# Đọc giá trị số nguyên từ body JSON: không chuyển được sang số -> trả default
def iv(body: dict, key: str, default: int = 0) -> int:
    v = body.get(key, default)
    try:
        if isinstance(v, str):
            v = v.strip()
        return int(v)
    except (TypeError, ValueError):
        return default


# Đọc giá trị số thực từ body JSON: không chuyển được -> trả default
def fv(body: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(body.get(key, default))
    except (TypeError, ValueError):
        return default


# Đảm bảo body là dict (client gửi mảng hoặc chuỗi thì coi như body rỗng)
def as_dict(body: Any) -> dict:
    return body if isinstance(body, dict) else {}
