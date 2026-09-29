import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { progressService } from '../../services/progressService';
import { analyticsService } from '../../services/analyticsService';
import WeeklyBarChart from '../../components/common/WeeklyBarChart.jsx';
import ProgressDoughnut from '../../components/common/ProgressDoughnut.jsx';
import TopicScoreBar from '../../components/common/TopicScoreBar.jsx';
import RecommendationCard from '../../components/common/RecommendationCard.jsx';

// Tên + màu của các mức năng lực
const LEVEL_LABEL = {
  Weak: { text: 'Yếu', color: '#DC2626' },
  Average: { text: 'Trung bình', color: '#D97706' },
  Good: { text: 'Khá', color: '#2563EB' },
  Excellent: { text: 'Tốt', color: '#059669' },
};

/** Tương đương _legacy/pages/student/progress.html — toàn bộ số liệu lấy từ API thật */
export default function Progress() {
  const [loading, setLoading] = useState(true);
  const [progressData, setProgressData] = useState(null);
  const [weeklyData, setWeeklyData] = useState([]);
  const [analytics, setAnalytics] = useState(null); // { overview, topics }

  // Khi mở trang: tải song song tiến độ, biểu đồ tuần, chỉ số tổng quan và điểm theo chủ đề
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [progressRes, weeklyRes, ovRes, topicRes] = await Promise.all([
        progressService.getProgress(),
        progressService.getWeeklyProgress(),
        analyticsService.getOverview(),
        analyticsService.getTopics(),
      ]);
      if (cancelled) return;
      setProgressData(progressRes?.data?.data || null);
      setWeeklyData(weeklyRes?.data?.data || []);
      setAnalytics({
        overview: ovRes?.data?.data || null,
        topics: topicRes?.data?.data || [],
      });
      setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Tổng hợp: số bài đã xong / còn lại, tổng thời gian xem video (đổi sang giờ/phút), % hoàn thành chung
  const totalLessons = progressData?.total_lessons ?? 0;
  const doneLessons = progressData?.done_lessons ?? 0;
  const remLessons = totalLessons - doneLessons;
  const totalSec = progressData?.total_watched_sec ?? 0;

  const hrs = Math.floor(totalSec / 3600);
  const min = Math.floor((totalSec % 3600) / 60);
  const hoursLabel = hrs > 0 ? `${hrs}h${min > 0 ? min + 'm' : ''}` : min > 0 ? `${min}m` : '0m';

  const overall = totalLessons > 0 ? Math.round((doneLessons / totalLessons) * 100) : 0;

  // Dữ liệu cho biểu đồ cột số bài hoàn thành theo ngày
  const weekLabels = weeklyData.map((d) => d.label);
  const weekCounts = weeklyData.map((d) => d.count);

  const courses = progressData?.courses || [];

  return (
    <main className="s-main">
      <div className="s-page-title">📈 Tiến độ học tập</div>
      <div className="s-page-subtitle">Theo dõi hành trình học tập của bạn</div>

      {/* Stats overview */}
      <div className="s-stats-grid" style={{ marginBottom: '1.75rem' }}>
        <div className="s-stat-card">
          <div className="s-stat-top">
            <div className="s-stat-icon" style={{ background: 'rgba(37,99,235,.1)' }}>
              📘
            </div>
          </div>
          <div className="s-stat-value" style={{ color: 'var(--s-primary)' }} id="pTotalLessons">
            {loading ? '—' : totalLessons || '0'}
          </div>
          <div className="s-stat-label">Tổng bài học</div>
        </div>
        <div className="s-stat-card">
          <div className="s-stat-top">
            <div className="s-stat-icon" style={{ background: 'rgba(16,185,129,.1)' }}>
              ✅
            </div>
          </div>
          <div className="s-stat-value" style={{ color: 'var(--s-success)' }} id="pDoneLessons">
            {loading ? '—' : doneLessons || '0'}
          </div>
          <div className="s-stat-label">Đã hoàn thành</div>
        </div>
        <div className="s-stat-card">
          <div className="s-stat-top">
            <div className="s-stat-icon" style={{ background: 'rgba(245,158,11,.1)' }}>
              ⏳
            </div>
          </div>
          <div className="s-stat-value" style={{ color: 'var(--s-warning)' }} id="pRemLessons">
            {loading ? '—' : remLessons || '0'}
          </div>
          <div className="s-stat-label">Còn lại</div>
        </div>
        <div className="s-stat-card">
          <div className="s-stat-top">
            <div className="s-stat-icon" style={{ background: 'rgba(139,92,246,.1)' }}>
              ⏱
            </div>
          </div>
          <div className="s-stat-value" style={{ color: '#8B5CF6' }} id="pHours">
            {loading ? '—' : hoursLabel}
          </div>
          <div className="s-stat-label">Tổng thời gian học</div>
        </div>
      </div>

      {/* Charts row */}
      <div className="s-grid-2" style={{ marginBottom: '1.75rem' }}>
        <div className="s-card">
          <div className="s-card-header">
            <span className="s-card-title">📊 Bài học hoàn thành theo tuần</span>
          </div>
          <div className="s-card-body">
            <div className="s-chart-wrap">
              <WeeklyBarChart data={weekCounts} labels={weekLabels} />
            </div>
          </div>
        </div>

        <div className="s-card">
          <div className="s-card-header">
            <span className="s-card-title">🍩 Tỷ lệ hoàn thành tổng thể</span>
          </div>
          <div className="s-card-body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
            <div className="s-chart-wrap" style={{ width: 180, height: 180 }}>
              <ProgressDoughnut completed={doneLessons} total={totalLessons} />
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--s-primary)' }} id="overallPct">
                {overall}%
              </div>
              <div style={{ fontSize: '.85rem', color: 'var(--s-text-muted)' }}>Tổng tiến độ</div>
            </div>
          </div>
        </div>
      </div>

      {/* Learning Analytics — PHASE 4 */}
      <div className="s-card" style={{ marginBottom: '1.75rem' }}>
        <div className="s-card-header">
          <span className="s-card-title">🧠 Phân tích học tập</span>
          {analytics?.overview?.level && LEVEL_LABEL[analytics.overview.level] && (
            <span
              className="s-badge"
              style={{
                color: LEVEL_LABEL[analytics.overview.level].color,
                background: `${LEVEL_LABEL[analytics.overview.level].color}1f`,
                fontWeight: 700,
              }}
            >
              Năng lực: {LEVEL_LABEL[analytics.overview.level].text}
            </span>
          )}
        </div>
        <div className="s-card-body">
          {loading && <div style={{ color: 'var(--s-text-muted)' }}>Đang tải...</div>}

          {!loading && analytics && (
            <>
              <div className="s-stats-grid" style={{ marginBottom: '1.5rem' }}>
                <div className="s-stat-card">
                  <div className="s-stat-value" style={{ color: 'var(--s-primary)' }}>
                    {analytics.overview?.avg_quiz_score != null ? `${analytics.overview.avg_quiz_score}%` : '—'}
                  </div>
                  <div className="s-stat-label">Điểm quiz trung bình</div>
                </div>
                <div className="s-stat-card">
                  <div className="s-stat-value" style={{ color: '#8B5CF6' }}>
                    {analytics.overview?.quiz_attempts ?? 0}
                  </div>
                  <div className="s-stat-label">Số lần làm quiz</div>
                </div>
                <div className="s-stat-card">
                  <div className="s-stat-value" style={{ color: 'var(--s-success)' }}>
                    {analytics.topics.filter((t) => t.status === 'Excellent').length}
                  </div>
                  <div className="s-stat-label">Chủ đề mạnh</div>
                </div>
                <div className="s-stat-card">
                  <div className="s-stat-value" style={{ color: 'var(--s-danger, #DC2626)' }}>
                    {analytics.topics.filter((t) => t.status === 'Weak' || t.status === 'Average').length}
                  </div>
                  <div className="s-stat-label">Chủ đề cần cải thiện</div>
                </div>
              </div>

              {analytics.topics.length === 0 ? (
                <div style={{ color: 'var(--s-text-muted)', fontSize: '.875rem' }}>
                  Chưa có dữ liệu theo chủ đề. Hãy làm một vài bài quiz để hệ thống phân tích điểm mạnh / điểm yếu của bạn.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '.9rem' }}>
                  <div style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--s-text-muted)', textTransform: 'uppercase' }}>
                    Điểm theo chủ đề (thấp → cao)
                  </div>
                  {analytics.topics.map((t) => (
                    <TopicScoreBar
                      key={t.topic}
                      topic={t.topic}
                      avgScore={t.avg_score}
                      status={t.status}
                      answered={t.answered}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Personalized Recommendation — PHASE 5 */}
      <div style={{ marginBottom: '1.75rem' }}>
        <RecommendationCard />
      </div>

      {/* Per-course progress */}
      <div className="s-card">
        <div className="s-card-header">
          <span className="s-card-title">📚 Tiến độ từng khóa học</span>
        </div>
        <div className="s-card-body">
          <div id="courseProgressList" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {loading && <div style={{ color: 'var(--s-text-muted)' }}>Đang tải...</div>}

            {!loading && courses.length === 0 && (
              <div className="s-empty">
                <div className="icon">📭</div>
                <h3>Bạn chưa đăng ký khóa học nào</h3>
                <p>Hãy khám phá và đăng ký khóa học để bắt đầu học!</p>
                <Link to="/student/courses" className="s-btn s-btn-primary s-btn-sm">
                  Khám phá khóa học
                </Link>
              </div>
            )}

            {!loading &&
              courses.map((c) => {
                const total = parseInt(c.total_lessons, 10) || 0;
                const done = parseInt(c.done_lessons, 10) || 0;
                const pct = total > 0 ? Math.round((done / total) * 100) : 0;
                const cHrs = Math.floor((c.watched_sec_total || 0) / 3600);
                const cMin = Math.floor(((c.watched_sec_total || 0) % 3600) / 60);
                const timeStr = cHrs > 0 ? `${cHrs}h ${cMin}m` : cMin > 0 ? `${cMin}m` : '0m';

                return (
                  <div
                    key={c.course_id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      padding: '1rem',
                      border: '1px solid var(--s-border)',
                      borderRadius: '10px',
                    }}
                  >
                    <div
                      style={{
                        width: 46,
                        height: 46,
                        borderRadius: 10,
                        background: 'linear-gradient(135deg,var(--s-primary),#8B5CF6)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.3rem',
                        flexShrink: 0,
                      }}
                    >
                      📘
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '.4rem' }}>
                        <span
                          style={{
                            fontWeight: 700,
                            fontSize: '.9rem',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            maxWidth: '60%',
                          }}
                        >
                          {c.course_title || 'Khóa học'}
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '.75rem', flexShrink: 0 }}>
                          <span style={{ fontSize: '.78rem', color: 'var(--s-text-muted)' }}>
                            {done}/{total} bài
                          </span>
                          <span style={{ fontWeight: 700, color: pct === 100 ? 'var(--s-success)' : 'var(--s-primary)' }}>{pct}%</span>
                        </div>
                      </div>
                      <div className="s-progress">
                        <div className={`s-progress-bar${pct === 100 ? ' green' : ''}`} style={{ width: `${pct}%` }}></div>
                      </div>
                      <div style={{ display: 'flex', gap: '1rem', marginTop: '.4rem', fontSize: '.75rem', color: 'var(--s-text-muted)' }}>
                        <span>✅ {done} hoàn thành</span>
                        <span>⏳ {total - done} còn lại</span>
                        <span>⏱ {timeStr} đã học</span>
                        {pct === 100 && <span style={{ color: 'var(--s-success)', fontWeight: 700 }}>🏆 Hoàn thành!</span>}
                      </div>
                    </div>
                    <Link to={`/chapters?course_id=${c.course_id}`} className="s-btn s-btn-outline s-btn-sm" style={{ flexShrink: 0 }}>
                      Xem
                    </Link>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    </main>
  );
}
