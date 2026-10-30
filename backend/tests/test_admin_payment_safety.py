"""Temporary transactions; simulated gateway; no real financial calls."""
import sys
import uuid
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, execute, q_one
from app.core.config import settings
from app.main import app
from app.services import vnpay
from app.routers import payments
from test_api import course, tokens

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def order(course, tokens, monkeypatch):
    headers = {role: {"Authorization": "Bearer " + token} for role, token in tokens.items()}
    db = SessionLocal()
    uid = q_one(db, "SELECT id FROM users WHERE email='em.hoang@gmail.com'")["id"]
    ref = "SAFETY-" + uuid.uuid4().hex
    pid = int(execute(db, "INSERT INTO payments (user_id,course_id,method,status,amount,transaction_ref,gateway_txn_no,paid_at) "
                      "VALUES (:u,:c,'vnpay','completed',100000,:ref,'555',NOW())", u=uid, c=course, ref=ref).lastrowid)
    execute(db, "INSERT IGNORE INTO enrollments (user_id,course_id) VALUES (:u,:c)", u=uid, c=course)
    success = {"vnp_ResponseCode": "00", "vnp_TransactionStatus": "00", "vnp_TransactionType": "02", "vnp_TxnRef": ref, "vnp_Amount": "10000000", "vnp_TransactionNo": "777"}
    gateway = Mock(return_value=success)
    query = Mock(side_effect=vnpay.VnpayQueryError("simulated unavailable"))
    monkeypatch.setattr(vnpay, "refund_transaction", gateway)
    monkeypatch.setattr(vnpay, "query_transaction", query)
    try:
        yield {"id": pid, "uid": uid, "course": course, "ref": ref, "db": db, "h": headers, "gateway": gateway, "query": query, "success": success}
    finally:
        db.rollback()
        execute(db, "DELETE FROM payments WHERE course_id=:c", c=course)
        execute(db, "DELETE FROM enrollments WHERE course_id=:c", c=course)
        db.close()


def post(o, endpoint="refund", role="admin", **body):
    return client.post("/api/payments/" + endpoint, headers=o["h"][role], json={"id": o["id"], "reason": "Refund safety test", "revoke_access": True, **body})


def detail(o):
    res = client.get("/api/payments/detail", headers=o["h"]["admin"], params={"id": o["id"]})
    assert res.status_code == 200
    return res.json()["data"]


def test_refund_completion_and_receipt(order):
    o = order
    assert post(o).status_code == 200
    data = detail(o)
    assert data["status"] == "refunded" and not data["enrolled"]
    assert data["refund_operation"]["state"] == "completed" and data["refund_txn_no"] == "777"
    manage = client.get("/api/payments/manage", headers=o["h"]["admin"], params={"course_id": o["course"]}).json()["data"][0]
    assert all(manage[k] for k in ("refunded_at", "refund_reason", "refund_txn_no"))
    assert post(o).status_code == 409 and o["gateway"].call_count == 1


def test_concurrent_refund_sends_once(order):
    o = order
    entered, release = threading.Event(), threading.Event()
    def blocked(**kw):
        entered.set(); assert release.wait(10)
        return o["success"]
    o["gateway"].side_effect = blocked
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(post, o)
        assert entered.wait(10)
        try:
            assert pool.submit(post, o).result(10).status_code == 409
        finally:
            release.set()
        assert first.result(10).status_code == 200
    assert o["gateway"].call_count == 1


def test_timeout_and_original_payment_are_not_refund_confirmation(order):
    o = order
    o["gateway"].side_effect = vnpay.VnpayQueryError("timeout")
    assert post(o).status_code == 200
    assert detail(o)["refund_operation"]["state"] == "unknown"
    assert post(o).status_code == 409
    o["query"].side_effect = None
    o["query"].return_value = {**o["success"], "vnp_TransactionType": "01"}
    post(o, "refund-reconcile")
    assert detail(o)["status"] == "completed" and detail(o)["enrolled"]
    o["query"].return_value = o["success"]
    assert post(o, "refund-reconcile").status_code == 200
    assert detail(o)["status"] == "refunded" and o["gateway"].call_count == 1


def test_atomic_rollback_and_local_recovery(order, monkeypatch):
    o = order
    original = Session.execute
    inject = {"once": True}
    def fail(self, statement, params=None, *args, **kwargs):
        if str(statement).startswith("DELETE FROM enrollments") and params and params.get("c") == o["course"] and inject["once"]:
            inject["once"] = False
            raise RuntimeError("simulated database failure")
        return original(self, statement, params, *args, **kwargs)
    monkeypatch.setattr(Session, "execute", fail)
    assert post(o).status_code == 503
    data = detail(o)
    assert data["status"] == "completed" and data["enrolled"] and data["refund_operation"]["state"] == "confirmed"
    assert post(o, "refund-reconcile").status_code == 200
    assert detail(o)["status"] == "refunded" and not detail(o)["enrolled"]
    assert o["gateway"].call_count == 1 and o["query"].call_count == 0


@pytest.mark.parametrize("status", ["05", "06", None])
def test_gateway_acceptance_is_not_final(order, status):
    o = order
    o["gateway"].return_value = {**o["success"], "vnp_TransactionStatus": status}
    post(o)
    data = detail(o)
    assert data["status"] == "completed" and data["enrolled"] and data["refund_operation"]["state"] == "pending"
    assert post(o).status_code == 409


@pytest.mark.parametrize("key,value", [("vnp_TxnRef", "other"), ("vnp_Amount", "1"), ("vnp_TransactionType", "03")])
def test_mismatched_confirmation_does_not_change_access(order, key, value):
    o = order
    o["gateway"].return_value = {**o["success"], key: value}
    post(o)
    assert detail(o)["status"] == "completed" and detail(o)["enrolled"]
    assert post(o).status_code == 409


def test_known_rejection_allows_explicit_retry(order):
    o = order
    o["gateway"].return_value = {"vnp_ResponseCode": "95"}
    assert post(o).status_code == 409
    o["gateway"].return_value = o["success"]
    assert post(o).status_code == 200
    assert o["gateway"].call_args_list[0].kwargs["request_id"] != o["gateway"].call_args_list[1].kwargs["request_id"]


@pytest.mark.parametrize("revoke,another", [(False, False), (True, True)])
def test_access_preserved_when_requested_or_another_paid_order(order, revoke, another):
    o = order
    if another:
        execute(o["db"], "INSERT INTO payments (user_id,course_id,method,status,amount,transaction_ref) VALUES (:u,:c,'vnpay','completed',100000,:ref)", u=o["uid"], c=o["course"], ref=o["ref"] + "-another")
    assert post(o, revoke_access=revoke).status_code == 200
    assert detail(o)["enrolled"]


@pytest.mark.parametrize("role", ["student", "teacher"])
@pytest.mark.parametrize("endpoint", ["refund", "refund-reconcile", "reconcile-pending"])
def test_admin_only(order, role, endpoint):
    assert post(order, endpoint, role).status_code == 403
    assert order["gateway"].call_count == 0


def test_no_invalid_manual_refund_and_strict_boolean(order):
    o = order
    assert post(o, revoke_access="false").status_code == 400
    execute(o["db"], "UPDATE payments SET gateway_txn_no='0' WHERE id=:id", id=o["id"])
    assert post(o).status_code == 409 and o["gateway"].call_count == 0


def test_missing_gateway_config_does_not_create_uncertain_operation(order, monkeypatch):
    monkeypatch.setattr(settings, "vnpay_tmn_code", "")
    assert post(order).status_code == 503
    assert detail(order)["refund_operation"] is None and order["gateway"].call_count == 0


def test_bulk_reconcile_respects_course_search_dates_and_pending(order, monkeypatch):
    o = order
    selected = []
    ids = []
    for suffix, status in (("include", "pending"), ("exclude", "pending"), ("include-done", "completed")):
        ids.append(int(execute(o["db"], "INSERT INTO payments (user_id,course_id,method,status,amount,transaction_ref) VALUES (:u,:c,'vnpay',:status,100000,:ref)", u=o["uid"], c=o["course"], status=status, ref=o["ref"] + "-" + suffix).lastrowid))
    def observe(db, row):
        assert row["course_id"] == o["course"]  # Never mutate unrelated transactions.
        selected.append(row["id"])
        return "waiting", ""
    monkeypatch.setattr(payments, "reconcile_payment", observe)
    response = client.post("/api/payments/reconcile-pending", headers=o["h"]["admin"], json={"course_id": o["course"], "q": o["ref"] + "-include"})
    assert response.status_code == 200 and response.json()["processed"] == 1 and selected == [ids[0]]
    selected.clear()
    response = client.post("/api/payments/reconcile-pending", headers=o["h"]["admin"], json={"course_id": o["course"], "date_to": "2000-01-01"})
    assert response.status_code == 200 and not selected


@pytest.mark.parametrize("filters", [{"date_from": "invalid"}, {"date_from": "2026-12-31", "date_to": "2026-01-01"}, {"date_to": "9999-12-31"}])
def test_filter_validation_shared_by_listing_and_bulk(order, filters):
    assert client.get("/api/payments/manage", headers=order["h"]["admin"], params=filters).status_code == 400
    assert client.post("/api/payments/reconcile-pending", headers=order["h"]["admin"], json=filters).status_code == 400


@pytest.mark.parametrize("kind", ["refund", "query"])
def test_transport_signature_correlation_and_stable_request_id(monkeypatch, kind):
    import httpx
    monkeypatch.setattr(settings, "vnpay_tmn_code", "TEST")
    monkeypatch.setattr(settings, "vnpay_hash_secret", "TEST_SECRET")
    payload = {"vnp_Command": "refund" if kind == "refund" else "querydr", "vnp_TmnCode": "TEST", "vnp_TxnRef": "ref", "vnp_ResponseCode": "00"}
    sent = []
    def fake(*args, **kwargs):
        sent.append(kwargs["json"])
        return httpx.Response(200, json=payload, request=httpx.Request("POST", "https://gateway.test"))
    monkeypatch.setattr(httpx, "post", fake)
    def call():
        return vnpay.refund_transaction(txn_ref="ref", amount=100000, transaction_no="555", transaction_date="20261030120000", created_by="admin", reason="test refund", request_id="stable") if kind == "refund" else vnpay.query_transaction(txn_ref="ref", transaction_date="20261030120000")
    with pytest.raises(vnpay.VnpayQueryError): call()
    fields = vnpay._REFUND_RSP_FIELDS if kind == "refund" else vnpay._QUERY_RSP_FIELDS
    payload["vnp_TxnRef"] = "wrong"
    payload["vnp_SecureHash"] = vnpay._pipe_sign(payload, fields)
    with pytest.raises(vnpay.VnpayQueryError): call()
    payload["vnp_TxnRef"] = "ref"; payload["vnp_SecureHash"] = vnpay._pipe_sign(payload, fields)
    assert call()["vnp_TxnRef"] == "ref"
    if kind == "refund": assert all(request["vnp_RequestId"] == "stable" for request in sent)
