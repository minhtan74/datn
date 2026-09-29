import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { enrollmentService } from '../../services/enrollmentService';

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

export default function TeacherStudents() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [teacherCourses, setTeacherCourses] = useState([]);
  const [enrollments, setEnrollments] = useState([]);

  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('all');

  // Khi mở trang: tải danh sách học viên đã ghi danh các khóa của giảng viên (kèm tiến độ, điểm quiz)
  useEffect(() => {
    let cancelled = false;
    async function loadData() {
      setLoading(true);
      // Backend tự lọc theo role: teacher -> getByTeacher(), admin -> getAll()
      // Không cần gọi riêng courseService vì enrollRes đã có course_title
      const enrollRes = await enrollmentService.getEnrollments();
      if (cancelled) return;

      const allEnrollments = enrollRes?.ok ? enrollRes.data.data || [] : [];
      setEnrollments(allEnrollments);

      // Rút ra danh sách khóa học duy nhất từ enrollments (để làm dropdown filter)
      const courseMap = new Map();
      allEnrollments.forEach((e) => {
        if (e.course_id && e.course_title && !courseMap.has(e.course_id)) {
          courseMap.set(e.course_id, { id: e.course_id, title: e.course_title });
        }
      });
      setTeacherCourses([...courseMap.values()]);
      setLoading(false);
    }
    loadData();
    return () => {
      cancelled = true;
    };
  }, [user]);

  // Lọc theo khóa học đang chọn + ô tìm kiếm (tên hoặc email học viên)
  const filtered = useMemo(() => {
    let list = enrollments;
    if (courseFilter !== 'all') {
      list = list.filter((e) => e.course_id === Number(courseFilter));
    }
    const q = search.toLowerCase().trim();
    if (q) {
      list = list.filter((e) => (e.user_name || '').toLowerCase().includes(q) || (e.user_email || '').toLowerCase().includes(q));
    }
    return list;
  }, [enrollments, courseFilter, search]);

  // Thống kê tổng hợp
  const uniqueStudents = useMemo(() => new Set(filtered.map((e) => e.user_id)).size, [filtered]);
  // Tiến độ trung bình (%) của các lượt ghi danh đang hiển thị
  const avgProgress = useMemo(() => {
    if (!filtered.length) return 0;
    const sum = filtered.reduce((acc, e) => {
      const total = Number(e.total_lessons || 0);
      const done = Number(e.completed_lessons || 0);
      return acc + (total > 0 ? (done / total) * 100 : 0);
    }, 0);
    return Math.round(sum / filtered.length);
  }, [filtered]);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">👨‍🎓 Danh sách Học viên</h1>
        <p className="page-subtitle">Theo dõi tiến trình học và kết quả kiểm tra của học sinh.</p>
      </div>

      {/* Thống kê nhanh */}
      {!loading && (
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          <div className="stat-card" style={{ flex: 1, minWidth: 140 }}>
            <div className="stat-icon" style={{ background: 'rgba(99,102,241,.15)', color: 'var(--primary)' }}>👥</div>
            <div className="stat-info">
              <div className="stat-value">{uniqueStudents}</div>
              <div className="stat-label">Học viên duy nhất</div>
            </div>
          </div>
          <div className="stat-card" style={{ flex: 1, minWidth: 140 }}>
            <div className="stat-icon" style={{ background: 'rgba(16,185,129,.15)', color: 'var(--success)' }}>📚</div>
            <div className="stat-info">
              <div className="stat-value">{filtered.length}</div>
              <div className="stat-label">Lượt đăng ký</div>
            </div>
          </div>
          <div className="stat-card" style={{ flex: 1, minWidth: 140 }}>
            <div className="stat-icon" style={{ background: 'rgba(245,158,11,.15)', color: 'var(--warning)' }}>📈</div>
            <div className="stat-info">
              <div className="stat-value">{avgProgress}%</div>
              <div className="stat-label">Tiến độ TB</div>
            </div>
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-body">
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Tìm kiếm học viên..."
              style={{ maxWidth: 300 }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select className="form-control" style={{ maxWidth: 220 }} value={courseFilter} onChange={(e) => setCourseFilter(e.target.value)}>
              <option value="all">Tất cả khóa học</option>
              {teacherCourses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="card">
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
                {loading && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: '2rem' }}>
                      <span
                        className="spinner"
                        style={{ width: 20, height: 20, border: '2px solid rgba(255,255,255,.3)', borderTopColor: 'var(--primary)' }}
                      ></span>{' '}
                      Đang tải danh sách học viên...
                    </td>
                  </tr>
                )}
                {!loading && filtered.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                      Không tìm thấy học viên nào.
                    </td>
                  </tr>
                )}
                {!loading &&
                   filtered.map((e, idx) => {
                    const total = Number(e.total_lessons || 0);
                    const completed = Number(e.completed_lessons || 0);
                    const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
                    const hasScore = e.avg_quiz_score !== null && e.avg_quiz_score !== undefined;
                    const quizScore = hasScore ? `${Number(e.avg_quiz_score).toFixed(0)}%` : 'Chưa thi';
                    const scoreBadge = hasScore
                      ? Number(e.avg_quiz_score) >= 80 ? 'success' : Number(e.avg_quiz_score) >= 50 ? 'warning' : 'danger'
                      : 'secondary';
                    return (
                      <tr key={`${e.user_id}-${e.course_id}` ?? idx}>
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
                              <span style={{ color: 'var(--text-muted)' }}>{completed}/{total} bài</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`badge badge-${scoreBadge}`}>{quizScore}</span>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                            📅 {formatDate(e.enroll_date)}
                          </span>
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
  );
}
