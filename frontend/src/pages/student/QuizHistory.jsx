import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { quizService } from '../../services/quizService';
import { gradingShort } from '../../utils/quizGrading';

// Định dạng thời điểm nộp bài theo giờ Việt Nam
function formatTime(value) {
  if (!value) return '—';
  const d = new Date(String(value).replace(' ', 'T'));
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString('vi-VN');
}

/** Lịch sử làm bài của học viên: mọi lượt đã nộp (hoặc của 1 quiz qua ?quiz_id=), bấm để xem lại */
export default function QuizHistory() {
  const [searchParams] = useSearchParams();
  const quizId = searchParams.get('quiz_id');
  const [rows, setRows] = useState(null); // null = đang tải
  const [error, setError] = useState(null);

  // Tải lịch sử (lọc theo quiz nếu URL có quiz_id)
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

  const quizTitle = quizId && rows?.length ? rows[0].quiz_title : null;

  return (
    <main className="s-main q-container">
      <nav className="q-breadcrumb" aria-label="Breadcrumb">
        <Link to="/student/dashboard">Dashboard</Link>
        <span className="q-breadcrumb-separator">›</span>
        {quizId ? <Link to="/student/quiz-history">Lịch sử làm bài</Link> : <span className="q-breadcrumb-current">Lịch sử làm bài</span>}
        {quizId && (
          <>
            <span className="q-breadcrumb-separator">›</span>
            <span className="q-breadcrumb-current">{quizTitle || 'Quiz'}</span>
          </>
        )}
      </nav>

      <div className="q-header">
        <h1 className="q-title">📜 Lịch sử làm bài{quizTitle ? `: ${quizTitle}` : ''}</h1>
        <p className="q-subtitle">
          Xem lại từng lượt đã nộp. Lượt gắn nhãn “Được tính điểm” là lượt dùng để tính điểm của bạn theo cách tính của quiz.
        </p>
      </div>

      {rows === null && (
        <div style={{ textAlign: 'center', padding: '4rem 0' }}>
          <div className="spinner mb-4"></div>
          <p style={{ fontSize: '0.9rem', color: 'var(--s-text-muted)' }}>Đang tải lịch sử...</p>
        </div>
      )}

      {rows !== null && rows.length === 0 && (
        <div className="s-empty">
          <div className="icon">📜</div>
          <h3>{error || 'Bạn chưa nộp bài quiz nào'}</h3>
          {!error && (
            <p style={{ color: 'var(--s-text-muted)' }}>
              <Link to="/quiz">Đến danh sách quiz →</Link>
            </p>
          )}
        </div>
      )}

      {/* Mỗi lượt: quiz, lượt thứ mấy, điểm, đạt / chưa đạt, có được tính điểm không, thời gian nộp */}
      {rows?.map((r) => (
        <div key={r.id} className="s-card" style={{ marginBottom: '0.75rem' }}>
          <div
            className="s-card-body"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}
          >
            <div style={{ minWidth: 0 }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.3rem' }}>
                {r.quiz_title} <span style={{ fontWeight: 500, color: 'var(--s-text-muted)' }}>· Lượt {r.attempt_no}</span>
              </h3>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', alignItems: 'center' }}>
                <span className="s-badge s-badge-blue">
                  {r.score}/{r.total} · {r.percent}%
                </span>
                {r.passed === true && <span className="s-badge s-badge-green">✓ Đạt</span>}
                {r.passed === false && <span className="s-badge s-badge-warn">Chưa đạt</span>}
                {r.counted && (
                  <span className="s-badge s-badge-green" title={`Cách tính điểm: ${gradingShort(r.grading_method)}`}>
                    ★ Được tính điểm
                  </span>
                )}
                <span style={{ fontSize: '0.8rem', color: 'var(--s-text-muted)' }}>
                  {r.course_title} · {formatTime(r.submit_time)}
                </span>
              </div>
            </div>
            <Link className="s-btn s-btn-outline s-btn-sm" to={`/student/quiz-result?result_id=${r.id}`}>
              Xem lại
            </Link>
          </div>
        </div>
      ))}
    </main>
  );
}
