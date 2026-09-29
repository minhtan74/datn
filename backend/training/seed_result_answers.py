"""(TÙY CHỌN – chỉ để DEMO) Sinh `result_answers` cho các bản ghi `results` cũ (seed)
chưa có chi tiết từng câu, để dashboard Phân tích theo topic có dữ liệu ngay.

- KHÔNG phải dữ liệu thật: chỉ phân bổ đúng/sai sao cho KHỚP điểm số đã lưu
  (score/total), chọn câu đúng theo hash tất định (ổn định giữa các lần chạy).
- Vòng lặp cá nhân hoá (Phase 5) và các lần làm quiz mới sẽ tạo dữ liệu thật.

    python training/seed_result_answers.py
"""
import hashlib
import os
import sys

import pymysql

DB = dict(host=os.environ.get("DB_HOST", "127.0.0.1"), port=int(os.environ.get("DB_PORT", "3306")),
          user=os.environ.get("DB_USER", "root"), password=os.environ.get("DB_PASS", ""),
          database=os.environ.get("DB_NAME", "studyonline_db"), charset="utf8mb4")

WRONG = {"A": "B", "B": "C", "C": "D", "D": "A"}


def rank(result_id: int, question_id: int) -> int:
    h = hashlib.md5(f"{result_id}:{question_id}".encode()).hexdigest()
    return int(h, 16)


def main():
    conn = pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor)
    made = 0
    with conn.cursor() as cur:
        cur.execute(
            "SELECT r.id, r.quiz_id, r.score, r.total FROM results r "
            "LEFT JOIN result_answers ra ON ra.result_id = r.id "
            "WHERE ra.id IS NULL"
        )
        results = cur.fetchall()
        for r in results:
            cur.execute(
                "SELECT id, correct_answer FROM questions WHERE quiz_id=%s ORDER BY order_index, id",
                (r["quiz_id"],),
            )
            qs = cur.fetchall()
            if not qs:
                continue
            ordered = sorted(qs, key=lambda q: rank(r["id"], q["id"]))
            n_correct = max(0, min(int(r["score"]), len(ordered)))
            correct_ids = {q["id"] for q in ordered[:n_correct]}
            for q in qs:
                is_ok = q["id"] in correct_ids
                chosen = q["correct_answer"] if is_ok else WRONG[q["correct_answer"]]
                cur.execute(
                    "INSERT INTO result_answers (result_id, question_id, chosen, is_correct) "
                    "VALUES (%s, %s, %s, %s)",
                    (r["id"], q["id"], chosen, 1 if is_ok else 0),
                )
                made += 1
    conn.commit()
    conn.close()
    print(f"Đã tạo {made} dòng result_answers cho {len(results)} bản ghi results cũ.")
    sys.exit(0)


if __name__ == "__main__":
    main()
