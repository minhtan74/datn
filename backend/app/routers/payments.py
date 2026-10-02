"""/api/payments — thanh toán khóa học qua VNPay Sandbox (+ chế độ giả lập khi PAYMENT_MOCK=true)."""
import datetime as dt
import random
from urllib.parse import urlencode

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import execute, get_db, q_all, q_one
from app.core.dependencies import get_current_user
from app.core.responses import ApiError, ok
from app.routers.enrollments import _enroll, _is_enrolled
from app.services import vnpay

from ._common import iv, sv

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Hệ thống chỉ thanh toán qua VNPay (học viên chọn thẻ / ngân hàng / QR ngay trên trang VNPay).
# Các giá trị cũ card / bank_transfer / momo / zalopay chỉ còn trong enum CSDL cho dữ liệu cũ.
METHOD = "vnpay"


# Đơn có đi qua cổng VNPay thật không: có mã giao dịch VNPay mới hỏi / hoàn tiền với VNPay được
# (đơn giả lập, dữ liệu mẫu không có mã này -> chỉ xử lý thủ công)
def _via_gateway(payment: dict) -> bool:
    return payment["method"] == METHOD and bool(payment.get("gateway_txn_no"))


# Kiểm tra user đã có giao dịch thanh toán thành công cho khóa học này chưa
def _has_paid(db: Session, user_id: int, course_id: int) -> bool:
    return (
        q_one(
            db,
            "SELECT id FROM payments WHERE user_id = :u AND course_id = :c "
            "AND status = 'completed'",
            u=user_id,
            c=course_id,
        )
        is not None
    )


# Sinh mã giao dịch dạng SO + thời gian (yyMMddHHmmss) + 4 số ngẫu nhiên (dùng làm vnp_TxnRef)
def _new_ref() -> str:
    return "SO" + dt.datetime.now().strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999))


# Khóa học phải tồn tại, user chưa đăng ký, và (với học viên) khóa phải đang mở bán
def _purchasable_course(db: Session, user: dict, course_id: int) -> dict:
    course = q_one(db, "SELECT * FROM courses WHERE id = :id", id=course_id)
    if not course:
        raise ApiError("Khóa học không tồn tại.", 404)
    if _is_enrolled(db, user["id"], course_id):
        raise ApiError("Bạn đã đăng ký khóa học này rồi.", 409)
    if user["role"] == "student" and course["status"] != "published":
        raise ApiError("Khóa học này chưa mở đăng ký.", 403)
    return course


# GET /api/payments — danh sách giao dịch, phạm vi xem tùy vai trò
@router.get("")
def index(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Admin: xem toàn bộ giao dịch của hệ thống (kèm tên học viên + tên khóa)
    if user["role"] == "admin":
        data = q_all(
            db,
            "SELECT p.*, u.fullname AS user_name, c.title AS course_title FROM payments p "
            "JOIN users u ON u.id = p.user_id JOIN courses c ON c.id = p.course_id "
            "ORDER BY p.created_at DESC",
        )
    # Giảng viên: chỉ xem giao dịch mua các khóa học do mình phụ trách
    elif user["role"] == "teacher":
        data = q_all(
            db,
            "SELECT p.*, u.fullname AS user_name, c.title AS course_title FROM payments p "
            "JOIN users u ON u.id = p.user_id JOIN courses c ON c.id = p.course_id "
            "WHERE c.teacher_id = :tid ORDER BY p.created_at DESC",
            tid=user["id"],
        )
    # Học viên: chỉ xem lịch sử thanh toán của chính mình
    else:
        data = q_all(
            db,
            "SELECT p.*, c.title AS course_title FROM payments p "
            "JOIN courses c ON c.id = p.course_id WHERE p.user_id = :u "
            "ORDER BY p.created_at DESC",
            u=user["id"],
        )
    return ok(data=data)


# POST /api/payments — đăng ký khóa học; khóa có phí thì tạo giao dịch (mock: thành công ngay)
@router.post("")
def create(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course_id = iv(body, "course_id")

    # Kiểm tra dữ liệu đầu vào: phải có khóa học
    if not course_id:
        raise ApiError("Thiếu course_id.")

    course = _purchasable_course(db, user, course_id)
    amount = float(course["price"] or 0)

    # Khóa miễn phí: ghi danh luôn, không tạo giao dịch
    if amount <= 0:
        _enroll(db, user["id"], course_id)
        return ok("Đăng ký thành công!", enrolled=True, payment_required=False)

    # Khóa có phí phải thanh toán qua VNPay (POST /api/payments/vnpay/create);
    # chỉ cho phép thanh toán giả lập khi bật PAYMENT_MOCK=true (demo offline)
    if not settings.payment_mock:
        raise ApiError("Khóa học có phí — vui lòng thanh toán qua VNPay.", 400)

    ref = _new_ref()
    # Tạo giao dịch ở trạng thái chờ (pending); đơn giả lập không có mã giao dịch VNPay
    res = execute(
        db,
        "INSERT INTO payments (user_id, course_id, amount, method, status, transaction_ref, note) "
        "VALUES (:u, :c, :amount, :method, 'pending', :ref, 'Thanh toán giả lập (PAYMENT_MOCK)')",
        u=user["id"],
        c=course_id,
        amount=amount,
        method=METHOD,
        ref=ref,
    )
    payment_id = res.lastrowid
    if not payment_id:
        raise ApiError("Không thể tạo giao dịch.")

    # MOCK: chưa tích hợp cổng thanh toán thật -> chuyển ngay sang 'completed' và ghi thời điểm trả tiền
    execute(
        db,
        "UPDATE payments SET status='completed', transaction_ref=:ref, paid_at=NOW() "
        "WHERE id=:id AND status='pending'",
        ref=ref,
        id=payment_id,
    )
    # Thanh toán xong thì ghi danh học viên vào khóa học
    _enroll(db, user["id"], course_id)

    return ok(
        "Thanh toán thành công! Bạn đã được đăng ký vào khóa học.",
        payment_id=int(payment_id),
        transaction_ref=ref,
        amount=amount,
        method=METHOD,
        enrolled=True,
        payment_required=True,
    )


# GET /api/payments/check?course_id=X — cho frontend biết user đã trả tiền / đã ghi danh khóa này chưa
@router.get("/check")
def check(
    course_id: int = Query(default=0),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not course_id:
        raise ApiError("Thiếu course_id.")
    return ok(
        has_paid=_has_paid(db, user["id"], course_id),
        enrolled=_is_enrolled(db, user["id"], course_id),
    )


# ── VNPay Sandbox ──────────────────────────────────────────────────────────

# POST /api/payments/vnpay/create — tạo đơn hàng (pending) và trả URL chuyển sang trang thanh toán VNPay
@router.post("/vnpay/create")
def vnpay_create(
    request: Request,
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course_id = iv(body, "course_id")
    if not course_id:
        raise ApiError("Thiếu course_id.")
    course = _purchasable_course(db, user, course_id)
    amount = float(course["price"] or 0)

    # Khóa miễn phí: ghi danh luôn, không cần qua VNPay
    if amount <= 0:
        _enroll(db, user["id"], course_id)
        return ok("Đăng ký thành công!", enrolled=True, payment_required=False)
    if not vnpay.is_configured():
        raise ApiError("Hệ thống chưa cấu hình cổng thanh toán VNPay. Vui lòng liên hệ quản trị viên.", 503)

    # Đơn VNPay cũ còn chờ của cùng khóa: hỏi VNPay trước — nếu thực ra đã thanh toán thì ghi danh luôn,
    # chưa thanh toán thì hủy (học viên đang mở lại thanh toán bằng đơn mới)
    for old in q_all(
        db,
        "SELECT * FROM payments WHERE user_id=:u AND course_id=:c AND method='vnpay' AND status='pending'",
        u=user["id"],
        c=course_id,
    ):
        outcome, _ = reconcile_payment(db, old, cancel_note="Đã hủy do tạo đơn thanh toán mới")
        if outcome == "paid":
            return ok(
                "Đơn thanh toán trước đó của bạn đã được VNPay xác nhận — bạn đã được ghi danh vào khóa học.",
                enrolled=True,
                payment_required=False,
            )

    # Tạo đơn hàng ở trạng thái chờ thanh toán; lưu vnp_CreateDate để sau này truy vấn (querydr)
    ref = _new_ref()
    create_date = vnpay.now_vn().strftime("%Y%m%d%H%M%S")
    execute(
        db,
        "INSERT INTO payments (user_id, course_id, amount, method, status, transaction_ref, vnp_create_date) "
        "VALUES (:u, :c, :amount, 'vnpay', 'pending', :ref, :cd)",
        u=user["id"],
        c=course_id,
        amount=amount,
        ref=ref,
        cd=create_date,
    )

    # IP của học viên (qua Nginx thì lấy từ X-Forwarded-For)
    ip = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip() or (
        request.client.host if request.client else "127.0.0.1"
    )
    url = vnpay.build_payment_url(
        txn_ref=ref,
        amount=amount,
        # Nội dung thanh toán: VNPay khuyến nghị tiếng Việt không dấu
        order_info=f"Thanh toan khoa hoc {course_id} - don {ref}",
        ip_addr=ip,
        create_date=create_date,
    )
    return ok("Đã tạo đơn hàng.", payment_url=url, transaction_ref=ref, amount=amount, payment_required=True)


# Áp dụng kết quả VNPay gửi về (dùng chung cho return URL và IPN).
# Trả về (mã kết quả, đơn hàng): invalid_signature | not_found | invalid_amount | already | success | failed
def _apply_vnpay_result(db: Session, params: dict) -> tuple[str, dict | None]:
    if not vnpay.verify(params):
        return "invalid_signature", None

    payment = q_one(
        db, "SELECT * FROM payments WHERE transaction_ref = :ref AND method = 'vnpay'",
        ref=params.get("vnp_TxnRef", ""),
    )
    if not payment:
        return "not_found", None
    # Số tiền VNPay báo về phải khớp số tiền của đơn (VNPay gửi số tiền x100)
    if str(params.get("vnp_Amount")) != str(int(round(float(payment["amount"]) * 100))):
        return "invalid_amount", payment
    if payment["status"] == "completed":
        return "already", payment

    code = params.get("vnp_ResponseCode")
    success = code == "00" and params.get("vnp_TransactionStatus", "00") == "00"
    info = dict(txn=params.get("vnp_TransactionNo"), bank=params.get("vnp_BankCode"), code=code)
    if success:
        _mark_paid(db, payment, note=vnpay.response_message(code), **info)
        outcome = "success"
    else:
        # Thất bại / học viên hủy: đánh dấu failed, KHÔNG tạo enrollment
        _mark_failed(db, payment, note=vnpay.response_message(code), **info)
        outcome = "failed"
    return outcome, q_one(db, "SELECT * FROM payments WHERE id = :id", id=payment["id"])


# Đơn đã thanh toán: chuyển 'completed' + ghi danh. Điều kiện status <> 'completed' đảm bảo chỉ xử lý
# 1 lần (return URL, IPN và đối soát có thể đến cùng lúc). Đơn 'failed' vẫn được chuyển nếu VNPay xác nhận
# đã trả tiền; đơn đã hoàn tiền thì không bao giờ bị lật lại.
def _mark_paid(db: Session, payment: dict, *, txn=None, bank=None, code="00", note=None) -> None:
    res = execute(
        db,
        "UPDATE payments SET status='completed', paid_at=NOW(), gateway_txn_no=:txn, bank_code=:bank, "
        "response_code=:code, note=:note WHERE id=:id AND status IN ('pending', 'failed')",
        id=payment["id"], txn=txn, bank=bank, code=code, note=note,
    )
    if res.rowcount:
        _enroll(db, payment["user_id"], payment["course_id"])


# Đơn thất bại / hết hạn: chỉ đổi khi đơn còn 'pending'; KHÔNG ghi danh
def _mark_failed(db: Session, payment: dict, *, txn=None, bank=None, code=None, note=None) -> None:
    execute(
        db,
        "UPDATE payments SET status='failed', gateway_txn_no=COALESCE(:txn, gateway_txn_no), "
        "bank_code=COALESCE(:bank, bank_code), response_code=COALESCE(:code, response_code), note=:note "
        "WHERE id=:id AND status = 'pending'",
        id=payment["id"], txn=txn, bank=bank, code=code, note=note,
    )


# GET /api/payments/vnpay/return — VNPay chuyển trình duyệt của học viên về đây sau khi thanh toán.
# Kiểm tra chữ ký + cập nhật đơn, rồi chuyển tiếp về trang kết quả trên giao diện.
@router.get("/vnpay/return")
def vnpay_return(request: Request, db: Session = Depends(get_db)):
    params = dict(request.query_params)
    outcome, payment = _apply_vnpay_result(db, params)
    status = "success" if outcome in ("success", "already") else "failed"
    query = urlencode(
        {
            "ref": params.get("vnp_TxnRef", ""),
            "status": status,
            "reason": "" if status == "success" else outcome,
            "code": params.get("vnp_ResponseCode", ""),
        }
    )
    return RedirectResponse(f"{settings.frontend_url.rstrip('/')}/student/payment-result?{query}", status_code=302)


# GET /api/payments/vnpay/ipn — VNPay gọi trực tiếp (server-to-server) để báo kết quả.
# Cần URL công khai (cấu hình trên trang quản lý merchant của VNPay); chạy local thì dựa vào return URL.
@router.get("/vnpay/ipn")
def vnpay_ipn(request: Request, db: Session = Depends(get_db)):
    outcome, _ = _apply_vnpay_result(db, dict(request.query_params))
    # Mã phản hồi theo tài liệu IPN của VNPay
    rsp = {
        "invalid_signature": ("97", "Invalid Checksum"),
        "not_found": ("01", "Order not found"),
        "invalid_amount": ("04", "Invalid amount"),
        "already": ("02", "Order already confirmed"),
        "success": ("00", "Confirm Success"),
        "failed": ("00", "Confirm Success"),
    }[outcome]
    return JSONResponse({"RspCode": rsp[0], "Message": rsp[1]})


# GET /api/payments/status?ref=... — trạng thái 1 đơn hàng (chỉ chủ đơn hoặc admin xem được)
@router.get("/status")
def payment_status(
    ref: str = Query(default=""),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = q_one(
        db,
        "SELECT p.id, p.user_id, p.course_id, p.amount, p.method, p.status, p.transaction_ref, "
        "p.gateway_txn_no, p.bank_code, p.response_code, p.note, p.paid_at, p.created_at, "
        "c.title AS course_title FROM payments p JOIN courses c ON c.id = p.course_id "
        "WHERE p.transaction_ref = :ref",
        ref=ref,
    )
    if not payment or (payment["user_id"] != user["id"] and user["role"] != "admin"):
        raise ApiError("Không tìm thấy đơn hàng.", 404)
    return ok(
        data={
            **payment,
            "message": vnpay.response_message(payment["response_code"]) if payment["response_code"] else None,
            "enrolled": _is_enrolled(db, payment["user_id"], payment["course_id"]),
        }
    )


# ── Quản lý giao dịch (admin) ──────────────────────────────────────────────

# Các trạng thái đơn hợp lệ để lọc
_STATUSES = ("pending", "completed", "failed", "refunded")


# GET /api/payments/manage — danh sách toàn bộ giao dịch cho admin: phân trang, lọc, tìm kiếm.
#   status, method, course_id: lọc; date_from / date_to (YYYY-MM-DD): theo ngày tạo đơn;
#   q: tìm theo mã đơn, mã GD VNPay, tên hoặc email học viên
@router.get("/manage")
def manage(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str = Query(default=""),
    method: str = Query(default=""),
    course_id: int = Query(default=0),
    date_from: str = Query(default=""),
    date_to: str = Query(default=""),
    q: str = Query(default=""),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise ApiError("Chỉ Admin mới quản lý giao dịch.", 403)

    # Ghép điều kiện lọc (luôn dùng tham số, không nối chuỗi giá trị người dùng)
    conds, params = [], {}
    if method:
        if method != METHOD:
            raise ApiError("Phương thức không hợp lệ.")
        conds.append("p.method = :method")
        params["method"] = method
    if course_id:
        conds.append("p.course_id = :cid")
        params["cid"] = course_id
    for key, op, val in (("df", ">=", date_from), ("dt", "<", date_to)):
        if not val:
            continue
        try:
            d = dt.date.fromisoformat(val)
        except ValueError:
            raise ApiError("Ngày không hợp lệ (định dạng YYYY-MM-DD).")
        # date_to tính trọn ngày -> so sánh với 0h ngày hôm sau
        params[key] = d + dt.timedelta(days=1) if key == "dt" else d
        conds.append(f"p.created_at {op} :{key}")
    if q.strip():
        conds.append(
            "(p.transaction_ref LIKE :q OR p.gateway_txn_no LIKE :q "
            "OR u.fullname LIKE :q OR u.email LIKE :q)"
        )
        params["q"] = f"%{q.strip()}%"

    base = (
        "FROM payments p JOIN users u ON u.id = p.user_id "
        "JOIN courses c ON c.id = p.course_id"
    )
    where_wo_status = (" WHERE " + " AND ".join(conds)) if conds else ""

    # Đếm theo trạng thái (theo các bộ lọc khác, chưa lọc trạng thái) -> hiện số trên các tab
    counts = {s: 0 for s in _STATUSES}
    for r in q_all(db, f"SELECT p.status, COUNT(*) AS n {base}{where_wo_status} GROUP BY p.status", **params):
        counts[r["status"]] = int(r["n"])

    # Lọc thêm theo trạng thái cho danh sách
    if status:
        if status not in _STATUSES:
            raise ApiError("Trạng thái không hợp lệ.")
        conds.append("p.status = :status")
        params["status"] = status
    where = (" WHERE " + " AND ".join(conds)) if conds else ""

    total = int(q_one(db, f"SELECT COUNT(*) AS n {base}{where}", **params)["n"])
    # Tổng tiền các đơn thành công trong kết quả lọc
    revenue = q_one(
        db, f"SELECT COALESCE(SUM(p.amount), 0) AS s {base}{where}"
        + (" AND" if where else " WHERE") + " p.status = 'completed'", **params,
    )["s"]

    rows = q_all(
        db,
        "SELECT p.id, p.amount, p.method, p.status, p.transaction_ref, p.gateway_txn_no, p.bank_code, "
        "p.response_code, p.note, p.created_at, p.paid_at, p.updated_at, p.user_id, p.course_id, "
        "u.fullname AS user_name, u.email, c.title AS course_title "
        f"{base}{where} ORDER BY p.created_at DESC, p.id DESC LIMIT :lim OFFSET :off",
        **params,
        lim=page_size,
        off=(page - 1) * page_size,
    )
    rows = [_decorate(db, r) for r in rows]

    return ok(
        data=rows,
        pagination={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": max(1, -(-total // page_size)),
        },
        counts=counts,
        revenue=float(revenue or 0),
    )


# ── Đối soát đơn "đang chờ" với VNPay ──────────────────────────────────────
# Tình huống: học viên đã trả tiền trên VNPay nhưng đóng tab trước khi được chuyển về web
# (chạy local thì VNPay cũng không gọi được IPN) -> đơn kẹt 'pending', học viên chưa được ghi danh.

# Quá thời hạn thanh toán (15 phút) + 5 phút dự phòng thì coi đơn là hết hạn
_EXPIRE_AFTER = dt.timedelta(minutes=vnpay.EXPIRE_MINUTES + 5)

RECONCILE_MESSAGES = {
    "paid": "VNPay xác nhận đã thanh toán — đơn chuyển sang thành công và học viên đã được ghi danh.",
    "failed": "VNPay báo giao dịch không thành công — đơn chuyển sang thất bại.",
    "expired": "Học viên không thanh toán trong thời hạn — đơn chuyển sang thất bại (hết hạn).",
    "cancelled": "Đơn chưa thanh toán đã được hủy.",
    "waiting": "Học viên chưa thanh toán và đơn vẫn còn hạn — giữ trạng thái đang chờ.",
    "not_pending": "Đơn không ở trạng thái đang chờ nên không cần đối soát.",
    "error": "Không kiểm tra được với VNPay — giữ nguyên đơn, vui lòng thử lại sau.",
}


def _is_expired(payment: dict) -> bool:
    created = payment.get("created_at")
    return bool(created) and dt.datetime.now() - created > _EXPIRE_AFTER


# Đối soát 1 đơn: hỏi VNPay rồi cập nhật đơn. cancel_note: hủy luôn nếu chưa thanh toán (kể cả còn hạn).
# Trả về (outcome, chi tiết): paid | failed | expired | cancelled | waiting | not_pending | error
def reconcile_payment(db: Session, payment: dict, *, cancel_note: str | None = None) -> tuple[str, str]:
    if payment["status"] != "pending":
        return "not_pending", ""
    expired = _is_expired(payment)

    # Đơn không qua cổng thanh toán (đơn giả lập cũ): không có gì để hỏi -> hết hạn thì hủy
    if payment["method"] != METHOD:
        if cancel_note or expired:
            _mark_failed(db, payment, note=cancel_note or "Đơn không qua cổng thanh toán, đã quá hạn — hủy.")
            return ("cancelled" if cancel_note else "expired"), ""
        return "waiting", ""

    tdate = payment.get("vnp_create_date") or (
        payment["created_at"].strftime("%Y%m%d%H%M%S") if payment.get("created_at") else ""
    )
    try:
        rsp = vnpay.query_transaction(txn_ref=payment["transaction_ref"], transaction_date=tdate)
    except vnpay.VnpayQueryError as e:
        return "error", str(e)

    code, tstatus = rsp.get("vnp_ResponseCode"), rsp.get("vnp_TransactionStatus")
    detail = f"VNPay: {rsp.get('vnp_ResponseCode')} - {rsp.get('vnp_Message') or ''}".strip(" -")
    if code == "00":
        # Số tiền VNPay ghi nhận phải khớp đơn
        if str(rsp.get("vnp_Amount")) != str(int(round(float(payment["amount"]) * 100))):
            return "error", "Số tiền VNPay ghi nhận không khớp với đơn hàng."
        info = dict(txn=rsp.get("vnp_TransactionNo"), bank=rsp.get("vnp_BankCode"))
        if tstatus == "00":
            _mark_paid(db, payment, code="00", note="Xác nhận qua đối soát VNPay (querydr).", **info)
            return "paid", detail
        if tstatus == "01" and not (cancel_note or expired):
            return "waiting", detail  # giao dịch chưa hoàn tất, còn hạn
        if tstatus == "01":
            _mark_failed(db, payment, note=cancel_note or "Hết hạn thanh toán (đối soát VNPay).", **info)
            return ("cancelled" if cancel_note else "expired"), detail
        _mark_failed(db, payment, code=tstatus, note=f"Giao dịch không thành công (VNPay trạng thái {tstatus}).", **info)
        return "failed", detail
    # 91 = VNPay không có giao dịch này -> học viên chưa hề thanh toán
    if code == "91":
        if cancel_note or expired:
            _mark_failed(db, payment, note=cancel_note or "Hết hạn thanh toán — học viên chưa thực hiện thanh toán.")
            return ("cancelled" if cancel_note else "expired"), detail
        return "waiting", detail
    return "error", detail


# Đối soát mọi đơn đang chờ. only_expired=True (job định kỳ): chỉ xét đơn đã quá hạn,
# tránh hỏi VNPay liên tục cho đơn học viên đang thanh toán dở.
def reconcile_pending(db: Session, *, only_expired: bool = False) -> dict:
    summary = {k: 0 for k in RECONCILE_MESSAGES}
    for p in q_all(db, "SELECT * FROM payments WHERE status = 'pending' ORDER BY id"):
        if only_expired and not _is_expired(p):
            continue
        outcome, _ = reconcile_payment(db, p)
        summary[outcome] += 1
    return summary


# Thêm thông tin hiển thị cho 1 dòng giao dịch (ý nghĩa mã VNPay, học viên còn ghi danh không)
def _decorate(db: Session, row: dict) -> dict:
    row["response_message"] = vnpay.response_message(row["response_code"]) if row.get("response_code") else None
    row["enrolled"] = _is_enrolled(db, row["user_id"], row["course_id"])
    return row


# POST /api/payments/reconcile {id} — admin đối soát 1 đơn đang chờ với VNPay
@router.post("/reconcile")
def reconcile_one(
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise ApiError("Chỉ Admin mới đối soát giao dịch.", 403)
    payment = q_one(db, "SELECT * FROM payments WHERE id = :id", id=iv(body, "id"))
    if not payment:
        raise ApiError("Không tìm thấy giao dịch.", 404)
    outcome, detail = reconcile_payment(db, payment)
    row = q_one(
        db,
        "SELECT p.*, u.fullname AS user_name, u.email, c.title AS course_title FROM payments p "
        "JOIN users u ON u.id = p.user_id JOIN courses c ON c.id = p.course_id WHERE p.id = :id",
        id=payment["id"],
    )
    return ok(RECONCILE_MESSAGES[outcome], outcome=outcome, detail=detail, data=_decorate(db, row))


# POST /api/payments/reconcile-pending — admin đối soát tất cả đơn đang chờ
@router.post("/reconcile-pending")
def reconcile_all(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user["role"] != "admin":
        raise ApiError("Chỉ Admin mới đối soát giao dịch.", 403)
    s = reconcile_pending(db)
    parts = [f"{s['paid']} đã thanh toán", f"{s['expired'] + s['cancelled'] + s['failed']} chuyển thất bại",
             f"{s['waiting']} còn chờ"] + ([f"{s['error']} lỗi kết nối"] if s["error"] else [])
    return ok("Đối soát xong: " + ", ".join(parts) + ".", summary=s)


# ── Hoàn tiền (admin) ──────────────────────────────────────────────────────

# POST /api/payments/refund {id, reason, revoke_access} — hoàn tiền toàn phần 1 đơn đã thanh toán.
#   Đơn có mã giao dịch VNPay: gửi yêu cầu hoàn tiền sang VNPay, VNPay đồng ý (mã 00) mới cập nhật đơn.
#   Đơn không có mã giao dịch VNPay (giả lập, dữ liệu mẫu): chỉ ghi nhận hoàn tiền thủ công.
#   revoke_access=true: xóa ghi danh (thu hồi quyền học); điểm quiz / tiến độ vẫn được giữ lại.
@router.post("/refund")
def refund(
    request: Request,
    body: dict = Body(default={}),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise ApiError("Chỉ Admin mới hoàn tiền giao dịch.", 403)
    reason = sv(body, "reason", "").strip()
    if len(reason) < 5:
        raise ApiError("Vui lòng nhập lý do hoàn tiền (ít nhất 5 ký tự).")
    revoke = bool(body.get("revoke_access", True))

    payment = q_one(db, "SELECT * FROM payments WHERE id = :id", id=iv(body, "id"))
    if not payment:
        raise ApiError("Không tìm thấy giao dịch.", 404)
    if payment["status"] != "completed":
        raise ApiError("Chỉ hoàn tiền được đơn đã thanh toán thành công.", 409)

    refund_txn = None
    gateway = _via_gateway(payment)
    if gateway:
        tdate = payment.get("vnp_create_date") or payment["created_at"].strftime("%Y%m%d%H%M%S")
        ip = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip() or (
            request.client.host if request.client else "127.0.0.1"
        )
        try:
            rsp = vnpay.refund_transaction(
                txn_ref=payment["transaction_ref"],
                amount=float(payment["amount"]),
                transaction_no=payment.get("gateway_txn_no"),
                transaction_date=tdate,
                created_by=user.get("email") or f"admin{user['id']}",
                reason=reason,
                ip_addr=ip,
            )
        except vnpay.VnpayQueryError as e:
            raise ApiError(f"Không gửi được yêu cầu hoàn tiền: {e}", 502)
        code = rsp.get("vnp_ResponseCode")
        if code != "00":
            msg = vnpay.REFUND_MESSAGES.get(code) or rsp.get("vnp_Message") or "Lỗi không xác định."
            raise ApiError(f"VNPay từ chối hoàn tiền (mã {code}): {msg}", 409)
        refund_txn = rsp.get("vnp_TransactionNo")

    # Cập nhật đơn (điều kiện status='completed' chống bấm 2 lần)
    res = execute(
        db,
        "UPDATE payments SET status='refunded', refunded_at=NOW(), refunded_by=:by, refund_reason=:reason, "
        "refund_txn_no=:rtxn, note=:note WHERE id=:id AND status='completed'",
        id=payment["id"],
        by=user["id"],
        reason=reason[:255],
        rtxn=refund_txn,
        note="Đã hoàn tiền qua VNPay." if gateway else "Đã ghi nhận hoàn tiền thủ công.",
    )
    if not res.rowcount:
        raise ApiError("Đơn đã được xử lý bởi thao tác khác.", 409)

    # Thu hồi quyền học (trừ khi học viên còn đơn thanh toán thành công khác cho cùng khóa)
    revoked = False
    if revoke and not _has_paid(db, payment["user_id"], payment["course_id"]):
        revoked = bool(
            execute(
                db,
                "DELETE FROM enrollments WHERE user_id = :u AND course_id = :c",
                u=payment["user_id"],
                c=payment["course_id"],
            ).rowcount
        )

    row = q_one(
        db,
        "SELECT p.*, u.fullname AS user_name, u.email, c.title AS course_title FROM payments p "
        "JOIN users u ON u.id = p.user_id JOIN courses c ON c.id = p.course_id WHERE p.id = :id",
        id=payment["id"],
    )
    msg = "Đã hoàn tiền" + (" qua VNPay" if gateway else " (ghi nhận thủ công)")
    msg += " và thu hồi quyền học." if revoked else "; học viên vẫn giữ quyền học." if not revoke else "."
    return ok(msg, revoked=revoked, data=_decorate(db, row))
