import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import { paymentService } from '../../services/paymentService';
import { monthlyBars } from '../../utils/monthlyBars';

// Chữ viết tắt làm avatar: 2 ký tự đầu của từ cuối trong tên
function initialsOf(name) {
  return name ? name.split(' ').pop().slice(0, 2).toUpperCase() : 'U';
}

// Định dạng ngày dd/mm/yyyy
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d)) return '—';
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

// Tiến độ (%) của 1 lượt ghi danh
function progressOf(e) {
  const total = Number(e.total_lessons || 0);
  return total > 0 ? Math.round((Number(e.completed_lessons || 0) / total) * 100) : 0;
}

/** Báo cáo của giảng viên: gộp Thống kê (doanh thu, top khóa học) và Học viên (tiến độ, điểm quiz) vào một trang, lọc chung theo khóa học */
export default function TeacherReports() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [teacherCourses, setTeacherCourses] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [payments, setPayments] = useState([]);
  const [courseFilter, setCourseFilter] = useState('all');
  const [search, setSearch] = useState('');

  // Khi mở trang: tải song song khóa học, ghi danh (kèm tiến độ, điểm quiz) và giao dịch; backend đã lọc theo giảng viên
  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      const [coursesRes, enrollRes, payRes] = await Promise.all([
        courseService.getCourses(),
        enrollmentService.getEnrollments(),
        paymentService.getPayments(),
      ]);
      if (cancelled) return;
      const allCourses = coursesRes?.ok ? coursesRes.data.data || [] : [];
      setTeacherCourses(allCourses.filter((c) => c.teacher_id === user?.id || user?.role === 'admin'));
      setEnrollments(enrollRes?.ok ? enrollRes.data.data || [] : []);
      setPayments(payRes?.ok ? payRes.data.data || [] : []);
      setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [user]);

  // Dữ liệu theo khóa học đang chọn (áp dụng cho mọi phần của trang)
  const inCourse = (x) => courseFilter === 'all' || x.course_id === Number(courseFilter);
  const scopedEnrollments = useMemo(() => enrollments.filter(inCourse), [enrollments, courseFilter]); // eslint-disable-line react-hooks/exhaustive-deps
  const paidPayments = useMemo(
    () => payments.filter((p) => p.status === 'completed' && inCourse(p)),
    [payments, courseFilter], // eslint-disable-line react-hooks/exhaustive-deps
  );

  // Ô tổng hợp: học viên duy nhất, lượt đăng ký, tiến độ trung bình, doanh thu (triệu đồng)
  const summary = useMemo(() => {
    const n = scopedEnrollments.length;
    const revenue = paidPayments.reduce((sum, p) => sum + Number(p.amount), 0);
    return {
      students: new Set(scopedEnrollments.map((e) => e.user_id)).size,
      enrollments: n,
      avgProgress: n ? Math.round(scopedEnrollments.reduce((s, e) => s + progressOf(e), 0) / n) : 0,
      revenue: (revenue / 1000000).toFixed(1) + 'Mđ',
    };
  }, [scopedEnrollments, paidPayments]);

  // Biểu đồ cột doanh thu 6 tháng gần nhất
  const revenueBars = useMemo(
    () => monthlyBars(paidPayments, (p) => p.paid_at, (p) => p.amount, (v) => Number(v).toLocaleString('vi-VN') + 'đ'),
    [paidPayments],
  );

  // Top 3 khóa học nhiều học viên nhất (trên toàn bộ khóa của giảng viên)
  const topCourses = useMemo(
    () =>
      teacherCourses
        .map((c) => ({ course: c, count: enrollments.filter((e) => e.course_id === c.id).length }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 3),
    [teacherCourses, enrollments],
  );

  // Bảng học viên: theo khóa đang chọn + ô tìm kiếm (tên hoặc email)
  const rows = useMemo(() => {
    const q = search.toLowerCase().trim();
    if (!q) return scopedEnrollments;
    return scopedEnrollments.filter((e) => (e.user_name || '').toLowerCase().includes(q) || (e.user_email || '').toLowerCase().includes(q));
  }, [scopedEnrollments, search]);

  const cards = [
    { icon: '👥', value: summary.students, label: 'Học viên', bg: 'rgba(99,102,241,.15)', color: 'var(--primary)' },
    { icon: '📚', value: summary.enrollments, label: 'Lượt đăng ký', bg: 'rgba(16,185,129,.15)', color: 'var(--success)' },
    { icon: '📈', value: `${summary.avgProgress}%`, label: 'Tiến độ trung bình', bg: 'rgba(245,158,11,.15)', color: 'var(--warning)' },
    { icon: '💵', value: summary.revenue, label: 'Doanh thu', bg: 'rgba(16,185,129,.15)', color: 'var(--success)' },
  ];

  return (
    <>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <h1 className="page-title">📊 Báo cáo</h1>
          <p className="page-subtitle">Học viên, tiến độ học tập, kết quả kiểm tra và doanh thu các khóa học của bạn.</p>
        </div>
        <select className="form-control" style={{ maxWidth: 260 }} value={courseFilter} onChange={(e) => setCourseFilter(e.target.value)}>
          <option value="all">Tất cả khóa học</option>
          {teacherCourses.map((c) => (
            <option key={c.id} value={c.id}>
              {c.title}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading-page">
          <div className="spinner" />
        </div>
      ) : (
        <>
          {/* Ô tổng hợp */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            {cards.map((c) => (
              <div className="stat-card" key={c.label}>
                <div className="stat-icon" style={{ background: c.bg, color: c.color }}>
                  {c.icon}
                </div>
                <div className="stat-info">
                  <div className="stat-value">{c.value}</div>
                  <div className="stat-label">{c.label}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Doanh thu theo tháng + top khóa học */}
          <div className="col-3-1" style={{ marginBottom: '1.5rem' }}>
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>📈 Doanh thu theo tháng (6 tháng gần nhất)</h3>
              <div className="bar-chart">
                {revenueBars.map((b) => (
                  <div className="bar-item" key={b.label}>
                    <div className="bar-value" style={{ height: `${b.height}%`, background: 'var(--success)' }} data-tooltip={b.tooltip}></div>
                    <span className="bar-label">{b.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '1.25rem' }}>🔥 Khóa học nhiều học viên nhất</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {topCourses.length === 0 && (
                  <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem' }}>Chưa có khóa học.</p>
                )}
                {topCourses.map(({ course, count }, i) => (
                  <div
                    key={course.id}
                    style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}
                  >
                    <div>
                      <strong style={{ fontSize: '0.9rem' }}>{course.title}</strong>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{count} học viên đăng ký</div>
                    </div>
                    <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                      Top {i + 1}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Bảng học viên */}
          <div className="card">
            <div className="card-body" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>👨‍🎓 Học viên ({rows.length})</h3>
              <input
                type="text"
                className="form-control"
                placeholder="Tìm theo tên hoặc email..."
                style={{ maxWidth: 300 }}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Avatar</th>
                      <th>Họ và tên</th>
                      <th>Email</th>
                      <th>Khóa học đăng ký</th>
                      <th>Tiến độ học tập</th>
                      <th>Điểm Quiz trung bình</th>
                      <th>Ngày đăng ký</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.length === 0 && (
                      <tr>
                        <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                          Không tìm thấy học viên nào.
                        </td>
                      </tr>
                    )}
                    {rows.map((e) => {
                      const progress = progressOf(e);
                      const hasScore = e.avg_quiz_score !== null && e.avg_quiz_score !== undefined;
                      const score = Number(e.avg_quiz_score);
                      const scoreBadge = hasScore ? (score >= 80 ? 'success' : score >= 50 ? 'warning' : 'danger') : 'secondary';
                      return (
                        <tr key={`${e.user_id}-${e.course_id}`}>
                          <td>
                            <div className="avatar" style={{ background: 'var(--primary)', fontSize: '0.8rem' }}>
                              {initialsOf(e.user_name)}
                            </div>
                          </td>
                          <td>
                            <strong>{e.user_name}</strong>
                          </td>
                          <td>{e.user_email}</td>
                          <td>
                            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{e.course_title}</span>
                          </td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <div className="course-progress-bar" style={{ margin: 0, width: 100 }}>
                                <div className="course-progress-fill" style={{ width: `${progress}%` }}></div>
                              </div>
                              <div style={{ fontSize: '0.72rem', lineHeight: 1.3 }}>
                                <strong>{progress}%</strong>
                                <br />
                                <span style={{ color: 'var(--text-muted)' }}>
                                  {Number(e.completed_lessons || 0)}/{Number(e.total_lessons || 0)} bài
                                </span>
                              </div>
                            </div>
                          </td>
                          <td>
                            <span className={`badge badge-${scoreBadge}`}>{hasScore ? `${score.toFixed(0)}%` : 'Chưa thi'}</span>
                          </td>
                          <td>
                            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>📅 {formatDate(e.enroll_date)}</span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
