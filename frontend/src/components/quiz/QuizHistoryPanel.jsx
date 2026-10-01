import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { quizService } from '../../services/quizService';
import { gradingShort } from '../../utils/quizGrading';

// Định dạng thời điểm nộp bài theo giờ Việt Nam
function formatTime(value) {
  if (!value) return '—';
  const d = new Date(String(value).replace(' ', 'T'));
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString('vi-VN');
}

// Màu thanh điểm: đạt → xanh, chưa đạt → cam, quiz không đặt điểm đạt → xanh dương
function barTone(r) {
  if (r.passed === true) return 'ok';
  if (r.passed === false) return 'warn';
  return 'info';
}

const FILTERS = [
  { key: 'all', label: 'Tất cả' },
  { key: 'passed', label: 'Đạt' },
  { key: 'failed', label: 'Chưa đạt' },
  { key: 'counted', label: 'Được tính điểm' },
];

/** Lịch sử làm bài của 1 quiz, hiện ngay dưới thẻ quiz ở trang Quiz: thống kê, bộ lọc, từng lượt (mới nhất trước), bấm để xem lại */
export default function QuizHistoryPanel({ quizId }) {
  const [rows, setRows] = useState(null); // null = đang tải
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  // Tải các lượt đã nộp của quiz này
  useEffect(() => {
    let cancelled = false;
    setRows(null);
    (async () => {
      const res = await quizService.getResults(quizId);
      if (cancelled) return;
      setError(res?.ok ? null : res?.data?.message || 'Không tải được lịch sử làm bài.');
      setRows(res?.ok ? res.data.data || [] : []);
    })();
    return () => {
      cancelled = true;
    };
  }, [quizId]);

  // Số liệu tổng quan: số lượt, điểm được tính (backend tính theo cách tính của quiz), điểm cao nhất, số lượt đạt
  const stats = useMemo(() => {
    if (!rows?.length) return null;
    const first = rows[0];
    const hasPassingScore = rows.some((r) => r.passed !== null && r.passed !== undefined);
    return {
      attempts: rows.length,
      graded: first.graded_percent,
      gradedPassed: first.graded_passed,
      method: first.grading_method,
      best: Math.max(...rows.map((r) => r.percent || 0)),
      passedCount: rows.filter((r) => r.passed === true).length,
      hasPassingScore,
    };
  }, [rows]);

  const visible = useMemo(
    () =>
      (rows || []).filter((r) => {
        if (filter === 'passed') return r.passed === true;
        if (filter === 'failed') return r.passed === false;
        if (filter === 'counted') return r.counted;
        return true;
      }),
    [rows, filter]
  );

  if (rows === null) {
    return (
      <div className="qh-panel" style={{ textAlign: 'center' }}>
        <div className="spinner mb-4"></div>
      </div>
    );
  }

  if (!rows.length) {
    return <div className="qh-panel qh-none">{error || 'Bạn chưa nộp lượt nào của quiz này.'}</div>;
  }

  return (
    <div className="qh-panel">
      <div className="qh-stats">
        <div className="qh-stat">
          <span className="qh-stat-value">{stats.attempts}</span>
          <span className="qh-stat-label">Lượt làm bài</span>
        </div>
        <div className="qh-stat">
          <span className="qh-stat-value">{stats.graded}%</span>
          <span className="qh-stat-label">
            Điểm được tính ({gradingShort(stats.method)})
            {stats.gradedPassed === true && ' · Đạt'}
            {stats.gradedPassed === false && ' · Chưa đạt'}
          </span>
        </div>
        <div className="qh-stat">
          <span className="qh-stat-value">{stats.best}%</span>
          <span className="qh-stat-label">Điểm cao nhất</span>
        </div>
        <div className="qh-stat">
          <span className="qh-stat-value">{stats.hasPassingScore ? `${stats.passedCount}/${stats.attempts}` : '—'}</span>
          <span className="qh-stat-label">Lượt đạt</span>
        </div>
      </div>

      <div className="qh-filters" role="tablist" aria-label="Lọc lượt làm bài">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            type="button"
            role="tab"
            aria-selected={filter === f.key}
            className={`qh-chip${filter === f.key ? ' active' : ''}`}
            onClick={() => setFilter(f.key)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {visible.length === 0 && <p className="qh-none">Không có lượt nào khớp bộ lọc này.</p>}

      <ul className="qh-list qh-list-boxed">
        {visible.map((r) => (
          <li key={r.id} className="qh-row">
            <span className="qh-attempt">Lượt {r.attempt_no}</span>

            <div className="qh-score">
              <div className="qh-score-top">
                <strong>
                  {r.score}/{r.total}
                </strong>
                <span>{r.percent}%</span>
              </div>
              <div className="qh-bar" aria-hidden="true">
                <div className={`qh-bar-fill ${barTone(r)}`} style={{ width: `${Math.min(100, r.percent || 0)}%` }} />
              </div>
            </div>

            <div className="qh-tags">
              {r.passed === true && <span className="s-badge s-badge-green">✓ Đạt</span>}
              {r.passed === false && <span className="s-badge s-badge-warn">Chưa đạt</span>}
              {r.counted && (
                <span className="s-badge s-badge-blue" title={`Cách tính điểm: ${gradingShort(r.grading_method)}`}>
                  ★ Được tính điểm
                </span>
              )}
            </div>

            <time className="qh-time">{formatTime(r.submit_time)}</time>

            <Link className="s-btn s-btn-outline s-btn-sm" to={`/student/quiz-result?result_id=${r.id}`}>
              Xem lại
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
