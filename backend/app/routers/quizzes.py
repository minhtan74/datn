"""/api/quizzes(/questions|/submit) — port của app/Controllers/QuizController.php."""
import hashlib
import hmac
import math
import os
import time

from fastapi import APIRouter, Body, Depends, File, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import execute, get_db, q_all, q_one, q_scalar
from app.core.dependencies import get_current_user, get_current_user_optional, get_viewer, require_roles
from app.core.responses import ApiError, ok
from app.services.analytics_service import GRADING_METHODS
from app.services.word_quiz_parser import WordQuizError, build_template, parse_docx

from ._common import assert_owns_course, can_access_course, course_id_of, iv, owns_course, sv

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


# Đếm số câu hỏi của một quiz (hiển thị "N câu" trên danh sách)
def _count_questions(db: Session, quiz_id: int) -> int:
    return int(q_scalar(db, "SELECT COUNT(*) FROM questions WHERE quiz_id = :q", q=quiz_id) or 0)


# ── CÀI ĐẶT LÀM BÀI ────────────────────────────────────────────────────────

# Thêm giờ ân hạn khi nộp bài có giới hạn thời gian (bù độ trễ mạng / tự nộp khi hết giờ)
_GRACE_SEC = 60


# Đọc cài đặt làm bài từ body; để trống hoặc 0 = không giới hạn (lưu NULL)
def _quiz_settings(body: dict) -> dict:
    def opt(key: str, hi: int, label: str) -> int | None:
        if body.get(key) in (None, ""):
            return None
        v = iv(body, key, -1)
        if v < 0 or v > hi:
            raise ApiError(f"{label} phải từ 0 đến {hi}.")
        return v or None

    return {
        "duration": opt("duration", 600, "Thời gian làm bài (phút)"),
        "passing_score": opt("passing_score", 100, "Điểm đạt (%)"),
        "max_attempts": opt("max_attempts", 100, "Số lần làm tối đa"),
    }


# Đề "có ràng buộc" (giới hạn thời gian hoặc số lượt) -> theo dõi lượt làm từ lúc mở đề
def _is_tracked(quiz: dict) -> bool:
    return bool(quiz.get("duration") or quiz.get("max_attempts"))


# Số lượt người dùng đã dùng: lượt đã nộp (results) + lượt đã mở nhưng chưa nộp / bỏ dở / quá giờ
def _attempts_used(db: Session, user_id: int, quiz_id: int) -> int:
    submitted = q_scalar(db, "SELECT COUNT(*) FROM results WHERE user_id = :u AND quiz_id = :q", u=user_id, q=quiz_id)
    unsubmitted = q_scalar(
        db,
        "SELECT COUNT(*) FROM quiz_attempts WHERE user_id = :u AND quiz_id = :q AND result_id IS NULL",
        u=user_id,
        q=quiz_id,
    )
    return int(submitted or 0) + int(unsubmitted or 0)


# Lượt đã quá giờ làm bài (+ ân hạn) chưa
def _expired(quiz: dict, attempt: dict) -> bool:
    return bool(quiz["duration"]) and time.time() > attempt["started_ts"] + quiz["duration"] * 60 + _GRACE_SEC


# Chốt lượt làm: đặt giờ kết thúc (và kết quả nếu đã nộp)
def _close_attempt(db: Session, attempt_id: int, result_id: int | None = None) -> None:
    execute(
        db,
        "UPDATE quiz_attempts SET finished_ts = :t, result_id = :r WHERE id = :id",
        t=int(time.time()),
        r=result_id,
        id=attempt_id,
    )


# Lượt đang làm dở (chưa nộp, chưa hết hạn) của người dùng; lượt quá giờ thì chốt lại (vẫn tính là đã dùng)
def _open_attempt(db: Session, user_id: int, quiz: dict) -> dict | None:
    attempt = q_one(
        db,
        "SELECT * FROM quiz_attempts WHERE user_id = :u AND quiz_id = :q AND finished_ts IS NULL "
        "ORDER BY id DESC LIMIT 1",
        u=user_id,
        q=quiz["id"],
    )
    if attempt and _expired(quiz, attempt):
        _close_attempt(db, attempt["id"])
        return None
    return attempt


# Chữ ký HMAC của lượt làm -> client không đoán / sửa được id lượt của người khác
def _attempt_sig(user_id: int, quiz_id: int, attempt_id: int) -> str:
    msg = f"quiz-attempt:{user_id}:{quiz_id}:{attempt_id}".encode()
    return hmac.new(settings.jwt_secret.encode(), msg, hashlib.sha256).hexdigest()


# Mở đề: tiếp tục lượt đang dở, chưa có thì tạo lượt mới (nếu còn lượt) -> trả thông tin cho client
def _start_or_resume(db: Session, user: dict, quiz: dict) -> dict:
    attempt = _open_attempt(db, user["id"], quiz)
    if not attempt:
        _assert_attempts_left(db, user, quiz)
        now = int(time.time())
        res = execute(
            db,
            "INSERT INTO quiz_attempts (user_id, quiz_id, started_ts) VALUES (:u, :q, :t)",
            u=user["id"],
            q=quiz["id"],
            t=now,
        )
        attempt = {"id": res.lastrowid, "started_ts": now}
    info = {
        "attempt_token": f"{attempt['id']}.{_attempt_sig(user['id'], quiz['id'], attempt['id'])}",
        "attempts_used": _attempts_used(db, user["id"], quiz["id"]),
    }
    if quiz["duration"]:
        # Thời gian còn lại tính từ giờ mở đề lần đầu -> tải lại trang không được cấp thêm giờ
        left = attempt["started_ts"] + quiz["duration"] * 60 - int(time.time())
        info.update(time_limit_sec=quiz["duration"] * 60, remaining_sec=max(0, left))
    return info


# Nộp bài đề có ràng buộc: token phải trỏ tới lượt đang làm của chính người dùng và chưa quá giờ
def _check_attempt_token(db: Session, user_id: int, quiz: dict, token: str) -> dict:
    attempt_raw, _, sig = (token or "").partition(".")
    attempt_id = int(attempt_raw) if attempt_raw.isdigit() else 0
    if not attempt_id or not hmac.compare_digest(_attempt_sig(user_id, quiz["id"], attempt_id), sig):
        raise ApiError("Phiên làm bài không hợp lệ. Vui lòng mở lại bài kiểm tra.", 400)
    attempt = q_one(
        db,
        "SELECT * FROM quiz_attempts WHERE id = :id AND user_id = :u AND quiz_id = :q",
        id=attempt_id,
        u=user_id,
        q=quiz["id"],
    )
    if not attempt:
        raise ApiError("Phiên làm bài không hợp lệ. Vui lòng mở lại bài kiểm tra.", 400)
    if attempt["finished_ts"]:
        raise ApiError("Lượt làm bài này đã kết thúc.", 403)
    if _expired(quiz, attempt):
        _close_attempt(db, attempt["id"])
        raise ApiError("Đã hết thời gian làm bài, bài nộp không được chấp nhận.", 403)
    return attempt


# Chặn làm tiếp khi đã dùng hết số lần làm cho phép
def _assert_attempts_left(db: Session, user: dict, quiz: dict) -> None:
    limit = quiz.get("max_attempts")
    if limit and _attempts_used(db, user["id"], quiz["id"]) >= limit:
        raise ApiError(f"Bạn đã dùng hết {limit} lượt làm bài kiểm tra này.", 403)


# Số lượt làm bài (của mọi người) đã nộp cho quiz
def _count_attempts(db: Session, quiz_id: int) -> int:
    return int(q_scalar(db, "SELECT COUNT(*) FROM results WHERE quiz_id = :q", q=quiz_id) or 0)


# Tiêu đề quiz: bắt buộc và không vượt độ dài cột quizzes.title (VARCHAR 255)
def _check_title(title: str) -> None:
    if len(title) > 255:
        raise ApiError("Tiêu đề quiz tối đa 255 ký tự.")


# Cách tính điểm khi làm nhiều lượt; thiếu trong body thì dùng default (None = giữ nguyên khi sửa)
def _grading_method(body: dict, default: str | None = "highest") -> str | None:
    if body.get("grading_method") in (None, ""):
        return default
    method = sv(body, "grading_method").lower()
    if method not in GRADING_METHODS:
        raise ApiError("Cách tính điểm phải là highest, latest, first hoặc average.")
    return method


# % điểm của 1 lượt làm, làm tròn 0.5 lên (giống Math.round bên PHP/JS cũ)
def _percent(score: int, total: int) -> int:
    return math.floor(score / total * 100 + 0.5) if total > 0 else 0


# Đạt / chưa đạt của 1 lượt theo điểm đạt lúc nộp; quiz không đặt điểm đạt -> None
def _passed(percent: float, passing_score: int | None) -> bool | None:
    return percent >= passing_score if passing_score else None


# Điểm được tính của học viên cho 1 quiz từ các lượt đã nộp (sắp theo thứ tự nộp) theo cách tính của quiz.
# Trả về (percent, passed, id lượt được tính — None nếu lấy trung bình)
def _graded(method: str, rows: list[dict]) -> tuple[int | None, bool | None, int | None]:
    if not rows:
        return None, None, None
    pcts = [_percent(r["score"], r["total"]) for r in rows]
    if method == "average":
        avg = round(sum(pcts) / len(pcts))
        return avg, _passed(avg, rows[-1]["passing_score"]), None
    if method in ("first", "latest"):
        i = 0 if method == "first" else len(rows) - 1
        return pcts[i], _passed(pcts[i], rows[i]["passing_score"]), rows[i]["id"]
    # highest: lượt điểm cao nhất (bằng điểm thì lấy lượt sớm nhất); đạt nếu có lượt nào đạt
    i = pcts.index(max(pcts))
    flags = [_passed(pc, r["passing_score"]) for pc, r in zip(pcts, rows)]
    passed = None if all(f is None for f in flags) else any(flags)
    return pcts[i], passed, rows[i]["id"]


# Các lượt đã nộp của học viên cho 1 quiz, theo thứ tự nộp
def _my_results(db: Session, user_id: int, quiz_id: int) -> list[dict]:
    return q_all(
        db,
        "SELECT id, score, total, passing_score, submit_time FROM results "
        "WHERE user_id = :u AND quiz_id = :q ORDER BY id ASC",
        u=user_id,
        q=quiz_id,
    )


# Tình trạng làm bài của học viên với 1 quiz (hiện trên danh sách quiz)
def _my_status(db: Session, user: dict, quiz: dict) -> dict:
    rows = _my_results(db, user["id"], quiz["id"])
    percent, passed, _ = _graded(quiz["grading_method"], rows)
    status = {
        "submitted": len(rows),
        "graded_percent": percent,
        "passed": passed,
        "in_progress": False,
        "remaining_sec": None,
        "attempts_left": None,
    }
    if _is_tracked(quiz):
        attempt = _open_attempt(db, user["id"], quiz)
        if attempt:
            status["in_progress"] = True
            if quiz["duration"]:
                status["remaining_sec"] = max(0, attempt["started_ts"] + quiz["duration"] * 60 - int(time.time()))
        if quiz["max_attempts"]:
            status["attempts_left"] = max(0, quiz["max_attempts"] - _attempts_used(db, user["id"], quiz["id"]))
    return status


# ── QUIZ CRUD ───────────────────────────────────────────────────────────────

# GET /api/quizzes — ?id=X: chi tiết 1 quiz; ?course_id=X: quiz của 1 khóa; không tham số: theo vai trò
@router.get("")
def index(
    id: int | None = Query(default=None),
    course_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: dict | None = Depends(get_current_user_optional),
):
    # Chi tiết 1 quiz kèm tên khóa học và số câu hỏi
    if id:
        quiz = q_one(
            db,
            "SELECT q.*, c.title AS course_title, ch.chapter_name, rl.title AS review_lesson_title "
            "FROM quizzes q JOIN courses c ON q.course_id = c.id "
            "LEFT JOIN chapters ch ON ch.id = q.chapter_id "
            "LEFT JOIN lessons rl ON rl.id = q.review_lesson_id WHERE q.id = :id",
            id=id,
        )
        if not quiz:
            raise ApiError("Không tìm thấy quiz.", 404)
        quiz["question_count"] = _count_questions(db, id)
        if user:
            quiz["my_attempts"] = _attempts_used(db, user["id"], id)
        return ok(data=quiz)

    # Danh sách quiz của 1 khóa học cụ thể
    if course_id:
        quizzes = q_all(
            db,
            "SELECT q.*, ch.chapter_name FROM quizzes q "
            "LEFT JOIN chapters ch ON ch.id = q.chapter_id "
            "WHERE q.course_id = :cid ORDER BY q.id ASC",
            cid=course_id,
        )
    else:
        # Không lọc theo course_id: admin thấy tất cả, giảng viên thấy quiz khóa của mình,
        # học viên thấy quiz của các khóa đã ghi danh.
        if not user:
            raise ApiError("Cần đăng nhập hoặc truyền course_id.", 401)
        if user["role"] == "student":
            quizzes = q_all(
                db,
                "SELECT q.*, c.title AS course_title, ch.chapter_name FROM quizzes q "
                "JOIN courses c ON q.course_id = c.id "
                "LEFT JOIN chapters ch ON ch.id = q.chapter_id "
                "JOIN enrollments e ON e.course_id = c.id AND e.user_id = :uid "
                "ORDER BY c.title ASC, q.id ASC",
                uid=user["id"],
            )
        elif user["role"] == "admin":
            quizzes = q_all(
                db,
                "SELECT q.*, c.title AS course_title, ch.chapter_name FROM quizzes q "
                "JOIN courses c ON q.course_id = c.id "
                "LEFT JOIN chapters ch ON ch.id = q.chapter_id ORDER BY q.created_at DESC",
            )
        else:
            quizzes = q_all(
                db,
                "SELECT q.*, c.title AS course_title, ch.chapter_name FROM quizzes q "
                "JOIN courses c ON q.course_id = c.id "
                "LEFT JOIN chapters ch ON ch.id = q.chapter_id "
                "WHERE c.teacher_id = :tid ORDER BY q.created_at DESC",
                tid=user["id"],
            )
    # Gắn thêm số câu hỏi cho từng quiz
    for q in quizzes:
        q["question_count"] = _count_questions(db, q["id"])
    # Học viên / khách: ẩn quiz chưa có câu hỏi (giảng viên vừa tạo, đang soạn dở)
    if not user or user["role"] == "student":
        quizzes = [q for q in quizzes if q["question_count"]]
        # Học viên: kèm tình trạng làm bài (chưa làm / đang làm dở / điểm được tính / còn mấy lượt)
        if user:
            for q in quizzes:
                q["my_status"] = _my_status(db, user, q)
    else:
        # Giảng viên / admin: kèm số lượt đã làm để form sửa biết quiz đã có kết quả hay chưa
        for q in quizzes:
            q["attempt_count"] = _count_attempts(db, q["id"])
    return ok(data=quizzes)


# POST /api/quizzes — giảng viên tạo quiz mới cho khóa học của mình
@router.post("")
def create(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    course_id = iv(body, "course_id")
    title = sv(body, "title")
    description = sv(body, "description")
    if not course_id or not title:
        raise ApiError("Dữ liệu không hợp lệ.")
    _check_title(title)
    # Chỉ chủ khóa học (hoặc admin) mới được thêm quiz
    assert_owns_course(db, user, course_id)
    res = execute(
        db,
        "INSERT INTO quizzes (course_id, title, description, duration, passing_score, max_attempts, grading_method) "
        "VALUES (:cid, :title, :descr, :duration, :passing_score, :max_attempts, :grading)",
        cid=course_id,
        title=title,
        descr=description,
        grading=_grading_method(body),
        **_quiz_settings(body),
    )
    return ok("Tạo thành công", id=res.lastrowid)


# PUT /api/quizzes — sửa tiêu đề / mô tả / khóa học của quiz
@router.put("")
def update(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    qid = iv(body, "id")
    course_id = iv(body, "course_id")
    title = sv(body, "title")
    description = sv(body, "description")
    if not qid or not course_id or not title:
        raise ApiError("Dữ liệu không hợp lệ.")
    _check_title(title)
    # Phải sở hữu khóa hiện tại của quiz
    assert_owns_course(db, user, course_id_of(db, "quizzes", qid))
    assert_owns_course(db, user, course_id)  # neu doi sang khoa khac, phai so huu ca khoa moi
    current = q_one(db, "SELECT course_id, chapter_id, review_lesson_id FROM quizzes WHERE id = :id", id=qid)
    if current["course_id"] != course_id:
        # Bộ ôn tập gắn với 1 chương / 1 bài học -> không được chuyển sang khóa khác
        if current["chapter_id"] or current["review_lesson_id"]:
            raise ApiError("Bộ câu hỏi ôn tập không thể chuyển sang khóa học khác.")
        # Đã có lượt làm -> chuyển khóa sẽ làm điểm của học viên khóa cũ tính sang khóa mới
        attempts = _count_attempts(db, qid)
        if attempts:
            raise ApiError(
                f"Quiz đã có {attempts} lượt làm bài nên không thể chuyển sang khóa học khác "
                "(điểm của học viên khóa hiện tại sẽ bị tính nhầm sang khóa mới).",
                409,
            )
    execute(
        db,
        "UPDATE quizzes SET course_id = :cid, title = :title, description = :descr, "
        "duration = :duration, passing_score = :passing_score, max_attempts = :max_attempts, "
        "grading_method = COALESCE(:grading, grading_method) WHERE id = :id",
        cid=course_id,
        title=title,
        descr=description,
        id=qid,
        grading=_grading_method(body, default=None),
        **_quiz_settings(body),
    )
    return ok("Cập nhật thành công")


# DELETE /api/quizzes?id=X — xóa quiz chưa có học viên làm bài
@router.delete("")
def delete(
    id: int = Query(default=0),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    if not id:
        raise ApiError("Thiếu ID.")
    assert_owns_course(db, user, course_id_of(db, "quizzes", id))
    # results/result_answers CASCADE theo quiz -> xóa quiz là mất điểm học viên và dữ liệu phân tích.
    attempts = q_scalar(db, "SELECT COUNT(*) FROM results WHERE quiz_id = :id", id=id) or 0
    if attempts:
        raise ApiError(
            f"Quiz đã có {attempts} lượt làm bài của học viên nên không thể xóa "
            "(sẽ mất điểm và dữ liệu phân tích học tập).",
            409,
        )
    execute(db, "DELETE FROM quizzes WHERE id = :id", id=id)
    return ok("Xóa thành công")


# ── QUESTIONS CRUD ─────────────────────────────────────────────────────────

# Các trường chứa đáp án -> ẩn đi khi trả câu hỏi cho học viên đang làm bài
_ANSWER_FIELDS = ("correct_answer", "explanation")
# Các mức độ khó hợp lệ của câu hỏi
_DIFFICULTIES = ("easy", "medium", "hard")


def _question_fields(body: dict) -> dict:
    """Kiểm tra & chuẩn hoá dữ liệu câu hỏi (giống ràng buộc của /api/ai/quiz/approve)."""
    content = sv(body, "content")
    options = {k: sv(body, k) for k in ("option_a", "option_b", "option_c", "option_d")}
    answer = (sv(body, "correct_answer") or "").upper()
    # Bắt buộc: có nội dung, ít nhất 2 phương án A/B, đáp án là A–D và phương án đó không trống
    if not content:
        raise ApiError("Nội dung câu hỏi không được trống.")
    if not options["option_a"] or not options["option_b"]:
        raise ApiError("Vui lòng nhập ít nhất phương án A và B.")
    if answer not in ("A", "B", "C", "D"):
        raise ApiError("Đáp án đúng phải là A, B, C hoặc D.")
    if not options[f"option_{answer.lower()}"]:
        raise ApiError(f"Đáp án đúng là {answer} nhưng phương án {answer} đang để trống.")
    # Độ khó không bắt buộc, nhưng nếu có thì phải thuộc easy/medium/hard
    difficulty = sv(body, "difficulty").lower() or None
    if difficulty and difficulty not in _DIFFICULTIES:
        raise ApiError("Độ khó phải là easy, medium hoặc hard.")
    # Trả về dict khớp tên cột bảng questions (topic cắt 100 ký tự theo độ dài cột)
    return {
        "content": content,
        **options,
        "correct_answer": answer,
        "order_index": max(0, iv(body, "order_index")),
        "topic": sv(body, "topic")[:100] or None,
        "difficulty": difficulty,
        "explanation": sv(body, "explanation") or None,
    }


def _question_access(db: Session, user: dict | None, course_id: int) -> bool:
    """Kiểm tra quyền xem câu hỏi; trả về True nếu được xem cả đáp án (chủ khóa / admin)."""
    if not user:
        raise ApiError("Vui lòng đăng nhập để làm bài.", 401)
    if not can_access_course(db, user, course_id):
        raise ApiError("Bạn cần đăng ký khóa học để làm bài kiểm tra này.", 403)
    is_owner = owns_course(db, user, course_id)
    # Giảng viên không học khóa của người khác -> không làm / xem đề quiz của khóa đó
    if user["role"] == "teacher" and not is_owner:
        raise ApiError("Giảng viên chỉ làm thử được quiz của khóa học mình phụ trách.", 403)
    return is_owner


# Bỏ đáp án đúng + giải thích khỏi câu hỏi (chống lộ đáp án khi học viên làm bài)
def _strip_answers(q: dict) -> dict:
    return {k: v for k, v in q.items() if k not in _ANSWER_FIELDS}


# GET /api/quizzes/questions — ?id=X: 1 câu hỏi; ?quiz_id=X: toàn bộ câu hỏi của quiz
@router.get("/questions")
def index_questions(
    id: int | None = Query(default=None),
    quiz_id: int | None = Query(default=None),
    user: dict | None = Depends(get_viewer),
    db: Session = Depends(get_db),
):
    # Lấy 1 câu hỏi; chỉ chủ khóa/admin mới thấy đáp án
    if id:
        q = q_one(db, "SELECT * FROM questions WHERE id = :id", id=id)
        if not q:
            raise ApiError("Không tìm thấy câu hỏi.", 404)
        with_answers = _question_access(db, user, course_id_of(db, "questions", id))
        return ok(data=q if with_answers else _strip_answers(q))
    # Lấy toàn bộ câu hỏi của quiz theo thứ tự; học viên nhận bản đã ẩn đáp án
    if quiz_id:
        quiz = q_one(db, "SELECT * FROM quizzes WHERE id = :id", id=quiz_id)
        if not quiz:
            return ok(data=[])
        with_answers = _question_access(db, user, quiz["course_id"])
        rows = q_all(
            db,
            "SELECT * FROM questions WHERE quiz_id = :q ORDER BY order_index ASC, id ASC",
            q=quiz_id,
        )
        if with_answers:
            return ok(data=rows)
        # Học viên: đề có giới hạn thời gian / số lượt -> mở đề là bắt đầu (hoặc tiếp tục) 1 lượt làm;
        # đề ôn tập không giới hạn thì làm tự do, không cần token
        extra = _start_or_resume(db, user, quiz) if _is_tracked(quiz) and rows else {}
        return ok(data=[_strip_answers(r) for r in rows], **extra)
    raise ApiError("Cần truyền quiz_id hoặc id.")


# POST /api/quizzes/questions — thêm câu hỏi vào quiz
@router.post("/questions")
def create_question(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    quiz_id = iv(body, "quiz_id")
    if not quiz_id:
        raise ApiError("Dữ liệu không hợp lệ.")
    # Kiểm tra dữ liệu câu hỏi, rồi kiểm tra quyền sở hữu khóa chứa quiz
    fields = _question_fields(body)
    assert_owns_course(db, user, course_id_of(db, "quizzes", quiz_id))
    execute(
        db,
        "INSERT INTO questions (quiz_id, content, option_a, option_b, option_c, option_d, "
        "correct_answer, order_index, topic, difficulty, explanation) "
        "VALUES (:q, :content, :option_a, :option_b, :option_c, :option_d, "
        ":correct_answer, :order_index, :topic, :difficulty, :explanation)",
        q=quiz_id,
        **fields,
    )
    return ok("Thêm câu hỏi thành công")


# PUT /api/quizzes/questions — sửa câu hỏi
@router.put("/questions")
def update_question(
    body: dict = Body(default={}),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    qid = iv(body, "id")
    if not qid:
        raise ApiError("Dữ liệu không hợp lệ.")
    fields = _question_fields(body)
    # Client cũ không gửi topic/difficulty/explanation -> giữ nguyên giá trị hiện có (vd câu do AI sinh).
    for key in ("topic", "difficulty", "explanation"):
        if key not in body:
            fields.pop(key)
    assert_owns_course(db, user, course_id_of(db, "questions", qid))
    # Ghép câu UPDATE động theo các trường cần cập nhật
    sets = ", ".join(f"{k} = :{k}" for k in fields)
    execute(db, f"UPDATE questions SET {sets} WHERE id = :id", id=qid, **fields)
    return ok("Cập nhật thành công")


# DELETE /api/quizzes/questions?id=X — xóa câu hỏi chưa có ai trả lời
@router.delete("/questions")
def delete_question(
    id: int = Query(default=0),
    user=Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    if not id:
        raise ApiError("Thiếu ID.")
    assert_owns_course(db, user, course_id_of(db, "questions", id))
    # Câu đã có học viên trả lời thì giữ lại để không mất dữ liệu phân tích theo chủ đề
    answered = q_scalar(db, "SELECT COUNT(*) FROM result_answers WHERE question_id = :id", id=id) or 0
    if answered:
        raise ApiError(
            f"Câu hỏi đã được trả lời {answered} lần nên không thể xóa (sẽ mất dữ liệu phân tích học tập).",
            409,
        )
    execute(db, "DELETE FROM questions WHERE id = :id", id=id)
    return ok("Xóa thành công")


# ── SUBMIT ─────────────────────────────────────────────────────────────────

# POST /api/quizzes/submit — học viên nộp bài: chấm điểm, lưu kết quả, trả đáp án đúng
@router.post("/submit")
def submit(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # answers dạng {"<question_id>": "A"|"B"|"C"|"D"}; sai kiểu thì coi như bỏ trống hết
    quiz_id = iv(body, "quiz_id")
    answers = body.get("answers") or {}
    if not isinstance(answers, dict):
        answers = {}

    # Lấy quiz và danh sách câu hỏi theo thứ tự hiển thị
    quiz = q_one(
        db,
        "SELECT q.*, c.title AS course_title FROM quizzes q "
        "JOIN courses c ON q.course_id = c.id WHERE q.id = :id",
        id=quiz_id,
    )
    questions = q_all(
        db,
        "SELECT * FROM questions WHERE quiz_id = :q ORDER BY order_index ASC, id ASC",
        q=quiz_id,
    )
    if not quiz or not questions:
        raise ApiError("Quiz không tồn tại hoặc chưa có câu hỏi.", 404)
    # Kết quả nộp bài trả về đáp án đúng -> chỉ học viên đã ghi danh hoặc chủ khóa / admin mới được nộp
    is_owner = _question_access(db, user, quiz["course_id"])
    # Chủ khóa/admin làm thử không bị giới hạn; học viên làm đề có ràng buộc phải nộp đúng lượt đang làm
    attempt = None
    result_id = None
    if not is_owner and _is_tracked(quiz):
        attempt = _check_attempt_token(db, user["id"], quiz, sv(body, "attempt_token"))

    # Chấm từng câu: so đáp án học viên chọn với correct_answer, cộng 1 điểm mỗi câu đúng
    score = 0
    total = len(questions)
    details = []
    for q in questions:
        # Key trong answers có thể là chuỗi hoặc số tùy client -> thử cả hai
        raw = answers.get(str(q["id"]))
        if raw is None:
            raw = answers.get(q["id"], "")
        chosen = str(raw or "").upper()
        correct = q["correct_answer"]
        is_right = chosen == correct
        if is_right:
            score += 1
        # Chi tiết từng câu để trang kết quả hiển thị đúng/sai + đáp án đúng
        details.append(
            {
                "question_id": q["id"],
                "content": q["content"],
                "option_a": q["option_a"],
                "option_b": q["option_b"],
                "option_c": q["option_c"],
                "option_d": q["option_d"],
                "chosen": chosen,
                "correct_answer": correct,
                "explanation": q["explanation"],
                "is_right": is_right,
            }
        )

    # Chủ khóa / admin làm thử: chỉ chấm và trả kết quả, KHÔNG lưu
    # (không tính vào thống kê, không khóa việc xóa quiz / câu hỏi)
    if not is_owner:
        # Lưu kết quả tổng của lượt làm bài, kèm điểm đạt của quiz lúc nộp
        # (giảng viên đổi điểm đạt về sau thì lượt cũ vẫn giữ nguyên trạng thái đạt / chưa đạt)
        res = execute(
            db,
            "INSERT INTO results (user_id, quiz_id, score, total, passing_score) VALUES (:u, :q, :s, :t, :ps)",
            u=user["id"],
            q=quiz_id,
            s=score,
            t=total,
            ps=quiz["passing_score"],
        )
        result_id = res.lastrowid
        # Lưu chi tiết từng câu -> phục vụ phân tích topic mạnh/yếu (Phase 4/5)
        if result_id:
            for d in details:
                execute(
                    db,
                    "INSERT INTO result_answers (result_id, question_id, chosen, is_correct) "
                    "VALUES (:r, :q, :c, :ic)",
                    r=result_id,
                    q=d["question_id"],
                    c=(d["chosen"] or None) if len(d["chosen"] or "") <= 1 else None,
                    ic=1 if d["is_right"] else 0,
                )
        # Chốt lượt làm của đề có ràng buộc, gắn với kết quả vừa lưu
        if attempt:
            _close_attempt(db, attempt["id"], result_id)

    return ok(
        result_id=result_id,
        **_result_payload(db, user, quiz, details, score, total, is_owner, quiz["passing_score"]),
    )


# Dựng dữ liệu kết quả 1 lượt làm (dùng cho cả lúc nộp bài và lúc xem lại lịch sử)
def _result_payload(
    db: Session, user: dict, quiz: dict, details: list[dict], score: int, total: int,
    is_owner: bool, passing_score: int | None,
) -> dict:
    # Đề giới hạn số lượt: chỉ trả đáp án đúng + giải thích khi đã dùng hết lượt và không còn lượt đang làm dở
    # (tránh học viên xem lại bài cũ để chép đáp án cho lượt đang làm). Đề không giới hạn / chủ khóa: luôn trả.
    limit = quiz["max_attempts"]
    used = _attempts_used(db, user["id"], quiz["id"])
    reveal = is_owner or not limit or (used >= limit and not _open_attempt(db, user["id"], quiz))
    if not reveal:
        for d in details:
            d["correct_answer"] = None
            d["explanation"] = None
    percent = _percent(score, total)
    return {
        "quiz": quiz,
        "score": score,
        "total": total,
        "percent": percent,
        # passed = None khi quiz không đặt điểm đạt
        "passed": _passed(percent, passing_score),
        "details": details,
        "answers_revealed": reveal,
        "attempts_used": used,
        "attempts_left": (max(0, limit - used) if limit and not is_owner else None),
    }


# ── LỊCH SỬ LÀM BÀI ─────────────────────────────────────────────────────────

# GET /api/quizzes/results — ?id=X: xem lại 1 lượt đã nộp; không có id: lịch sử làm bài của học viên
# (?quiz_id=X để lọc 1 quiz). Mỗi lượt có số thứ tự và cờ "được tính điểm" theo cách tính của quiz.
@router.get("/results")
def results(
    id: int | None = Query(default=None),
    quiz_id: int | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if id:
        return ok(**_result_detail(db, user, id))
    where, params = "r.user_id = :u", {"u": user["id"]}
    if quiz_id:
        where, params = where + " AND r.quiz_id = :q", {**params, "q": quiz_id}
    rows = q_all(
        db,
        "SELECT r.id, r.quiz_id, r.score, r.total, r.passing_score, r.submit_time, "
        "q.title AS quiz_title, q.grading_method, q.max_attempts, q.chapter_id, q.review_lesson_id, "
        "c.title AS course_title "
        "FROM results r JOIN quizzes q ON q.id = r.quiz_id JOIN courses c ON c.id = q.course_id "
        f"WHERE {where} ORDER BY r.id ASC",
        **params,
    )
    # Đánh số lượt + đánh dấu lượt được tính điểm theo từng quiz
    by_quiz: dict[int, list[dict]] = {}
    for r in rows:
        by_quiz.setdefault(r["quiz_id"], []).append(r)
    for quiz_rows in by_quiz.values():
        _, _, counted_id = _graded(quiz_rows[0]["grading_method"], quiz_rows)
        for n, r in enumerate(quiz_rows, start=1):
            r["attempt_no"] = n
            r["percent"] = _percent(r["score"], r["total"])
            r["passed"] = _passed(r["percent"], r["passing_score"])
            # Trung bình: mọi lượt đều được tính; cách khác: chỉ 1 lượt
            r["counted"] = counted_id == r["id"] or r["grading_method"] == "average"
    # Mới nhất lên đầu
    return ok(data=list(reversed(rows)))


# Chi tiết 1 lượt đã nộp: chính học viên đó, hoặc chủ khóa / admin
def _result_detail(db: Session, user: dict, result_id: int) -> dict:
    r = q_one(db, "SELECT * FROM results WHERE id = :id", id=result_id)
    if not r:
        raise ApiError("Không tìm thấy bài làm.", 404)
    quiz = q_one(
        db,
        "SELECT q.*, c.title AS course_title FROM quizzes q "
        "JOIN courses c ON q.course_id = c.id WHERE q.id = :id",
        id=r["quiz_id"],
    )
    is_owner = owns_course(db, user, quiz["course_id"])
    if r["user_id"] != user["id"] and not is_owner:
        raise ApiError("Bạn không có quyền xem bài làm này.", 403)
    # Đáp án đã chọn lưu ở result_answers; nội dung câu hỏi lấy từ bảng questions
    answers = q_all(
        db,
        "SELECT ra.chosen, ra.is_correct, q.id AS question_id, q.content, q.option_a, q.option_b, "
        "q.option_c, q.option_d, q.correct_answer, q.explanation "
        "FROM result_answers ra JOIN questions q ON q.id = ra.question_id "
        "WHERE ra.result_id = :r ORDER BY q.order_index ASC, q.id ASC",
        r=result_id,
    )
    details = [
        {
            "question_id": a["question_id"],
            "content": a["content"],
            "option_a": a["option_a"],
            "option_b": a["option_b"],
            "option_c": a["option_c"],
            "option_d": a["option_d"],
            "chosen": a["chosen"] or "",
            "correct_answer": a["correct_answer"],
            "explanation": a["explanation"],
            # Giữ kết quả chấm lúc nộp (đáp án sửa về sau không đổi điểm lượt cũ)
            "is_right": bool(a["is_correct"]),
        }
        for a in answers
    ]
    # Xem lại với tư cách học viên làm bài (chủ khóa xem bài của học viên thì luôn thấy đáp án)
    owner_view = is_owner and r["user_id"] != user["id"]
    student = {"id": r["user_id"]}
    payload = _result_payload(db, student, quiz, details, r["score"], r["total"], owner_view, r["passing_score"])
    return {**payload, "result_id": r["id"], "submit_time": r["submit_time"]}


# ── NHẬP BỘ ĐỀ TỪ FILE WORD ───────────────────────────────────────────────────

# Giới hạn kích thước file Word nhập đề
_WORD_MAX_BYTES = 5 * 1024 * 1024


# Lưu ảnh trong câu hỏi ra uploads/images/quiz (phục vụ công khai qua /uploads/images); tên file = mã băm
# nội dung -> cùng 1 ảnh nhập nhiều lần chỉ lưu 1 file. Trả URL tương đối để chạy được cả dev lẫn Docker.
def _save_quiz_image(blob: bytes, ext: str) -> str:
    folder = os.path.join(settings.upload_dir, "images", "quiz")
    os.makedirs(folder, exist_ok=True)
    name = f"{hashlib.sha1(blob).hexdigest()[:24]}.{ext}"
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(blob)
    return f"/uploads/images/quiz/{name}"


# POST /api/quizzes/import-word — đọc file .docx thành bản nháp câu hỏi (CHƯA lưu).
# Giảng viên xem / sửa bản nháp rồi lưu qua /api/ai/quiz/approve với source = "word".
@router.post("/import-word")
async def import_word(
    file: UploadFile = File(...),
    user=Depends(require_roles("admin", "teacher")),
):
    if not (file.filename or "").lower().endswith(".docx"):
        raise ApiError("Chỉ nhận file Word .docx (file .doc cũ: mở bằng Word rồi Lưu thành .docx).")
    data = await file.read(_WORD_MAX_BYTES + 1)
    if len(data) > _WORD_MAX_BYTES:
        raise ApiError("File quá lớn (tối đa 5MB).")
    try:
        result = parse_docx(data, save_image=_save_quiz_image)
    except WordQuizError as e:
        raise ApiError(str(e))
    if not result["questions"] and not result["errors"]:
        raise ApiError(
            "Không tìm thấy câu hỏi nào. Mỗi câu cần bắt đầu bằng \"Câu 1:\", \"Câu 2:\"... — "
            "tải file mẫu để xem định dạng.",
            422,
        )
    return ok(data=result)


# GET /api/quizzes/import-word/template — file Word mẫu để giảng viên điền đề
@router.get("/import-word/template")
def import_word_template(user=Depends(require_roles("admin", "teacher"))):
    return Response(
        content=build_template(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="mau-de-trac-nghiem.docx"'},
    )
