"""PHASE 7 — Sinh dataset fine-tuning cho AI Quiz Generator.

Nguồn:
  1. training/dataset/qa_bank.jsonl  — cặp Q&A biên soạn tay (có context/topic/difficulty/explanation)
  2. (tuỳ chọn) 30 câu hỏi mẫu trong DB studyonline_db  — gộp theo quiz

Đầu ra (định dạng instruction / input / output — output là JSON schema StudyOnline):
  training/dataset/train.jsonl · validation.jsonl · test.jsonl

    python training/prepare_dataset.py [--no-db] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "dataset")

DIFF_VI = {"easy": "dễ", "medium": "trung bình", "hard": "khó"}

INSTR_TEMPLATES = [
    "Tạo {n} câu hỏi trắc nghiệm về chủ đề \"{topic}\" ở mức {diff}. Trả về JSON đúng schema StudyOnline.",
    "Dựa vào nội dung bài học, hãy soạn {n} câu hỏi trắc nghiệm 4 đáp án (mức {diff}) về \"{topic}\". Trả về JSON.",
    "Sinh {n} câu hỏi kiểm tra kiến thức mức {diff} cho chủ đề \"{topic}\", mỗi câu có 4 lựa chọn A/B/C/D, một đáp án đúng và giải thích. Xuất JSON.",
    "Hãy tạo bộ {n} câu hỏi trắc nghiệm ({diff}) bám sát tài liệu về \"{topic}\". Định dạng JSON theo schema StudyOnline.",
    "Biên soạn {n} câu trắc nghiệm mức {diff} về \"{topic}\" kèm đáp án đúng và lời giải thích ngắn. Trả JSON.",
    "Từ đoạn tài liệu sau, tạo {n} câu hỏi ôn tập trắc nghiệm mức {diff} cho chủ đề \"{topic}\". Xuất JSON schema StudyOnline.",
    "Ra đề {n} câu trắc nghiệm ({diff}) về \"{topic}\", mỗi câu 4 phương án. Trả kết quả dạng JSON.",
    "Với vai trò giảng viên, hãy soạn {n} câu hỏi kiểm tra (mức {diff}) về \"{topic}\" dựa trên tài liệu. Định dạng JSON.",
    "Tạo đề trắc nghiệm gồm {n} câu ở độ khó {diff} cho chủ đề \"{topic}\". Mỗi câu có options A-D, correct_answer, explanation, difficulty, topic. Trả JSON.",
    "Hãy sinh {n} câu hỏi nhiều lựa chọn (mức {diff}) bao quát nội dung \"{topic}\" trong tài liệu. Xuất JSON.",
]


def _load_bank() -> list[dict]:
    rows = []
    with open(os.path.join(DS, "qa_bank.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _q_obj(r: dict) -> dict:
    return {
        "question": r["question"],
        "options": r["options"],
        "correct_answer": r["correct_answer"],
        "explanation": r.get("explanation", ""),
        "difficulty": r.get("difficulty", "medium"),
        "topic": r["topic"],
    }


def _example(instruction: str, context: str, questions: list[dict]) -> dict:
    return {
        "instruction": instruction,
        "input": context.strip(),
        "output": json.dumps({"questions": questions}, ensure_ascii=False),
    }


def _ctx_join(items: list[dict]) -> str:
    seen, parts = set(), []
    for it in items:
        c = it["context"].strip()
        if c not in seen:
            seen.add(c)
            parts.append(c)
    return " ".join(parts)


def build_from_bank(bank: list[dict], rng: random.Random) -> list[dict]:
    by_topic: dict[str, list[dict]] = defaultdict(list)
    by_area: dict[str, list[dict]] = defaultdict(list)
    for r in bank:
        by_topic[r["topic"]].append(r)
        area = r["topic"].split(" - ")[0].strip()
        by_area[area].append(r)

    out: list[dict] = []

    # (1) 1 câu / ví dụ  x 3 biến thể instruction
    for it in bank:
        d = DIFF_VI[it.get("difficulty", "medium")]
        for tmpl in rng.sample(INSTR_TEMPLATES, 3):
            out.append(_example(tmpl.format(n=1, topic=it["topic"], diff=d), it["context"], [_q_obj(it)]))

    # (2) nhiều câu cùng CHỦ ĐỀ hẹp (nếu đủ)
    for topic, items in by_topic.items():
        if len(items) < 2:
            continue
        diffs = {it.get("difficulty", "medium") for it in items}
        dl = DIFF_VI[sorted(diffs)[0]] if len(diffs) == 1 else "hỗn hợp"
        for n in range(2, min(len(items), 4) + 1):
            for _ in range(3):
                s = rng.sample(items, n)
                out.append(
                    _example(rng.choice(INSTR_TEMPLATES).format(n=n, topic=topic, diff=dl),
                             _ctx_join(s), [_q_obj(x) for x in s])
                )

    # (3) nhiều câu theo LĨNH VỰC rộng (Python / JavaScript / SQL / HTTP ...)
    for area, items in by_area.items():
        if len(items) < 3:
            continue
        for n in (2, 3, 4, 5):
            if n > len(items):
                break
            for _ in range(6):
                s = rng.sample(items, n)
                dl = "hỗn hợp" if len({x.get("difficulty", "medium") for x in s}) > 1 \
                    else DIFF_VI[s[0].get("difficulty", "medium")]
                out.append(
                    _example(rng.choice(INSTR_TEMPLATES).format(n=n, topic=area, diff=dl),
                             _ctx_join(s), [_q_obj(x) for x in s])
                )
    return out


def build_from_db(rng: random.Random) -> list[dict]:
    try:
        import sys

        sys.path.insert(0, os.path.dirname(HERE))
        from app.core.database import q_all
        from app.core.database import SessionLocal
    except Exception as e:  # noqa: BLE001
        print(f"  (bỏ qua nguồn DB: {e})")
        return []

    db = SessionLocal()
    try:
        rows = q_all(
            db,
            "SELECT q.id, q.content, q.option_a, q.option_b, q.option_c, q.option_d, "
            "q.correct_answer, q.topic, q.difficulty, qz.title AS quiz_title, "
            "c.title AS course_title FROM questions q "
            "JOIN quizzes qz ON qz.id = q.quiz_id JOIN courses c ON c.id = qz.course_id "
            "ORDER BY q.quiz_id, q.order_index, q.id",
        )
    finally:
        db.close()

    by_quiz: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_quiz[(r["quiz_title"], r["course_title"])].append(r)

    out: list[dict] = []
    for (quiz_title, course_title), items in by_quiz.items():
        topics = sorted({(it["topic"] or "kiến thức chung") for it in items})
        context = (
            f"Khóa học: {course_title}. Bài kiểm tra: {quiz_title}. "
            f"Các chủ đề liên quan: {', '.join(topics)}."
        )
        questions = [
            {
                "question": it["content"],
                "options": {
                    "A": it["option_a"], "B": it["option_b"],
                    "C": it["option_c"], "D": it["option_d"],
                },
                "correct_answer": it["correct_answer"],
                "explanation": "",
                "difficulty": it["difficulty"] or "medium",
                "topic": it["topic"] or "kiến thức chung",
            }
            for it in items
        ]
        tmpl = rng.choice(INSTR_TEMPLATES)
        out.append(
            _example(
                tmpl.format(n=len(questions), topic=course_title, diff="hỗn hợp"),
                context,
                questions,
            )
        )
        # thêm biến thể lấy 3 câu
        if len(questions) >= 3:
            sample = rng.sample(questions, 3)
            out.append(
                _example(
                    rng.choice(INSTR_TEMPLATES).format(n=3, topic=course_title, diff="trung bình"),
                    context,
                    sample,
                )
            )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-db", action="store_true", help="Không lấy dữ liệu từ DB")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    bank = _load_bank()
    examples = build_from_bank(bank, rng)
    if not args.no_db:
        examples += build_from_db(rng)

    # khử trùng lặp theo (instruction, output)
    uniq, seen = [], set()
    for ex in examples:
        key = (ex["instruction"], ex["output"])
        if key not in seen:
            seen.add(key)
            uniq.append(ex)
    rng.shuffle(uniq)

    n = len(uniq)
    n_test = max(1, int(n * 0.1))
    n_val = max(1, int(n * 0.1))
    test, val, train = uniq[:n_test], uniq[n_test : n_test + n_val], uniq[n_test + n_val :]

    for name, part in (("train", train), ("validation", val), ("test", test)):
        path = os.path.join(DS, f"{name}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for ex in part:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"  {name:11s}: {len(part):4d}  -> {path}")

    print(f"\nTổng: {n} ví dụ (train {len(train)} / val {len(val)} / test {len(test)}).")


if __name__ == "__main__":
    main()
