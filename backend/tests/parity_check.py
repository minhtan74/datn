"""So sánh phản hồi giữa backend PHP (legacy) và FastAPI cho các endpoint GET.

Chạy song song 2 server rồi:
    python tests/parity_check.py
Mặc định:  PHP  = http://127.0.0.1:8001    FastAPI = http://127.0.0.1:8080
Ghi đè:    set PHP_BASE / FASTAPI_BASE

Cùng trỏ vào 1 database nên dữ liệu phải trùng khớp từng byte (trừ token JWT).
"""
import json
import os
import sys

import httpx

PHP = os.environ.get("PHP_BASE", "http://127.0.0.1:8001")
FA = os.environ.get("FASTAPI_BASE", "http://127.0.0.1:8080")

ACCOUNTS = {
    "admin": ("admin@gmail.com", "123456"),
    "teacher": ("an.nguyen@studyonline.vn", "123456"),
    "student": ("em.hoang@gmail.com", "123456"),
}

passed = 0
failed = 0
failures: list[str] = []


def login(base: str, email: str, password: str) -> dict:
    r = httpx.post(f"{base}/api/auth/login", json={"email": email, "password": password}, timeout=30)
    return r.json()


def norm(obj):
    """Bỏ các trường biến động để so sánh (token JWT, thời điểm 'now')."""
    if isinstance(obj, dict):
        return {k: norm(v) for k, v in obj.items() if k not in ("token", "iat", "exp")}
    if isinstance(obj, list):
        return [norm(x) for x in obj]
    return obj


def check(name: str, path: str, token: str | None = None, method: str = "GET", body=None):
    global passed, failed
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        rp = httpx.request(method, f"{PHP}{path}", headers=headers, json=body, timeout=30)
        rf = httpx.request(method, f"{FA}{path}", headers=headers, json=body, timeout=30)
    except Exception as e:  # noqa: BLE001
        failed += 1
        failures.append(f"[{name}] request lỗi: {e}")
        print(f"  ✗ {name}: {e}")
        return

    same_status = rp.status_code == rf.status_code
    try:
        jp, jf = norm(rp.json()), norm(rf.json())
    except Exception:  # noqa: BLE001
        jp, jf = rp.text, rf.text
    same_body = jp == jf

    if same_status and same_body:
        passed += 1
        print(f"  ✓ {name}  ({rp.status_code})")
    else:
        failed += 1
        detail = f"[{name}] status php={rp.status_code} fa={rf.status_code}"
        if not same_body:
            detail += (
                "\n     php=" + json.dumps(jp, ensure_ascii=False)[:500]
                + "\n     fa =" + json.dumps(jf, ensure_ascii=False)[:500]
            )
        print(f"  ✗ {name}")
        failures.append(detail)


def main():
    print(f"PHP     = {PHP}")
    print(f"FastAPI = {FA}\n")

    tokens_php, tokens_fa = {}, {}
    print("── Auth ──")
    for role, (email, pw) in ACCOUNTS.items():
        lp, lf = login(PHP, email, pw), login(FA, email, pw)
        tokens_php[role] = lp.get("token")
        tokens_fa[role] = lf.get("token")
        ok = norm(lp) == norm(lf) and lp.get("success") and lf.get("token")
        print(("  ✓ " if ok else "  ✗ ") + f"login {role}")
        if not ok:
            failures.append(f"login {role}: php={lp} fa={lf}")

    T = tokens_fa  # dùng token FastAPI cho cả 2 (cùng secret nên PHP verify được)

    print("\n── Public / chung ──")
    check("courses.list", "/api/courses")
    check("courses.detail", "/api/courses?id=1")
    check("courses.detail.404", "/api/courses?id=99999")
    check("chapters.byCourse", "/api/chapters?course_id=1")
    check("chapters.detail", "/api/chapters?id=1")
    check("chapters.missingParam", "/api/chapters")
    check("lessons.byChapter", "/api/lessons?chapter_id=1")
    check("lessons.detail", "/api/lessons?id=1")
    check("quizzes.list", "/api/quizzes")
    check("quizzes.byCourse", "/api/quizzes?course_id=1")
    check("quizzes.detail", "/api/quizzes?id=1")
    check("questions.byQuiz", "/api/quizzes/questions?quiz_id=1")
    check("questions.detail", "/api/quizzes/questions?id=1")

    print("\n── Auth-required (GET) ──")
    check("auth.me.admin", "/api/auth/me", T["admin"])
    check("auth.me.noToken", "/api/auth/me")
    check("users.list", "/api/users", T["admin"])
    check("users.detail", "/api/users?id=2", T["admin"])
    check("users.forbidden.student", "/api/users", T["student"])
    check("enroll.mine.student", "/api/enrollments", T["student"])
    check("enroll.idsOnly.student", "/api/enrollments?ids_only=1", T["student"])
    check("enroll.check.student", "/api/enrollments?course_id=1", T["student"])
    check("enroll.byTeacher", "/api/enrollments", T["teacher"])
    check("enroll.all.admin", "/api/enrollments", T["admin"])
    check("payments.mine.student", "/api/payments", T["student"])
    check("payments.byTeacher", "/api/payments", T["teacher"])
    check("payments.all.admin", "/api/payments", T["admin"])
    check("payments.check", "/api/payments/check?course_id=1", T["student"])
    check("progress.summary", "/api/progress", T["student"])
    check("progress.byCourse", "/api/progress?course_id=1", T["student"])
    check("progress.weekly", "/api/progress?weekly=1", T["student"])
    check("progress.recent", "/api/progress?recent=1", T["student"])
    check("reports.summary.7d", "/api/reports/summary", T["admin"])
    check("reports.summary.30d", "/api/reports/summary?range=30d", T["admin"])
    check("reports.summary.today", "/api/reports/summary?range=today", T["admin"])
    check("reports.summary.1y", "/api/reports/summary?range=1y", T["admin"])
    check("reports.forbidden.teacher", "/api/reports/summary", T["teacher"])

    print("\n── 404 / method ──")
    check("unknown.path", "/api/khong-ton-tai")

    print(f"\n{'='*48}\nPASS={passed}  FAIL={failed}")
    if failures:
        print("\nChi tiết lỗi:")
        for f in failures:
            print(" -", f)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
