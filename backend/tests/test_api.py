r"""PHASE 11 — pytest cho FastAPI backend (chạy in-process, dùng DB studyonline_db).

    cd backend
    .\.venv\Scripts\python.exe -m pytest tests/test_api.py -q

Các test có ghi dữ liệu đều tự dọn. AI dùng chế độ offline (stub/heuristic) nên kết
quả tất định — không cần LLM_API_KEY.
"""
import os
import sys
import time

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402

client = TestClient(app)

ADMIN = ("admin@gmail.com", "123456")
TEACHER = ("an.nguyen@studyonline.vn", "123456")
STUDENT = ("em.hoang@gmail.com", "123456")


def _token(email, pw):
    r = client.post("/api/auth/login", json={"email": email, "password": pw})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


@pytest.fixture(scope="module")
def tokens():
    return {
        "admin": _token(*ADMIN),
        "teacher": _token(*TEACHER),
        "student": _token(*STUDENT),
    }


# ── Auth ───────────────────────────────────────────────────────────────────

def test_health():
    assert client.get("/api/health").json() == {"success": True, "status": "ok"}


def test_login_ok_and_envelope():
    r = client.post("/api/auth/login", json=dict(zip(("email", "password"), STUDENT)))
    b = r.json()
    assert r.status_code == 200 and b["success"] is True
    assert "token" in b and b["user"]["role"] == "student"


def test_login_bad_password():
    r = client.post("/api/auth/login", json={"email": STUDENT[0], "password": "sai"})
    assert r.status_code == 401
    assert r.json() == {"success": False, "message": "Email hoặc mật khẩu không chính xác."}


def test_me_requires_token():
    assert client.get("/api/auth/me").status_code == 401


def test_me_ok(tokens):
    b = client.get("/api/auth/me", headers=_h(tokens["teacher"])).json()
    assert b["success"] and b["user"]["email"] == TEACHER[0]


def test_register_and_change_password_and_cleanup(tokens):
    email = f"pytest_{int(time.time())}@t.local"
    r = client.post("/api/auth/register", json={
        "fullname": "Pytest User", "email": email,
        "password": "123456", "confirm_password": "123456",
    })
    assert r.json()["success"]
    tok = _token(email, "123456")
    uid = client.get("/api/auth/me", headers=_h(tok)).json()["user"]["id"]

    assert client.post("/api/auth/change-password", headers=_h(tok),
                       json={"old_password": "123456", "new_password": "1234567"}).json()["success"]
    assert client.post("/api/auth/change-password", headers=_h(tok),
                       json={"old_password": "wrong", "new_password": "xxxxxx"}).status_code == 400

    client.request("DELETE", f"/api/users?id={uid}", headers=_h(tokens["admin"]))


# ── RBAC ───────────────────────────────────────────────────────────────────

def test_student_cannot_list_users(tokens):
    assert client.get("/api/users", headers=_h(tokens["student"])).status_code == 403


def test_student_cannot_create_course(tokens):
    r = client.post("/api/courses", headers=_h(tokens["student"]), json={"title": "x"})
    assert r.status_code == 403


# ── LMS CRUD (một luồng đầy đủ, tự dọn) ────────────────────────────────────

@pytest.fixture()
def course(tokens):
    r = client.post("/api/courses", headers=_h(tokens["teacher"]),
                    json={"title": "PYTEST Course", "description": "d", "thumbnail": ""})
    cid = int(r.json()["id"])
    yield cid
    client.request("DELETE", f"/api/courses?id={cid}", headers=_h(tokens["teacher"]))
    # API từ chối xóa khóa còn học viên ghi danh (quy tắc an toàn dữ liệu) -> dọn thẳng trong DB để test
    # không để lại khóa "PYTEST Course" cùng kết quả làm bài trong lịch sử của học viên mẫu
    from sqlalchemy import text

    from app.core.database import SessionLocal

    with SessionLocal() as db:
        db.execute(text("DELETE FROM courses WHERE id = :id AND title LIKE 'PYTEST%'"), {"id": cid})
        db.commit()


def test_course_crud(tokens, course):
    got = client.get(f"/api/courses?id={course}").json()
    assert got["data"]["title"] == "PYTEST Course"
    client.put("/api/courses", headers=_h(tokens["teacher"]),
               json={"id": course, "title": "PYTEST v2", "description": "d2"})
    assert client.get(f"/api/courses?id={course}").json()["data"]["title"] == "PYTEST v2"


def test_full_learning_flow(tokens, course):
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    ch = int(client.post("/api/chapters", headers=T,
                         json={"course_id": course, "chapter_name": "C1"}).json()["id"])
    ls = int(client.post("/api/lessons", headers=T,
                         json={"chapter_id": ch, "title": "L1", "description": "",
                               "video_url": "", "document_url": ""}).json()["id"])
    qz = int(client.post("/api/quizzes", headers=T,
                         json={"course_id": course, "title": "Q1", "description": ""}).json()["id"])
    client.post("/api/quizzes/questions", headers=T, json={
        "quiz_id": qz, "content": "2+2=?", "option_a": "3", "option_b": "4",
        "option_c": "5", "option_d": "6", "correct_answer": "B", "order_index": 0,
    })
    # Chưa ghi danh thì không xem được câu hỏi; chủ khóa xem được cả đáp án.
    assert client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).status_code == 403
    teacher_view = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=T).json()["data"][0]
    assert teacher_view["correct_answer"] == "B"
    qid = teacher_view["id"]

    assert client.post("/api/enrollments", headers=S, json={"course_id": course}).json()["success"]
    assert client.post("/api/enrollments", headers=S, json={"course_id": course}).status_code == 409
    ids = client.get("/api/enrollments?ids_only=1", headers=S).json()["data"]
    assert course in ids

    student_view = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).json()["data"][0]
    assert "correct_answer" not in student_view

    client.post("/api/progress", headers=S,
                json={"lesson_id": ls, "watched_sec": 60, "is_completed": 1})
    assert ls in client.get(f"/api/progress?course_id={course}", headers=S).json()["data"]

    sub = client.post("/api/quizzes/submit", headers=S,
                      json={"quiz_id": qz, "answers": {str(qid): "B"}}).json()
    assert sub["score"] == 1 and sub["total"] == 1 and sub["percent"] == 100

    # Đã có lượt làm bài -> không xóa được quiz / câu hỏi (giữ điểm & dữ liệu phân tích).
    assert client.request("DELETE", f"/api/quizzes?id={qz}", headers=T).status_code == 409
    assert client.request("DELETE", f"/api/quizzes/questions?id={qid}", headers=T).status_code == 409

    # Học viên thấy quiz của khóa đã ghi danh khi không truyền course_id.
    assert qz in [q["id"] for q in client.get("/api/quizzes", headers=S).json()["data"]]

    client.request("DELETE", f"/api/enrollments?course_id={course}", headers=S)


def test_chapter_review_questions(tokens, course):
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    ch = int(client.post("/api/chapters", headers=T,
                         json={"course_id": course, "chapter_name": "Chương ôn"}).json()["id"])
    client.post("/api/lessons", headers=T,
                json={"chapter_id": ch, "title": "Biến trong Python",
                      "description": "Biến là tên gọi dùng để lưu trữ giá trị trong bộ nhớ.",
                      "video_url": "", "document_url": ""})
    # Chưa có bộ ôn tập; học viên không được tạo
    row = client.get(f"/api/chapters?id={ch}").json()["data"]
    assert row["review_quiz_id"] is None and row["review_question_count"] == 0
    assert client.post("/api/chapters/review", headers=S, json={"chapter_id": ch}).status_code == 403

    # Mở 2 lần vẫn ra cùng 1 bộ ôn tập
    rq = client.post("/api/chapters/review", headers=T, json={"chapter_id": ch}).json()["data"]["quiz_id"]
    assert client.post("/api/chapters/review", headers=T, json={"chapter_id": ch}).json()["data"]["quiz_id"] == rq
    quiz = client.get(f"/api/quizzes?id={rq}").json()["data"]
    assert quiz["chapter_id"] == ch and quiz["chapter_name"] == "Chương ôn"

    # Thêm câu thủ công + câu AI duyệt vào cùng bộ, thứ tự nối tiếp
    client.post("/api/quizzes/questions", headers=T, json={
        "quiz_id": rq, "content": "1+1=?", "option_a": "1", "option_b": "2",
        "option_c": "3", "option_d": "4", "correct_answer": "B"})
    r = client.post("/api/ai/quiz/approve", headers=T, json={
        "course_id": course, "chapter_id": ch, "questions": [{
            "question": "2+2=?", "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
            "correct_answer": "B"}]}).json()
    assert r["data"]["quiz_id"] == rq
    qs = client.get(f"/api/quizzes/questions?quiz_id={rq}", headers=T).json()["data"]
    assert [q["content"] for q in qs] == ["1+1=?", "2+2=?"]
    assert client.get(f"/api/chapters?course_id={course}").json()["data"][0]["review_question_count"] == 2

    # Sinh bằng AI theo chương (offline heuristic dùng mô tả bài học làm ngữ liệu)
    g = client.post("/api/ai/generate-quiz", headers=T,
                    json={"course_id": course, "chapter_id": ch, "number_of_questions": 3})
    assert g.status_code in (200, 422)
    if g.status_code == 200:
        assert g.json()["data"]["meta"]["topic"] == "Chương ôn"

    # Bộ ôn tập không chuyển được sang khóa khác
    assert client.put("/api/quizzes", headers=T, json={
        "id": rq, "course_id": 1, "title": "x"}).status_code in (400, 403)

    # Xóa chương chưa có lượt làm -> bộ ôn tập bị xóa theo
    client.request("DELETE", f"/api/chapters?id={ch}", headers=T)
    assert client.get(f"/api/quizzes?id={rq}").status_code == 404


def test_lesson_review_and_quiz_settings(tokens, course):
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    ch = int(client.post("/api/chapters", headers=T,
                         json={"course_id": course, "chapter_name": "C"}).json()["id"])
    ls = int(client.post("/api/lessons", headers=T,
                         json={"chapter_id": ch, "title": "Vòng lặp for",
                               "description": "Vòng lặp for dùng để lặp qua các phần tử của một dãy.",
                               "video_url": "", "document_url": ""}).json()["id"])
    # Chưa có bộ ôn tập; học viên không được tạo; mở 2 lần ra cùng 1 bộ
    assert client.get(f"/api/lessons?chapter_id={ch}", headers=T).json()["data"][0]["review_quiz_id"] is None
    assert client.post("/api/lessons/review", headers=S, json={"lesson_id": ls}).status_code == 403
    rq = client.post("/api/lessons/review", headers=T, json={"lesson_id": ls}).json()["data"]["quiz_id"]
    assert client.post("/api/lessons/review", headers=T, json={"lesson_id": ls}).json()["data"]["quiz_id"] == rq
    quiz = client.get(f"/api/quizzes?id={rq}").json()["data"]
    assert quiz["review_lesson_id"] == ls and quiz["review_lesson_title"] == "Vòng lặp for"

    # Câu thủ công + câu AI duyệt vào cùng bộ ôn tập của bài
    client.post("/api/quizzes/questions", headers=T, json={
        "quiz_id": rq, "content": "for dùng để?", "option_a": "rẽ nhánh", "option_b": "lặp",
        "option_c": "", "option_d": "", "correct_answer": "B"})
    r = client.post("/api/ai/quiz/approve", headers=T, json={
        "course_id": course, "review_lesson_id": ls, "questions": [{
            "question": "range(3) sinh mấy số?", "options": {"A": "2", "B": "3", "C": "4", "D": "5"},
            "correct_answer": "B"}]}).json()
    assert r["data"]["quiz_id"] == rq
    assert client.get(f"/api/lessons?id={ls}", headers=T).json()["data"]["review_question_count"] == 2
    # Duyệt thành quiz mới kèm cài đặt làm bài; cài đặt sai phạm vi bị từ chối
    one = [{"question": "1+1?", "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "correct_answer": "B",
            "verify": {"answer": "B", "reason": "x"}, "plan_key": "single"}]
    assert client.post("/api/ai/quiz/approve", headers=T, json={
        "course_id": course, "title": "AI", "questions": one, "passing_score": 101}).status_code == 400
    nq = client.post("/api/ai/quiz/approve", headers=T, json={
        "course_id": course, "title": "AI cuối khóa", "questions": one,
        "duration": 45, "passing_score": 70, "max_attempts": 1}).json()["data"]["quiz_id"]
    got = client.get(f"/api/quizzes?id={nq}").json()["data"]
    assert (got["duration"], got["passing_score"], got["max_attempts"], got["source"]) == (45, 70, 1, "ai")
    # Sinh bằng AI theo bài (offline heuristic dùng mô tả bài học làm ngữ liệu)
    g = client.post("/api/ai/generate-quiz", headers=T,
                    json={"course_id": course, "lesson_id": ls, "number_of_questions": 2})
    assert g.status_code in (200, 422)
    # Phân bổ độ khó: sai phạm vi bị từ chối; hợp lệ thì mỗi câu gắn đúng mức của lô sinh ra nó
    bad = {"course_id": course, "lesson_id": ls, "difficulty_mix": {"easy": 25}}
    assert client.post("/api/ai/generate-quiz", headers=T, json=bad).status_code == 400
    empty = {"course_id": course, "lesson_id": ls, "difficulty_mix": {"easy": 0, "medium": 0, "hard": 0}}
    assert client.post("/api/ai/generate-quiz", headers=T, json=empty).status_code == 422
    g = client.post("/api/ai/generate-quiz", headers=T, json={
        "course_id": course, "lesson_id": ls, "difficulty_mix": {"easy": 1, "medium": 0, "hard": 1}})
    if g.status_code == 200:
        meta = g.json()["data"]["meta"]
        assert meta["distribution_requested"] == {"easy": 1, "hard": 1}
        levels = [q["difficulty"] for q in g.json()["data"]["questions"]]
        assert set(levels) <= {"easy", "hard"} and len(levels) == meta["returned"]

    # Cài đặt làm bài: sai phạm vi bị từ chối; giới hạn 10 phút, đạt 50%, 1 lượt
    base = {"id": rq, "course_id": course, "title": "Ôn tập bài"}
    assert client.put("/api/quizzes", headers=T, json={**base, "passing_score": 150}).status_code == 400
    client.put("/api/quizzes", headers=T, json={**base, "duration": 10, "passing_score": 50, "max_attempts": 1})

    client.post("/api/enrollments", headers=S, json={"course_id": course})
    got = client.get(f"/api/quizzes/questions?quiz_id={rq}", headers=S).json()
    assert got["time_limit_sec"] == 600 and got["attempt_token"]
    answers = {str(q["id"]): "B" for q in got["data"]}
    # Không có / sửa token -> từ chối; token hợp lệ -> chấm, đạt
    assert client.post("/api/quizzes/submit", headers=S, json={"quiz_id": rq, "answers": answers}).status_code == 400
    aid, sig = got["attempt_token"].split(".")
    forged = f"{int(aid) + 1}.{sig}"
    assert client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": rq, "answers": answers, "attempt_token": forged}).status_code == 400
    sub = client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": rq, "answers": answers, "attempt_token": got["attempt_token"]}).json()
    assert sub["percent"] == 100 and sub["passed"] is True
    # Hết lượt: không mở lại đề, không nộp tiếp; chủ khóa vẫn xem đủ đề
    assert client.get(f"/api/quizzes/questions?quiz_id={rq}", headers=S).status_code == 403
    assert client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": rq, "answers": answers, "attempt_token": got["attempt_token"]}).status_code == 403
    assert len(client.get(f"/api/quizzes/questions?quiz_id={rq}", headers=T).json()["data"]) == 2
    client.request("DELETE", f"/api/enrollments?course_id={course}", headers=S)

    # Xóa bài: bộ ôn tập đã có lượt làm được giữ lại (thành quiz thường)
    client.request("DELETE", f"/api/lessons?id={ls}", headers=T)
    assert client.get(f"/api/quizzes?id={rq}").json()["data"]["review_lesson_id"] is None


def test_answers_hidden_until_last_attempt_and_fair_analytics(tokens, course):
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    q = {"option_a": "sai", "option_b": "đúng", "option_c": "x", "option_d": "y", "correct_answer": "B"}
    # Bài chính thức cho làm 2 lần
    qz = int(client.post("/api/quizzes", headers=T, json={
        "course_id": course, "title": "Chính thức", "max_attempts": 2}).json()["id"])
    client.post("/api/quizzes/questions", headers=T, json={"quiz_id": qz, "content": "Câu CT", "topic": "Chủ đề CT", **q})
    # Bộ ôn tập của chương (làm lại không giới hạn)
    ch = int(client.post("/api/chapters", headers=T, json={"course_id": course, "chapter_name": "C"}).json()["id"])
    rq = client.post("/api/chapters/review", headers=T, json={"chapter_id": ch}).json()["data"]["quiz_id"]
    client.post("/api/quizzes/questions", headers=T, json={"quiz_id": rq, "content": "Câu ÔT", "topic": "Chủ đề ÔT", **q})
    client.post("/api/enrollments", headers=S, json={"course_id": course})
    open1 = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).json()
    qid = open1["data"][0]["id"]
    rqid = client.get(f"/api/quizzes/questions?quiz_id={rq}", headers=S).json()["data"][0]["id"]

    # Lượt 1/2: có đúng/sai nhưng KHÔNG có đáp án đúng; lượt 2/2 (cuối): có đáp án
    s1 = client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": qz, "answers": {str(qid): "A"}, "attempt_token": open1["attempt_token"]}).json()
    assert s1["answers_revealed"] is False and s1["attempts_left"] == 1
    assert s1["details"][0]["correct_answer"] is None and s1["details"][0]["is_right"] is False
    open2 = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).json()
    s2 = client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": qz, "answers": {str(qid): "B"}, "attempt_token": open2["attempt_token"]}).json()
    assert s2["answers_revealed"] is True and s2["attempts_left"] == 0 and s2["details"][0]["correct_answer"] == "B"
    # Chủ khóa làm thử luôn thấy đáp án
    assert client.post("/api/quizzes/submit", headers=T, json={
        "quiz_id": qz, "answers": {}}).json()["details"][0]["correct_answer"] == "B"
    # Ôn tập không giới hạn lượt: luôn thấy đáp án. Làm sai 2 lần rồi đúng 1 lần
    for ans in ("A", "A", "B"):
        r = client.post("/api/quizzes/submit", headers=S, json={"quiz_id": rq, "answers": {str(rqid): ans}}).json()
        assert r["answers_revealed"] is True and r["details"][0]["correct_answer"] == "B"

    # Điểm TB / số lượt chỉ tính bài chính thức: (0% + 100%) / 2 = 50%, 2 lượt (không tính 3 lượt ôn tập)
    # Điểm được tính theo cách tính của quiz (mặc định lượt cao nhất); 2 lượt 0% và 100%
    ov = client.get(f"/api/analytics/overview?course_id={course}", headers=S).json()["data"]
    assert ov["avg_quiz_score"] == 100.0 and ov["quiz_attempts"] == 2
    for method, expect in (("average", 50.0), ("first", 0.0), ("latest", 100.0)):
        client.put("/api/quizzes", headers=T, json={
            "id": qz, "course_id": course, "title": "Chính thức", "max_attempts": 2, "grading_method": method})
        ov = client.get(f"/api/analytics/overview?course_id={course}", headers=S).json()["data"]
        assert ov["avg_quiz_score"] == expect, method
    assert client.put("/api/quizzes", headers=T, json={
        "id": qz, "course_id": course, "title": "Chính thức", "grading_method": "tệ nhất"}).status_code == 400
    # Lịch sử: 2 lượt, mới nhất trước, lượt cuối được tính (latest); xem lại lượt 1 thấy đáp án (đã hết lượt)
    hist = client.get(f"/api/quizzes/results?quiz_id={qz}", headers=S).json()["data"]
    assert [h["attempt_no"] for h in hist] == [2, 1] and [h["counted"] for h in hist] == [True, False]
    first = client.get(f"/api/quizzes/results?id={hist[1]['id']}", headers=S).json()
    assert first["percent"] == 0 and first["answers_revealed"] and first["details"][0]["chosen"] == "A"
    # Người khác không xem được bài làm của học viên; chủ khóa thì xem được
    other = _h(_token("binh.tran@studyonline.vn", "123456"))
    assert client.get(f"/api/quizzes/results?id={hist[1]['id']}", headers=other).status_code == 403
    assert client.get(f"/api/quizzes/results?id={hist[1]['id']}", headers=T).json()["score"] == 0
    # Danh sách quiz của học viên kèm tình trạng làm bài
    st = [q for q in client.get("/api/quizzes", headers=S).json()["data"] if q["id"] == qz][0]["my_status"]
    assert st["submitted"] == 2 and st["graded_percent"] == 100 and st["attempts_left"] == 0
    # Chủ đề: bài chính thức tính mọi lượt (1/2 đúng), ôn tập chỉ tính lượt gần nhất (đúng)
    tp = {t["topic"]: t for t in client.get(f"/api/analytics/topics?course_id={course}", headers=S).json()["data"]}
    assert (tp["Chủ đề CT"]["answered"], tp["Chủ đề CT"]["correct"]) == (2, 1)
    assert (tp["Chủ đề ÔT"]["answered"], tp["Chủ đề ÔT"]["correct"]) == (1, 1)
    client.request("DELETE", f"/api/enrollments?course_id={course}", headers=S)


def test_paid_course_cannot_be_bypassed(tokens, course):
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    client.put("/api/courses", headers=T, json={"id": course, "title": "PYTEST Paid", "description": "d",
                                                  "price": 499000, "status": "published"})
    ch = int(client.post("/api/chapters", headers=T,
                         json={"course_id": course, "chapter_name": "C1"}).json()["id"])
    ls = int(client.post("/api/lessons", headers=T,
                         json={"chapter_id": ch, "title": "L1", "description": "",
                               "video_url": "v.mp4", "document_url": ""}).json()["id"])

    assert client.post("/api/enrollments", headers=S, json={"course_id": course}).status_code == 402
    # Trước đây gửi tiến độ sẽ tự ghi danh vào khóa trả phí.
    assert client.post("/api/progress", headers=S, json={"lesson_id": ls, "is_completed": 1}).status_code == 403
    assert course not in client.get("/api/enrollments?ids_only=1", headers=S).json()["data"]
    assert client.get(f"/api/lessons?id={ls}", headers=S).status_code == 403
    locked = client.get(f"/api/lessons?chapter_id={ch}", headers=S).json()["data"][0]
    assert locked["locked"] and locked["video_url"] is None


def test_lesson_media_signed_links(tokens, course):
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    up = client.post("/api/upload", headers=T, files={"file": ("d.pdf", b"%PDF-1.4 test", "application/pdf")},
                     data={"type": "document"}).json()
    ch = int(client.post("/api/chapters", headers=T, json={"course_id": course, "chapter_name": "C"}).json()["id"])
    ls = int(client.post("/api/lessons", headers=T, json={"chapter_id": ch, "title": "L", "description": "",
                                                          "video_url": "", "document_url": up["url"]}).json()["id"])
    try:
        assert client.get(up["url"].split("8080")[-1]).status_code == 404  # không còn phục vụ tĩnh
        src = client.get(f"/api/lessons?id={ls}", headers=T).json()["data"]["document_src"]
        path = src.split("8080")[-1]
        assert client.get(path).status_code == 200
        assert client.get(path[:-4] + "0000").status_code == 403
        # Học viên chưa ghi danh không lấy được link; link của người khác cũng không mở được bài khác.
        assert client.get(f"/api/lessons?id={ls}", headers=S).status_code == 403
    finally:
        from app.core.media import resolve_upload_path
        p = resolve_upload_path(up["url"])
        if p and os.path.exists(p):
            os.remove(p)


def test_admin_data_safety_rules(tokens, course):
    A, T, S = _h(tokens["admin"]), _h(tokens["teacher"]), _h(tokens["student"])
    # Khóa đã có học viên -> không xóa được (tránh mất đăng ký/thanh toán).
    assert client.post("/api/enrollments", headers=S, json={"course_id": course}).json()["success"]
    assert client.request("DELETE", f"/api/courses?id={course}", headers=T).status_code == 409
    client.request("DELETE", f"/api/enrollments?course_id={course}", headers=S)

    # Không hạ giảng viên đang phụ trách khóa học xuống học viên.
    me = client.get("/api/auth/me", headers=T).json()["user"]
    r = client.put("/api/users", headers=A, json={**me, "role": "student"})
    assert r.status_code == 409

    # Admin chuyển khóa học sang giảng viên khác; không được giao cho học viên.
    stu = client.get("/api/auth/me", headers=S).json()["user"]
    assert client.put("/api/courses", headers=A, json={"id": course, "title": "PYTEST", "teacher_id": stu["id"]}).status_code == 400

    # Tạo user: mật khẩu >= 6 ký tự, email hợp lệ.
    assert client.post("/api/users", headers=A, json={"fullname": "x", "email": "x@y.z", "password": "123",
                                                      "role": "student"}).status_code == 400
    assert client.post("/api/users", headers=A, json={"fullname": "x", "email": "not-an-email", "password": "123456",
                                                      "role": "student"}).status_code == 400


def test_question_validation_and_topic(tokens, course):
    T = _h(tokens["teacher"])
    qz = int(client.post("/api/quizzes", headers=T,
                         json={"course_id": course, "title": "Q", "description": ""}).json()["id"])
    base = {"quiz_id": qz, "content": "1+1=?", "option_a": "1", "option_b": "2", "option_c": "", "option_d": ""}
    assert client.post("/api/quizzes/questions", headers=T, json={**base, "correct_answer": "E"}).status_code == 400
    assert client.post("/api/quizzes/questions", headers=T, json={**base, "correct_answer": "C"}).status_code == 400
    r = client.post("/api/quizzes/questions", headers=T,
                    json={**base, "correct_answer": "B", "topic": "Số học", "difficulty": "easy"})
    assert r.status_code == 200
    q = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=T).json()["data"][0]
    assert q["topic"] == "Số học" and q["difficulty"] == "easy"
    # Sửa mà không gửi topic (client cũ) -> giữ nguyên chủ đề.
    client.put("/api/quizzes/questions", headers=T, json={**base, "id": q["id"], "correct_answer": "B"})
    assert client.get(f"/api/quizzes/questions?id={q['id']}", headers=T).json()["data"]["topic"] == "Số học"


def test_admin_can_reset_password(tokens):
    A = _h(tokens["admin"])
    email = f"pytest_reset_{int(time.time())}@example.com"
    client.post("/api/users", headers=A, json={"fullname": "Reset", "email": email, "password": "123456", "role": "student"})
    uid = next(u["id"] for u in client.get("/api/users", headers=A).json()["data"] if u["email"] == email)
    try:
        r = client.put("/api/users", headers=A, json={"id": uid, "fullname": "Reset", "email": email,
                                                      "role": "student", "password": "newpass1"})
        assert r.status_code == 200
        assert client.post("/api/auth/login", json={"email": email, "password": "newpass1"}).status_code == 200
        assert client.post("/api/auth/login", json={"email": email, "password": "123456"}).status_code == 401
    finally:
        client.request("DELETE", f"/api/users?id={uid}", headers=A)


def test_upload_and_user_list_restricted(tokens):
    files = {"file": ("x.png", b"\x89PNG....", "image/png")}
    assert client.post("/api/upload", headers=_h(tokens["student"]), files=files,
                       data={"type": "image"}).status_code == 403
    evil = {"file": ("evil.html", b"<script>alert(1)</script>", "image/png")}
    assert client.post("/api/upload", headers=_h(tokens["teacher"]), files=evil,
                       data={"type": "image"}).status_code == 400
    assert client.get("/api/users", headers=_h(tokens["teacher"])).status_code == 403


# ── Analytics / Recommendation ────────────────────────────────────────────

def test_analytics_shapes(tokens):
    S = _h(tokens["student"])
    ov = client.get("/api/analytics/overview", headers=S).json()["data"]
    assert {"avg_quiz_score", "level", "completion_pct", "quiz_attempts"} <= ov.keys()
    tp = client.get("/api/analytics/topics", headers=S).json()
    assert "data" in tp and "weak_topics" in tp
    qp = client.get("/api/analytics/quiz-progress?quiz_id=1", headers=S).json()["data"]
    assert "attempts" in qp and "attempt_count" in qp


def test_recommendation_flow(tokens):
    S = _h(tokens["student"])
    cur = client.get("/api/recommendations", headers=S).json()["data"]
    assert "current" in cur and "history" in cur
    assert cur["current"]["level"] in {"Weak", "Average", "Good", "Excellent"}
    assert isinstance(cur["current"]["items"], list) and cur["current"]["items"]
    ref = client.post("/api/recommendations/refresh", headers=S, json={}).json()
    assert ref["success"] and ref["data"]["id"]
    # dọn: xoá lịch sử vừa tạo qua DB
    from app.core.database import execute, SessionLocal
    db = SessionLocal()
    execute(db, "DELETE FROM recommendations WHERE id = :i", i=ref["data"]["id"])
    db.close()


# ── AI (offline: stub / heuristic) ───────────────────────────────────────

def test_ai_status(tokens):
    d = client.get("/api/ai/status", headers=_h(tokens["student"])).json()["data"]
    assert "llm" in d and "embedding" in d


def test_ai_chat_grounded_and_refusal(tokens):
    S = _h(tokens["student"])
    ok = client.post("/api/ai/chat", headers=S,
                     json={"course_id": 2, "message": "Promise có những trạng thái nào?"}).json()["data"]
    assert ok["answer"] and ("pending" in ok["answer"].lower() or ok["sources"])
    no = client.post("/api/ai/chat", headers=S,
                     json={"course_id": 2, "message": "Cách nấu phở bò gia truyền?"}).json()["data"]
    assert no["answer"] == "Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học."
    assert no["sources"] == []
    # dọn hội thoại
    from app.core.database import execute, SessionLocal
    db = SessionLocal()
    execute(db, "DELETE FROM ai_conversations WHERE user_id = (SELECT id FROM users WHERE email=:e)",
            e=STUDENT[0])
    db.close()


def test_ai_chat_requires_login():
    r = client.post("/api/ai/chat", json={"course_id": 2, "message": "map() là gì?"})
    assert r.status_code == 401


def test_ai_chat_blocks_unenrolled_course(tokens, course):
    # Khóa tạm vừa tạo -> học viên chắc chắn chưa ghi danh (dữ liệu mẫu thay đổi khi dùng app thật).
    S = _h(tokens["student"])
    r = client.post("/api/ai/chat", headers=S, json={"course_id": course, "message": "Bất cứ câu gì"})
    assert r.status_code == 403, r.text
    assert r.json()["success"] is False


def test_ai_chat_teacher_not_blocked_by_enrollment(tokens):
    # Giảng viên không bị chặn bởi kiểm tra enrollment (dùng để xem trước/hỗ trợ mọi khóa).
    T = _h(tokens["teacher"])
    r = client.post("/api/ai/chat", headers=T, json={"course_id": 3, "message": "Xin chào"})
    assert r.status_code == 200, r.text
    from app.core.database import execute, SessionLocal
    db = SessionLocal()
    execute(db, "DELETE FROM ai_conversations WHERE user_id = (SELECT id FROM users WHERE email=:e)",
            e=TEACHER[0])
    db.close()


def test_ai_chat_rejects_empty_and_too_long_question(tokens):
    S = _h(tokens["student"])
    empty = client.post("/api/ai/chat", headers=S, json={"course_id": 2, "message": "   "})
    assert empty.status_code == 400

    too_long = client.post("/api/ai/chat", headers=S, json={"course_id": 2, "message": "a" * 2001})
    assert too_long.status_code == 400


def test_ai_generate_and_approve_quiz(tokens):
    # course_id=7 (Nguyên Lí HDH) — khóa TEACHER (an.nguyen) thực sự sở hữu và có
    # tài liệu đã lập chỉ mục; generate-quiz/approve giờ đòi hỏi đúng quyền sở hữu.
    T = _h(tokens["teacher"])
    gen = client.post("/api/ai/generate-quiz", headers=T,
                      json={"course_id": 7, "number_of_questions": 3, "difficulty": "medium"}).json()
    assert gen["success"], gen
    qs = gen["data"]["questions"]
    assert 1 <= len(qs) <= 3
    for q in qs:
        assert set(q["options"]) == {"A", "B", "C", "D"}
        assert q["correct_answer"] in {"A", "B", "C", "D"}

    ap = client.post("/api/ai/quiz/approve", headers=T,
                     json={"course_id": 7, "title": "PYTEST AI Quiz", "questions": qs}).json()
    assert ap["success"]
    quiz_id = ap["data"]["quiz_id"]
    shown = client.get(f"/api/quizzes?id={quiz_id}").json()["data"]
    assert shown["source"] == "ai" and shown["question_count"] == len(qs)
    client.request("DELETE", f"/api/quizzes?id={quiz_id}", headers=T)


def test_ai_documents_list(tokens):
    d = client.get("/api/ai/documents?course_id=1", headers=_h(tokens["teacher"])).json()
    assert d["success"] and isinstance(d["data"], list)


# ── 404 / envelope lỗi ───────────────────────────────────────────────────

def test_unknown_route_envelope():
    r = client.get("/api/khong-co")
    assert r.status_code == 404 and r.json()["success"] is False


# ── Thanh toán VNPay Sandbox (giả lập phản hồi VNPay bằng chữ ký tự tạo) ─────

def _vnpay_callback(ref, amount, code, txn_no="14000001"):
    """Tạo bộ tham số giống VNPay gửi về (return URL / IPN), có chữ ký hợp lệ."""
    from app.services import vnpay
    params = {
        "vnp_TmnCode": "TESTCODE", "vnp_TxnRef": ref, "vnp_Amount": str(int(amount * 100)),
        "vnp_ResponseCode": code, "vnp_TransactionStatus": code, "vnp_TransactionNo": txn_no,
        "vnp_BankCode": "NCB", "vnp_OrderInfo": "Thanh toan khoa hoc", "vnp_PayDate": "20260928120000",
    }
    params["vnp_SecureHash"] = vnpay._sign(vnpay._hash_data(params))
    return params


def test_vnpay_payment_flow(tokens, course, monkeypatch):
    from urllib.parse import parse_qs, parse_qsl, urlparse

    from app.core.config import settings
    from app.core.database import SessionLocal, execute
    from app.services import vnpay

    monkeypatch.setattr(settings, "vnpay_tmn_code", "TESTCODE")
    monkeypatch.setattr(settings, "vnpay_hash_secret", "TESTSECRET")
    monkeypatch.setattr(settings, "payment_mock", False)
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    client.put("/api/courses", headers=T, json={"id": course, "title": "PYTEST VNPay", "description": "d",
                                                  "price": 499000, "status": "published"})
    try:
        # Không còn thanh toán giả lập cho khóa có phí
        assert client.post("/api/payments", headers=S, json={"course_id": course, "method": "card"}).status_code == 400

        # 1) Tạo đơn -> URL VNPay có chữ ký hợp lệ, số tiền x100
        r = client.post("/api/payments/vnpay/create", headers=S, json={"course_id": course}).json()
        assert r["success"] and r["payment_url"].startswith(settings.vnpay_payment_url)
        sent = dict(parse_qsl(urlparse(r["payment_url"]).query))
        assert sent["vnp_Amount"] == "49900000" and vnpay.verify(sent)
        ref1 = r["transaction_ref"]

        # 2) Học viên hủy thanh toán (mã 24) -> đơn failed, KHÔNG ghi danh
        resp = client.get("/api/payments/vnpay/return", params=_vnpay_callback(ref1, 499000, "24"),
                          follow_redirects=False)
        assert resp.status_code == 302
        loc = parse_qs(urlparse(resp.headers["location"]).query)
        assert loc["status"] == ["failed"] and loc["ref"] == [ref1]
        st = client.get(f"/api/payments/status?ref={ref1}", headers=S).json()["data"]
        assert st["status"] == "failed" and not st["enrolled"]
        assert course not in client.get("/api/enrollments?ids_only=1", headers=S).json()["data"]

        # 3) Chữ ký sai / số tiền sai bị từ chối
        bad = _vnpay_callback(ref1, 499000, "00")
        bad["vnp_SecureHash"] = "0" * 128
        assert client.get("/api/payments/vnpay/ipn", params=bad).json()["RspCode"] == "97"
        r2 = client.post("/api/payments/vnpay/create", headers=S, json={"course_id": course}).json()
        ref2 = r2["transaction_ref"]
        assert client.get("/api/payments/vnpay/ipn",
                          params=_vnpay_callback(ref2, 1000, "00")).json()["RspCode"] == "04"

        # 4) Thanh toán thành công -> completed + ghi danh; gọi lại IPN -> "đã xác nhận"
        resp = client.get("/api/payments/vnpay/return", params=_vnpay_callback(ref2, 499000, "00"),
                          follow_redirects=False)
        assert parse_qs(urlparse(resp.headers["location"]).query)["status"] == ["success"]
        st = client.get(f"/api/payments/status?ref={ref2}", headers=S).json()["data"]
        assert st["status"] == "completed" and st["enrolled"] and st["gateway_txn_no"] == "14000001"
        assert course in client.get("/api/enrollments?ids_only=1", headers=S).json()["data"]
        assert client.get("/api/payments/vnpay/ipn",
                          params=_vnpay_callback(ref2, 499000, "00")).json()["RspCode"] == "02"

        # Người khác không xem được đơn của học viên
        assert client.get(f"/api/payments/status?ref={ref2}", headers=T).status_code == 404
    finally:
        db = SessionLocal()
        execute(db, "DELETE FROM payments WHERE course_id = :c", c=course)
        execute(db, "DELETE FROM enrollments WHERE course_id = :c", c=course)
        db.close()


def test_admin_manage_payments(tokens):
    A, S = _h(tokens["admin"]), _h(tokens["student"])
    assert client.get("/api/payments/manage", headers=S).status_code == 403
    r = client.get("/api/payments/manage?page_size=5", headers=A).json()
    assert r["success"] and len(r["data"]) <= 5
    assert r["pagination"]["total"] == sum(r["counts"].values())
    # Lọc theo trạng thái
    done = client.get("/api/payments/manage?status=completed&page_size=100", headers=A).json()
    assert done["pagination"]["total"] == r["counts"]["completed"]
    assert all(p["status"] == "completed" for p in done["data"])
    # Tìm theo mã đơn
    ref = done["data"][0]["transaction_ref"]
    if ref:
        hit = client.get(f"/api/payments/manage?q={ref}", headers=A).json()["data"]
        assert [p["transaction_ref"] for p in hit] == [ref]
    # Tham số sai -> 400
    assert client.get("/api/payments/manage?status=abc", headers=A).status_code == 400
    assert client.get("/api/payments/manage?date_from=2026-13-01", headers=A).status_code == 400


def test_vnpay_reconcile_pending(tokens, course, monkeypatch):
    """Đối soát đơn 'đang chờ': VNPay (giả lập) báo đã trả tiền / chưa trả / lỗi kết nối."""
    from app.core.config import settings
    from app.core.database import SessionLocal, execute, q_one
    from app.services import vnpay

    monkeypatch.setattr(settings, "vnpay_tmn_code", "TESTCODE")
    monkeypatch.setattr(settings, "vnpay_hash_secret", "TESTSECRET")
    A, T, S = _h(tokens["admin"]), _h(tokens["teacher"]), _h(tokens["student"])
    client.put("/api/courses", headers=T, json={"id": course, "title": "PYTEST Reconcile", "description": "d",
                                                  "price": 300000, "status": "published"})
    answers = {}  # txn_ref -> phản hồi querydr giả lập (hoặc Exception)

    def fake_query(*, txn_ref, transaction_date, ip_addr="127.0.0.1"):
        a = answers[txn_ref]
        if isinstance(a, Exception):
            raise a
        return {"vnp_ResponseCode": "00", "vnp_Amount": "30000000", "vnp_TransactionNo": "999", "vnp_BankCode": "NCB", **a}

    monkeypatch.setattr(vnpay, "query_transaction", fake_query)
    db = SessionLocal()
    sid = q_one(db, "SELECT id FROM users WHERE email = :e", e=STUDENT[0])["id"]

    def new_order(ref, minutes_ago=0):
        execute(db, "INSERT INTO payments (user_id, course_id, amount, method, status, transaction_ref, created_at) "
                    "VALUES (:u, :c, 300000, 'vnpay', 'pending', :r, NOW() - INTERVAL :m MINUTE)",
                u=sid, c=course, r=ref, m=minutes_ago)
        return q_one(db, "SELECT id FROM payments WHERE transaction_ref = :r", r=ref)["id"]

    def status_of(ref):
        db.commit()  # kết thúc transaction cũ để đọc dữ liệu mới nhất
        return q_one(db, "SELECT status FROM payments WHERE transaction_ref = :r", r=ref)["status"]

    try:
        # Chỉ admin được đối soát
        pid = new_order("PYT-WAIT", minutes_ago=2)
        assert client.post("/api/payments/reconcile", headers=S, json={"id": pid}).status_code == 403
        # Chưa trả tiền nhưng còn hạn -> giữ nguyên
        answers["PYT-WAIT"] = {"vnp_TransactionStatus": "01"}
        r = client.post("/api/payments/reconcile", headers=A, json={"id": pid}).json()
        assert r["outcome"] == "waiting" and status_of("PYT-WAIT") == "pending"
        # Lỗi kết nối VNPay -> giữ nguyên đơn
        answers["PYT-WAIT"] = vnpay.VnpayQueryError("timeout")
        assert client.post("/api/payments/reconcile", headers=A, json={"id": pid}).json()["outcome"] == "error"
        assert status_of("PYT-WAIT") == "pending"

        # Quá hạn và chưa trả tiền -> thất bại.
        # (Không gọi /reconcile-pending ở đây vì nó đối soát cả đơn thật trong DB — chỉ kiểm tra quyền.)
        assert client.post("/api/payments/reconcile-pending", headers=S).status_code == 403
        pid = new_order("PYT-EXP", minutes_ago=60)
        answers["PYT-EXP"] = {"vnp_TransactionStatus": "01"}
        assert client.post("/api/payments/reconcile", headers=A, json={"id": pid}).json()["outcome"] == "expired"
        assert status_of("PYT-EXP") == "failed"
        assert course not in client.get("/api/enrollments?ids_only=1", headers=S).json()["data"]

        # Học viên đã trả tiền nhưng đóng tab -> đối soát hoàn tất + ghi danh
        pid = new_order("PYT-PAID", minutes_ago=3)
        answers["PYT-PAID"] = {"vnp_TransactionStatus": "00"}
        r = client.post("/api/payments/reconcile", headers=A, json={"id": pid}).json()
        assert r["outcome"] == "paid" and r["data"]["status"] == "completed" and r["data"]["enrolled"]
        assert course in client.get("/api/enrollments?ids_only=1", headers=S).json()["data"]
        # Đơn đã xử lý thì không đối soát lại
        assert client.post("/api/payments/reconcile", headers=A, json={"id": pid}).json()["outcome"] == "not_pending"

        # Mua lại khi đơn cũ còn chờ mà thực ra đã trả tiền -> ghi danh luôn, không tạo đơn mới
        client.request("DELETE", f"/api/enrollments?course_id={course}", headers=S)
        execute(db, "DELETE FROM payments WHERE course_id = :c", c=course)
        new_order("PYT-OLD", minutes_ago=5)
        answers["PYT-OLD"] = {"vnp_TransactionStatus": "00"}
        r = client.post("/api/payments/vnpay/create", headers=S, json={"course_id": course}).json()
        assert r["success"] and r["enrolled"] and "payment_url" not in r
        assert status_of("PYT-OLD") == "completed"

        # Đơn đã hoàn tiền không bao giờ bị lật lại thành công
        execute(db, "UPDATE payments SET status='refunded' WHERE transaction_ref='PYT-OLD'")
        from app.routers.payments import _mark_paid
        _mark_paid(db, q_one(db, "SELECT * FROM payments WHERE transaction_ref='PYT-OLD'"))
        assert status_of("PYT-OLD") == "refunded"
    finally:
        execute(db, "DELETE FROM payments WHERE course_id = :c", c=course)
        execute(db, "DELETE FROM enrollments WHERE course_id = :c", c=course)
        db.close()


def test_vnpay_refund(tokens, course, monkeypatch):
    """Hoàn tiền: VNPay đồng ý -> refunded (+ thu hồi quyền học tùy chọn); VNPay từ chối -> giữ nguyên."""
    from app.core.config import settings
    from app.core.database import SessionLocal, execute, q_one
    from app.services import vnpay

    monkeypatch.setattr(settings, "vnpay_tmn_code", "TESTCODE")
    monkeypatch.setattr(settings, "vnpay_hash_secret", "TESTSECRET")
    A, T, S = _h(tokens["admin"]), _h(tokens["teacher"]), _h(tokens["student"])
    client.put("/api/courses", headers=T, json={"id": course, "title": "PYTEST Refund", "description": "d",
                                                  "price": 300000, "status": "published"})
    reply = {"code": "00"}
    sent = []

    def fake_refund(**kw):
        sent.append(kw)
        return {"vnp_ResponseCode": reply["code"], "vnp_Message": "x", "vnp_TransactionNo": "777"}

    monkeypatch.setattr(vnpay, "refund_transaction", fake_refund)
    db = SessionLocal()
    sid = q_one(db, "SELECT id FROM users WHERE email = :e", e=STUDENT[0])["id"]

    def paid_order(ref, method="vnpay"):
        execute(db, "INSERT INTO payments (user_id, course_id, amount, method, status, transaction_ref, "
                    "gateway_txn_no, paid_at) VALUES (:u, :c, 300000, :m, 'completed', :r, '555', NOW())",
                u=sid, c=course, r=ref, m=method)
        execute(db, "INSERT IGNORE INTO enrollments (user_id, course_id) VALUES (:u, :c)", u=sid, c=course)
        return q_one(db, "SELECT id FROM payments WHERE transaction_ref = :r", r=ref)["id"]

    def enrolled():
        return course in client.get("/api/enrollments?ids_only=1", headers=S).json()["data"]

    try:
        pid = paid_order("PYT-RF1")
        body = {"id": pid, "reason": "Học viên yêu cầu hoàn tiền", "revoke_access": True}
        # Quyền + kiểm tra dữ liệu
        assert client.post("/api/payments/refund", headers=S, json=body).status_code == 403
        assert client.post("/api/payments/refund", headers=A, json={**body, "reason": "x"}).status_code == 400
        # VNPay từ chối -> đơn giữ nguyên, vẫn học được
        reply["code"] = "95"
        r = client.post("/api/payments/refund", headers=A, json=body)
        assert r.status_code == 409 and "95" in r.json()["message"]
        db.commit()
        assert q_one(db, "SELECT status FROM payments WHERE id=:i", i=pid)["status"] == "completed" and enrolled()
        # VNPay đồng ý -> refunded + thu hồi quyền học; gửi đúng số tiền / mã GD gốc
        reply["code"] = "00"
        r = client.post("/api/payments/refund", headers=A, json=body).json()
        assert r["success"] and r["revoked"] and r["data"]["status"] == "refunded"
        assert r["data"]["refund_txn_no"] == "777" and r["data"]["refund_reason"] == body["reason"]
        assert sent[-1]["amount"] == 300000 and sent[-1]["transaction_no"] == "555"
        assert not enrolled()
        # Không hoàn tiền 2 lần
        assert client.post("/api/payments/refund", headers=A, json=body).status_code == 409

        # Đơn giả lập cũ + giữ quyền học: không gọi VNPay
        n_calls = len(sent)
        pid2 = paid_order("PYT-RF2", method="card")
        r = client.post("/api/payments/refund", headers=A,
                        json={"id": pid2, "reason": "Hoàn tiền thủ công", "revoke_access": False}).json()
        assert r["success"] and not r["revoked"] and len(sent) == n_calls and enrolled()
    finally:
        execute(db, "DELETE FROM payments WHERE course_id = :c", c=course)
        execute(db, "DELETE FROM enrollments WHERE course_id = :c", c=course)
        db.close()


def test_quiz_attempt_rules(tokens, course):
    """Lượt làm bắt đầu từ lúc mở đề; chủ khóa làm thử không lưu; giảng viên khác không làm được."""
    T, S = _h(tokens["teacher"]), _h(tokens["student"])
    other = _h(_token("binh.tran@studyonline.vn", "123456"))
    qz = int(client.post("/api/quizzes", headers=T, json={
        "course_id": course, "title": "Có giờ", "duration": 10, "max_attempts": 2}).json()["id"])
    client.post("/api/quizzes/questions", headers=T, json={
        "quiz_id": qz, "content": "1+1?", "option_a": "1", "option_b": "2", "option_c": "3", "option_d": "4",
        "correct_answer": "B", "explanation": "Vì 1+1=2"})
    client.post("/api/enrollments", headers=S, json={"course_id": course})

    # Mở lại đề: tiếp tục đúng lượt cũ (cùng token), không được cấp thêm giờ, không tốn thêm lượt
    a = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).json()
    b = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).json()
    assert a["attempt_token"] == b["attempt_token"] and b["attempts_used"] == 1
    assert b["remaining_sec"] <= a["remaining_sec"] <= 600
    qid = a["data"][0]["id"]
    # Không có token -> từ chối; nộp đúng lượt -> được chấm; nộp lại lượt đã xong -> từ chối
    assert client.post("/api/quizzes/submit", headers=S, json={"quiz_id": qz, "answers": {}}).status_code == 400
    r1 = client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": qz, "answers": {str(qid): "A"}, "attempt_token": a["attempt_token"]}).json()
    assert r1["attempts_left"] == 1 and r1["details"][0]["explanation"] is None
    assert client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": qz, "answers": {str(qid): "B"}, "attempt_token": a["attempt_token"]}).status_code == 403
    # Mở lượt 2 rồi bỏ dở -> vẫn tính là đã dùng: hết lượt, không mở được nữa
    c = client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).json()
    assert c["attempt_token"] != a["attempt_token"] and c["attempts_used"] == 2
    assert client.get(f"/api/quizzes?id={qz}", headers=S).json()["data"]["my_attempts"] == 2
    # Lượt cuối đang làm dở: xem lại lượt 1 không được lộ đáp án; danh sách báo đang làm dở
    old = client.get(f"/api/quizzes/results?id={r1['result_id']}", headers=S).json()
    assert old["answers_revealed"] is False and old["details"][0]["correct_answer"] is None
    st = [q for q in client.get("/api/quizzes", headers=S).json()["data"] if q["id"] == qz][0]["my_status"]
    assert st["in_progress"] is True and 0 < st["remaining_sec"] <= 600
    # Lượt cuối: có đáp án đúng + giải thích
    r2 = client.post("/api/quizzes/submit", headers=S, json={
        "quiz_id": qz, "answers": {str(qid): "B"}, "attempt_token": c["attempt_token"]}).json()
    assert r2["answers_revealed"] is True and r2["details"][0]["explanation"] == "Vì 1+1=2"
    assert client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=S).status_code == 403

    # Giảng viên khác: không mở đề, không nộp bài quiz của khóa không phải của mình
    assert client.get(f"/api/quizzes/questions?quiz_id={qz}", headers=other).status_code == 403
    assert client.post("/api/quizzes/submit", headers=other, json={"quiz_id": qz, "answers": {}}).status_code == 403

    # Chủ khóa làm thử: có kết quả + giải thích nhưng không lưu -> quiz không có lượt làm mới
    before = [q for q in client.get("/api/quizzes", headers=T).json()["data"] if q["id"] == qz][0]["attempt_count"]
    own = client.post("/api/quizzes/submit", headers=T, json={"quiz_id": qz, "answers": {str(qid): "B"}}).json()
    assert own["score"] == 1 and own["details"][0]["explanation"] == "Vì 1+1=2"
    after = [q for q in client.get("/api/quizzes", headers=T).json()["data"] if q["id"] == qz][0]["attempt_count"]
    assert before == after == 2
    client.request("DELETE", f"/api/enrollments?course_id={course}", headers=S)
