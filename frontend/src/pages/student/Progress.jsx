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

/** Tiến độ & phân tích học tập: cột trái tổng quan (dính khi cuộn), cột phải gợi ý học tập, chủ đề, biểu đồ tuần, từng khóa học */
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

  // Tổng hợp bài học: đã xong / tổng, % hoàn thành chung
  const totalLessons = progressData?.total_lessons ?? 0;
  const doneLessons = progressData?.done_lessons ?? 0;
  const overall = totalLessons > 0 ? Math.round((doneLessons / totalLessons) * 100) : 0;
  const courses = progressData?.courses || [];

  // Chỉ số quiz + mức năng lực (điểm mỗi quiz đã tính theo cách tính điểm của quiz ở backend)
  const ov = analytics?.overview;
  const level = ov?.level && LEVEL_LABEL[ov.level];
  const topics = analytics?.topics || [];
  // Chủ đề mạnh: Khá + Tốt (≥ 70%); cần cải thiện: Yếu + Trung bình (< 70%)
  const strongCount = topics.filter((t) => t.status === 'Good' || t.status === 'Excellent').length;
  const weakCount = topics.length - strongCount;

  return (
    <main className="s-main">
      <div className="s-page-title">📈 Tiến độ & phân tích học tập</div>
      <div className="s-page-subtitle">Theo dõi hành trình học tập và điểm mạnh / điểm yếu của bạn</div>

      <div className="pg-layout">
        {/* Cột trái: tổng quan */}
        <aside className="pg-side">
          <div className="s-card pg-overview">
            <div className="pg-donut">
              <ProgressDoughnut completed={doneLessons} total={totalLessons} />
              <div className="pg-donut-center">
                <strong>{loading ? '—' : `${overall}%`}</strong>
                <span>hoàn thành</span>
              </div>
            </div>
            <p className="pg-donut-caption">
              {loading ? 'Đang tải...' : `${doneLessons}/${totalLessons} bài học đã hoàn thành`}
            </p>

            {level && (
              <span className="pg-level" style={{ color: level.color, background: `${level.color}1f` }}>
                Năng lực: {level.text}
              </span>
            )}

            <dl className="pg-metrics">
              <div>
                <dt>Điểm quiz trung bình</dt>
                <dd>{ov?.avg_quiz_score != null ? `${ov.avg_quiz_score}%` : '—'}</dd>
              </div>
              <div>
                <dt>Lượt làm quiz</dt>
                <dd>{loading ? '—' : ov?.quiz_attempts ?? 0}</dd>
              </div>
              <div>
                <dt>Bài còn lại</dt>
                <dd>{loading ? '—' : Math.max(0, totalLessons - doneLessons)}</dd>
              </div>
            </dl>
            <p className="pg-note">Điểm quiz: mỗi bài kiểm tra lấy 1 điểm theo cách tính của quiz; không tính bộ ôn tập.</p>
          </div>
        </aside>

        {/* Cột phải: phân tích chi tiết */}
        <div className="pg-content">
          {/* Gợi ý học tập đầu cột phải để học viên thấy ngay việc nên làm tiếp */}
          <RecommendationCard />

          <div className="s-card">
            <div className="s-card-header">
              <span className="s-card-title">🧠 Điểm theo chủ đề</span>
              {topics.length > 0 && (
                <div className="pg-chips">
                  <span className="s-badge s-badge-green">Mạnh: {strongCount}</span>
                  <span className="s-badge s-badge-warn">Cần cải thiện: {weakCount}</span>
                </div>
              )}
            </div>
            <div className="s-card-body">
              {loading && <div className="pg-muted">Đang tải...</div>}
              {!loading && topics.length === 0 && (
                <div className="pg-muted">
                  Chưa có dữ liệu theo chủ đề. Hãy làm một vài bài quiz để hệ thống phân tích điểm mạnh / điểm yếu của bạn.
                </div>
              )}
              {!loading && topics.length > 0 && (
                <>
                  <div className="pg-topics">
                    {topics.map((t) => (
                      <TopicScoreBar key={t.topic} topic={t.topic} avgScore={t.avg_score} status={t.status} answered={t.answered} />
                    ))}
                  </div>
                  <p className="pg-note">
                    Sắp xếp từ yếu đến mạnh. Mạnh: ≥ 70% · Cần cải thiện: &lt; 70%. Chỉ tính lượt được tính điểm của mỗi quiz và lượt
                    gần nhất của bộ ôn tập.
                  </p>
                </>
              )}
            </div>
          </div>

          <div className="s-card">
            <div className="s-card-header">
              <span className="s-card-title">📊 Bài học hoàn thành theo tuần</span>
            </div>
            <div className="s-card-body">
              <div className="s-chart-wrap">
                <WeeklyBarChart data={weeklyData.map((d) => d.count)} labels={weeklyData.map((d) => d.label)} />
              </div>
            </div>
          </div>

          {/* Tiến độ từng khóa học */}
          <div className="s-card">
            <div className="s-card-header">
              <span className="s-card-title">📚 Tiến độ từng khóa học</span>
            </div>
            <div className="s-card-body">
              {loading && <div className="pg-muted">Đang tải...</div>}

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

              <div className="pg-courses">
                {!loading &&
                  courses.map((c) => {
                    const total = parseInt(c.total_lessons, 10) || 0;
                    const done = parseInt(c.done_lessons, 10) || 0;
                    const pct = total > 0 ? Math.round((done / total) * 100) : 0;
                    return (
                      <div key={c.course_id} className="pg-course">
                        <div className="pg-course-main">
                          <div className="pg-course-top">
                            <span className="pg-course-title">{c.course_title || 'Khóa học'}</span>
                            <span className={`pg-course-pct${pct === 100 ? ' done' : ''}`}>{pct}%</span>
                          </div>
                          <div className="s-progress">
                            <div className={`s-progress-bar${pct === 100 ? ' green' : ''}`} style={{ width: `${pct}%` }}></div>
                          </div>
                          <div className="pg-course-meta">
                            <span>
                              {done}/{total} bài
                            </span>
                            {pct === 100 && <span className="pg-course-done">🏆 Hoàn thành</span>}
                          </div>
                        </div>
                        <Link to={`/chapters?course_id=${c.course_id}`} className="s-btn s-btn-outline s-btn-sm">
                          Xem
                        </Link>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
