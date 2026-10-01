import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { quizService } from '../../services/quizService';
import RichText from '../../components/common/RichText.jsx';

const OPTION_KEYS = ['A', 'B', 'C', 'D'];

/** Kết quả 1 lượt làm quiz.
 * Vừa nộp bài: dữ liệu truyền qua navigate(..., { state }) từ QuizShow.jsx.
 * Tải lại trang / mở từ Lịch sử làm bài: tải lại từ server theo ?result_id=.
 */
export default function QuizResult() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const resultId = searchParams.get('result_id');
  // Vừa nộp bài (có state) -> hiện ngay; ngược lại tải theo result_id
  const fromSubmit = Boolean(state);
  const [data, setData] = useState(state || null);
  const [error, setError] = useState(null);

  // Không có state thì tải bài làm từ server; không có cả result_id -> quay về danh sách quiz
  useEffect(() => {
    if (state) {
      setData(state);
      return;
    }
    if (!resultId) {
      navigate('/quiz', { replace: true });
      return;
    }
    let cancelled = false;
    (async () => {
      const res = await quizService.getResult(resultId);
      if (cancelled) return;
      if (res?.ok && res.data?.success) setData(res.data);
      else setError(res?.data?.message || 'Không tải được bài làm.');
    })();
    return () => {
      cancelled = true;
    };
  }, [state, resultId, navigate]);

  useEffect(() => {
    if (data?.quiz?.title) document.title = `Kết quả: ${data.quiz.title}`;
  }, [data]);

  if (error) {
    return (
      <main className="s-main q-container qh-page">
        <div className="alert alert-danger">{error}</div>
        <Link to="/quiz">← Danh sách Quiz</Link>
      </main>
    );
  }
  if (!data) {
    return (
      <main className="s-main q-container qh-page" style={{ textAlign: 'center', padding: '5rem 0' }}>
        <div className="spinner mb-4"></div>
      </main>
    );
  }

  const { quiz, score, total, percent, passed, details, answers_revealed: revealed, attempts_left: attemptsLeft } = data;
  // Màu điểm: >= 80% xanh lá, >= 50% vàng, dưới 50% đỏ
  const color = percent >= 80 ? 'var(--s-success)' : percent >= 50 ? 'var(--s-warning)' : 'var(--s-danger)';

  return (
    <main className="s-main q-container qh-page">
      {/* Breadcrumbs */}
      <nav className="q-breadcrumb" aria-label="Breadcrumb">
        <Link to="/student/dashboard">Dashboard</Link>
        <span className="q-breadcrumb-separator">›</span>
        <Link to="/quiz">Danh sách Quiz</Link>
        <span className="q-breadcrumb-separator">›</span>
        <span className="q-breadcrumb-current">Kết quả bài làm</span>
      </nav>

      {/* Bố cục 2 cột: ô điểm bên trái (dính khi cuộn), danh sách câu hỏi bên phải */}
      <div className="qr-layout">
      <aside className="qr-side">
      {/* Score Overview Panel */}
      <div className="q-score-panel">
        <div
          id="scoreCircle"
          className="q-score-circle-wrap"
          style={{ background: `conic-gradient(${color} ${percent * 3.6}deg, var(--s-surface-2) 0deg)` }}
        >
          <div className="q-score-circle-inner">
            <div
              style={{
                fontSize: '1.05rem',
                color: 'var(--s-text-muted)',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                marginBottom: '0.25rem',
              }}
            >
              Kết quả
            </div>
            <span style={{ color, fontSize: '4rem', lineHeight: 1, fontWeight: 900 }}>
              {score}
              <span style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--s-text-muted)' }}>/{total}</span>
            </span>
            <span
              style={{
                fontSize: '0.95rem',
                color: 'var(--s-text-muted)',
                fontWeight: 600,
                marginTop: '0.6rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <span style={{ color: 'var(--s-success)' }}>✓ {score} Đúng</span>
              <span style={{ color: 'var(--s-border)' }}>|</span>
              <span style={{ color: 'var(--s-danger)' }}>✗ {total - score} Sai</span>
            </span>
            <div
              style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color,
                marginTop: '0.6rem',
                background: `${color}10`,
                padding: '0.25rem 0.75rem',
                borderRadius: '20px',
              }}
            >
              Đạt {percent}%
            </div>
          </div>
        </div>

        <div id="scoreSummary" className="q-score-summary">
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--s-text)', marginBottom: '0.25rem' }}>{quiz.title}</h2>
          <p style={{ color: 'var(--s-text-muted)', marginBottom: '0.5rem' }}>
            {quiz.course_title}
            {/* Xem lại từ lịch sử: kèm thời điểm nộp */}
            {!fromSubmit && data.submit_time ? ` · nộp lúc ${new Date(String(data.submit_time).replace(' ', 'T')).toLocaleString('vi-VN')}` : ''}
          </p>
          {/* Lượt đã lưu (học viên) -> xem các lượt khác của quiz này */}
          {(data.result_id || !fromSubmit) && (
            <Link
              to={`/quiz?history=${quiz.id}`}
              style={{ display: 'inline-block', fontSize: '0.85rem', marginBottom: '0.5rem' }}
            >
              📜 Lịch sử làm bài quiz này
            </Link>
          )}
          {/* Quiz có điểm đạt -> báo Đạt / Chưa đạt */}
          {passed !== null && passed !== undefined && (
            <span
              className={`s-badge ${passed ? 's-badge-green' : 's-badge-warn'}`}
              style={{ fontSize: '0.9rem', textTransform: 'none', letterSpacing: 'normal' }}
            >
              {passed ? `🎉 Đạt yêu cầu (≥ ${quiz.passing_score}%)` : `Chưa đạt — cần tối thiểu ${quiz.passing_score}%`}
            </span>
          )}
        </div>
      </div>
      </aside>

      <div className="qr-content">
      {/* Đề giới hạn lượt làm: chưa phải lượt cuối thì chỉ báo đúng/sai, đáp án đúng để dành tới lượt cuối */}
      {revealed === false && (
        <div className="alert alert-warning" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <span>
            🔒 Đáp án đúng sẽ được hiển thị sau lượt làm cuối cùng. Bạn còn <strong>{attemptsLeft}</strong> lượt.
          </span>
          <Link to={`/quiz-show?id=${quiz.id}`} className="s-btn s-btn-primary s-btn-sm">
            Làm lại
          </Link>
        </div>
      )}
      {fromSubmit && revealed && attemptsLeft === 0 && (
        <div className="alert alert-info">Đây là lượt làm cuối cùng — đáp án đúng đã được hiển thị bên dưới.</div>
      )}

      {/* Detail Card Header */}
      <div className="q-detail-header">
        <h3>Chi tiết câu trả lời</h3>
        <span>{revealed === false ? 'Câu nào đúng / sai (chưa hiện đáp án)' : 'Xem lại các lỗi sai của bạn'}</span>
      </div>

      {/* Detail Question List */}
      <div id="detailList">
        {details.map((d, i) => (
          <div key={i} className="question-card">
            <div className="question-num">
              <span>Câu {i + 1}</span>
              <span
                className={`s-badge ${d.is_right ? 's-badge-green' : 's-badge-warn'}`}
                style={{ textTransform: 'none', letterSpacing: 'normal' }}
              >
                {d.is_right ? '✓ Đúng' : '✗ Sai'}
              </span>
            </div>
            <div className="question-content" style={{ whiteSpace: 'pre-wrap' }}>
              <RichText text={d.content} />
            </div>
            <ul className="option-list">
              {/* Bỏ phương án C/D để trống; khi đáp án bị ẩn chỉ tô phương án đã chọn (xanh nếu đúng, đỏ nếu sai) */}
              {OPTION_KEYS.filter((k) => d[`option_${k.toLowerCase()}`]).map((k) => {
                let cls = '';
                let suffix = null;
                if (k === d.correct_answer || (d.is_right && k === d.chosen)) {
                  cls = 'option-correct';
                  if (k === d.chosen) {
                    suffix = (
                      <span
                        className="s-badge s-badge-green"
                        style={{ marginLeft: 'auto', fontSize: '0.7rem', textTransform: 'none', letterSpacing: 'normal', padding: '0.15rem 0.5rem' }}
                      >
                        Bạn chọn
                      </span>
                    );
                  }
                } else if (k === d.chosen && !d.is_right) {
                  cls = 'option-wrong';
                  suffix = (
                    <span
                      className="s-badge s-badge-warn"
                      style={{
                        marginLeft: 'auto',
                        fontSize: '0.7rem',
                        textTransform: 'none',
                        letterSpacing: 'normal',
                        padding: '0.15rem 0.5rem',
                        color: 'var(--s-danger)',
                        background: 'rgba(239, 68, 68, 0.1)',
                      }}
                    >
                      Bạn chọn
                    </span>
                  );
                }
                return (
                  <li key={k} className={`option-item ${cls}`}>
                    <span className="option-key">{k}</span>
                    <span className="option-text" style={{ whiteSpace: 'pre-wrap' }}>
                      <RichText text={d[`option_${k.toLowerCase()}`]} imgMaxHeight={160} />
                    </span>
                    {suffix}
                  </li>
                );
              })}
            </ul>
            {/* Giải thích của giảng viên / AI: server chỉ gửi khi đã hiện đáp án đúng */}
            {d.explanation && (
              <div
                style={{
                  marginTop: '0.75rem',
                  padding: '0.6rem 0.8rem',
                  borderRadius: 8,
                  fontSize: '0.875rem',
                  background: 'var(--s-surface-2)',
                  color: 'var(--s-text)',
                  whiteSpace: 'pre-wrap',
                }}
              >
                💡 <strong>Giải thích:</strong> <RichText text={d.explanation} />
              </div>
            )}
          </div>
        ))}
      </div>
      </div>
      </div>
    </main>
  );
}
