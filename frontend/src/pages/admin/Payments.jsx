import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { paymentService } from '../../services/paymentService';
import { courseService } from '../../services/courseService';
import Modal from '../../components/common/Modal.jsx';
import { useToast } from '../../hooks/useToast';

// Định dạng tiền và ngày giờ
function fmtMoney(n) {
  return Number(n || 0).toLocaleString('vi-VN') + 'đ';
}
function fmtDateTime(str) {
  if (!str) return '—';
  const d = new Date(String(str).replace(' ', 'T'));
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleString('vi-VN', { hour12: false });
}

// Nhãn trạng thái đơn hàng
const STATUS = {
  completed: { label: 'Thành công', cls: 'badge-success' },
  pending: { label: 'Đang chờ', cls: 'badge-warning' },
  failed: { label: 'Thất bại', cls: 'badge-danger' },
  refunded: { label: 'Đã hoàn tiền', cls: 'badge-info' },
};
function StatusBadge({ status }) {
  const s = STATUS[status] || { label: status, cls: 'badge-primary' };
  return <span className={`badge ${s.cls}`} style={{ whiteSpace: 'nowrap' }}>{s.label}</span>;
}

// Tên phương thức thanh toán (hệ thống chỉ thanh toán qua VNPay)
const METHODS = {
  vnpay: '🔴 VNPay',
};

// Đơn có mã giao dịch VNPay mới hoàn tiền qua VNPay được; không có (giả lập, dữ liệu mẫu) -> ghi nhận thủ công
const viaGateway = (p) => p.method === 'vnpay' && !!p.gateway_txn_no && p.gateway_txn_no !== '0';
const REFUND_STATE = { sending: 'Đang gửi yêu cầu', pending: 'VNPay đang xử lý', unknown: 'Cần đối soát hoàn tiền', confirmed: 'Cần hoàn tất cập nhật quyền học', completed: 'Đã hoàn tiền', failed: 'VNPay từ chối yêu cầu' };

// Tab lọc theo trạng thái (kèm số lượng)
const STATUS_TABS = [
  { key: '', label: 'Tất cả' },
  { key: 'completed', label: 'Thành công' },
  { key: 'pending', label: 'Đang chờ' },
  { key: 'failed', label: 'Thất bại' },
  { key: 'refunded', label: 'Đã hoàn tiền' },
];

const PAGE_SIZE = 20;
const emptyFilters = { course_id: '', date_from: '', date_to: '' };

/** Trang Quản lý giao dịch (admin): toàn bộ giao dịch, lọc / tìm kiếm / phân trang, xem chi tiết đơn. */
export default function AdminPayments() {
  const { showToast } = useToast();
  const [rows, setRows] = useState(null); // null = đang tải
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, total: 0, total_pages: 1 });
  const [counts, setCounts] = useState({});
  const [revenue, setRevenue] = useState(0);
  const [courses, setCourses] = useState([]);

  // Bộ lọc
  const [status, setStatus] = useState('');
  const [filters, setFilters] = useState(emptyFilters);
  const [search, setSearch] = useState('');
  const [query, setQuery] = useState(''); // từ khóa đã "chốt" sau khi ngừng gõ
  const [page, setPage] = useState(1);
  const [detail, setDetail] = useState(null);
  const detailSequence = useRef(0);
  useEffect(() => () => { detailSequence.current++; }, []);
  // Tăng lên để tải lại danh sách sau khi đối soát; cờ đang đối soát (tất cả / 1 đơn)
  const [reloadKey, setReloadKey] = useState(0);
  const [syncingAll, setSyncingAll] = useState(false);
  const [syncingOne, setSyncingOne] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  // Form hoàn tiền trong hộp thoại chi tiết
  const [refundOpen, setRefundOpen] = useState(false);
  const [refundReason, setRefundReason] = useState('');
  const [revokeAccess, setRevokeAccess] = useState(true);
  const [refunding, setRefunding] = useState(false);

  // Danh sách khóa học cho ô lọc
  useEffect(() => {
    (async () => {
      const res = await courseService.getCourses();
      if (res?.data?.success) setCourses(res.data.data || []);
    })();
  }, []);

  // Ngừng gõ 400ms mới tìm kiếm, và quay về trang 1
  useEffect(() => {
    const t = setTimeout(() => {
      setQuery(search.trim());
      setPage(1);
    }, 400);
    return () => clearTimeout(t);
  }, [search]);

  // Tải danh sách mỗi khi bộ lọc / trang thay đổi
  useEffect(() => {
    let cancelled = false;
    (async () => {
      setRows(null);
      setError(null);
      const res = await paymentService.manage({ page, page_size: PAGE_SIZE, status, q: query, ...filters, method: 'vnpay' });
      if (cancelled) return;
      if (res?.data?.success) {
        setRows(res.data.data || []);
        setPagination(res.data.pagination);
        setCounts(res.data.counts || {});
        setRevenue(res.data.revenue || 0);
      } else {
        setRows([]);
        setPagination({ page: 1, total: 0, total_pages: 1 });
        setCounts({}); setRevenue(0);
        setError(res?.data?.message || 'Không thể tải danh sách giao dịch.');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [page, status, query, filters, reloadKey]);

  // Đổi 1 bộ lọc -> về trang 1
  function setFilter(key, value) {
    setFilters((f) => ({ ...f, [key]: value }));
    setPage(1);
  }
  function resetFilters() {
    setFilters(emptyFilters);
    setSearch('');
    setStatus('');
    setPage(1);
  }

  // Đối soát tất cả đơn đang chờ với VNPay
  async function handleReconcileAll() {
    if (!window.confirm(`Đối soát ${counts.pending || 0} đơn đang chờ khớp bộ lọc tìm kiếm, khóa học và ngày hiện tại?`)) return;
    setSyncingAll(true);
    try {
      const res = await paymentService.reconcileAll({ ...filters, q: query });
      showToast(res?.data?.message || 'Không thể đối soát.', res?.data?.success ? 'success' : 'error');
      setReloadKey((k) => k + 1);
    } finally {
      setSyncingAll(false);
    }
  }

  // Đối soát 1 đơn (trong hộp thoại chi tiết): hiển thị kết quả và cập nhật lại đơn
  async function handleReconcileOne() {
    const seq = detailSequence.current;
    setSyncingOne(true);
    setSyncResult(null);
    try {
      const res = await paymentService.reconcile(detail.id);
      setReloadKey(k => k + 1);
      if (seq !== detailSequence.current) return;
      if (res?.data?.success) {
        setDetail(res.data.data);
        setSyncResult({ outcome: res.data.outcome, message: res.data.message, detail: res.data.detail });
      } else {
        setSyncResult({ outcome: 'error', message: res?.data?.message || 'Không thể đối soát.' });
      }
    } finally {
      setSyncingOne(false);
    }
  }

  async function openDetail(p) {
    const seq = ++detailSequence.current;
    setDetail(p);
    setSyncResult(null);
    setRefundOpen(false);
    setRefundReason('');
    setRevokeAccess(true);
    const res = await paymentService.detail(p.id);
    if (seq !== detailSequence.current) return;
    if (res.ok) setDetail(res.data.data);
    else setSyncResult({ outcome: 'error', message: res.data?.message || 'Không thể tải chi tiết giao dịch.' });
  }
  function closeDetail() { detailSequence.current++; setDetail(null); }

  // Hoàn tiền toàn phần: hỏi xác nhận, gửi yêu cầu (đơn VNPay -> VNPay xử lý), cập nhật lại đơn
  async function handleRefund() {
    const seq = detailSequence.current;
    const reason = refundReason.trim();
    if (reason.length < 5) {
      setSyncResult({ outcome: 'error', message: 'Vui lòng nhập lý do hoàn tiền (ít nhất 5 ký tự).' });
      return;
    }
    const via = 'qua VNPay';
    const revokeText = revokeAccess ? ' và THU HỒI quyền học của học viên' : '';
    if (!window.confirm(`Hoàn ${fmtMoney(detail.amount)} ${via} cho ${detail.user_name}${revokeText}? Thao tác không thể hoàn tác.`)) return;
    setRefunding(true);
    setSyncResult(null);
    try {
      const res = await paymentService.refund(detail.id, reason, revokeAccess);
      setReloadKey(k => k + 1);
      if (seq !== detailSequence.current) return;
      if (res?.data?.success) {
        setDetail(res.data.data);
        setRefundOpen(false);
        setSyncResult({ outcome: res.data.data.refund_operation?.state === 'completed' ? 'paid' : 'waiting', message: res.data.message });
      } else {
        setSyncResult({ outcome: 'error', message: res?.data?.message || 'Không thể hoàn tiền.' });
        const latest = await paymentService.detail(detail.id);
        if (seq === detailSequence.current && latest.ok) setDetail(latest.data.data);
      }
    } finally {
      setRefunding(false);
    }
  }

  async function handleRefundReconcile() {
    const seq = detailSequence.current;
    setRefunding(true); setSyncResult(null);
    try {
      const res = await paymentService.reconcileRefund(detail.id);
      setReloadKey(k => k + 1);
      if (seq !== detailSequence.current) return;
      if (res.data?.data) setDetail(res.data.data);
      setSyncResult({ outcome: !res.ok ? 'error' : res.data.data.refund_operation?.state === 'completed' ? 'paid' : 'waiting', message: res.data?.message || 'Không thể đối soát hoàn tiền.' });
    } finally { setRefunding(false); }
  }

  const allCount = Object.values(counts).reduce((a, b) => a + b, 0);
  const hasFilter = search || status || Object.values(filters).some(Boolean);
  const refundOperation = detail?.refund_operation;
  const canRefund = detail?.status === 'completed' && viaGateway(detail) && (!refundOperation || refundOperation.state === 'failed');

  return (
    <>
      <div className="page-header">
        <div className="breadcrumb">
          <Link to="/admin">Admin</Link> / <span>Quản lý Giao dịch</span>
        </div>
        <h1 className="page-title">💳 Quản lý Giao dịch</h1>
        <p className="page-subtitle">Tra cứu các giao dịch VNPay, lọc theo trạng thái và xem chi tiết thanh toán khóa học.</p>
      </div>

      {/* Tab trạng thái kèm số lượng + nút đối soát */}
      <div className="user-tabs" style={{ alignItems: 'center' }}>
        {STATUS_TABS.map((t) => (
          <button
            key={t.key || 'all'}
            type="button"
            className={`user-tab${status === t.key ? ' active' : ''}`}
            onClick={() => {
              setStatus(t.key);
              setPage(1);
            }}
          >
            {t.label}
            <span className="user-tab-count">{error ? '—' : rows === null ? '…' : t.key ? counts[t.key] || 0 : allCount}</span>
          </button>
        ))}
        <button
          type="button"
          className="btn btn-outline btn-sm"
          style={{ marginLeft: 'auto' }}
          disabled={syncingAll || rows === null || !!error || !counts.pending}
          title="Chỉ đối soát đơn đang chờ khớp tìm kiếm, khóa học và khoảng ngày đang chọn, không phụ thuộc tab trạng thái"
          onClick={handleReconcileAll}
        >
          {syncingAll ? '⏳ Đang đối soát...' : `🔄 Đối soát ${rows === null || error ? '—' : counts.pending || 0} đơn chờ trong bộ lọc`}
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          {/* Bộ lọc + tìm kiếm */}
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ flex: '1 1 240px' }}>
              <label className="form-label">Tìm kiếm</label>
              <input
                type="text"
                className="form-control"
                placeholder="Mã đơn, mã GD VNPay, tên hoặc email học viên..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div style={{ flex: '0 1 220px' }}>
              <label className="form-label">Khóa học</label>
              <select className="form-control" value={filters.course_id} onChange={(e) => setFilter('course_id', e.target.value)}>
                <option value="">Tất cả khóa học</option>
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>{c.title}</option>
                ))}
              </select>
            </div>
            <div style={{ flex: '0 1 150px' }}>
              <label className="form-label">Từ ngày</label>
              <input type="date" className="form-control" value={filters.date_from} onChange={(e) => setFilter('date_from', e.target.value)} />
            </div>
            <div style={{ flex: '0 1 150px' }}>
              <label className="form-label">Đến ngày</label>
              <input type="date" className="form-control" value={filters.date_to} onChange={(e) => setFilter('date_to', e.target.value)} />
            </div>
            {hasFilter && (
              <button type="button" className="btn btn-ghost btn-sm" onClick={resetFilters} style={{ marginBottom: 2 }}>
                ✕ Xóa lọc
              </button>
            )}
          </div>

          {/* Tóm tắt kết quả lọc */}
          <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <span>
              Tìm thấy <strong style={{ color: 'var(--secondary)' }}>{error || rows === null ? '—' : pagination.total}</strong> giao dịch
            </span>
            <span>
              Doanh thu (đơn thành công trong kết quả lọc): <strong style={{ color: 'var(--success)' }}>{error || rows === null ? '—' : fmtMoney(revenue)}</strong>
            </span>
          </div>

          {error && <div role="alert" className="alert alert-danger">{error} <button className="btn btn-outline btn-sm" onClick={() => setReloadKey(k => k + 1)}>Thử tải lại</button></div>}

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Mã đơn / Ngày tạo</th>
                  <th>Học viên</th>
                  <th>Khóa học</th>
                  <th>Số tiền</th>
                  <th>Phương thức</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {rows === null && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Đang tải giao dịch...</td>
                  </tr>
                )}
                {rows?.length === 0 && !error && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Không có giao dịch phù hợp.</td>
                  </tr>
                )}
                {rows?.map((p) => (
                  <tr key={p.id} className="row-clickable" title="Bấm để xem chi tiết" onClick={() => openDetail(p)}>
                    <td>
                      <span style={{ display: 'block', fontFamily: 'monospace', fontSize: '0.8rem' }}>{p.transaction_ref || `#${p.id}`}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{fmtDateTime(p.created_at)}</span>
                    </td>
                    <td>
                      <strong style={{ display: 'block' }}>{p.user_name}</strong>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{p.email}</span>
                    </td>
                    <td style={{ maxWidth: 200 }}>
                      <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.course_title}</span>
                    </td>
                    <td style={{ fontWeight: 700, whiteSpace: 'nowrap', textDecoration: p.status === 'refunded' ? 'line-through' : 'none' }}>{fmtMoney(p.amount)}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>{METHODS[p.method] || p.method}</td>
                    <td><StatusBadge status={p.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Phân trang */}
          {pagination.total_pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.75rem', marginTop: '1.25rem' }}>
              <button className="btn btn-outline btn-sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>‹ Trước</button>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Trang <strong>{pagination.page}</strong> / {pagination.total_pages}
              </span>
              <button className="btn btn-outline btn-sm" disabled={page >= pagination.total_pages} onClick={() => setPage((p) => p + 1)}>Sau ›</button>
            </div>
          )}
        </div>
      </div>

      {/* Chi tiết đơn hàng */}
      <Modal open={!!detail} onClose={closeDetail} overlayClassName="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[2000] overflow-y-auto p-4 md:p-10">
        {detail && (
          <div
            className="card modal-panel"
            style={{ width: '100%', maxWidth: 520, maxHeight: 'calc(100dvh - 5rem)', overflowY: 'auto', margin: '0 auto', animation: 'modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="card-header">
              <h3>Chi tiết giao dịch</h3>
              <button className="btn-icon" aria-label="Đóng chi tiết" onClick={closeDetail}>✕</button>
            </div>
            <div className="card-body" style={{ fontSize: '0.88rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.4rem', fontWeight: 800 }}>{fmtMoney(detail.amount)}</span>
                <StatusBadge status={detail.status} />
              </div>
              {[
                ['Mã đơn hàng', detail.transaction_ref || `#${detail.id}`],
                ['Học viên', `${detail.user_name} (${detail.email})`],
                ['Khóa học', detail.course_title],
                ['Phương thức', METHODS[detail.method] || detail.method],
                ['Mã GD VNPay', detail.gateway_txn_no && detail.gateway_txn_no !== '0' ? detail.gateway_txn_no : '—'],
                ['Ngân hàng', detail.bank_code || '—'],
                ['Mã phản hồi', detail.response_code ? `${detail.response_code} — ${detail.response_message}` : '—'],
                ['Ghi chú', detail.note || '—'],
                ['Ngày tạo đơn', fmtDateTime(detail.created_at)],
                ['Ngày thanh toán', fmtDateTime(detail.paid_at)],
                ['Cập nhật lần cuối', fmtDateTime(detail.updated_at)],
                ['Quyền học khóa này', detail.enrolled ? '✅ Đang được học' : '— Chưa ghi danh'],
                // Thông tin hoàn tiền (chỉ đơn đã hoàn)
                ...(detail.status === 'refunded'
                  ? [
                      ['Ngày hoàn tiền', fmtDateTime(detail.refunded_at)],
                      ['Lý do hoàn tiền', detail.refund_reason || '—'],
                      ['Mã GD hoàn (VNPay)', detail.refund_txn_no || '—'],
                    ]
                  : []),
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', padding: '0.45rem 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>{k}</span>
                  <strong style={{ textAlign: 'right', wordBreak: 'break-word' }}>{v}</strong>
                </div>
              ))}
              {refundOperation && <div role="status" style={{ marginTop: 16, padding: 12, background: 'var(--surface-2)', borderRadius: 8 }}>
                <strong>{REFUND_STATE[refundOperation.state] || refundOperation.state}</strong><p>{refundOperation.message}</p>
                {['sending', 'pending', 'unknown', 'confirmed'].includes(refundOperation.state) && <button className="btn btn-primary btn-sm" disabled={refunding} onClick={handleRefundReconcile}>
                  {refunding ? 'Đang kiểm tra…' : 'Đối soát hoàn tiền'}
                </button>}
              </div>}
              {/* Kết quả đối soát vừa chạy */}
              {syncResult && (
                <div
                  className={`alert ${syncResult.outcome === 'paid' ? 'alert-success' : syncResult.outcome === 'error' ? 'alert-danger' : 'alert-info'}`}
                  style={{ marginTop: '1rem', fontSize: '0.82rem' }}
                >
                  {syncResult.message}
                  {syncResult.detail && <div style={{ opacity: 0.75, marginTop: 4 }}>{syncResult.detail}</div>}
                </div>
              )}
              {/* Hoàn tiền: chỉ đơn đã thanh toán thành công */}
              {canRefund && !refundOpen && (
                <button className="btn btn-outline btn-sm" style={{ width: '100%', marginTop: '1rem', color: 'var(--danger)', borderColor: 'var(--danger)' }} onClick={() => setRefundOpen(true)}>
                  ↩️ Hoàn tiền
                </button>
              )}
              {canRefund && refundOpen && (
                <div style={{ marginTop: '1rem', padding: '0.9rem', border: '1px solid var(--border)', borderRadius: 8 }}>
                  <div style={{ fontWeight: 700, marginBottom: '0.5rem' }}>
                    ↩️ Hoàn tiền toàn phần {fmtMoney(detail.amount)} qua VNPay
                  </div>
                  <textarea
                    className="form-control"
                    rows={2}
                    maxLength={255}
                    placeholder="Lý do hoàn tiền (bắt buộc), VD: Học viên đăng ký nhầm khóa"
                    value={refundReason}
                    onChange={(e) => setRefundReason(e.target.value)}
                  />
                  <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', marginTop: '0.6rem', fontSize: '0.82rem', cursor: 'pointer' }}>
                    <input type="checkbox" checked={revokeAccess} onChange={(e) => setRevokeAccess(e.target.checked)} style={{ marginTop: 3 }} />
                    <span>
                      Thu hồi quyền học khóa này
                      <span style={{ display: 'block', color: 'var(--text-muted)' }}>Điểm quiz và tiến độ vẫn được lưu, hiện lại nếu học viên mua lại khóa.</span>
                    </span>
                  </label>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                    <button className="btn btn-ghost btn-sm" style={{ flex: 1 }} disabled={refunding} onClick={() => setRefundOpen(false)}>Hủy</button>
                    <button className="btn btn-sm" style={{ flex: 2, background: 'var(--danger)', color: '#fff' }} disabled={refunding} onClick={handleRefund}>
                      {refunding ? '⏳ Đang gửi yêu cầu...' : 'Xác nhận hoàn tiền'}
                    </button>
                  </div>
                </div>
              )}
              {detail.status === 'pending' && (
                <>
                  <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--warning)' }}>
                    ⚠️ Đơn đang chờ: học viên chưa hoàn tất thanh toán, hoặc đã trả tiền nhưng chưa được VNPay chuyển về
                    hệ thống (đóng trình duyệt giữa chừng). Bấm kiểm tra để hỏi VNPay trạng thái thật.
                  </p>
                  <button className="btn btn-primary btn-sm" style={{ width: '100%', marginTop: '0.5rem' }} disabled={syncingOne} onClick={handleReconcileOne}>
                    {syncingOne ? '⏳ Đang hỏi VNPay...' : detail.method === 'vnpay' ? '🔄 Kiểm tra với VNPay' : '🔄 Kiểm tra / hủy đơn quá hạn'}
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
