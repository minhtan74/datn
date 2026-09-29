"""Smoke test luồng ghi (CRUD + học tập) trên FastAPI. Tự dọn dữ liệu sau khi chạy.

    python tests/smoke_writes.py           # mặc định http://127.0.0.1:8080
    set FASTAPI_BASE=... để đổi
"""
import os
import sys
import time

import httpx

BASE = os.environ.get("FASTAPI_BASE", "http://127.0.0.1:8080")
ADMIN = ("admin@gmail.com", "123456")
TEACHER = ("an.nguyen@studyonline.vn", "123456")

ok_count = 0
fail_count = 0


def _tok(email, pw):
    r = httpx.post(f"{BASE}/api/auth/login", json={"email": email, "password": pw})
    return r.json()["token"]


def call(method, path, token=None, expect=200, **kw):
    global ok_count, fail_count
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = httpx.request(method, f"{BASE}{path}", headers=headers, timeout=30, **kw)
    body = None
    try:
        body = r.json()
    except Exception:  # noqa: BLE001
        body = r.text
    tag = f"{method} {path}"
    if r.status_code == expect and (not isinstance(body, dict) or body.get("success") in (True, None) or expect != 200):
        ok_count += 1
        print(f"  ✓ {tag} -> {r.status_code}")
    else:
        fail_count += 1
        print(f"  ✗ {tag} -> {r.status_code} (mong {expect})  {body}")
    return body


def main():
    admin = _tok(*ADMIN)
    teacher = _tok(*TEACHER)

    print("── Đăng ký học viên tạm ──")
    email = f"smoke_{int(time.time())}@test.local"
    call("POST", "/api/auth/register", json={
        "fullname": "Smoke Student", "email": email,
        "password": "123456", "confirm_password": "123456",
    })
    student = _tok(email, "123456")
    me = call("GET", "/api/auth/me", student)
    student_id = me["user"]["id"]

    print("── Giáo viên: tạo course/chapter/lesson/quiz/question ──")
    c = call("POST", "/api/courses", teacher, json={
        "title": "SMOKE Course", "description": "tmp", "thumbnail": "",
    })
    course_id = int(c["id"])
    ch = call("POST", "/api/chapters", teacher, json={
        "course_id": course_id, "chapter_name": "SMOKE Chapter",
    })
    chapter_id = int(ch["id"])
    ls = call("POST", "/api/lessons", teacher, json={
        "chapter_id": chapter_id, "title": "SMOKE Lesson",
        "description": "d", "video_url": "https://youtu.be/abc", "document_url": "",
    })
    lesson_id = int(ls["id"])
    call("PUT", "/api/lessons", teacher, json={
        "id": lesson_id, "title": "SMOKE Lesson v2", "description": "d2",
        "video_url": "https://youtu.be/abc", "document_url": "",
    })
    qz = call("POST", "/api/quizzes", teacher, json={
        "course_id": course_id, "title": "SMOKE Quiz", "description": "",
    })
    quiz_id = int(qz["id"])
    call("POST", "/api/quizzes/questions", teacher, json={
        "quiz_id": quiz_id, "content": "1+1=?", "option_a": "1", "option_b": "2",
        "option_c": "3", "option_d": "4", "correct_answer": "b", "order_index": 0,
    })
    qlist = call("GET", f"/api/quizzes/questions?quiz_id={quiz_id}", teacher)
    question_id = qlist["data"][0]["id"]
    call("PUT", "/api/quizzes/questions", teacher, json={
        "id": question_id, "content": "1+1=?", "option_a": "1", "option_b": "2",
        "option_c": "3", "option_d": "4", "correct_answer": "B", "order_index": 1,
    })
    qd = call("GET", f"/api/quizzes?id={quiz_id}")
    assert qd["data"]["question_count"] == 1, qd

    print("── Học viên: enroll / progress / submit ──")
    call("POST", "/api/enrollments", student, json={"course_id": course_id})
    call("POST", "/api/enrollments", student, json={"course_id": course_id}, expect=409)
    ids = call("GET", "/api/enrollments?ids_only=1", student)
    assert course_id in ids["data"], ids
    call("POST", "/api/progress", student, json={
        "lesson_id": lesson_id, "watched_sec": 120, "is_completed": 1,
    })
    done = call("GET", f"/api/progress?course_id={course_id}", student)
    assert lesson_id in done["data"], done
    sub = call("POST", "/api/quizzes/submit", student, json={
        "quiz_id": quiz_id, "answers": {str(question_id): "B"},
    })
    assert sub["score"] == 1 and sub["total"] == 1 and sub["percent"] == 100, sub
    call("GET", "/api/progress", student)
    call("GET", "/api/progress?weekly=1", student)
    call("GET", "/api/progress?recent=1", student)

    print("── Thanh toán khóa có phí ──")
    paid = call("POST", "/api/courses", teacher, json={
        "title": "SMOKE Paid", "description": "", "thumbnail": "", "price": 199000, "status": "published",
    })
    paid_id = int(paid["id"])
    call("POST", "/api/enrollments", student, json={"course_id": paid_id}, expect=402)
    # Khóa có phí chỉ thanh toán qua VNPay (luồng VNPay được kiểm tra trong tests/test_api.py)
    call("POST", "/api/payments", student, json={"course_id": paid_id, "method": "card"}, expect=400)
    chk = call("GET", f"/api/payments/check?course_id={paid_id}", student)
    assert not chk["has_paid"] and not chk["enrolled"], chk

    print("── Đổi mật khẩu học viên ──")
    call("POST", "/api/auth/change-password", student, json={
        "old_password": "123456", "new_password": "654321",
    })
    call("POST", "/api/auth/change-password", student, json={
        "old_password": "123456", "new_password": "abcdef",
    }, expect=400)

    print("── Dọn dẹp ──")
    # Quiz/câu hỏi đã có lượt làm bài -> API chặn xóa; dữ liệu được dọn cùng khóa học bằng SQL bên dưới.
    call("DELETE", f"/api/quizzes/questions?id={question_id}", teacher, expect=409)
    call("DELETE", f"/api/quizzes?id={quiz_id}", teacher, expect=409)
    call("DELETE", f"/api/lessons?id={lesson_id}", teacher)
    call("DELETE", f"/api/chapters?id={chapter_id}", teacher)
    # API cố ý không cho xóa khóa học / user đã có đăng ký, thanh toán -> kiểm tra điều đó rồi dọn bằng SQL.
    call("DELETE", f"/api/courses?id={course_id}", teacher, expect=409)
    call("DELETE", f"/api/users?id={student_id}", admin, expect=409)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.core.database import SessionLocal, execute

    db = SessionLocal()
    execute(db, "DELETE FROM courses WHERE id IN (:a, :b)", a=course_id, b=paid_id)
    execute(db, "DELETE FROM users WHERE id = :id", id=student_id)
    db.close()

    print(f"\n{'='*44}\nPASS={ok_count}  FAIL={fail_count}")
    sys.exit(1 if fail_count else 0)


if __name__ == "__main__":
    main()
