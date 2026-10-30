"""Đo câu trả lời đầu tiên của AI thật, lưu nguồn để chấm từng câu; không sửa/tinh chỉnh AI khi đo.

Chạy từ backend: .venv/Scripts/python ../docs/ai-accuracy-current-run.py --phase baseline
Các phase: baseline (40 kiến thức + 10 ngoài phạm vi), extra (10 câu mới), clarification (8 câu thiếu dữ kiện).
Không tự chấm đúng bằng từ khóa. Kết quả cần được đối chiếu với rubric và các trang nguồn đã lưu.
"""
from __future__ import annotations

import argparse
import concurrent.futures
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
import threading
import time
import uuid

import httpx

sys.stdout.reconfigure(encoding="utf-8")
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent / "backend"))
from app.core.database import SessionLocal, execute, q_all, q_one, q_scalar
from app.core.config import settings

ACCOUNTS = {"student_em": "em.hoang@gmail.com", "student_phuong": "phuong.vu@gmail.com",
            "teacher_an": "an.nguyen@studyonline.vn", "teacher_binh": "binh.tran@studyonline.vn", "admin": "admin@gmail.com"}
PREFIX = "ai-accuracy-current-2026-10-30"
NO_ANSWER = "Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học."


def dump(file, data):
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def counts():
    with SessionLocal() as db:
        return {table: q_scalar(db, "SELECT COUNT(*) FROM " + table)
                for table in ("ai_conversations", "ai_messages", "documents", "document_chunks")}


def version():
    files = ["ai/rag/clarification.py", "ai/rag/rag_pipeline.py", "ai/tutor.py", "routers/ai.py"]
    return {file: hashlib.sha256((D.parent / "backend/app" / file).read_bytes()).hexdigest() for file in files}


def evidence(sources, course_id):
    rows = []
    with SessionLocal() as db:
        for source in sources:
            doc = q_one(db, "SELECT id,course_id,lesson_id,title FROM documents WHERE id=:id", id=source.get("document_id"))
            chunks = q_all(db, "SELECT id,page,content FROM document_chunks WHERE document_id=:d "
                           "AND (:p IS NULL OR page=:p) ORDER BY chunk_index,id", d=source.get("document_id"), p=source.get("page"))
            rows.append({"citation": source, "document": doc, "chunks": chunks,
                         "metadata_valid": bool(doc and doc["course_id"] == course_id and chunks)})
    return rows


def plan_for(phase):
    if phase == "baseline":
        plan = json.loads((D / "ai-accuracy-fixed-plan.json").read_text(encoding="utf-8"))
        return [{**p, "group": "boundary" if p["gold"] == "refuse" else "knowledge", "sample": "fixed"} for p in plan]
    if phase == "extra":
        return [{**p, "group": "knowledge", "sample": "new"} for p in
                json.loads((D / (PREFIX + "-new-plan.json")).read_text(encoding="utf-8"))]
    questions = [("Giải thích giúp em", "topic"), ("giai thich giup em", "topic"),
                 ("code em bị lỗi", "debug"), ("Giải câu 2", "exercise"), ("Nên chọn cái nào?", "comparison"),
                 ("Nó hoạt động thế nào?", "topic"), ("Cho ví dụ đi", "topic"), ("Hướng dẫn làm bài này", "exercise")]
    roles = list(ACCOUNTS)
    return [{"id": f"clarification-{i:02}", "role": roles[(i - 1) % len(roles)], "course_id": 1,
             "reference_lesson": None, "question": question, "gold": kind, "group": "clarification", "sample": "control"}
            for i, (question, kind) in enumerate(questions, 1)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("baseline", "extra", "clarification"), required=True)
    args = parser.parse_args()
    target = D / (PREFIX + "-" + args.phase)
    results_file = target.with_name(target.name + "-results.json")
    state_file = target.with_name(target.name + "-state.json")
    if results_file.exists():
        raise SystemExit("Đã có kết quả phase này; giữ nguyên câu trả lời đầu tiên, không ghi đè.")
    plan = plan_for(args.phase)
    dump(target.with_name(target.name + "-plan.json"), plan)
    run_id = uuid.uuid4().hex[:12]
    state = {"run_id": run_id, "phase": args.phase, "started_at": datetime.now().astimezone().isoformat(),
             "max_parallel": 2, "first_response_only": True, "counts_before": counts(), "code_before": version(),
             "thresholds": {"offline": settings.rag_similarity_threshold, "llm_similarity": settings.rag_llm_min_similarity,
                            "llm_lexical": settings.rag_llm_min_lexical}, "accounts": ACCOUNTS}
    clients, users, rows = {}, {}, []
    lock = threading.Lock()
    for role, email in ACCOUNTS.items():
        client = httpx.Client(base_url="http://127.0.0.1:8080", timeout=210)
        response = client.post("/api/auth/login", json={"email": email, "password": "123456"})
        response.raise_for_status()
        auth = response.json()
        client.headers["Authorization"] = "Bearer " + auth["token"]
        clients[role], users[role] = client, auth["user"]["id"]
    state["engine"] = clients["admin"].get("/api/ai/status").json().get("data")
    dump(state_file, state)

    def ask(p):
        client, user_id = clients[p["role"]], users[p["role"]]
        # Tạo trước một hội thoại rỗng có mã audit duy nhất để luôn dọn được đúng id kể cả request timeout.
        title = f"AUDIT {run_id} {p['id']}"
        with SessionLocal() as db:
            conv_id = int(execute(db, "INSERT INTO ai_conversations(user_id,course_id,title) VALUES(:u,:c,:t)",
                                  u=user_id, c=p["course_id"], t=title).lastrowid)
        row = {**p, "conversation_id": conv_id}
        started = time.perf_counter()
        try:
            response = client.post("/api/ai/chat", json={"course_id": p["course_id"], "conversation_id": conv_id, "message": p["question"]})
            row["http_status"] = response.status_code
            response.raise_for_status()
            data = response.json().get("data", {})
            row.update(answer=data.get("answer", ""), sources=data.get("sources", []), used_context=data.get("used_context"),
                       needs_clarification=data.get("needs_clarification", False), clarification_kind=data.get("clarification_kind"))
            row["elapsed_seconds"] = round(time.perf_counter() - started, 3)
            row["refused"] = "không tìm thấy thông tin phù hợp" in row["answer"].lower()
            row["fallback"] = "tạm gián đoạn" in row["answer"]
            row["llm_error"] = row["answer"].startswith("[Lỗi gọi LLM")
            row["citation_evidence"] = evidence(row["sources"], p["course_id"])
            row["citation_metadata_valid"] = all(e["metadata_valid"] for e in row["citation_evidence"])
        except Exception as exc:
            row["error"] = type(exc).__name__ + ": " + str(exc)
            row.setdefault("elapsed_seconds", round(time.perf_counter() - started, 3))
        finally:
            # Chỉ xóa hội thoại do đúng ca kiểm thử này tạo, tuyệt đối không xóa theo email/ngày.
            with SessionLocal() as db:
                execute(db, "DELETE FROM ai_conversations WHERE id=:id AND user_id=:u AND title=:t", id=conv_id, u=user_id, t=title)
                row["cleaned"] = q_scalar(db, "SELECT COUNT(*) FROM ai_conversations WHERE id=:id", id=conv_id) == 0
            with lock:
                rows.append(row)
                dump(results_file, sorted(rows, key=lambda r: r["id"]))
                print(json.dumps({"done": len(rows), "total": len(plan), "id": p["id"], "seconds": row["elapsed_seconds"],
                                  "refused": row.get("refused"), "clarification": row.get("needs_clarification"),
                                  "error": row.get("error")}, ensure_ascii=False), flush=True)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for f in concurrent.futures.as_completed([pool.submit(ask, p) for p in plan]):
                f.result()
    finally:
        for client in clients.values():
            client.close()
        state.update(finished_at=datetime.now().astimezone().isoformat(), counts_after=counts(), code_after=version(), recorded=len(rows))
        state["code_unchanged"] = state["code_before"] == state["code_after"]
        state["counts_restored"] = state["counts_before"] == state["counts_after"]
        dump(state_file, state)


if __name__ == "__main__":
    main()
