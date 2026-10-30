"""Admin-only refund safety. Claim before sending; recover uncertain outcomes by query."""
import secrets
from decimal import Decimal
from sqlalchemy import text
from app.core.database import q_one
from app.core.responses import ApiError
from app.services import vnpay

ACTIVE = {"sending", "pending", "unknown", "confirmed"}


def payment(db, pid):
    row = q_one(db, "SELECT * FROM payments WHERE id=:id FOR UPDATE", id=pid)
    if not row:
        raise ApiError("Không tìm thấy giao dịch.", 404)
    return row


def operation(db, pid):
    return q_one(db, "SELECT * FROM payment_refund_operations WHERE payment_id=:id FOR UPDATE", id=pid)


def change(db, pid, actor, state, message, code=None, txn=None):
    db.execute(text("UPDATE payment_refund_operations SET state=:state,message=:msg,gateway_code=COALESCE(:code,gateway_code),"
                    "gateway_txn_no=COALESCE(:txn,gateway_txn_no),updated_at=NOW() WHERE payment_id=:id"),
               {"id": pid, "state": state, "msg": message, "code": code, "txn": txn})
    db.execute(text("INSERT INTO payment_refund_operation_events (payment_id,actor_id,state,message) VALUES (:id,:actor,:state,:msg)"),
               {"id": pid, "actor": actor, "state": state, "msg": message})


def finalize(db, pid, actor):
    # Serialize access changes for the same learner before locking orders.
    owner = q_one(db, "SELECT user_id FROM payments WHERE id=:id", id=pid)
    if not owner:
        raise ApiError("Không tìm thấy giao dịch.", 404)
    q_one(db, "SELECT id FROM users WHERE id=:id FOR UPDATE", id=owner["user_id"])
    p = payment(db, pid)
    op = operation(db, pid)
    if op["state"] == "completed":
        db.rollback()
        return False
    if op["state"] != "confirmed" or p["status"] != "completed":
        raise ApiError("Chưa đủ điều kiện hoàn tất hoàn tiền.", 409)
    db.execute(text("UPDATE payments SET status='refunded',refunded_at=NOW(),refunded_by=:admin,refund_reason=:reason,"
                    "refund_txn_no=:txn,note='Đã xác nhận hoàn tiền qua VNPay.' WHERE id=:id"),
               {"id": pid, "admin": op["admin_id"], "reason": op["reason"], "txn": op["gateway_txn_no"]})
    another = q_one(db, "SELECT id FROM payments WHERE user_id=:u AND course_id=:c AND status='completed' AND id<>:id LIMIT 1 FOR UPDATE",
                    u=p["user_id"], c=p["course_id"], id=pid)
    revoked = False
    if op["revoke_access"] and not another:
        revoked = bool(db.execute(text("DELETE FROM enrollments WHERE user_id=:u AND course_id=:c"), {"u": p["user_id"], "c": p["course_id"]}).rowcount)
    change(db, pid, actor, "completed", "Đã xác nhận hoàn tiền và cập nhật quyền học.")
    db.commit()
    return revoked


def result(db, pid, actor, response, *, query=False):
    p = payment(db, pid)
    op = operation(db, pid)
    if op["state"] in ("completed", "confirmed"):
        db.rollback()
        return finalize(db, pid, actor) if op["state"] == "confirmed" else False
    code, status = response.get("vnp_ResponseCode"), response.get("vnp_TransactionStatus")
    full = response.get("vnp_TransactionType") == "02"
    if code == "00" and (not query or full):
        try:
            matches = response.get("vnp_TxnRef") == p["transaction_ref"] and Decimal(str(response.get("vnp_Amount"))) == Decimal(str(p["amount"])) * 100
        except Exception:
            matches = False
        if not matches:
            change(db, pid, actor, "unknown", "Phản hồi không khớp mã đơn/số tiền. Cần đối soát.")
        elif full and status == "00" and response.get("vnp_TransactionNo") not in (None, "", "0"):
            change(db, pid, actor, "confirmed", "VNPay xác nhận hoàn tiền toàn phần.", code, response["vnp_TransactionNo"])
        elif status == "09":
            change(db, pid, actor, "failed", "VNPay từ chối hoàn tiền.", code)
        else:
            change(db, pid, actor, "pending", "VNPay đã tiếp nhận, đang chờ kết quả cuối cùng.", code)
    elif code == "94":
        change(db, pid, actor, "pending", "VNPay đang xử lý yêu cầu trước đó. Chỉ đối soát, không gửi lại.", code)
    elif not query and code in ("02", "03", "91", "95", "97"):
        change(db, pid, actor, "failed", "VNPay từ chối yêu cầu (mã " + code + ").", code)
    else:
        change(db, pid, actor, "unknown", "Chưa xác định được kết quả. Hãy đối soát, không gửi lại hoàn tiền.", code)
    db.commit()  # Preserve the gateway receipt even if local finalization fails.
    op = operation(db, pid)
    confirmed = op["state"] == "confirmed"
    db.rollback()
    if confirmed:
        try:
            return finalize(db, pid, actor)
        except Exception:
            db.rollback()
            raise ApiError("Đã có xác nhận VNPay; cập nhật quyền học chưa hoàn tất. Bấm Đối soát hoàn tiền để hoàn tất, không gửi lại tiền.", 503)
    return False


def send(db, pid, user, reason, revoke, ip):
    if not isinstance(reason, str) or not 5 <= len(reason.strip()) <= 255:
        raise ApiError("Lý do cần từ 5 đến 255 ký tự.")
    if not isinstance(revoke, bool):
        raise ApiError("Lựa chọn thu hồi quyền học phải là true hoặc false.")
    if not vnpay.is_configured():
        raise ApiError("Chưa cấu hình VNPay. Chưa gửi yêu cầu hoàn tiền.", 503)
    p = payment(db, pid)
    if p["status"] != "completed" or p["method"] != "vnpay" or str(p.get("gateway_txn_no") or "") in ("", "0"):
        raise ApiError("Cần đơn VNPay thành công có mã giao dịch hợp lệ. Không ghi nhận hoàn tiền thủ công.", 409)
    op = operation(db, pid)
    if op and op["state"] != "failed":
        raise ApiError("Yêu cầu đã được gửi hoặc chưa rõ kết quả. Hãy đối soát hoàn tiền, không gửi lại.", 409)
    rid = secrets.token_hex(16)
    db.execute(text("INSERT INTO payment_refund_operations (payment_id,request_id,state,reason,admin_id,revoke_access,message) "
                    "VALUES (:id,:rid,'sending',:reason,:admin,:revoke,'Đang gửi yêu cầu tới VNPay.') "
                    "ON DUPLICATE KEY UPDATE request_id=:rid,reason=:reason,admin_id=:admin,revoke_access=:revoke"),
               {"id": pid, "rid": rid, "reason": reason.strip(), "admin": user["id"], "revoke": revoke})
    change(db, pid, user["id"], "sending", "Đang gửi yêu cầu tới VNPay.")
    db.commit()  # Durable cross-worker claim, before any gateway side effect.
    try:
        response = vnpay.refund_transaction(txn_ref=p["transaction_ref"], amount=float(p["amount"]), transaction_no=p["gateway_txn_no"],
            transaction_date=p.get("vnp_create_date") or p["created_at"].strftime("%Y%m%d%H%M%S"), created_by=user["email"],
            reason=reason.strip(), ip_addr=ip, request_id=rid)
    except Exception:
        payment(db, pid)
        if operation(db, pid)["state"] == "sending":
            change(db, pid, user["id"], "unknown", "Chưa nhận được phản hồi hợp lệ. Hãy đối soát, không gửi lại hoàn tiền.")
            db.commit()
        return False
    return result(db, pid, user["id"], response)


def reconcile(db, pid, user):
    p = payment(db, pid)
    op = operation(db, pid)
    if not op or op["state"] not in ACTIVE:
        raise ApiError("Không có yêu cầu hoàn tiền cần đối soát.", 409)
    confirmed = op["state"] == "confirmed"
    db.rollback()
    if confirmed:
        return finalize(db, pid, user["id"])
    try:
        response = vnpay.query_transaction(txn_ref=p["transaction_ref"], transaction_date=p.get("vnp_create_date") or p["created_at"].strftime("%Y%m%d%H%M%S"))
    except Exception:
        return False
    return result(db, pid, user["id"], response, query=True)
