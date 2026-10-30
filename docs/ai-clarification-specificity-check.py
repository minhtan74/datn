"""Đo riêng lỗi hỏi lại thừa: 3 ca hồi quy thật và 6 ca vẫn cần hỏi thêm. Không ghi đè bộ đo cũ."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
import time
import uuid

import httpx

sys.stdout.reconfigure(encoding="utf-8")
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent / "backend"))
from app.core.database import SessionLocal, execute, q_all, q_scalar
from app.ai.rag import clarification

PLAN = [
    ("regression-os", "student_phuong", 7, "Máy một lõi có làm đồng thời nhiều việc được không, điều đó có phải song song thật trên lõi đó không?", None),
    ("regression-map", "teacher_an", 3, "HashMap.put cùng một khóa hai lần có tự báo lỗi trùng không? Nếu cần từ chối trùng nên làm gì?", None),
    ("regression-testing", "teacher_binh", 515, "Sau khi sửa lỗi ghi danh trùng, chạy lại đúng ca từng gây lỗi đã thay thế được kiểm thử hồi quy chưa? Phân biệt confirmation testing với regression testing.", None),
    ("missing-topic", "student_em", 1, "Giải thích giúp em", "topic"),
    ("missing-code", "student_em", 1, "Code Python của em bị lỗi", "debug"),
    ("missing-exercise", "student_em", 1, "Giải câu 2 giúp em", "exercise"),
    ("missing-comparison", "student_em", 1, "Nên chọn cái nào?", "comparison"),
    ("missing-reference", "student_em", 1, "Trong Python, nó là gì?", "topic"),
    ("missing-function", "student_em", 1, "Hàm này hoạt động thế nào?", "topic"),
]
ACCOUNTS = {"student_em": "em.hoang@gmail.com", "student_phuong": "phuong.vu@gmail.com",
            "teacher_an": "an.nguyen@studyonline.vn", "teacher_binh": "binh.tran@studyonline.vn"}


def counts():
    with SessionLocal() as db:
        return {t: q_scalar(db, "SELECT COUNT(*) FROM " + t) for t in ("ai_conversations", "ai_messages", "documents", "document_chunks")}


def main():
    dest = D / "ai-clarification-specificity-results.json"
    if dest.exists():
        raise SystemExit("Đã có kết quả; không ghi đè câu trả lời đầu tiên.")
    clients, users, rows = {}, {}, []
    run = uuid.uuid4().hex[:12]
    state = {"started_at": datetime.now().astimezone().isoformat(), "before": counts(), "cases": rows}
    # Gating toàn bộ 50 câu kiến thức đã đóng băng, không cần gọi LLM để kiểm tra bước này.
    baseline = json.loads((D / "ai-accuracy-fixed-plan.json").read_text(encoding="utf-8"))
    new = json.loads((D / "ai-accuracy-current-2026-10-30-new-plan.json").read_text(encoding="utf-8"))
    knowledge = [r for r in baseline if r["gold"] != "refuse"] + new
    state["knowledge_gate"] = [{"id": r["id"], "question": r["question"], "clarification_kind": clarification.request_kind(r["question"])} for r in knowledge]
    state["code_sha256"] = hashlib.sha256((D.parent / "backend/app/ai/rag/clarification.py").read_bytes()).hexdigest()
    try:
        for role, email in ACCOUNTS.items():
            client = httpx.Client(base_url="http://127.0.0.1:8080", timeout=150)
            res = client.post("/api/auth/login", json={"email": email, "password": "123456"})
            res.raise_for_status()
            auth = res.json()
            client.headers["Authorization"] = "Bearer " + auth["token"]
            clients[role], users[role] = client, auth["user"]["id"]
        state["engine"] = clients["teacher_an"].get("/api/ai/status").json()["data"]
        for case_id, role, course_id, question, expected_kind in PLAN:
            title = f"AUDIT specificity {run} {case_id}"
            with SessionLocal() as db:
                conv_id = int(execute(db, "INSERT INTO ai_conversations(user_id,course_id,title) VALUES(:u,:c,:t)", u=users[role], c=course_id, t=title).lastrowid)
            row = {"id": case_id, "role": role, "course_id": course_id, "question": question, "expected_kind": expected_kind}
            started = time.perf_counter()
            try:
                response = clients[role].post("/api/ai/chat", json={"course_id": course_id, "conversation_id": conv_id, "message": question})
                row.update(http_status=response.status_code, elapsed_seconds=round(time.perf_counter() - started, 3), data=response.json().get("data", {}))
                data = row["data"]
                row["intent_passed"] = (response.status_code == 200 and bool(data.get("answer")) and
                    (not data.get("needs_clarification") and data.get("used_context") and bool(data.get("sources")) if expected_kind is None else
                     data.get("needs_clarification") is True and data.get("clarification_kind") == expected_kind and data.get("sources") == []))
                row["citation_evidence"] = []
                with SessionLocal() as db:
                    for s in data.get("sources", []):
                        row["citation_evidence"].append({"source": s, "chunks": q_all(db,
                            "SELECT id,course_id,document_id,page,content FROM document_chunks WHERE document_id=:d AND (:p IS NULL OR page=:p) ORDER BY id",
                            d=s.get("document_id"), p=s.get("page"))})
            except Exception as exc:
                row.update(intent_passed=False, error=type(exc).__name__ + ": " + str(exc))
            finally:
                with SessionLocal() as db:
                    execute(db, "DELETE FROM ai_conversations WHERE id=:id AND title=:t AND user_id=:u", id=conv_id, t=title, u=users[role])
                rows.append(row)
                print(json.dumps({k: row.get(k) for k in ("id", "http_status", "elapsed_seconds", "intent_passed", "error")}, ensure_ascii=False), flush=True)
                dest.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        for client in clients.values():
            client.close()
        state.update(after=counts(), finished_at=datetime.now().astimezone().isoformat())
        state["data_restored"] = state["before"] == state["after"]
        state["knowledge_gate_passed"] = sum(r["clarification_kind"] is None for r in state["knowledge_gate"])
        dest.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
