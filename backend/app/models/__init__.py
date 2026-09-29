"""SQLAlchemy models — ánh xạ 1-1 với schema MySQL studyonline_db hiện có.

Phase 2 chủ yếu dùng SQL thô (core/database.py) để đảm bảo parity với bản PHP;
các model này phục vụ Alembic (baseline + migration bảng AI ở phase sau) và
để code phase 4+ dùng ORM cho phần mới.
"""
import datetime as dt

from sqlalchemy import (
    DECIMAL,
    JSON,
    TIMESTAMP,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Các kiểu ENUM dùng chung, khớp với định nghĩa cột trong MySQL
ROLE_ENUM = Enum("student", "teacher", "admin", name="user_role")
LEVEL_ENUM = Enum("beginner", "intermediate", "advanced", name="course_level")
COURSE_STATUS_ENUM = Enum("draft", "published", "archived", name="course_status")
LESSON_STATUS_ENUM = Enum("draft", "published", name="lesson_status")
ANSWER_ENUM = Enum("A", "B", "C", "D", name="answer_enum")
DIFFICULTY_ENUM = Enum("easy", "medium", "hard", name="difficulty_enum")
PAY_METHOD_ENUM = Enum("card", "bank_transfer", "momo", "zalopay", "vnpay", name="pay_method")
PAY_STATUS_ENUM = Enum("pending", "completed", "failed", "refunded", name="pay_status")


# Người dùng: admin / giảng viên / học viên; is_active = 0 là tài khoản bị khóa
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fullname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(ROLE_ENUM, default="student")
    avatar: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


# Khóa học do 1 giảng viên phụ trách; price = 0 là miễn phí
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    thumbnail: Mapped[str | None] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, default=0)
    level: Mapped[str] = mapped_column(LEVEL_ENUM, default="beginner")
    status: Mapped[str] = mapped_column(COURSE_STATUS_ENUM, default="draft")
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


# Chương của khóa học, sắp theo order_index
class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    chapter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# Bài học thuộc chương: video / tài liệu PDF; is_free = 1 là bài học thử (xem không cần ghi danh)
class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(String(500))
    document_url: Mapped[str | None] = mapped_column(String(500))
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_free: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(LESSON_STATUS_ENUM, default="draft")
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


# Ghi danh: học viên nào học khóa nào (mỗi cặp user + khóa chỉ 1 dòng)
class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_enrollment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    enroll_date: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# Tiến độ học từng bài: số giây đã xem, đã hoàn thành chưa, thời điểm hoàn thành
class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_progress"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    is_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    watched_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[dt.datetime | None] = mapped_column(TIMESTAMP)
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


# Bài kiểm tra của khóa học; source cho biết do giảng viên tạo, do AI sinh hay nhập từ file Word;
# chapter_id khác NULL nghĩa là bộ câu hỏi ôn tập của chương
class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    # Có giá trị -> đây là bộ câu hỏi ôn tập của chương (mỗi chương tối đa 1 bộ)
    chapter_id: Mapped[int | None] = mapped_column(
        ForeignKey("chapters.id", ondelete="SET NULL"), unique=True
    )
    # Có giá trị -> bộ câu hỏi ôn tập theo kiến thức của bài học (mỗi bài tối đa 1 bộ)
    review_lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL"), unique=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(
        Enum("manual", "ai", "word", name="quiz_source"), nullable=False, default="manual"
    )
    # Cài đặt làm bài: NULL = không giới hạn thời gian / không xét đạt / làm lại không giới hạn
    duration: Mapped[int | None] = mapped_column(Integer)
    passing_score: Mapped[int | None] = mapped_column(Integer)
    max_attempts: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# Câu hỏi trắc nghiệm 4 phương án; topic dùng để phân tích điểm theo chủ đề
class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # TEXT: phương án có thể chứa công thức [[math:...]] / ảnh [[img:...]] khi nhập từ Word
    option_a: Mapped[str] = mapped_column(Text, nullable=False)
    option_b: Mapped[str] = mapped_column(Text, nullable=False)
    option_c: Mapped[str] = mapped_column(Text, nullable=False)
    option_d: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(ANSWER_ENUM, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(100))
    difficulty: Mapped[str | None] = mapped_column(DIFFICULTY_ENUM)
    explanation: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


# Kết quả 1 lượt làm quiz (số câu đúng / tổng số câu)
class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Điểm đạt (%) của quiz tại thời điểm nộp; NULL = quiz không đặt điểm đạt
    passing_score: Mapped[int | None] = mapped_column(Integer)
    submit_time: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# Lượt làm đề có giới hạn thời gian / số lượt: tạo lúc mở đề, gắn result_id khi nộp
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    started_ts: Mapped[int] = mapped_column(Integer, nullable=False)
    finished_ts: Mapped[int | None] = mapped_column(Integer)
    result_id: Mapped[int | None] = mapped_column(ForeignKey("results.id", ondelete="SET NULL"))


# Chi tiết từng câu trả lời trong 1 lượt làm bài (đúng/sai) — nguồn dữ liệu phân tích chủ đề yếu
class ResultAnswer(Base):
    __tablename__ = "result_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result_id: Mapped[int] = mapped_column(
        ForeignKey("results.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    chosen: Mapped[str | None] = mapped_column(String(1))
    is_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


# Bản chụp số liệu học tập của học viên trong 1 khóa (cập nhật khi làm mới gợi ý)
class LearningAnalytics(Base):
    __tablename__ = "learning_analytics"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_la"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    avg_quiz_score: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False, default=0)
    completion_pct: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False, default=0)
    completed_lessons: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_lessons: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_time_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quiz_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weak_topics: Mapped[dict | None] = mapped_column(JSON)
    strong_topics: Mapped[dict | None] = mapped_column(JSON)
    computed_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


# Lịch sử các lần gợi ý học tập đã lưu
class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE")
    )
    level: Mapped[str] = mapped_column(
        Enum("Weak", "Average", "Good", "Excellent", name="rec_level"), nullable=False
    )
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    items: Mapped[dict] = mapped_column(JSON, nullable=False)
    based_on: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# Giao dịch thanh toán mua khóa học
class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, default=0)
    method: Mapped[str] = mapped_column(PAY_METHOD_ENUM, default="card")
    status: Mapped[str] = mapped_column(PAY_STATUS_ENUM, default="pending")
    transaction_ref: Mapped[str | None] = mapped_column(String(100), unique=True)
    # Kết quả trả về từ cổng VNPay
    gateway_txn_no: Mapped[str | None] = mapped_column(String(50))
    bank_code: Mapped[str | None] = mapped_column(String(20))
    response_code: Mapped[str | None] = mapped_column(String(10))
    note: Mapped[str | None] = mapped_column(Text)
    paid_at: Mapped[dt.datetime | None] = mapped_column(TIMESTAMP)
    created_at: Mapped[dt.datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


__all__ = [
    "User", "Course", "Chapter", "Lesson", "Enrollment", "LessonProgress",
    "Quiz", "Question", "Result", "ResultAnswer", "LearningAnalytics",
    "Recommendation", "Payment",
]
