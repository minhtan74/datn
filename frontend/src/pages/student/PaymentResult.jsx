import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { paymentService } from '../../services/paymentService';

// Định dạng tiền và ngày giờ hiển thị trên biên nhận
function fmtMoney(n) {
  return Number(n || 0).toLocaleString('vi-VN') + 'đ';
}
function fmtDateTime(str) {
  if (!str) return '—';
  const d = new Date(String(str).replace(' ', 'T'));
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleString('vi-VN');
}

// Lý do thất bại do backend phát hiện (không phải do ngân hàng)
const REASON_TEXT = {
  invalid_signature: 'Dữ liệu trả về không hợp lệ (sai chữ ký). Giao dịch không được ghi nhận.',
  not_found: 'Không tìm thấy đơn hàng tương ứng.',
  invalid_amount: 'Số tiền thanh toán không khớp với đơn hàng.',
};

/**
 * Trang kết quả thanh toán VNPay. Backend (/api/payments/vnpay/return) đã kiểm tra chữ ký
 * và cập nhật đơn rồi chuyển về đây kèm ?ref=...&status=...; trang đọc lại trạng thái
 * thật của đơn từ API để hiển thị (không tin tham số trên URL).
 */
export default function PaymentResult() {
  const [params] = useSearchParams();
  const ref = params.get('ref') || '';
  const reason = params.get('reason') || '';
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ref) {
      setLoading(false);
      return;
    }
    (async () => {
      const res = await paymentService.getStatus(ref);
      if (res?.data?.success) setPayment(res.data.data);
      setLoading(false);
    })();
  }, [ref]);

  if (loading) {
    return (
      <main className="s-main" style={{ textAlign: 'center', padding: '5rem 1rem', color: 'var(--s-text-muted)' }}>
        ⏳ Đang kiểm tra kết quả thanh toán...
      </main>
    );
  }

  const success = payment?.status === 'completed';
  const refunded = payment?.status === 'refunded';
  const message = success
    ? 'Khóa học đã được mở. Chúc bạn học tốt!'
    : refunded
    ? 'Đơn hàng này đã được hoàn tiền.'
    : REASON_TEXT[reason] || payment?.message || 'Giao dịch không thành công. Bạn chưa bị trừ tiền cho khóa học này.';

  return (
    <main className="s-main">
      <div
        style={{
          maxWidth: 520,
          margin: '2rem auto',
          background: 'var(--s-surface, #fff)',
          border: '1px solid var(--s-border, #e2e8f0)',
          borderRadius: 16,
          padding: '2rem 1.75rem',
          textAlign: 'center',
        }}
      >
        {/* Biểu tượng + tiêu đề kết quả */}
        <div style={{ fontSize: '3rem', lineHeight: 1 }}>{success ? '✅' : refunded ? '↩️' : '❌'}</div>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '0.75rem 0 0.35rem' }}>
          {success ? 'Thanh toán thành công' : refunded ? 'Đã hoàn tiền' : 'Thanh toán thất bại'}
        </h1>
        <p style={{ color: 'var(--s-text-muted)', fontSize: '0.9rem' }}>{message}</p>

        {/* Thông tin đơn hàng */}
        {payment ? (
          <div style={{ textAlign: 'left', background: 'var(--s-surface-2)', borderRadius: 10, padding: '1rem 1.1rem', margin: '1.25rem 0', fontSize: '0.86rem' }}>
            {[
              ['Khóa học', payment.course_title],
              ['Số tiền', fmtMoney(payment.amount)],
              ['Mã đơn hàng', payment.transaction_ref],
              // Giao dịch bị hủy: VNPay trả mã giao dịch "0" -> coi như chưa có
              ['Mã GD VNPay', payment.gateway_txn_no && payment.gateway_txn_no !== '0' ? payment.gateway_txn_no : '—'],
              ['Ngân hàng', payment.bank_code || '—'],
              ['Thời gian', fmtDateTime(payment.paid_at || payment.created_at)],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', padding: '0.3rem 0' }}>
                <span style={{ color: 'var(--s-text-muted)' }}>{k}</span>
                <strong style={{ textAlign: 'right', wordBreak: 'break-word' }}>{v}</strong>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ margin: '1.25rem 0', fontSize: '0.86rem', color: 'var(--s-text-muted)' }}>
            Không tìm thấy thông tin đơn hàng{ref ? ` ${ref}` : ''}.
          </p>
        )}

        {/* Hành động tiếp theo */}
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          {success ? (
            <Link className="s-btn s-btn-primary" to={`/chapters?course_id=${payment.course_id}`}>
              🚀 Vào học ngay
            </Link>
          ) : (
            <Link className="s-btn s-btn-primary" to="/student/courses">
              🔁 Thử thanh toán lại
            </Link>
          )}
          <Link className="s-btn s-btn-ghost" to="/student/my-courses">
            Khóa học của tôi
          </Link>
        </div>
      </div>
    </main>
  );
}
