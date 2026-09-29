import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import { progressService } from '../../services/progressService';

// Biểu tượng và màu nền trang trí thẻ khóa học
const EMOJIS = ['🎨', '💻', '📊', '🔬', '🌐', '📱', '🎵', '✏️', '🧪', '📐'];
const COLORS = ['#2563EB,#8B5CF6', '#0F766E,#06B6D4', '#7C3AED,#EC4899', '#DC2626,#F59E0B', '#059669,#2563EB', '#D97706,#EF4444'];

// Các tab lọc theo trạng thái học
const FILTERS = [
  { key: 'all', label: 'Tất cả' },
  { key: 'inprogress', label: 'Đang học' },
  { key: 'done', label: 'Hoàn thành' },
  { key: 'notstarted', label: 'Chưa bắt đầu' },
];

/**
 * Lấy tiến độ thực từ GET /api/progress (không param) trả về:
 * { data: { courses: [{course_id, total_lessons, done_lessons}] } }
 */
export default function MyCourses() {
  const [allCourses, setAllCourses] = useState(null); // null = đang tải
  // courseProgress: Map<courseId, { pct, status, totalLessons, doneLessons }>
  const [courseProgress, setCourseProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [currentFilter, setCurrentFilter] = useState('all');
  const [searchVal, setSearchVal] = useState('');

  // Khi mở trang: tải khóa học, tiến độ và id khóa đã ghi danh; chỉ giữ các khóa đã ghi danh
  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      const [coursesRes, progressRes, enrolledRes] = await Promise.all([
        courseService.getCourses(),
        progressService.getProgress(), // GET /api/progress → { courses: [{course_id, total_lessons, done_lessons}] }
        enrollmentService.getEnrolledIds(),
      ]);

      if (cancelled) return;

      const enrolledIds = new Set(enrolledRes?.data?.data || []);
      const list = (coursesRes?.data?.data || []).filter((c) => enrolledIds.has(c.id));
      setAllCourses(list);

      // Xây dựng map tiến độ từ dữ liệu backend
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

      // Với các khóa học chưa bắt đầu học → mặc định 0%
      list.forEach((c) => {
        if (!progressMap[c.id]) {
          progressMap[c.id] = { pct: 0, status: 'notstarted', totalLessons: 0, doneLessons: 0 };
        }
      });

      setCourseProgress(progressMap);
      setLoading(false);
    })();
    return () => { cancelled = true; };
  }, []);

  // Lọc theo tab trạng thái + ô tìm kiếm tên khóa
  const filtered = (allCourses || []).filter((c) => {
    const prog = courseProgress[c.id] || { pct: 0, status: 'notstarted' };
    const matchFilter = currentFilter === 'all' || prog.status === currentFilter;
    const matchSearch = !searchVal || (c.title || '').toLowerCase().includes(searchVal.toLowerCase());
    return matchFilter && matchSearch;
  });

  return (
    <main className="s-main">
      <div className="s-page-title">📚 Khóa học của tôi</div>
      <div className="s-page-subtitle">Danh sách các khóa học bạn đang theo học</div>

      {/* Filter Bar */}
      <div className="s-filter-bar">
        <input
          className="s-input"
          type="text"
          placeholder="🔍 Tìm tên khóa học..."
          value={searchVal}
          onChange={(e) => setSearchVal(e.target.value)}
        />
        <div className="s-filter-tabs">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              className={`s-filter-tab${currentFilter === f.key ? ' active' : ''}`}
              onClick={() => setCurrentFilter(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Course Grid */}
      <div className="s-course-grid" id="courseGrid">
        {loading && (
          <div style={{ color: 'var(--s-text-muted)', padding: '2rem' }}>Đang tải khóa học...</div>
        )}

        {!loading && filtered.length === 0 && (
          <div className="s-empty" style={{ gridColumn: '1/-1' }}>
            <div className="icon">📭</div>
            <h3>Không có khóa học nào</h3>
            <p>Thử thay đổi bộ lọc hoặc tìm kiếm khác.</p>
          </div>
        )}

        {!loading &&
          filtered.map((c) => {
            const idx = (allCourses || []).indexOf(c);
            const prog = courseProgress[c.id] || { pct: 0, status: 'notstarted', totalLessons: 0, doneLessons: 0 };
            const { pct, status, totalLessons, doneLessons } = prog;

            const statusBadge =
              status === 'done' ? (
                <span className="s-badge s-badge-green">✅ Hoàn thành</span>
              ) : status === 'notstarted' ? (
                <span className="s-badge s-badge-gray">⏸ Chưa bắt đầu</span>
              ) : (
                <span className="s-badge s-badge-warn">▶ Đang học</span>
              );

            return (
              <div key={c.id} className="s-course-card">
                <div className="s-course-thumb" style={{ background: `linear-gradient(135deg,${COLORS[idx % COLORS.length]})` }}>
                  <span style={{ fontSize: '2.5rem' }}>{EMOJIS[idx % EMOJIS.length]}</span>
                </div>
                <div className="s-course-body">
                  <h3>{c.title || 'Khóa học'}</h3>
                  <p className="teacher">👨‍🏫 {c.teacher_name || 'Giảng viên StudyOnline'}</p>
                  <div className="s-course-meta">
                    <span>📖 {doneLessons}/{totalLessons} bài hoàn thành</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '.5rem' }}>
                    <span style={{ fontSize: '.78rem', color: 'var(--s-text-muted)' }}>{pct}% hoàn thành</span>
                    {statusBadge}
                  </div>
                  <div className="s-progress">
                    <div
                      className={`s-progress-bar${status === 'done' ? ' green' : ''}`}
                      style={{ width: `${pct}%`, transition: 'width 0.6s ease' }}
                    />
                  </div>
                </div>
                <div className="s-course-footer">
                  <span style={{ fontSize: '.8rem', color: 'var(--s-text-muted)' }}>📅 Cập nhật gần đây</span>
                  <Link to={`/chapters?course_id=${c.id}`} className="s-btn s-btn-primary s-btn-sm">
                    {status === 'notstarted' ? '🚀 Bắt đầu' : status === 'done' ? '🔄 Xem lại' : '▶ Tiếp tục'}
                  </Link>
                </div>
              </div>
            );
          })}
      </div>
    </main>
  );
}
