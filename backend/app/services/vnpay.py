"""Cổng thanh toán VNPay (API phiên bản 2.1.0) — tạo URL thanh toán và kiểm tra chữ ký.

Chữ ký: sắp xếp các tham số vnp_* theo tên, nối "key=quote_plus(value)" bằng "&",
rồi HMAC-SHA512 với chuỗi bí mật (vnp_HashSecret) — giống bản mẫu Python của VNPay.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
from urllib.parse import quote_plus

from app.core.config import settings

# VNPay yêu cầu thời gian theo giờ Việt Nam (GMT+7)
_VN_TZ = dt.timezone(dt.timedelta(hours=7))
# Đơn thanh toán hết hạn sau 15 phút nếu học viên không thanh toán
EXPIRE_MINUTES = 15

# Ý nghĩa các mã phản hồi thường gặp (vnp_ResponseCode) — hiển thị cho học viên
RESPONSE_MESSAGES = {
    "00": "Giao dịch thành công.",
    "07": "Trừ tiền thành công nhưng giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).",
    "09": "Thẻ/Tài khoản chưa đăng ký dịch vụ InternetBanking tại ngân hàng.",
    "10": "Xác thực thông tin thẻ/tài khoản không đúng quá 3 lần.",
    "11": "Đã hết hạn chờ thanh toán. Vui lòng thực hiện lại giao dịch.",
    "12": "Thẻ/Tài khoản bị khóa.",
    "13": "Nhập sai mật khẩu xác thực giao dịch (OTP).",
    "24": "Bạn đã hủy giao dịch.",
    "51": "Tài khoản không đủ số dư để thực hiện giao dịch.",
    "65": "Tài khoản đã vượt quá hạn mức giao dịch trong ngày.",
    "75": "Ngân hàng thanh toán đang bảo trì.",
    "79": "Nhập sai mật khẩu thanh toán quá số lần quy định.",
    "99": "Lỗi không xác định.",
}


def is_configured() -> bool:
    return bool(settings.vnpay_tmn_code.strip() and settings.vnpay_hash_secret.strip())


def response_message(code: str | None) -> str:
    return RESPONSE_MESSAGES.get(code or "", f"Giao dịch không thành công (mã {code}).")


# Chuỗi dữ liệu cần ký: các tham số vnp_* (trừ chữ ký) sắp xếp theo tên, giá trị mã hóa URL
def _hash_data(params: dict) -> str:
    items = sorted(
        (k, v) for k, v in params.items()
        if k.startswith("vnp_") and k not in ("vnp_SecureHash", "vnp_SecureHashType") and v not in (None, "")
    )
    return "&".join(f"{k}={quote_plus(str(v))}" for k, v in items)


def _sign(data: str) -> str:
    return hmac.new(settings.vnpay_hash_secret.strip().encode(), data.encode(), hashlib.sha512).hexdigest()


def now_vn() -> dt.datetime:
    return dt.datetime.now(_VN_TZ)


# Tạo URL chuyển học viên sang trang thanh toán VNPay.
# create_date (yyyyMMddHHmmss) phải được lưu lại để sau này truy vấn giao dịch (querydr).
def build_payment_url(*, txn_ref: str, amount: float, order_info: str, ip_addr: str, create_date: str) -> str:
    now = dt.datetime.strptime(create_date, "%Y%m%d%H%M%S").replace(tzinfo=_VN_TZ)
    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": settings.vnpay_tmn_code.strip(),
        # Số tiền gửi sang VNPay phải nhân 100 (bỏ phần thập phân)
        "vnp_Amount": int(round(amount * 100)),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": order_info,
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": settings.vnpay_return_url,
        "vnp_IpAddr": ip_addr or "127.0.0.1",
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": (now + dt.timedelta(minutes=EXPIRE_MINUTES)).strftime("%Y%m%d%H%M%S"),
    }
    query = _hash_data(params)
    return f"{settings.vnpay_payment_url}?{query}&vnp_SecureHash={_sign(query)}"


# Kiểm tra chữ ký của dữ liệu VNPay gửi về (return URL / IPN) — chống giả mạo kết quả
def verify(params: dict) -> bool:
    received = (params.get("vnp_SecureHash") or "").lower()
    if not received or not is_configured():
        return False
    return hmac.compare_digest(received, _sign(_hash_data(params)).lower())


# ── Truy vấn kết quả giao dịch (querydr) — dùng khi đối soát đơn còn "đang chờ" ─────

# Thứ tự trường để ký yêu cầu / kiểm tra chữ ký phản hồi (nối bằng "|") theo tài liệu VNPay
_QUERY_REQ_FIELDS = (
    "vnp_RequestId", "vnp_Version", "vnp_Command", "vnp_TmnCode", "vnp_TxnRef",
    "vnp_TransactionDate", "vnp_CreateDate", "vnp_IpAddr", "vnp_OrderInfo",
)
_QUERY_RSP_FIELDS = (
    "vnp_ResponseId", "vnp_Command", "vnp_ResponseCode", "vnp_Message", "vnp_TmnCode", "vnp_TxnRef",
    "vnp_Amount", "vnp_BankCode", "vnp_PayDate", "vnp_TransactionNo", "vnp_TransactionType",
    "vnp_TransactionStatus", "vnp_OrderInfo", "vnp_PromotionCode", "vnp_PromotionAmount",
)


class VnpayQueryError(Exception):
    """Không hỏi được VNPay (lỗi mạng, sai chữ ký phản hồi...) -> giữ nguyên đơn, thử lại sau."""


def _pipe_sign(data: dict, fields: tuple) -> str:
    return _sign("|".join(str(data.get(f) or "") for f in fields))


# Hỏi VNPay kết quả của 1 giao dịch. transaction_date = vnp_CreateDate đã gửi khi tạo đơn.
# Trả về dict phản hồi đã kiểm chữ ký: vnp_ResponseCode ("00" = truy vấn thành công, "91" = không
# tìm thấy giao dịch) và vnp_TransactionStatus ("00" = đã thanh toán thành công).
def query_transaction(*, txn_ref: str, transaction_date: str, ip_addr: str = "127.0.0.1") -> dict:
    import secrets

    import httpx

    if not is_configured():
        raise VnpayQueryError("Chưa cấu hình VNPay.")
    req = {
        "vnp_RequestId": secrets.token_hex(16),
        "vnp_Version": "2.1.0",
        "vnp_Command": "querydr",
        "vnp_TmnCode": settings.vnpay_tmn_code.strip(),
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"Truy van giao dich {txn_ref}",
        "vnp_TransactionDate": transaction_date,
        "vnp_CreateDate": now_vn().strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": ip_addr,
    }
    req["vnp_SecureHash"] = _pipe_sign(req, _QUERY_REQ_FIELDS)
    try:
        r = httpx.post(settings.vnpay_api_url, json=req, timeout=20)
        r.raise_for_status()
        rsp = r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise VnpayQueryError(f"Không kết nối được VNPay: {e}") from e

    # Phản hồi có chữ ký thì phải khớp (phản hồi lỗi định dạng đôi khi không kèm chữ ký)
    got = (rsp.get("vnp_SecureHash") or "").lower()
    if got and not hmac.compare_digest(got, _pipe_sign(rsp, _QUERY_RSP_FIELDS).lower()):
        raise VnpayQueryError("Chữ ký phản hồi từ VNPay không hợp lệ.")
    return rsp


# ── Hoàn tiền (refund) ────────────────────────────────────────────────────

_REFUND_REQ_FIELDS = (
    "vnp_RequestId", "vnp_Version", "vnp_Command", "vnp_TmnCode", "vnp_TransactionType", "vnp_TxnRef",
    "vnp_Amount", "vnp_TransactionNo", "vnp_TransactionDate", "vnp_CreateBy", "vnp_CreateDate",
    "vnp_IpAddr", "vnp_OrderInfo",
)
_REFUND_RSP_FIELDS = (
    "vnp_ResponseId", "vnp_Command", "vnp_ResponseCode", "vnp_Message", "vnp_TmnCode", "vnp_TxnRef",
    "vnp_Amount", "vnp_BankCode", "vnp_PayDate", "vnp_TransactionNo", "vnp_TransactionType",
    "vnp_TransactionStatus", "vnp_OrderInfo",
)

# Ý nghĩa mã phản hồi của API hoàn tiền
REFUND_MESSAGES = {
    "00": "Yêu cầu hoàn tiền thành công.",
    "02": "Mã website (TMN code) không hợp lệ.",
    "03": "Dữ liệu gửi sang không đúng định dạng.",
    "91": "VNPay không tìm thấy giao dịch cần hoàn tiền.",
    "94": "Giao dịch đã được gửi yêu cầu hoàn tiền trước đó, VNPay đang xử lý.",
    "95": "Giao dịch này không thành công bên VNPay nên VNPay từ chối hoàn tiền.",
    "97": "Chữ ký không hợp lệ.",
    "99": "Lỗi khác từ VNPay.",
}


# Gửi yêu cầu hoàn tiền TOÀN PHẦN (vnp_TransactionType=02) cho 1 giao dịch đã thanh toán.
# transaction_date = vnp_CreateDate của đơn gốc; created_by = người thực hiện (email admin).
def refund_transaction(*, txn_ref: str, amount: float, transaction_no: str | None, transaction_date: str,
                       created_by: str, reason: str, ip_addr: str = "127.0.0.1") -> dict:
    import secrets

    import httpx

    if not is_configured():
        raise VnpayQueryError("Chưa cấu hình VNPay.")
    req = {
        "vnp_RequestId": secrets.token_hex(16),
        "vnp_Version": "2.1.0",
        "vnp_Command": "refund",
        "vnp_TmnCode": settings.vnpay_tmn_code.strip(),
        "vnp_TransactionType": "02",
        "vnp_TxnRef": txn_ref,
        "vnp_Amount": int(round(amount * 100)),
        "vnp_OrderInfo": f"Hoan tien don {txn_ref}: {reason}"[:255],
        "vnp_TransactionNo": transaction_no or "",
        "vnp_TransactionDate": transaction_date,
        "vnp_CreateBy": created_by,
        "vnp_CreateDate": now_vn().strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": ip_addr,
    }
    req["vnp_SecureHash"] = _pipe_sign(req, _REFUND_REQ_FIELDS)
    try:
        r = httpx.post(settings.vnpay_api_url, json=req, timeout=30)
        r.raise_for_status()
        rsp = r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise VnpayQueryError(f"Không kết nối được VNPay: {e}") from e
    got = (rsp.get("vnp_SecureHash") or "").lower()
    if got and not hmac.compare_digest(got, _pipe_sign(rsp, _REFUND_RSP_FIELDS).lower()):
        raise VnpayQueryError("Chữ ký phản hồi từ VNPay không hợp lệ.")
    return rsp
