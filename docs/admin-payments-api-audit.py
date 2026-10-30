r"""Diagnostic audit. Temporary data only; every VNPay query/refund is replaced.

Run from backend: .venv\Scripts\python.exe ../docs/admin-payments-api-audit.py
Observations intentionally record confirmed defects, not a passing release gate.
"""
import datetime as dt
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import threading
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.database import SessionLocal, q_one
from app.core.security import hash_password
from app.main import app
from app.routers import payments

client = TestClient(app, raise_server_exceptions=False)
report = {"checks": [], "findings": {}, "external_gateway_calls": 0}


def check(name, passed):
    assert passed, name
    report["checks"].append(name)


def main():
    sessions = {}
    for role, email in (("admin", "admin@gmail.com"), ("teacher", "an.nguyen@studyonline.vn"), ("student", "em.hoang@gmail.com")):
        login = client.post("/api/auth/login", json={"email": email, "password": "123456"})
        assert login.status_code == 200
        sessions[role] = {"Authorization": "Bearer " + login.json()["token"]}
    admin = sessions["admin"]
    cid = uid = None
    prefix = "ADM-AUDIT-" + uuid.uuid4().hex
    refs = {}
    try:
        with SessionLocal() as db:
            db.execute(text("INSERT INTO users (fullname,email,password,role,is_active) VALUES ('Transaction Audit',:email,:pw,'student',1)"),
                       {"email": prefix.lower()+"@example.test", "pw": hash_password("Temporary123!")})
            db.commit()
            uid = q_one(db, "SELECT id FROM users WHERE email=:email", email=prefix.lower()+"@example.test")["id"]
        created = client.post("/api/courses", headers=sessions["teacher"], json={"title": prefix, "description": "Temporary admin transaction audit"})
        assert created.status_code == 200
        cid = int(created.json()["id"])
        with SessionLocal() as db:
            for index in range(28):
                status = ("completed", "pending", "failed", "refunded")[index % 4]
                ref = prefix + "-" + str(index)
                db.execute(text("INSERT INTO payments (user_id,course_id,amount,method,status,transaction_ref,gateway_txn_no,created_at,paid_at,refunded_at,refund_reason,refund_txn_no) "
                                "VALUES (:u,:c,100000,'vnpay',:status,:ref,:txn,NOW(),:paid,:refunded,:reason,:refund_txn)"),
                           {"u": uid, "c": cid, "status": status, "ref": ref, "txn": str(900000 + index),
                            "paid": dt.datetime.now() if status in ("completed", "refunded") else None,
                            "refunded": dt.datetime.now() if status == "refunded" else None,
                            "reason": "Audit refund reason" if status == "refunded" else None,
                            "refund_txn": "audit-refund-123" if status == "refunded" else None})
                db.commit()
                refs[index] = q_one(db, "SELECT * FROM payments WHERE transaction_ref=:r", r=ref)
        for role in ("teacher", "student"):
            check(role + " cannot manage", client.get("/api/payments/manage", headers=sessions[role]).status_code == 403)
            for endpoint in ("reconcile", "reconcile-pending", "refund"):
                check(role + " cannot " + endpoint, client.post("/api/payments/"+endpoint, headers=sessions[role], json={"id": refs[0]["id"], "reason": "Audit reason"}).status_code == 403)
        check("Guest cannot manage", client.get("/api/payments/manage").status_code == 401)
        result = client.get("/api/payments/manage", headers=admin, params={"course_id": cid, "page_size": 20}).json()
        check("Pagination total and first page", result["pagination"]["total"] == 28 and len(result["data"]) == 20)
        check("Counts accurate", result["counts"] == {"completed": 7, "pending": 7, "failed": 7, "refunded": 7})
        check("Revenue accurate", result["revenue"] == 700000)
        second = client.get("/api/payments/manage", headers=admin, params={"course_id": cid, "page": 2, "page_size": 20}).json()
        check("Second page has no duplicate rows", len(second["data"]) == 8 and not ({r["id"] for r in result["data"]} & {r["id"] for r in second["data"]}))
        for status in ("completed", "pending", "failed", "refunded"):
            filtered = client.get("/api/payments/manage", headers=admin, params={"course_id": cid, "status": status}).json()
            check("Status filter " + status, filtered["pagination"]["total"] == 7 and all(r["status"] == status for r in filtered["data"]))
        exact = client.get("/api/payments/manage", headers=admin, params={"q": refs[3]["transaction_ref"]}).json()
        check("Search transaction reference", len(exact["data"]) == 1 and exact["data"][0]["id"] == refs[3]["id"])
        check("Search gateway number", client.get("/api/payments/manage", headers=admin, params={"course_id": cid, "q": "900003"}).json()["pagination"]["total"] == 1)
        check("Inclusive date bounds", client.get("/api/payments/manage", headers=admin, params={"course_id": cid, "date_from": dt.date.today().isoformat(), "date_to": dt.date.today().isoformat()}).json()["pagination"]["total"] == 28)
        for params in ({"status": "invalid"}, {"date_from": "2026-13-01"}, {"method": "momo"}, {"page": 0}):
            check("Invalid filter rejected: " + str(params), client.get("/api/payments/manage", headers=admin, params=params).status_code in (400, 422))
        missing = [key for key in ("refunded_at", "refund_reason", "refund_txn_no") if key not in exact["data"][0]]
        check("Confirmed missing refund fields", len(missing) == 3)
        report["findings"]["missing_refund_detail"] = {"missing_api_fields": missing, "database_values_present": True}

        # Both requests enter the simulated gateway before either may update the DB.
        barrier = threading.Barrier(2)
        gateway_calls = []
        def simultaneous_refund(**kwargs):
            gateway_calls.append(kwargs["txn_ref"])
            barrier.wait(timeout=10)
            return {"vnp_ResponseCode": "00", "vnp_TransactionNo": "audit-refund"}
        with patch.object(payments.vnpay, "refund_transaction", simultaneous_refund):
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(lambda _: client.post("/api/payments/refund", headers=admin,
                    json={"id": refs[0]["id"], "reason": "Audit concurrent refund", "revoke_access": False}).status_code, range(2)))
        check("Confirmed duplicate gateway calls on concurrent refund", len(gateway_calls) == 2 and sorted(outcomes) == [200, 409])
        report["findings"]["concurrent_refund"] = {"gateway_attempts": len(gateway_calls), "http_statuses": sorted(outcomes), "real_money_movement_tested": False}

        real_execute = payments.execute
        def fail_enrollment_delete(db, sql, **kwargs):
            if sql.startswith("DELETE FROM enrollments") and kwargs.get("c") == cid:
                raise RuntimeError("Simulated enrollment update failure")
            return real_execute(db, sql, **kwargs)
        with SessionLocal() as db:
            # Other completed fixture orders must not prevent the intended revoke path.
            db.execute(text("UPDATE payments SET status='failed' WHERE course_id=:c AND status='completed' AND id<>:id"), {"c": cid, "id": refs[4]["id"]})
            db.execute(text("INSERT IGNORE INTO enrollments (user_id,course_id) VALUES (:u,:c)"), {"u": uid, "c": cid}); db.commit()
        with patch.object(payments.vnpay, "refund_transaction", return_value={"vnp_ResponseCode": "00", "vnp_TransactionNo": "audit-atomic"}), patch.object(payments, "execute", fail_enrollment_delete):
            response = client.post("/api/payments/refund", headers=admin, json={"id": refs[4]["id"], "reason": "Audit failure injection", "revoke_access": True})
        with SessionLocal() as db:
            status = q_one(db, "SELECT status FROM payments WHERE id=:id", id=refs[4]["id"])["status"]
            enrollment = bool(q_one(db, "SELECT id FROM enrollments WHERE user_id=:u AND course_id=:c", u=uid, c=cid))
        check("Confirmed partial local commit on refund failure", response.status_code == 500 and status == "refunded" and enrollment)
        report["findings"]["non_atomic_refund"] = {"http_status": response.status_code, "payment_status": status, "enrollment_retained": enrollment}

        # Isolate bulk reconciliation to this fixture's pending rows. Never touch real orders.
        real_q_all = payments.q_all
        bulk_calls = []
        def scoped_q_all(db, sql, **kwargs):
            if sql == "SELECT * FROM payments WHERE status = 'pending' ORDER BY id":
                return real_q_all(db, "SELECT * FROM payments WHERE status='pending' AND course_id=:c ORDER BY id", c=cid)
            return real_q_all(db, sql, **kwargs)
        def fake_query(**kwargs):
            assert kwargs["txn_ref"].startswith(prefix)
            bulk_calls.append(kwargs["txn_ref"])
            return {"vnp_ResponseCode": "91", "vnp_Message": "Not found"}
        filtered = client.get("/api/payments/manage", headers=admin, params={"course_id": cid, "q": "900001"}).json()
        with patch.object(payments, "q_all", scoped_q_all), patch.object(payments.vnpay, "query_transaction", fake_query):
            response = client.post("/api/payments/reconcile-pending", headers=admin)
        check("Confirmed bulk reconcile ignores displayed search", filtered["counts"]["pending"] == 1 and len(bulk_calls) == 7 and response.status_code == 200)
        report["findings"]["bulk_filter_scope"] = {"visible_pending": 1, "fixture_pending_queried": len(bulk_calls), "isolated_to_fixture": True}
    finally:
        with SessionLocal() as db:
            if cid:
                db.execute(text("DELETE FROM payments WHERE course_id=:c"), {"c": cid})
                db.execute(text("DELETE FROM enrollments WHERE course_id=:c"), {"c": cid})
                db.execute(text("DELETE FROM courses WHERE id=:c"), {"c": cid})
            if uid:
                db.execute(text("DELETE FROM users WHERE id=:u"), {"u": uid})
            db.commit()
        report["temporary_data_cleaned"] = True
        target = Path(__file__).with_name("admin-payments-api-audit.json")
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"checks": len(report["checks"]), "findings": len(report["findings"]), "temporary_data_cleaned": True}))


if __name__ == "__main__":
    main()
