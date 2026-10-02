"""Đánh giá độ chính xác của AI Tutor (RAG hỏi đáp) trên bộ câu hỏi rag_eval/questions.jsonl.

Đo (số liệu thật, chạy trên CSDL đang cấu hình trong backend/.env, CHỈ ĐỌC — không tạo hội thoại):
  - Truy hồi   : Hit@1, Hit@k, MRR — đoạn chứa đủ ý mong đợi có nằm trong top-k không
  - Quyết định : tỷ lệ trả lời câu trong phạm vi, tỷ lệ từ chối câu ngoài phạm vi (lạc đề + gần lĩnh vực)
  - Nội dung   : câu trả lời có chứa đủ ý mong đợi (so khớp từ khóa, không phân biệt hoa thường)
  - Tổng hợp   : độ chính xác chung = (trả lời đúng + từ chối đúng) / tổng số câu
  - Ngưỡng     : mô phỏng kết quả nếu đổi rag_similarity_threshold (không sửa cấu hình)

Mỗi dòng questions.jsonl: {"course_id", "type": in_scope|out_of_scope|near_miss, "question",
"expect": [[phương án 1, phương án 2], [...]]} — câu trả lời đúng khi mỗi nhóm có ít nhất 1 phương án.

Cách dùng (từ thư mục backend):
    .venv\\Scripts\\python training\\rag_eval\\evaluate_rag.py
Thêm --judge để LLM chấm thêm từng câu trả lời (khi đã cấu hình LLM; câu trả lời diễn đạt tự do dễ bị chấm từ khóa bỏ sót).
Kết quả in ra màn hình và lưu vào training/rag_eval/results/ (bảng từng câu .csv + tóm tắt .md).
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
import unicodedata
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from app.ai import model_manager  # noqa: E402
from app.ai.rag import extractive, rag_pipeline, retriever  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402

SWEEP = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65]

# Chỉ dẫn cho LLM chấm: so câu trả lời với các ý bắt buộc, chỉ trả về một từ
_JUDGE_SYSTEM = (
    "Bạn là giáo viên chấm câu trả lời của trợ giảng AI. Câu trả lời ĐÚNG khi nó trả lời đúng câu hỏi "
    "và thể hiện được các ý chính bắt buộc (diễn đạt khác vẫn tính). Câu trả lời sai kiến thức, lạc đề "
    "hoặc thiếu ý chính là SAI. Chỉ trả về đúng một từ: DUNG hoặc SAI."
)


# Chuẩn hoá để so khớp: dựng sẵn dấu (NFC) + chữ thường
def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").casefold()


# Văn bản có chứa đủ ý mong đợi: mỗi nhóm phải có ít nhất 1 phương án xuất hiện
def _covers(text: str, expect: list[list[str]]) -> bool:
    t = _norm(text)
    return all(any(_norm(alt) in t for alt in group) for group in expect)


# Câu trả lời là lời từ chối "không tìm thấy thông tin" (LLM có thể diễn đạt hơi khác câu mẫu)
def _is_refusal(answer: str) -> bool:
    return "không tìm thấy thông tin phù hợp" in _norm(answer)


# Gọi quy trình RAG; lỗi tạm thời của LLM (quá giới hạn lượt gọi...) thì chờ rồi thử lại, không tính là trả lời sai
def _ask(db, question: str, course_id: int) -> dict:
    for wait in (0, 20, 45, 90):
        time.sleep(wait)
        res = rag_pipeline.answer(db, question, course_id=course_id)
        if not res["answer"].startswith("[Lỗi gọi LLM"):
            return res
    raise SystemExit(f"LLM lỗi liên tục ở câu: {question} | {res['answer'][:300]}")


# LLM chấm 1 câu trả lời theo các ý bắt buộc; lỗi tạm thời thì chờ rồi thử lại
def _judge(question: str, expect: list[list[str]], answer: str) -> bool:
    must = "; ".join(" hoặc ".join(g) for g in expect)
    prompt = (
        f"CÂU HỎI: {question}\n"
        f"Ý CHÍNH BẮT BUỘC: {must}\n"
        f"CÂU TRẢ LỜI CẦN CHẤM: {answer}\n\n"
        "Kết luận (DUNG hoặc SAI):"
    )
    for wait in (0, 20, 45, 90):
        time.sleep(wait)
        # 20 token: với 5 token Gemini chỉ kịp viết "D" (chữ DUNG bị tách thành nhiều token)
        out = model_manager.generate(_JUDGE_SYSTEM, prompt, max_tokens=20)
        if not out.startswith("[Lỗi gọi LLM"):
            return "DUNG" in out.upper() or "đúng" in _norm(out)
    raise SystemExit("LLM chấm lỗi liên tục")


def _load() -> list[dict]:
    with open(os.path.join(HERE, "questions.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _pct(a: int, b: int) -> str:
    return f"{a * 100 / b:.1f}%" if b else "—"


# Dòng báo cáo riêng cho câu hỏi gõ KHÔNG DẤU (questions.jsonl có "variant": "khong_dau"), so với các câu có dấu
def _variant_lines(rows: list[dict]) -> list[str]:
    nd = [r for r in rows if r.get("variant") == "khong_dau"]
    if not nd:
        return []
    acc = [r for r in rows if r.get("variant") != "khong_dau"]
    ok_nd, ok_acc = sum(r["correct"] for r in nd), sum(r["correct"] for r in acc)
    return [
        f"| Câu hỏi có dấu | {_pct(ok_acc, len(acc))} ({ok_acc}/{len(acc)}) |",
        f"| Câu hỏi gõ không dấu | {_pct(ok_nd, len(nd))} ({ok_nd}/{len(nd)}) |",
    ]


def main() -> None:
    cases = _load()
    db = SessionLocal()
    provider = model_manager.active_provider()
    use_judge = "--judge" in sys.argv and provider != "stub"
    k = settings.ai_max_context_chunks
    thr = settings.rag_similarity_threshold
    print(f"Chế độ: {provider} ({model_manager.info()['model']}) | top-k={k} | ngưỡng={thr} | {len(cases)} câu\n")

    rows = []
    for i, c in enumerate(cases, start=1):
        # Truy hồi riêng để đo Hit@k và lấy điểm cosine tốt nhất (dùng cho mô phỏng ngưỡng)
        chunks = retriever.retrieve(db, c["question"], course_id=c["course_id"], k=k)
        best = max((ch["cosine"] for ch in chunks), default=0.0)
        rank = next((r for r, ch in enumerate(chunks, start=1) if c["expect"] and _covers(ch["content"], c["expect"])), None)

        # Chạy đúng quy trình RAG của hệ thống (truy hồi -> ngưỡng -> sinh câu trả lời)
        t0 = time.perf_counter()
        res = _ask(db, c["question"], c["course_id"])
        ms = (time.perf_counter() - t0) * 1000
        answered = not _is_refusal(res["answer"])

        # Nội dung nếu được trả lời bất kể ngưỡng (chỉ tính được ở chế độ offline, dùng cho mô phỏng)
        if provider == "stub" and c["type"] == "in_scope":
            content_any = _covers(extractive.answer(c["question"], chunks) or "", c["expect"])
        else:
            content_any = None

        judged = None
        if c["type"] == "in_scope":
            ok_content = answered and _covers(res["answer"], c["expect"])
            if use_judge and answered:
                judged = _judge(c["question"], c["expect"], res["answer"])
            verdict = "ĐÚNG" if ok_content else ("SAI NỘI DUNG" if answered else "TỪ CHỐI SAI")
        else:
            ok_content = not answered
            judged = ok_content if use_judge else None
            verdict = "TỪ CHỐI ĐÚNG" if not answered else "TRẢ LỜI SAI"
        rows.append({**c, "rank": rank, "best_cosine": round(best, 4), "answered": answered,
                     "correct": ok_content, "judged": judged, "verdict": verdict, "content_any": content_any,
                     "latency_ms": round(ms), "answer": res["answer"].replace("\n", " ")})
        jtxt = "" if judged is None else (" | LLM chấm: đúng" if judged else " | LLM chấm: SAI")
        print(f"{i:3d}. {verdict:13s} cos={best:.3f} [{c['course_id']}] {c['question']}{jtxt}")

    ins = [r for r in rows if r["type"] == "in_scope"]
    outs = [r for r in rows if r["type"] != "in_scope"]
    far = [r for r in outs if r["type"] == "out_of_scope"]
    near = [r for r in outs if r["type"] == "near_miss"]
    n_in = len(ins)

    hit1 = sum(1 for r in ins if r["rank"] == 1)
    hitk = sum(1 for r in ins if r["rank"])
    mrr = sum(1 / r["rank"] for r in ins if r["rank"]) / n_in
    ans_in = sum(r["answered"] for r in ins)
    ok_in = sum(r["correct"] for r in ins)
    wrong_content = sum(1 for r in ins if r["verdict"] == "SAI NỘI DUNG")
    false_refuse = n_in - ans_in
    ref_far = sum(r["correct"] for r in far)
    ref_near = sum(r["correct"] for r in near)
    ok_all = ok_in + ref_far + ref_near
    # Quyết định "trả lời" coi như bài toán phân loại: dương = câu trong phạm vi
    tp, fp = ans_in, sum(r["answered"] for r in outs)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / n_in
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    lat = sorted(r["latency_ms"] for r in rows)
    judge_line = []
    if use_judge:
        ok_in_j = sum(1 for r in ins if r["judged"])
        ok_all_j = ok_in_j + ref_far + ref_near
        judge_line = [
            f"| **Độ chính xác chung — LLM chấm** | **{_pct(ok_all_j, len(rows))}** ({ok_all_j}/{len(rows)}) |",
            f"| Trả lời đúng câu trong phạm vi — LLM chấm | {_pct(ok_in_j, n_in)} ({ok_in_j}/{n_in}) |",
        ]

    lines = [
        f"# Đánh giá AI Tutor (RAG) — {datetime.now():%Y-%m-%d %H:%M}",
        "",
        f"- Chế độ: **{provider}** ({model_manager.info()['model']}), top-k = {k}, ngưỡng từ chối = {thr}",
        f"- Bộ câu hỏi: {len(rows)} câu — {n_in} trong phạm vi, {len(far)} lạc đề, {len(near)} gần lĩnh vực (không có trong tài liệu)",
        "",
        "## Kết quả chính",
        "",
        "| Chỉ số | Giá trị |",
        "|---|---|",
        f"| **Độ chính xác chung** (trả lời đúng + từ chối đúng) | **{_pct(ok_all, len(rows))}** ({ok_all}/{len(rows)}) |",
        f"| Trả lời đúng câu trong phạm vi | {_pct(ok_in, n_in)} ({ok_in}/{n_in}) |",
        *judge_line,
        f"| Độ đúng khi đã trả lời | {_pct(ok_in, ans_in)} ({ok_in}/{ans_in}) |",
        f"| Từ chối đúng câu lạc đề | {_pct(ref_far, len(far))} ({ref_far}/{len(far)}) |",
        f"| Từ chối đúng câu gần lĩnh vực | {_pct(ref_near, len(near))} ({ref_near}/{len(near)}) |",
        *_variant_lines(rows),
        "",
        "## Truy hồi (câu trong phạm vi)",
        "",
        "| Chỉ số | Giá trị |",
        "|---|---|",
        f"| Hit@1 | {_pct(hit1, n_in)} |",
        f"| Hit@{k} | {_pct(hitk, n_in)} |",
        f"| MRR | {mrr:.3f} |",
        "",
        "## Phân tích lỗi",
        "",
        f"- Từ chối sai (có trong tài liệu nhưng không trả lời): {false_refuse}",
        f"- Trả lời nhưng thiếu ý chính: {wrong_content}",
        f"- Trả lời câu không có trong tài liệu: {fp} (lạc đề {len(far) - ref_far}, gần lĩnh vực {len(near) - ref_near})",
        f"- Quyết định trả lời: precision {precision:.3f}, recall {recall:.3f}, F1 {f1:.3f}",
        f"- Thời gian phản hồi: trung bình {sum(lat) / len(lat):.0f} ms, p95 {lat[int(len(lat) * 0.95) - 1]} ms",
        "",
        "## Mô phỏng ngưỡng từ chối",
        "",
        "| Ngưỡng | Trả lời câu trong phạm vi | Trả lời đúng (ước tính) | Trả lời nhầm câu ngoài phạm vi |",
        "|---|---|---|---|",
    ]
    for t in SWEEP:
        a_in = sum(1 for r in ins if r["best_cosine"] >= t)
        a_out = sum(1 for r in outs if r["best_cosine"] >= t)
        if provider == "stub":
            est = _pct(sum(1 for r in ins if r["best_cosine"] >= t and r["content_any"]), n_in)
        else:
            est = "— (cần chạy lại với LLM)"
        mark = " ← hiện tại" if abs(t - thr) < 1e-9 else ""
        lines.append(f"| {t:.2f}{mark} | {_pct(a_in, n_in)} | {est} | {_pct(a_out, len(outs))} |")
    lines += [
        "",
        "Ghi chú: \"đúng\" nghĩa là câu trả lời chứa đủ từ khóa ý chính mong đợi; cách chấm này có thể bỏ sót câu trả lời",
        "đúng nhưng diễn đạt khác (thường gặp khi dùng LLM), nên nên đọc thêm bảng từng câu trong file .csv.",
    ]
    report = "\n".join(lines)
    print("\n" + report)

    # Lưu bảng từng câu + tóm tắt để đưa vào báo cáo
    out_dir = os.path.join(HERE, "results")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, f"{datetime.now():%Y%m%d_%H%M}_{provider}")
    with open(stem + ".md", "w", encoding="utf-8") as f:
        f.write(report + "\n")
    with open(stem + ".csv", "w", encoding="utf-8-sig", newline="") as f:
        cols = ["course_id", "type", "question", "verdict", "judged", "best_cosine", "rank", "latency_ms", "answer"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"\nĐã lưu: {stem}.md và .csv")


if __name__ == "__main__":
    main()
