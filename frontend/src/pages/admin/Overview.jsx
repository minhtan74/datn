import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { userService } from '../../services/userService';
import { courseService } from '../../services/courseService';
import { reportService } from '../../services/reportService';
import CourseThumb from '../../components/common/CourseThumb.jsx';

// Nhãn + màu cho trạng thái khóa học
const COURSE_STATUS = {
  published: { label: 'Đã xuất bản', cls: 'badge-success' },
  draft: { label: 'Bản nháp', cls: 'badge-warning' },
  archived: { label: 'Lưu trữ', cls: 'badge-info' },
};

// Cách diễn đạt + màu cho từng trạng thái giao dịch trong "Hoạt động gần đây"
const PAYMENT_STATUS = {
  completed: { text: 'đã thanh toán', color: 'var(--success)' },
  pending: { text: 'đang chờ thanh toán', color: 'var(--warning)' },
  failed: { text: 'thanh toán thất bại', color: 'var(--danger)' },
  refunded: { text: 'đã được hoàn tiền', color: 'var(--info)' },
};

// Định dạng số kiểu Việt Nam (1.234.567)
function fmt(num) {
  return Number(num || 0).toLocaleString('vi-VN');
}

// Định dạng tiền VND
function fmtMoney(num) {
  return Number(num || 0).toLocaleString('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 });
}

// API trả "YYYY-MM-DD HH:MM:SS"; Safari không parse được dấu cách nên đổi sang "T".
function parseTime(str) {
  return str ? new Date(String(str).replace(' ', 'T')).getTime() || 0 : 0;
}

// Đổi thời điểm thành chuỗi tương đối: "Vừa xong", "5 phút trước", "3 ngày trước"...
function timeAgo(str) {
  const t = parseTime(str);
  if (!t) return '';
  const mins = Math.floor((Date.now() - t) / 60000);
  if (mins < 1) return 'Vừa xong';
  if (mins < 60) return `${mins} phút trước`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} giờ trước`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days} ngày trước`;
  return new Date(t).toLocaleDateString('vi-VN');
}

// Gộp lượt ghi danh + giao dịch gần đây thành 1 dòng thời gian, mới nhất trước, lấy 6 mục
function buildActivities(report) {
  const enrollments = (report?.recent_enrollments || []).map((e) => ({
    key: `e${e.id}`,
    time: e.enroll_date,
    color: 'var(--primary)',
    text: (
      <>
        <strong>{e.user_name}</strong> đăng ký khóa <strong>{e.course_title}</strong>
      </>
    ),
  }));
  const payments = (report?.recent_payments || []).map((p) => {
    const s = PAYMENT_STATUS[p.status] || { text: p.status, color: 'var(--text-muted)' };
    return {
      key: `p${p.id}`,
      time: p.created_at,
      color: s.color,
      text: (
        <>
          <strong>{p.user_name}</strong> {s.text} {fmtMoney(p.amount)} cho <strong>{p.course_title}</strong>
        </>
      ),
    };
  });
  return [...enrollments, ...payments]
    .filter((a) => parseTime(a.time))
    .sort((a, b) => parseTime(b.time) - parseTime(a.time))
    .slice(0, 6);
}

/** Tương đương renderUsersTable/#adminUsersTable row avatar: từ cuối cùng, 2 ký tự đầu. */
function rowInitials(fullname) {
  return fullname ? fullname.split(' ').pop().slice(0, 2).toUpperCase() : 'U';
}

// Màu nhãn vai trò
function roleBadgeClass(role) {
  return role === 'admin' ? 'badge-danger' : role === 'teacher' ? 'badge-success' : 'badge-primary';
}

/** Tương đương #dashboardView trong _legacy/pages/admin/dashboard.html (view "dashboard"). */
export default function AdminOverview() {
  const [users, setUsers] = useState(null); // null = đang tải
  const [courses, setCourses] = useState(null);
  const [report, setReport] = useState(null);
  const [loadErrors, setLoadErrors] = useState([]);

  // Khi mở trang: gọi song song 3 API (khóa học, người dùng, báo cáo); API nào lỗi thì ghi nhận để hiện cảnh báo
  useEffect(() => {
    (async () => {
      const [coursesRes, usersRes, reportRes] = await Promise.all([
        courseService.getCourses(),
        userService.getUsers(),
        reportService.getSummary(),
      ]);
      const okOf = (res) => res?.ok && res.data?.success;
      const errors = [];
      if (!okOf(coursesRes)) errors.push('khóa học');
      if (!okOf(usersRes)) errors.push('người dùng');
      if (!okOf(reportRes)) errors.push('doanh thu & hoạt động');
      setLoadErrors(errors);
      setCourses(okOf(coursesRes) ? coursesRes.data.data || [] : []);
      setUsers(okOf(usersRes) ? usersRes.data.data || [] : []);
      setReport(okOf(reportRes) ? reportRes.data.data : {});
    })();
  }, []);

  // Tính các số liệu thống kê từ dữ liệu đã tải (số giảng viên, học viên, tài khoản bị khóa, khóa nháp/đã xuất bản...)
  const allUsers = users || [];
  const allCourses = courses || [];
  const teachers = allUsers.filter((u) => u.role === 'teacher');
  const students = allUsers.filter((u) => u.role === 'student');
  const lockedCount = allUsers.filter((u) => !u.is_active).length;
  const teachingCount = teachers.filter((t) => allCourses.some((c) => c.teacher_id === t.id)).length;
  const draftCount = allCourses.filter((c) => c.status === 'draft').length;
  const publishedCount = allCourses.filter((c) => c.status === 'published').length;
  const ov = report?.overview || {};
  const activities = buildActivities(report);
  const loading = users === null || courses === null || report === null;
  const show = (v) => (loading ? '—' : v);

  // Công thức % giữ nguyên fetchAndRefreshData() bản gốc: pA = phần còn lại (100 - pS - pT),
  // không tính riêng theo admins.length để làm tròn luôn khớp tổng 100%.
  const total = allUsers.length || 1;
  const pS = Math.round((students.length / total) * 100);
  const pT = Math.round((teachers.length / total) * 100);
  const pA = 100 - pS - pT;

  // Biểu đồ tròn phân bổ vai trò vẽ bằng CSS conic-gradient
  const conicBackground = `conic-gradient(var(--primary) 0% ${pS}%, var(--accent) ${pS}% ${pS + pT}%, var(--warning) ${pS + pT}% 100%)`;

  return (
    <>
      <div className="page-header">
        <div className="breadcrumb">
          <Link to="/admin">Admin</Link> / <span>Dashboard</span>
        </div>
        <h1 className="page-title">Dashboard Tổng quan</h1>
        <p className="page-subtitle">Thống kê hoạt động và quản lý hệ thống thời gian thực.</p>
      </div>

      {loadErrors.length > 0 && (
        <div className="alert alert-danger" style={{ marginBottom: '1.5rem' }}>
          Không tải được dữ liệu {loadErrors.join(', ')}. Các số liệu liên quan bên dưới có thể chưa chính xác —
          hãy tải lại trang hoặc kiểm tra máy chủ API.
        </div>
      )}

      {/* Hàng thẻ thống kê: tổng user, giảng viên, học viên, khóa học, doanh thu, lượt đăng ký */}
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
        <div className="stat-card">
          <div className="stat-icon-wrap" style={{ background: 'rgba(37,99,235,0.1)', color: 'var(--primary)' }}>
            👥
          </div>
          <div>
            <div className="stat-label">Tổng User</div>
            <div className="stat-value">{show(allUsers.length)}</div>
            <span className="stat-trend" style={{ color: lockedCount ? 'var(--danger)' : 'var(--text-muted)' }}>
              {show(lockedCount ? `${lockedCount} tài khoản đang khóa` : 'Không có tài khoản bị khóa')}
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrap" style={{ background: 'rgba(16,185,129,0.1)', color: 'var(--success)' }}>
            👨‍🏫
          </div>
          <div>
            <div className="stat-label">Giảng viên</div>
            <div className="stat-value">{show(teachers.length)}</div>
            <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>
              {show(`${teachingCount} người đang có khóa học`)}
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrap" style={{ background: 'rgba(6,182,212,0.1)', color: 'var(--info)' }}>
            🎒
          </div>
          <div>
            <div className="stat-label">Học viên</div>
            <div className="stat-value">{show(students.length)}</div>
            <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>
              {ov.new_students_30d == null ? '—' : `+${fmt(ov.new_students_30d)} trong 30 ngày`}
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrap" style={{ background: 'rgba(139,92,246,0.1)', color: 'var(--accent)' }}>
            📚
          </div>
          <div>
            <div className="stat-label">Khóa học</div>
            <div className="stat-value">{show(allCourses.length)}</div>
            <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>
              {show(`${publishedCount} xuất bản · ${draftCount} bản nháp`)}
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrap" style={{ background: 'rgba(16,185,129,0.12)', color: 'var(--success)' }}>
            💰
          </div>
          <div>
            <div className="stat-label">Doanh thu</div>
            <div className="stat-value" style={{ fontSize: '1.3rem' }}>
              {ov.total_revenue == null ? '—' : fmtMoney(ov.total_revenue)}
            </div>
            <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>
              {ov.total_orders == null
                ? '—'
                : `${fmt(ov.total_orders)} đơn thành công · ${fmt(ov.pending_orders)} đang chờ`}
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-wrap" style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--warning)' }}>
            📝
          </div>
          <div>
            <div className="stat-label">Lượt đăng ký học</div>
            <div className="stat-value">{ov.total_enrollments == null ? '—' : fmt(ov.total_enrollments)}</div>
            <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>
              {ov.avg_completion_pct == null ? '—' : `Hoàn thành TB ${ov.avg_completion_pct}%`}
            </span>
          </div>
        </div>
      </div>

      <div className="col-3-1">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          <div className="card">
            <div className="card-header">
              {/* Bảng khóa học mới nhất */}
              <h3 style={{ fontSize: '1.1rem' }}>📚 Khóa học mới nhất</h3>
              <Link to="/admin/courses" className="btn btn-ghost btn-sm">
                Xem tất cả
              </Link>
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Thumbnail</th>
                      <th>Tên khóa học</th>
                      <th>Giảng viên</th>
                      <th>Trạng thái</th>
                    </tr>
                  </thead>
                  <tbody>
                    {courses === null && (
                      <tr>
                        <td colSpan={4} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                          Đang tải dữ liệu...
                        </td>
                      </tr>
                    )}
                    {courses !== null && allCourses.length === 0 && (
                      <tr>
                        <td colSpan={4} style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-muted)' }}>
                          Không có khóa học nào.
                        </td>
                      </tr>
                    )}
                    {allCourses.slice(0, 5).map((c) => (
                      <tr key={c.id}>
                        <td>
                          <div
                            style={{
                              width: 40,
                              height: 28,
                              borderRadius: 'var(--radius-sm)',
                              overflow: 'hidden',
                              background: 'var(--primary-light)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <CourseThumb src={c.thumbnail} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          </div>
                        </td>
                        <td>
                          <strong>{c.title}</strong>
                        </td>
                        <td>{c.teacher_name || 'Chưa phân công'}</td>
                        <td>
                          {(() => {
                            const s = COURSE_STATUS[c.status] || { label: c.status || '—', cls: 'badge-primary' };
                            return (
                              <span className={`badge ${s.cls}`} style={{ whiteSpace: 'nowrap' }}>
                                {s.label}
                              </span>
                            );
                          })()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              {/* Bảng người dùng mới nhất */}
              <h3 style={{ fontSize: '1.1rem' }}>👥 Người dùng mới nhất</h3>
              <Link to="/admin/users" className="btn btn-ghost btn-sm">
                Xem tất cả
              </Link>
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Avatar</th>
                      <th>Họ tên</th>
                      <th>Email</th>
                      <th>Vai trò</th>
                      <th>Trạng thái</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users === null && (
                      <tr>
                        <td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                          Đang tải dữ liệu...
                        </td>
                      </tr>
                    )}
                    {users !== null && allUsers.length === 0 && (
                      <tr>
                        <td colSpan={5} style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-muted)' }}>
                          Không có thành viên nào.
                        </td>
                      </tr>
                    )}
                    {allUsers.slice(0, 5).map((u) => (
                      <tr key={u.id}>
                        <td>
                          <div className="avatar avatar-sm" style={{ background: 'var(--primary)', fontSize: '0.75rem' }}>
                            {rowInitials(u.fullname)}
                          </div>
                        </td>
                        <td>
                          <strong>{u.fullname}</strong>
                        </td>
                        <td>{u.email}</td>
                        <td>
                          <span className={`badge ${roleBadgeClass(u.role)}`}>{(u.role || '').toUpperCase()}</span>
                        </td>
                        <td>
                          <span
                            className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}
                            style={{ whiteSpace: 'nowrap' }}
                          >
                            {u.is_active ? 'Hoạt động' : 'Đã khóa'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          <div className="card" style={{ padding: '1.5rem' }}>
            {/* Biểu đồ tỷ lệ học viên / giảng viên / admin */}
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1.25rem' }}>📊 Phân bổ vai trò</h3>
            <div style={{ position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center', height: 180 }}>
              <div
                style={{
                  width: 140,
                  height: 140,
                  borderRadius: '50%',
                  background: conicBackground,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <div
                  style={{
                    width: 90,
                    height: 90,
                    borderRadius: '50%',
                    background: 'var(--surface)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <strong style={{ fontSize: '1.2rem', color: 'var(--text)' }}>{allUsers.length}</strong>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Thành viên
                  </span>
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ width: 10, height: 10, background: 'var(--primary)', borderRadius: '50%' }}></span>
                  Học viên (Students)
                </span>
                <strong>{users === null ? '—' : `${pS}%`}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ width: 10, height: 10, background: 'var(--accent)', borderRadius: '50%' }}></span>
                  Giảng viên (Teachers)
                </span>
                <strong>{users === null ? '—' : `${pT}%`}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ width: 10, height: 10, background: 'var(--warning)', borderRadius: '50%' }}></span>
                  Quản trị (Admins)
                </span>
                <strong>{users === null ? '—' : `${pA}%`}</strong>
              </div>
            </div>
          </div>

          <div className="card" style={{ padding: '1.5rem' }}>
            {/* Dòng thời gian hoạt động gần đây */}
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>🔔 Hoạt động gần đây</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.85rem' }}>
              {report === null && <p style={{ margin: 0, color: 'var(--text-muted)' }}>Đang tải...</p>}
              {report !== null && activities.length === 0 && (
                <p style={{ margin: 0, color: 'var(--text-muted)' }}>Chưa có hoạt động nào.</p>
              )}
              {activities.map((a) => (
                <div key={a.key} style={{ borderLeft: '2px solid var(--border)', paddingLeft: '1rem', position: 'relative' }}>
                  <span
                    style={{
                      position: 'absolute',
                      left: -6,
                      top: 4,
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      background: a.color,
                    }}
                  ></span>
                  <p style={{ margin: 0, color: 'var(--text)' }}>{a.text}</p>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-light)' }}>{timeAgo(a.time)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
