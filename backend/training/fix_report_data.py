"""(TÙY CHỌN – chỉ để DEMO) Làm dữ liệu mẫu nhất quán về thời gian cho trang Báo cáo admin.

Chạy SAU seed_learning_data.py. Chạy lại nhiều lần vẫn an toàn.
  1. Xoá ghi danh khoá CÓ PHÍ mà không có thanh toán thành công (kèm kết quả quiz,
     tiến độ, hội thoại AI, phân tích/gợi ý của học viên trong khoá đó).
  2. Ngày tạo khoá học phải trước mọi hoạt động của khoá.
  3. Ngày ghi danh = ngày thanh toán (khoá có phí) / vài ngày trước hoạt động đầu tiên (khoá miễn phí).
  4. Lượt làm quiz / tiến độ bài học nằm trước ngày ghi danh -> dời vào sau ngày ghi danh.
  5. Ngày tạo đơn thanh toán không được sau ngày thanh toán.
  6. Ngày tạo tài khoản trước hoạt động đầu tiên (học viên) / trước khoá học đầu tiên (giảng viên).

    python training/fix_report_data.py
"""
import hashlib
import os
import random
from datetime import datetime, timedelta

import pymysql

DB = dict(host=os.environ.get("DB_HOST", "127.0.0.1"), port=int(os.environ.get("DB_PORT", "3306")),
          user=os.environ.get("DB_USER", "root"), password=os.environ.get("DB_PASS", ""),
          database=os.environ.get("DB_NAME", "studyonline_db"), charset="utf8mb4")


# Số ngẫu nhiên tất định theo khoá -> chạy lại cho cùng kết quả
def rng_for(*key) -> random.Random:
    return random.Random(int(hashlib.md5(":".join(map(str, key)).encode()).hexdigest(), 16))


def one(cur, sql, args=()):
    cur.execute(sql, args)
    row = cur.fetchone()
    return next(iter(row.values())) if row else None


# Thời điểm hoạt động học tập sớm nhất của 1 học viên trong 1 khoá (quiz hoặc hoàn thành bài)
def first_activity(cur, uid, cid):
    a = one(cur, "SELECT MIN(r.submit_time) FROM results r JOIN quizzes q ON q.id=r.quiz_id "
                 "WHERE r.user_id=%s AND q.course_id=%s", (uid, cid))
    b = one(cur, "SELECT MIN(lp.completed_at) FROM lesson_progress lp JOIN lessons l ON l.id=lp.lesson_id "
                 "JOIN chapters ch ON ch.id=l.chapter_id WHERE lp.user_id=%s AND ch.course_id=%s", (uid, cid))
    vals = [v for v in (a, b) if v]
    return min(vals) if vals else None


# Bước 1: xoá ghi danh khoá có phí chưa thanh toán thành công + dữ liệu học tập liên quan
def remove_unpaid_enrollments(cur) -> list[tuple]:
    cur.execute(
        "SELECT e.id, e.user_id, e.course_id FROM enrollments e JOIN courses c ON c.id=e.course_id "
        "JOIN users u ON u.id=e.user_id AND u.role='student' "
        "WHERE c.price > 0 AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.user_id=e.user_id "
        "AND p.course_id=e.course_id AND p.status='completed')"
    )
    removed = []
    for e in cur.fetchall():
        uid, cid = e["user_id"], e["course_id"]
        cur.execute("DELETE ra FROM result_answers ra JOIN results r ON r.id=ra.result_id "
                    "JOIN quizzes q ON q.id=r.quiz_id WHERE r.user_id=%s AND q.course_id=%s", (uid, cid))
        cur.execute("DELETE r FROM results r JOIN quizzes q ON q.id=r.quiz_id "
                    "WHERE r.user_id=%s AND q.course_id=%s", (uid, cid))
        cur.execute("DELETE lp FROM lesson_progress lp JOIN lessons l ON l.id=lp.lesson_id "
                    "JOIN chapters ch ON ch.id=l.chapter_id WHERE lp.user_id=%s AND ch.course_id=%s", (uid, cid))
        for t in ("ai_conversations", "learning_analytics", "recommendations"):
            cur.execute(f"DELETE FROM {t} WHERE user_id=%s AND course_id=%s", (uid, cid))
        cur.execute("DELETE FROM enrollments WHERE id=%s", (e["id"],))
        removed.append((uid, cid))
    return removed


# Bước 2: khoá học được tạo trước hoạt động sớm nhất (thanh toán / quiz / hoàn thành bài) 15–40 ngày
def fix_course_dates(cur) -> int:
    n = 0
    cur.execute("SELECT id, created_at FROM courses")
    for c in cur.fetchall():
        cid = c["id"]
        firsts = [
            one(cur, "SELECT MIN(paid_at) FROM payments WHERE course_id=%s AND paid_at IS NOT NULL", (cid,)),
            one(cur, "SELECT MIN(r.submit_time) FROM results r JOIN quizzes q ON q.id=r.quiz_id "
                     "WHERE q.course_id=%s", (cid,)),
            one(cur, "SELECT MIN(lp.completed_at) FROM lesson_progress lp JOIN lessons l ON l.id=lp.lesson_id "
                     "JOIN chapters ch ON ch.id=l.chapter_id WHERE ch.course_id=%s", (cid,)),
        ]
        firsts = [f for f in firsts if f]
        if firsts and c["created_at"] > min(firsts):
            rng = rng_for("course", cid)
            new = min(firsts) - timedelta(days=rng.randint(15, 40), hours=rng.randint(0, 10))
            cur.execute("UPDATE courses SET created_at=%s WHERE id=%s", (new, cid))
            n += 1
    return n


# Bước 3 + 4: đặt ngày ghi danh hợp lý, rồi dời hoạt động bị trước ngày ghi danh vào sau nó
def fix_enrollments(cur, now: datetime) -> tuple[int, int, int]:
    n_enr = n_res = n_lp = 0
    cur.execute("SELECT e.id, e.user_id, e.course_id, e.enroll_date, c.created_at AS course_created, c.price "
                "FROM enrollments e JOIN courses c ON c.id=e.course_id")
    for e in cur.fetchall():
        uid, cid = e["user_id"], e["course_id"]
        rng = rng_for("enroll", uid, cid)
        paid = one(cur, "SELECT MIN(paid_at) FROM payments WHERE user_id=%s AND course_id=%s "
                        "AND status='completed'", (uid, cid))
        if paid:
            enroll = paid
        else:
            act = first_activity(cur, uid, cid)
            if act:
                enroll = act - timedelta(days=rng.randint(1, 5), hours=rng.randint(0, 12))
            else:
                span = max((now - e["course_created"]).days - 6, 1)
                enroll = e["course_created"] + timedelta(days=3 + rng.randint(0, span))
            enroll = max(enroll, e["course_created"] + timedelta(days=1))
        if enroll != e["enroll_date"]:
            cur.execute("UPDATE enrollments SET enroll_date=%s WHERE id=%s", (enroll, e["id"]))
            n_enr += 1

        # Cửa sổ dời hoạt động: từ ngày ghi danh tới tối đa 75 ngày sau (không vượt hiện tại)
        end = min(now - timedelta(hours=1), enroll + timedelta(days=75))

        # Lượt làm quiz: nếu có lượt trước ngày ghi danh thì rải đều lại toàn bộ lượt của quiz đó (giữ thứ tự)
        cur.execute("SELECT id FROM quizzes WHERE course_id=%s", (cid,))
        for q in cur.fetchall():
            cur.execute("SELECT id, submit_time FROM results WHERE user_id=%s AND quiz_id=%s ORDER BY submit_time, id",
                        (uid, q["id"]))
            rows = cur.fetchall()
            if not rows or rows[0]["submit_time"] >= enroll:
                continue
            step = (end - enroll) / (len(rows) + 1)
            for i, r in enumerate(rows, start=1):
                cur.execute("UPDATE results SET submit_time=%s WHERE id=%s",
                            ((enroll + step * i).replace(microsecond=0), r["id"]))
                n_res += 1

        # Tiến độ bài học: tương tự, rải đều các bài đã hoàn thành theo thứ tự cũ
        cur.execute("SELECT lp.id, lp.completed_at FROM lesson_progress lp JOIN lessons l ON l.id=lp.lesson_id "
                    "JOIN chapters ch ON ch.id=l.chapter_id WHERE lp.user_id=%s AND ch.course_id=%s "
                    "AND lp.completed_at IS NOT NULL ORDER BY lp.completed_at, lp.id", (uid, cid))
        rows = cur.fetchall()
        if rows and rows[0]["completed_at"] < enroll:
            step = (end - enroll) / (len(rows) + 1)
            for i, r in enumerate(rows, start=1):
                cur.execute("UPDATE lesson_progress SET completed_at=%s, updated_at=updated_at WHERE id=%s",
                            ((enroll + step * i).replace(microsecond=0), r["id"]))
                n_lp += 1
    return n_enr, n_res, n_lp


# Bước 5: đơn thanh toán được tạo vài phút trước khi thanh toán
def fix_payment_dates(cur) -> int:
    cur.execute("SELECT id, created_at, paid_at FROM payments WHERE paid_at IS NOT NULL AND created_at > paid_at")
    rows = cur.fetchall()
    for p in rows:
        mins = rng_for("pay", p["id"]).randint(1, 10)
        cur.execute("UPDATE payments SET created_at=%s WHERE id=%s", (p["paid_at"] - timedelta(minutes=mins), p["id"]))
    return len(rows)


# Bước 6: ngày tạo tài khoản
def fix_user_dates(cur) -> int:
    n = 0
    cur.execute("SELECT id, role, created_at FROM users")
    users = cur.fetchall()
    for u in users:
        uid, rng = u["id"], rng_for("user", u["id"])
        if u["role"] == "student":
            first = [
                one(cur, "SELECT MIN(enroll_date) FROM enrollments WHERE user_id=%s", (uid,)),
                one(cur, "SELECT MIN(created_at) FROM payments WHERE user_id=%s", (uid,)),
            ]
            first = [f for f in first if f]
            target = min(first) - timedelta(days=rng.randint(1, 10), hours=rng.randint(0, 12)) if first else None
        elif u["role"] == "teacher":
            first = one(cur, "SELECT MIN(created_at) FROM courses WHERE teacher_id=%s", (uid,))
            target = first - timedelta(days=rng.randint(10, 30)) if first else None
        else:
            continue
        if target and u["created_at"] > target:
            cur.execute("UPDATE users SET created_at=%s WHERE id=%s", (target, uid))
            n += 1
    # Admin: tài khoản đầu tiên của hệ thống
    earliest = one(cur, "SELECT MIN(created_at) FROM users WHERE role <> 'admin'")
    if earliest:
        n += cur.execute("UPDATE users SET created_at=%s WHERE role='admin' AND created_at > %s",
                         (earliest - timedelta(days=7), earliest))
    return n


def main():
    now = datetime.now().replace(microsecond=0)
    conn = pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cur:
            removed = remove_unpaid_enrollments(cur)
            c = fix_course_dates(cur)
            e, r, lp = fix_enrollments(cur, now)
            p = fix_payment_dates(cur)
            u = fix_user_dates(cur)
        conn.commit()
    finally:
        conn.close()
    print(f"Xoá {len(removed)} ghi danh chưa thanh toán {removed}; sửa ngày: {c} khoá học, {e} ghi danh, "
          f"{r} lượt quiz, {lp} tiến độ bài, {p} đơn thanh toán, {u} tài khoản.")


if __name__ == "__main__":
    main()
