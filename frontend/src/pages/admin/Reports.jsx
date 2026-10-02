import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Chart, registerables } from 'chart.js';
import { reportService } from '../../services/reportService';
import { useToast } from '../../hooks/useToast';
import CourseThumb from '../../components/common/CourseThumb.jsx';

Chart.register(...registerables);

/* ─── Helpers ─────────────────────────────────────────────────────── */
function fmt(num) {
  return Number(num || 0).toLocaleString('vi-VN');
}
function fmtMoney(num) {
  return Number(num || 0).toLocaleString('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 });
}
// API trả "YYYY-MM-DD HH:MM:SS"; Safari không parse được dấu cách nên đổi sang "T".
// Định dạng ngày dd/mm/yyyy; chuỗi ngày không hợp lệ hiển thị "—"
function fmtDate(str) {
  if (!str) return '—';
  const d = new Date(String(str).replace(' ', 'T'));
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
// Nhãn màu cho trạng thái giao dịch
function statusBadge(status) {
  const map = {
    completed: { label: 'Thành công', cls: 'badge-success' },
    pending:   { label: 'Đang xử lý', cls: 'badge-warning' },
    failed:    { label: 'Thất bại',   cls: 'badge-danger' },
    refunded:  { label: 'Đã hoàn tiền', cls: 'badge-info' },
  };
  const s = map[status] || { label: status, cls: 'badge-primary' };
  return <span className={`badge ${s.cls}`}>{s.label}</span>;
}
// Tên + biểu tượng của các phương thức thanh toán
// Hệ thống chỉ thanh toán qua VNPay
const METHOD_NAMES = { vnpay: 'VNPay' };
const METHOD_ICONS = { vnpay: '🔴' };
function methodLabel(m) {
  return METHOD_ICONS[m] ? `${METHOD_ICONS[m]} ${METHOD_NAMES[m]}` : m;
}
// Thanh tiến độ nhỏ: >= 75% xanh lá, >= 40% vàng, còn lại đỏ
function ProgressBar({ pct }) {
  const p = Math.min(100, Math.max(0, Math.round(pct || 0)));
  const color = p >= 75 ? 'var(--success)' : p >= 40 ? 'var(--warning)' : 'var(--danger)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ flex: 1, height: 6, background: 'var(--surface-2)', borderRadius: 99, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${p}%`, background: color, borderRadius: 99, transition: 'width .4s' }} />
      </div>
      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', minWidth: 32, textAlign: 'right' }}>{p}%</span>
    </div>
  );
}

/* ─── Biểu đồ doanh thu (thích ứng theo range) ─────────────────── */
// Biểu đồ doanh thu (Chart.js): vẽ lại mỗi khi dữ liệu thay đổi, hủy biểu đồ cũ trước khi vẽ mới
function RevenueLineChart({ data }) {
  const canvasRef = useRef(null);
  const chartRef  = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Nếu không có dữ liệu thực (tất cả = 0), vẫn vẽ nhưng hiển thị trục
    const hasData = data?.length > 0;
    if (chartRef.current) chartRef.current.destroy();

    if (!hasData) return;

    // Chọn loại biểu đồ: nhiều điểm → line mượt; ít điểm → bar
    const useLineChart = data.length > 10;
    const primaryColor = '#2563eb';

    chartRef.current = new Chart(canvasRef.current, {
      type: useLineChart ? 'line' : 'bar',
      data: {
        labels: data.map((d) => d.label),
        datasets: [
          {
            label: 'Doanh thu (VNĐ)',
            data:  data.map((d) => d.revenue),
            backgroundColor: useLineChart ? 'rgba(37,99,235,0.10)' : 'rgba(37,99,235,0.18)',
            borderColor:     primaryColor,
            borderWidth: useLineChart ? 2 : 2,
            borderRadius: useLineChart ? 0 : 6,
            fill: useLineChart,
            tension: 0.35,
            pointRadius: data.length > 20 ? 2 : 4,
            pointHoverRadius: 6,
            pointBackgroundColor: primaryColor,
            hoverBackgroundColor: 'rgba(37,99,235,0.35)',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ' Doanh thu: ' + fmt(ctx.parsed.y) + ' ₫',
              afterLabel: (ctx) => {
                const orders = data[ctx.dataIndex]?.orders;
                return orders != null ? ` Số đơn: ${orders}` : '';
              },
            },
          },
        },
        scales: {
          y: {
            ticks: { callback: (v) => fmt(v) + ' ₫', font: { size: 11 } },
            grid: { color: 'rgba(0,0,0,.05)' },
            beginAtZero: true,
          },
          x: {
            grid: { display: false },
            ticks: {
              // Khi quá nhiều điểm, chỉ hiện 1 số nhãn để tránh chật
              maxTicksLimit: data.length > 20 ? 8 : data.length > 10 ? 12 : data.length,
              maxRotation: 0,
              font: { size: 10 },
            },
          },
        },
      },
    });
    return () => { chartRef.current?.destroy(); };
  }, [data]);

  // Hiện placeholder khi chưa có dữ liệu
  if (!data?.length) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '0.5rem' }}>
        <span style={{ fontSize: '2rem' }}>📊</span>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Chưa có dữ liệu trong khoảng thời gian này</p>
      </div>
    );
  }

  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />;
}

/* ─── Biểu đồ Doughnut phương thức ──────────────────────────────── */
// Biểu đồ tròn doanh thu theo phương thức thanh toán
function MethodDoughnut({ data }) {
  const canvasRef = useRef(null);
  const chartRef  = useRef(null);
  const COLORS = ['#2563eb', '#8b5cf6', '#ec4899', '#06b6d4', '#f59e0b'];

  useEffect(() => {
    if (!data?.length || !canvasRef.current) return;
    if (chartRef.current) chartRef.current.destroy();
    chartRef.current = new Chart(canvasRef.current, {
      type: 'doughnut',
      data: {
        labels: data.map((d) => METHOD_NAMES[d.method] || d.method),
        datasets: [{
          data:            data.map((d) => d.revenue),
          backgroundColor: COLORS.slice(0, data.length),
          borderWidth:     2,
          borderColor:     '#fff',
          hoverOffset:     8,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } },
          tooltip: { callbacks: { label: (ctx) => ' ' + fmt(ctx.parsed) + ' ₫' } },
        },
      },
    });
    return () => { chartRef.current?.destroy(); };
  }, [data]);

  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />;
}

/* ─── Nút xuất CSV (tải toàn bộ dữ liệu, không giới hạn 20 dòng) ─── */
function ExportButton({ type, label = '⬇ Xuất CSV' }) {
  const { showToast } = useToast();
  const [busy, setBusy] = useState(false);

  async function handleClick() {
    setBusy(true);
    try {
      const done = await reportService.exportCsv(type);
      if (!done) showToast('Không thể xuất báo cáo.', 'error');
    } catch {
      showToast('Lỗi kết nối máy chủ.', 'error');
    } finally {
      setBusy(false);
    }
  }

  return (
    <button className="btn btn-outline btn-sm" onClick={handleClick} disabled={busy} style={{ whiteSpace: 'nowrap' }}>
      {busy ? 'Đang xuất...' : label}
    </button>
  );
}

// Màu theo mức điểm (%): >= 70 xanh lá, >= 50 vàng, còn lại đỏ
function scoreColor(pct) {
  if (pct == null) return 'var(--text-muted)';
  return pct >= 70 ? 'var(--success)' : pct >= 50 ? 'var(--warning)' : 'var(--danger)';
}

// Tiêu đề 1 khối trong tab Học tập, kèm nút xuất CSV (nếu có)
function SectionHeader({ title, exportType }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', padding: '1rem 1.5rem 0.5rem' }}>
      <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>{title}</h4>
      {exportType && <ExportButton type={exportType} />}
    </div>
  );
}

// Ghi chú dưới các bảng chỉ hiện dữ liệu mới nhất
function LimitNote({ count, limit }) {
  if (count < limit) return null;
  return (
    <p style={{ padding: '0.75rem 1.5rem', fontSize: '0.78rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border)' }}>
      Đang hiển thị {limit} mục mới nhất — bấm “Xuất CSV” để tải toàn bộ.
    </p>
  );
}

/* ─── Tab Học tập ─────────────────────────────────────────────────── */
function LearningTab({ data }) {
  const ov = data.overview || {};
  const kpis = [
    { label: 'Lượt làm quiz', value: fmt(ov.quiz_attempts), sub: `${fmt(ov.active_learners)} học viên tham gia` },
    { label: 'Điểm quiz TB', value: `${ov.avg_quiz_score ?? 0}%`, sub: 'Trên tất cả lượt làm', color: scoreColor(ov.avg_quiz_score) },
    { label: 'Tỷ lệ đạt', value: ov.pass_rate != null ? `${ov.pass_rate}%` : '—', sub: 'Theo điểm đạt của từng quiz (bỏ quiz không đặt điểm đạt)' },
    { label: 'Câu hỏi AI Tutor', value: fmt(ov.ai_questions), sub: `${ov.ai_no_answer_rate ?? 0}% không tìm thấy trong tài liệu` },
  ];

  return (
    <div className="card-body" style={{ padding: 0 }}>
      {/* KPI học tập */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', padding: '1.25rem 1.5rem' }}>
        {kpis.map((k) => (
          <div key={k.label} style={{ border: '1px solid var(--border)', borderRadius: 10, padding: '0.9rem 1rem' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>{k.label}</div>
            <div style={{ fontSize: '1.35rem', fontWeight: 800, color: k.color || 'var(--secondary)' }}>{k.value}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{k.sub}</div>
          </div>
        ))}
      </div>

      {/* Học tập theo khóa */}
      <SectionHeader title="📘 Kết quả học tập theo khóa học" exportType="learning" />
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Khóa học</th>
              <th>Học viên</th>
              <th>Lượt làm quiz</th>
              <th>Điểm TB</th>
              <th>Tỷ lệ đạt</th>
              <th>Hoàn thành TB</th>
            </tr>
          </thead>
          <tbody>
            {data.by_course?.map((c) => (
              <tr key={c.id}>
                <td style={{ maxWidth: 240 }}>
                  <strong style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.title}</strong>
                </td>
                <td>{fmt(c.students)}</td>
                <td>{fmt(c.attempts)}</td>
                <td style={{ fontWeight: 700, color: scoreColor(c.avg_score) }}>{c.avg_score != null ? `${c.avg_score}%` : '—'}</td>
                <td>{c.pass_rate != null ? `${c.pass_rate}%` : '—'}</td>
                <td style={{ minWidth: 140 }}>
                  {c.avg_completion != null ? <ProgressBar pct={c.avg_completion} /> : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Chủ đề yếu nhất */}
      <SectionHeader title="⚠️ Chủ đề học viên làm sai nhiều nhất" exportType="topics" />
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Chủ đề</th>
              <th>Khóa học</th>
              <th>Số câu đã làm</th>
              <th>Tỷ lệ đúng</th>
              <th>Học viên</th>
            </tr>
          </thead>
          <tbody>
            {data.weak_topics?.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Chưa đủ dữ liệu (cần ≥ 10 câu trả lời mỗi chủ đề).</td></tr>
            )}
            {data.weak_topics?.map((t, i) => (
              <tr key={`${t.topic}-${t.course_title}`}>
                <td style={{ color: 'var(--text-muted)' }}>{i + 1}</td>
                <td><strong>{t.topic}</strong></td>
                <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: 200 }}>
                  <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.course_title}</span>
                </td>
                <td>{t.correct}/{t.answered}</td>
                <td style={{ fontWeight: 700, color: scoreColor(t.correct_pct) }}>{t.correct_pct}%</td>
                <td>{fmt(t.students)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Sử dụng AI Tutor */}
      <SectionHeader title="🤖 Sử dụng AI Tutor theo khóa học" />
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Khóa học</th>
              <th>Người dùng</th>
              <th>Cuộc trò chuyện</th>
              <th>Câu hỏi</th>
              <th>Không tìm thấy trong tài liệu</th>
            </tr>
          </thead>
          <tbody>
            {data.ai_by_course?.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Chưa có ai sử dụng AI Tutor.</td></tr>
            )}
            {data.ai_by_course?.map((a) => (
              <tr key={a.id}>
                <td><strong>{a.title}</strong></td>
                <td>{fmt(a.users)}</td>
                <td>{fmt(a.conversations)}</td>
                <td>{fmt(a.questions)}</td>
                <td>
                  {fmt(a.no_answer)}
                  {a.questions > 0 && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}> ({Math.round((a.no_answer / a.questions) * 100)}%)</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ─── Component chính ────────────────────────────────────────────── */
// Loại file CSV xuất ra tương ứng với từng tab bảng
const EXPORT_BY_TAB = { revenue: 'payments', students: 'enrollments', courses: 'courses' };

export default function AdminReports() {
  const [loading, setLoading] = useState(true);
  const [report,  setReport]  = useState(null);
  const [error,   setError]   = useState(null);
  const [activeTab, setActiveTab] = useState('revenue'); // 'revenue' | 'students' | 'courses' | 'learning'

  // Số liệu học tập: chỉ tải khi mở tab "Học tập" lần đầu
  const [learning, setLearning] = useState(null);
  const [learningError, setLearningError] = useState(null);
  useEffect(() => {
    if (activeTab !== 'learning' || learning) return;
    (async () => {
      const res = await reportService.getLearning();
      if (res?.data?.success) setLearning(res.data.data);
      else setLearningError(res?.data?.message || 'Không thể tải số liệu học tập.');
    })();
  }, [activeTab, learning]);

  // Bộ lọc biểu đồ doanh thu
  const [chartRange,   setChartRange]   = useState('7d');
  const [chartData,    setChartData]    = useState([]);
  const [chartLoading, setChartLoading] = useState(false);

  // Các khoảng thời gian cho biểu đồ doanh thu và tiêu đề tương ứng
  const RANGES = [
    { key: 'today', label: 'Hôm nay' },
    { key: '7d',    label: '7 ngày'  },
    { key: '30d',   label: '30 ngày' },
    { key: '1y',    label: '1 năm'  },
  ];
  const RANGE_TITLES = {
    today: 'Doanh thu hôm nay (theo giờ)',
    '7d':  'Doanh thu 7 ngày gần nhất',
    '30d': 'Doanh thu 30 ngày gần nhất',
    '1y':  'Doanh thu 12 tháng gần nhất',
  };

  // Khi mở trang: tải toàn bộ dữ liệu báo cáo 1 lần
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const res = await reportService.getSummary(chartRange);
        if (res?.data?.success) {
          setReport(res.data.data);
          setChartData(res.data.data.revenue_weekly || []);
        } else setError('Không thể tải dữ liệu báo cáo.');
      } catch {
        setError('Lỗi kết nối đến server.');
      } finally {
        setLoading(false);
      }
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Chỉ reload phần biểu đồ khi đổi range (giữ nguyên KPI và các dữ liệu khác)
  async function handleRangeChange(range) {
    setChartRange(range);
    setChartLoading(true);
    try {
      const res = await reportService.getSummary(range);
      if (res?.data?.success) setChartData(res.data.data.revenue_weekly || []);
    } finally {
      setChartLoading(false);
    }
  }

  const ov = report?.overview || {};

  /* KPI cards */
  // Các thẻ KPI: doanh thu, học viên, lượt ghi danh, tỷ lệ hoàn thành...
  const kpis = [
    {
      icon: '💰', label: 'Tổng doanh thu', value: fmtMoney(ov.total_revenue),
      sub: `${fmt(ov.total_orders)} đơn thành công`, color: 'rgba(16,185,129,.12)', iconColor: 'var(--success)',
    },
    {
      icon: '🎒', label: 'Tổng học viên', value: fmt(ov.total_students),
      sub: `+${fmt(ov.new_students_30d)} trong 30 ngày`, color: 'rgba(37,99,235,.1)', iconColor: 'var(--primary)',
    },
    {
      icon: '📊', label: 'Tỷ lệ hoàn thành TB', value: `${ov.avg_completion_pct ?? '—'}%`,
      sub: 'Trên tất cả khóa học', color: 'rgba(139,92,246,.1)', iconColor: 'var(--accent)',
    },
    {
      icon: '⏳', label: 'Đơn đang xử lý', value: fmt(ov.pending_orders),
      sub: `${fmt(ov.failed_orders)} thất bại · ${fmt(ov.refunded_orders)} hoàn tiền (${fmtMoney(ov.refunded_amount)})`,
      color: 'rgba(245,158,11,.1)', iconColor: 'var(--warning)',
    },
  ];

  return (
    <>
      {/* ── Page Header ── */}
      <div className="page-header">
        <div className="breadcrumb">
          <Link to="/admin">Admin</Link> / <span>Báo cáo</span>
        </div>
        <h1 className="page-title">📄 Báo cáo &amp; Thống kê</h1>
        <p className="page-subtitle">Phân tích doanh thu, học viên và hiệu suất khóa học toàn hệ thống.</p>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '5rem 0' }}>
          <div className="spinner" style={{ width: 36, height: 36, border: '3px solid var(--border)', borderTopColor: 'var(--primary)' }} />
          <p style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Đang tải dữ liệu báo cáo...</p>
        </div>
      )}

      {!loading && error && (
        <div className="alert alert-danger">{error}</div>
      )}

      {!loading && report && (
        <>
          {/* ── KPI Cards ── */}
          <div className="stats-grid" style={{ marginBottom: '2rem' }}>
            {kpis.map((k) => (
              <div key={k.label} className="stat-card">
                <div className="stat-icon-wrap" style={{ background: k.color, color: k.iconColor, fontSize: '1.4rem' }}>
                  {k.icon}
                </div>
                <div>
                  <div className="stat-label">{k.label}</div>
                  <div className="stat-value" style={{ fontSize: '1.4rem' }}>{k.value}</div>
                  <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>{k.sub}</span>
                </div>
              </div>
            ))}
          </div>

          {/* ── Biểu đồ doanh thu 7 ngày ── */}
          <div className="grid grid-2" style={{ marginBottom: '2rem', alignItems: 'start' }}>
            {/* Bar chart doanh thu */}
            <div className="card">
              <div className="card-header" style={{ flexWrap: 'wrap', gap: '0.5rem' }}>
                {/* Biểu đồ doanh thu + nút chọn khoảng thời gian */}
                <h3 style={{ fontSize: '1rem', flex: 1, minWidth: 160 }}>📈 {RANGE_TITLES[chartRange]}</h3>
                {/* Bộ lọc khoảng thời gian */}
                <div style={{ display: 'flex', gap: '0.35rem', flexShrink: 0 }}>
                  {RANGES.map((r) => (
                    <button
                      key={r.key}
                      onClick={() => handleRangeChange(r.key)}
                      disabled={chartLoading}
                      style={{
                        padding: '0.3rem 0.75rem',
                        fontSize: '0.78rem',
                        fontWeight: chartRange === r.key ? 700 : 500,
                        borderRadius: 99,
                        border: chartRange === r.key ? '2px solid var(--primary)' : '1px solid var(--border)',
                        background: chartRange === r.key ? 'var(--primary)' : 'transparent',
                        color: chartRange === r.key ? '#fff' : 'var(--text-muted)',
                        cursor: chartLoading ? 'wait' : 'pointer',
                        transition: 'all 0.18s',
                        opacity: chartLoading && chartRange !== r.key ? 0.5 : 1,
                      }}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="card-body" style={{ height: 220, position: 'relative' }}>
                {chartLoading && (
                  <div style={{
                    position: 'absolute', inset: 0, display: 'flex', alignItems: 'center',
                    justifyContent: 'center', background: 'rgba(0,0,0,.04)', borderRadius: 8, zIndex: 1,
                  }}>
                    <div className="spinner" style={{ width: 28, height: 28, border: '3px solid var(--border)', borderTopColor: 'var(--primary)' }} />
                  </div>
                )}
                <RevenueLineChart data={chartData} />
              </div>
            </div>

            {/* Doughnut phương thức */}
            <div className="card">
              <div className="card-header">
                {/* Biểu đồ doanh thu theo phương thức thanh toán */}
                <h3 style={{ fontSize: '1rem' }}>💳 Doanh thu theo phương thức</h3>
              </div>
              <div className="card-body" style={{ height: 220 }}>
                {report.revenue_by_method?.length > 0 ? (
                  <MethodDoughnut data={report.revenue_by_method} />
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '0.5rem' }}>
                    <span style={{ fontSize: '2.5rem' }}>💳</span>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Chưa có giao dịch hoàn thành</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ── Tabs bảng chi tiết ── */}
          <div className="card">
            {/* Tab bar */}
            <div
              className="card-header"
              style={{ padding: '0 1.5rem', borderBottom: '1px solid var(--border)', gap: 0, justifyContent: 'flex-start', overflowX: 'auto', flexWrap: 'nowrap' }}
            >
              {[
                { key: 'revenue',  label: '💰 Giao dịch' },
                { key: 'students', label: '🎒 Đăng ký học' },
                { key: 'courses',  label: '📚 Top khóa học' },
                { key: 'learning', label: '📘 Học tập' },
              ].map((t) => (
                <button
                  key={t.key}
                  onClick={() => setActiveTab(t.key)}
                  style={{
                    padding: '1rem 1.25rem',
                    background: 'none',
                    border: 'none',
                    borderBottom: activeTab === t.key ? '2px solid var(--primary)' : '2px solid transparent',
                    color: activeTab === t.key ? 'var(--primary)' : 'var(--text-muted)',
                    fontWeight: activeTab === t.key ? 700 : 500,
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    whiteSpace: 'nowrap',
                    marginBottom: -1,
                  }}
                >
                  {t.label}
                </button>
              ))}
              {/* Nút xuất CSV cho bảng của tab đang mở (tab Học tập có nút riêng từng khối) */}
              {EXPORT_BY_TAB[activeTab] && (
                <div style={{ marginLeft: 'auto', paddingLeft: '1rem' }}>
                  <ExportButton type={EXPORT_BY_TAB[activeTab]} />
                </div>
              )}
            </div>

            {/* ── Tab: Giao dịch ── */}
            {activeTab === 'revenue' && (
              <div className="card-body" style={{ padding: 0 }}>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Học viên</th>
                        <th>Khóa học</th>
                        <th>Phương thức</th>
                        <th>Số tiền</th>
                        <th>Trạng thái</th>
                        <th>Ngày thanh toán</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.recent_payments?.length === 0 && (
                        <tr><td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Chưa có giao dịch nào.</td></tr>
                      )}
                      {report.recent_payments?.map((p) => (
                        <tr key={p.id}>
                          <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>#{p.id}</td>
                          <td><strong>{p.user_name}</strong></td>
                          <td style={{ maxWidth: 200 }}>
                            <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {p.course_title}
                            </span>
                          </td>
                          <td>{methodLabel(p.method)}</td>
                          <td
                            style={{
                              fontWeight: 700,
                              color: p.status === 'completed' ? 'var(--success)' : 'var(--text-muted)',
                              textDecoration: p.status === 'refunded' ? 'line-through' : 'none',
                            }}
                          >
                            {fmtMoney(p.amount)}
                          </td>
                          <td>{statusBadge(p.status)}</td>
                          <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                            {p.paid_at ? (
                              fmtDate(p.paid_at)
                            ) : (
                              <span title="Chưa thanh toán — hiển thị ngày tạo đơn">{fmtDate(p.created_at)} (tạo đơn)</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <LimitNote count={report.recent_payments?.length || 0} limit={20} />
              </div>
            )}

            {/* ── Tab: Đăng ký học ── */}
            {activeTab === 'students' && (
              <div className="card-body" style={{ padding: 0 }}>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Học viên</th>
                        <th>Email</th>
                        <th>Khóa học</th>
                        <th>Tiến độ</th>
                        <th>Ngày đăng ký</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.recent_enrollments?.length === 0 && (
                        <tr><td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Chưa có đăng ký nào.</td></tr>
                      )}
                      {report.recent_enrollments?.map((e) => {
                        const pct = e.total_lessons > 0 ? (e.done_lessons / e.total_lessons) * 100 : 0;
                        return (
                          <tr key={e.id}>
                            <td><strong>{e.user_name}</strong></td>
                            <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{e.email}</td>
                            <td style={{ maxWidth: 200 }}>
                              <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                {e.course_title}
                              </span>
                            </td>
                            <td style={{ minWidth: 140 }}>
                              <ProgressBar pct={pct} />
                              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                {e.done_lessons}/{e.total_lessons} bài
                              </span>
                            </td>
                            <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{fmtDate(e.enroll_date)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <LimitNote count={report.recent_enrollments?.length || 0} limit={20} />
              </div>
            )}

            {/* ── Tab: Top khóa học ── */}
            {activeTab === 'courses' && (
              <div className="card-body" style={{ padding: 0 }}>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Khóa học</th>
                        <th>Giảng viên</th>
                        <th>Học viên</th>
                        <th>Doanh thu</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.top_courses?.length === 0 && (
                        <tr><td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Chưa có dữ liệu.</td></tr>
                      )}
                      {report.top_courses?.map((c, i) => (
                        <tr key={c.id}>
                          <td>
                            <span style={{
                              display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                              width: 26, height: 26, borderRadius: '50%', fontSize: '0.75rem', fontWeight: 800,
                              background: i === 0 ? '#fef3c7' : i === 1 ? '#f3f4f6' : i === 2 ? '#fde8d8' : 'var(--surface-2)',
                              color: i === 0 ? '#d97706' : i === 1 ? '#6b7280' : i === 2 ? '#c2410c' : 'var(--text-muted)',
                            }}>
                              {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}
                            </span>
                          </td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                              <CourseThumb
                                src={c.thumbnail}
                                style={{ width: 40, height: 28, objectFit: 'cover', borderRadius: 4, flexShrink: 0 }}
                                fallback={
                                  <div style={{ width: 40, height: 28, background: 'var(--primary-light)', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', flexShrink: 0 }}>📘</div>
                                }
                              />
                              <strong style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 200, display: 'block' }}>{c.title}</strong>
                            </div>
                          </td>
                          <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{c.teacher_name || '—'}</td>
                          <td>
                            <span className="badge badge-primary">👥 {fmt(c.student_count)}</span>
                          </td>
                          <td style={{ fontWeight: 700, color: +c.revenue > 0 ? 'var(--success)' : 'var(--text-muted)' }}>
                            {+c.price > 0 ? fmtMoney(c.revenue) : 'Miễn phí'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* ── Tab: Học tập ── */}
            {activeTab === 'learning' && (
              learning ? (
                <LearningTab data={learning} />
              ) : learningError ? (
                <div className="alert alert-danger" style={{ margin: '1.5rem' }}>{learningError}</div>
              ) : (
                <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  Đang tải số liệu học tập...
                </div>
              )
            )}
          </div>
        </>
      )}
    </>
  );
}
