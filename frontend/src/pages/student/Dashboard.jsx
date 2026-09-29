import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import { progressService } from '../../services/progressService';

// Thứ tự hiển thị "Tiếp tục học": đang học dở trước, rồi chưa bắt đầu, cuối cùng là đã xong.
const STATUS_ORDER = { inprogress: 0, notstarted: 1, done: 2 };
import WeeklyBarChart from '../../components/common/WeeklyBarChart.jsx';
import RecommendationCard from '../../components/common/RecommendationCard.jsx';

// Biểu tượng và màu nền trang trí thẻ khóa học
const EMOJIS = ['🎨', '💻', '📊', '🔬', '🌐', '📱', '🎵', '✏️'];
const COLORS = [
  '#2563EB,#8B5CF6',
  '#0F766E,#06B6D4',
  '#7C3AED,#EC4899',
  '#DC2626,#F59E0B',
  '#059669,#2563EB',
  '#D97706,#EF4444',
];

/** Chuyển timestamp thành chuỗi thời gian tương đối: "2 giờ trước", "hôm qua"... */
function formatRelativeTime(dateStr) {
  if (!dateStr) return '';
  const now = new Date();
  const d = new Date(dateStr);
  const diffMs = now - d;
  const diffMin = Math.floor(diffMs / 60000);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  if (diffMin < 5) return 'Vừa xong';
  if (diffMin < 60) return `${diffMin} phút trước`;
  if (diffHour < 24) return `${diffHour} giờ trước`;
  if (diffDay === 1) return 'Hôm qua';
  if (diffDay < 7) return `${diffDay} ngày trước`;
  if (diffDay < 30) return `${Math.floor(diffDay / 7)} tuần trước`;
  return d.toLocaleDateString('vi-VN');
}

/** Tương đương _legacy/pages/student/dashboard.html — nối API tiến độ thực */
export default function Dashboard() {
  const { user } = useAuth();
  const [courses, setCourses] = useState(null); // khóa đã ghi danh; null = đang tải
  const [suggested, setSuggested] = useState(null); // khóa đã xuất bản nhưng chưa ghi danh
  // courseProgress: Map<courseId, { pct, status, totalLessons, doneLessons }>
  const [courseProgress, setCourseProgress] = useState({});
  const [stats, setStats] = useState({ total: 0, inProgress: 0, done: 0 });
  const [weeklyData, setWeeklyData] = useState(null);   // null = loading
  const [weeklyLabels, setWeeklyLabels] = useState([]);
  const [recentActivities, setRecentActivities] = useState(null); // null = loading

  // Khi mở trang: tải song song khóa học, tiến độ, biểu đồ tuần, hoạt động gần đây, id khóa đã ghi danh
  useEffect(() => {
    let cancelled = false;
    (async () => {
      // 3 lần gọi song song
      const [coursesRes, progressRes, weeklyRes, activitiesRes, enrolledRes] = await Promise.all([
        courseService.getCourses(),
        progressService.getProgress(),         // tổng hợp khóa học
        progressService.getWeeklyProgress(),   // GET /api/progress?weekly=1
        progressService.getRecentActivities(), // GET /api/progress?recent=1
        enrollmentService.getEnrolledIds(),
      ]);

      if (cancelled) return;

      // --- Danh sách khóa: tách khóa đã ghi danh và khóa để đề xuất ---
      const enrolledIds = new Set(enrolledRes?.data?.data || []);
      const catalog = coursesRes?.data?.data || [];
      const list = catalog.filter((c) => enrolledIds.has(c.id));
      setSuggested(catalog.filter((c) => !enrolledIds.has(c.id) && c.status === 'published'));

      // --- Tiến độ theo khóa ---
      const progressMap = {};
      const byCourse = progressRes?.data?.data?.courses || [];
      byCourse.forEach((c) => {
        const total = Number(c.total_lessons) || 0;
        const done  = Number(c.done_lessons)  || 0;
        const pct   = total > 0 ? Math.round((done / total) * 100) : 0;
        // Trạng thái: chưa học bài nào = chưa bắt đầu; xong 100% = hoàn thành; còn lại = đang học
        const status = done === 0 ? 'notstarted' : pct >= 100 ? 'done' : 'inprogress';
        progressMap[c.course_id] = { pct, status, totalLessons: total, doneLessons: done };
      });
      // Khóa đã ghi danh nhưng chưa có dữ liệu tiến độ -> mặc định 0%
      list.forEach((c) => {
        if (!progressMap[c.id]) {
          progressMap[c.id] = { pct: 0, status: 'notstarted', totalLessons: 0, doneLessons: 0 };
        }
      });
      // Sắp xếp theo STATUS_ORDER, cùng trạng thái thì khóa có % cao hơn lên trước
      list.sort(
        (a, b) =>
          STATUS_ORDER[progressMap[a.id].status] - STATUS_ORDER[progressMap[b.id].status] ||
          progressMap[b.id].pct - progressMap[a.id].pct,
      );
      setCourses(list);
      setCourseProgress(progressMap);
      // Đếm số khóa cho các thẻ thống kê (tổng / đang học / hoàn thành)
      const total = list.length;
      const done = list.filter((c) => progressMap[c.id].status === 'done').length;
      const inProgress = list.filter((c) => progressMap[c.id].status === 'inprogress').length;
      setStats({ total, inProgress, done });

      // --- Biểu đồ tuần ---
      const weeklyRows = weeklyRes?.data?.data || [];
      setWeeklyLabels(weeklyRows.map((r) => r.label || r.date?.slice(5) || ''));
      setWeeklyData(weeklyRows.map((r) => Number(r.count) || 0));

      // --- Hoạt động gần đây ---
      const activities = activitiesRes?.data?.data || [];
      setRecentActivities(activities.slice(0, 6));
    })();
    return () => { cancelled = true; };
  }, []);

  return (
    <main className="s-main">
      {/* Welcome Banner */}
      <div className="s-welcome">
        <div>
          <p style={{ fontSize: '.8rem', fontWeight: 700, textTransform: 'uppercase', opacity: 0.7, marginBottom: '.25rem' }}>
            🌟 Chào mừng trở lại
          </p>
          <h1 id="welcomeName">Xin chào, {user?.fullname}! 👋</h1>
          <p>Hãy tiếp tục hành trình học tập hôm nay nhé.</p>
          <Link to="/student/courses" className="s-btn s-btn-lg" style={{ background: '#fff', color: 'var(--s-primary)', marginTop: '.25rem' }}>
            Khám phá khóa học →
          </Link>
        </div>
      </div>

      {/* Stats Grid — dữ liệu thực từ API */}
      <div className="s-stats-grid">
        <div className="s-stat-card">
          <div className="s-stat-top">
            <div className="s-stat-icon" style={{ background: 'rgba(37,99,235,.1)' }}>📚</div>
          </div>
          <div className="s-stat-value" style={{ color: 'var(--s-primary)' }}>
            {courses === null ? '—' : stats.total}
          </div>
          <div className="s-stat-label">Tổng khóa học</div>
        </div>

        <div className="s-stat-card">
          <div className="s-stat-top">
            <div className="s-stat-icon" style={{ background: 'rgba(245,158,11,.1)' }}>⏳</div>
          </div>
          <div className="s-stat-value" style={{ color: 'var(--s-warning)' }}>
            {courses === null ? '—' : stats.inProgress}
          </div>
          <div className="s-stat-label">Đang theo học</div>
        </div>

        <div className="s-stat-card">
          <div className="s-stat-top">
            <div className="s-stat-icon" style={{ background: 'rgba(16,185,129,.1)' }}>✅</div>
          </div>
          <div className="s-stat-value" style={{ color: 'var(--s-success)' }}>
            {courses === null ? '—' : stats.done}
          </div>
          <div className="s-stat-label">Đã hoàn thành</div>
        </div>
      </div>

      {/* Personalized Recommendation — PHASE 5 */}
      <div style={{ marginBottom: '1.75rem' }}>
        <RecommendationCard compact />
      </div>

      {/* Charts + Recent Activity */}
      <div className="s-grid-2" style={{ marginBottom: '1.75rem' }}>
        {/* Weekly Chart — dữ liệu thực từ API */}
        <div className="s-card">
          <div className="s-card-header">
            <span className="s-card-title">📈 Tiến độ học trong tuần</span>
            <span className="s-badge s-badge-blue">7 ngày qua</span>
          </div>
          <div className="s-card-body">
            <div className="s-chart-wrap">
              {weeklyData === null ? (
                <div style={{ textAlign: 'center', paddingTop: '4rem', color: 'var(--s-text-muted)', fontSize: '.875rem' }}>Đang tải...</div>
              ) : (
                <WeeklyBarChart data={weeklyData} labels={weeklyLabels} />
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity — dữ liệu thực từ API */}
        <div className="s-card">
          <div className="s-card-header">
            <span className="s-card-title">🕐 Hoạt động gần đây</span>
            <Link to="/student/progress" className="s-btn s-btn-ghost s-btn-sm">Xem tất cả</Link>
          </div>
          <div className="s-card-body">
            <div className="s-activity-list" id="activityList">
              {recentActivities === null && (
                <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--s-text-muted)', fontSize: '.875rem' }}>Đang tải...</div>
              )}
              {recentActivities !== null && recentActivities.length === 0 && (
                <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--s-text-muted)', fontSize: '.875rem' }}>
                  Chưa có hoạt động nào. Hãy bắt đầu học!
                </div>
              )}
              {recentActivities !== null && recentActivities.map((act, i) => (
                <div key={i} className="s-activity-item">
                  <div className="s-activity-icon" style={{ background: 'rgba(37,99,235,.1)' }}>📘</div>
                  <div className="s-activity-body">
                    <p>
                      Hoàn thành bài: <strong>{act.lesson_title || 'Bài học'}</strong>
                    </p>
                    <p style={{ fontSize: '.75rem', color: 'var(--s-text-muted)', marginBottom: '.15rem', fontWeight: 400 }}>
                      {act.course_title || ''}
                    </p>
                    <span>{formatRelativeTime(act.completed_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Continue Courses */}
      <div className="s-card" style={{ marginBottom: '1.75rem' }}>
        <div className="s-card-header">
          <span className="s-card-title">▶️ Tiếp tục học</span>
          <Link to="/student/my-courses" className="s-btn s-btn-ghost s-btn-sm">
            Xem tất cả
          </Link>
        </div>
        <div className="s-card-body">
          <div id="continueList" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))', gap: '1rem' }}>
            {courses === null && <div style={{ color: 'var(--s-text-muted)', fontSize: '.9rem', padding: '1rem 0' }}>Đang tải khóa học...</div>}
            {courses !== null && courses.length === 0 && (
              <div className="s-empty">
                <div className="icon">📚</div>
                <h3>Bạn chưa đăng ký khóa học nào</h3>
                <p>Hãy đăng ký khóa học đầu tiên!</p>
                <Link to="/student/courses" className="s-btn s-btn-primary" style={{ marginTop: '1rem' }}>
                  Khám phá ngay
                </Link>
              </div>
            )}
            {courses !== null &&
              courses.slice(0, 3).map((c, i) => {
                const prog = courseProgress[c.id];
                const pct = prog?.pct ?? 0;
                const status = prog?.status ?? 'notstarted';
                return (
                  <div
                    key={c.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      padding: '1rem',
                      border: '1px solid var(--s-border)',
                      borderRadius: '10px',
                      background: 'var(--s-surface-2)',
                    }}
                  >
                    <div
                      style={{
                        width: 52,
                        height: 52,
                        borderRadius: 10,
                        background: `linear-gradient(135deg,${COLORS[i % COLORS.length]})`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.5rem',
                        flexShrink: 0,
                      }}
                    >
                      {EMOJIS[i % EMOJIS.length]}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div
                        style={{ fontWeight: 700, fontSize: '.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                      >
                        {c.title || 'Khóa học'}
                      </div>
                      <div style={{ fontSize: '.78rem', color: 'var(--s-text-muted)', marginBottom: '.5rem' }}>
                        {prog ? `${pct}% hoàn thành` : 'Đang tải...'}
                      </div>
                      <div className="s-progress">
                        <div
                          className={`s-progress-bar${status === 'done' ? ' green' : ''}`}
                          style={{ width: `${pct}%`, transition: 'width 0.6s ease' }}
                        />
                      </div>
                    </div>
                    <Link to={`/chapters?course_id=${c.id}`} className="s-btn s-btn-primary s-btn-sm" style={{ flexShrink: 0 }}>
                      {status === 'done' ? '🔄' : '▶'}
                    </Link>
                  </div>
                );
              })}
          </div>
        </div>
      </div>

      {/* Suggested Courses */}
      <div className="s-card">
        <div className="s-card-header">
          <span className="s-card-title">💡 Khóa học đề xuất</span>
          <Link to="/student/courses" className="s-btn s-btn-primary s-btn-sm">
            Xem tất cả
          </Link>
        </div>
        <div className="s-card-body">
          <div className="s-course-grid" id="suggestedList">
            {suggested === null && <div style={{ color: 'var(--s-text-muted)', fontSize: '.9rem' }}>Đang tải...</div>}
            {suggested !== null && suggested.length === 0 && (
              <p style={{ color: 'var(--s-text-muted)' }}>Bạn đã đăng ký tất cả khóa học hiện có. 🎉</p>
            )}
            {suggested !== null &&
              suggested.slice(0, 6).map((c, i) => (
                <div key={c.id} className="s-course-card">
                  <div className="s-course-thumb" style={{ background: `linear-gradient(135deg,${COLORS[i % COLORS.length]})` }}>
                    <span>{EMOJIS[i % EMOJIS.length]}</span>
                  </div>
                  <div className="s-course-body">
                    <h3>{c.title || 'Khóa học'}</h3>
                    <p className="teacher">👨‍🏫 {c.teacher_name || 'Giảng viên StudyOnline'}</p>
                    <div className="s-course-meta">
                      <span>{+c.price > 0 ? `💰 ${Number(c.price).toLocaleString('vi-VN')}đ` : '🆓 Miễn phí'}</span>
                    </div>
                  </div>
                  <div className="s-course-footer">
                    <Link to={`/chapters?course_id=${c.id}`} className="s-btn s-btn-ghost s-btn-sm">
                      Xem đề cương
                    </Link>
                    <Link to="/student/courses" className="s-btn s-btn-primary s-btn-sm">
                      Đăng ký
                    </Link>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </main>
  );
}
