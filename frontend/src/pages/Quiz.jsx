import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { quizService } from '../services/quizService';
import { formatClock, gradingShort } from '../utils/quizGrading';
import QuizHistoryPanel from '../components/quiz/QuizHistoryPanel.jsx';

const QUIZ_STATES = [
  { key: 'not_started', label: 'Chưa làm', icon: '○' },
  { key: 'in_progress', label: 'Đang làm dở', icon: '◷' },
  { key: 'submitted', label: 'Đã nộp', icon: '✓' },
  { key: 'unfinished', label: 'Chưa nộp', icon: '!' },
];

// Mỗi quiz thuộc một nhóm. Lượt đang làm lại được ưu tiên, điểm các lượt đã nộp vẫn giữ.
function stateOf(quiz) {
  const s = quiz.my_status;
  if (!s) return null;
  if (s.in_progress) return 'in_progress';
  if (s.submitted > 0) return 'submitted';
  if (s.attempts_used > 0) return 'unfinished';
  return 'not_started';
}

/** Tách trạng thái nộp bài khỏi điểm đạt; không ẩn kết quả cũ khi đang làm lại. */
function QuizStatus({ quiz }) {
  const s = quiz.my_status;
  if (!s) return null;
  const state = stateOf(quiz);
  const label = QUIZ_STATES.find((item) => item.key === state).label;
  return (
    <>
      <span className="s-badge ql-state-label">
        {label}{s.in_progress && s.remaining_sec != null ? ` · còn ${formatClock(s.remaining_sec)}` : ''}
      </span>
      {s.submitted > 0 && (
        <>
          <span className="s-badge s-badge-blue" title={`Điểm các lượt đã nộp, tính theo ${gradingShort(quiz.grading_method)}`}>
            Điểm: {s.graded_percent}% ({gradingShort(quiz.grading_method)})
          </span>
          {s.passed === true && <span className="s-badge s-badge-green">✓ Đạt</span>}
          {s.passed === false && <span className="s-badge s-badge-warn">Chưa đạt</span>}
          <span className="ql-status-note">Đã nộp {s.submitted} lượt</span>
        </>
      )}
      {state === 'unfinished' && <span className="ql-status-note">Lượt trước đã kết thúc, chưa có bài nộp.</span>}
      {s.attempts_left != null && (
        <span className="ql-status-note">{s.attempts_left === 0 ? 'Đã dùng hết lượt mới' : `Còn ${s.attempts_left} lượt mới`}</span>
      )}
    </>
  );
}

// Nút chính theo tình trạng: tiếp tục lượt dở / làm lại / làm bài; hết lượt thì khóa
function actionOf(quiz, isManager) {
  if (isManager) return { label: 'Làm thử', disabled: false };
  const s = quiz.my_status;
  if (!s) return { label: 'Làm bài', disabled: false };
  if (s.in_progress) return { label: 'Tiếp tục làm', disabled: false };
  if (s.attempts_left === 0) return { label: 'Hết lượt', disabled: true };
  return { label: s.submitted || s.attempts_used ? 'Làm lại' : 'Làm bài', disabled: false };
}

/** Tương đương initQuizList() trong _legacy/js/quiz.js + _legacy/pages/quiz.html */
export default function Quiz() {
  const [searchParams, setSearchParams] = useSearchParams();
  const courseId = searchParams.get('course_id');
  // Quiz đang mở lịch sử làm bài (mở sẵn nếu URL có ?history=<id>, vd từ trang kết quả)
  const [historyId, setHistoryId] = useState(Number(searchParams.get('history')) || null);
  const { user } = useAuth();
  // Admin / giảng viên thấy thêm nút quản lý (sửa, xóa quiz)
  const isManager = user?.role === 'admin' || user?.role === 'teacher';

  const [quizzes, setQuizzes] = useState(null); // null = đang tải
  const [loadError, setLoadError] = useState(null);
  const selectedStatus = searchParams.get('status');
  const statusFilter = QUIZ_STATES.some((s) => s.key === selectedStatus) ? selectedStatus : 'all';
  const counts = Object.fromEntries(QUIZ_STATES.map((s) => [s.key, 0]));
  for (const q of quizzes || []) {
    const state = stateOf(q);
    if (state) counts[state] += 1;
  }
  const visibleQuizzes = (quizzes || []).filter((q) => isManager || statusFilter === 'all' || stateOf(q) === statusFilter);

  function filterByStatus(status) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (status === 'all') next.delete('status');
      else next.set('status', status);
      return next;
    });
  }

  // Tải danh sách quiz (theo khóa nếu URL có course_id)
  async function loadQuizzes() {
    setQuizzes(null);
    const res = await quizService.getQuizzes(courseId);
    setLoadError(res?.ok ? null : res?.data?.message || 'Không tải được danh sách quiz.');
    setQuizzes(res?.data?.data || []);
  }

  useEffect(() => {
    loadQuizzes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId]);

  // Xóa quiz (có xác nhận); backend từ chối nếu quiz đã có người làm
  async function handleDelete(id) {
    if (!window.confirm('Xóa quiz này?')) return;
    const r = await quizService.deleteQuiz(id);
    if (r?.ok) loadQuizzes();
    else window.alert(r?.data?.message || 'Không thể xóa quiz.');
  }

  return (
    <main className="s-main q-container qh-page">
      <div className="q-header">
        <h1 className="q-title">📝 Danh sách Quiz</h1>
        <p className="q-subtitle">Chọn một bài tập trắc nghiệm dưới đây để kiểm tra và củng cố kiến thức học tập.</p>
      </div>

      {!isManager && quizzes !== null && !loadError && quizzes.length > 0 && (
        <section className="ql-overview" aria-labelledby="quiz-status-title">
          <div className="ql-overview-heading">
            <h2 id="quiz-status-title">Theo dõi bài làm</h2>
            <button type="button" className={`qh-chip${statusFilter === 'all' ? ' active' : ''}`}
              aria-pressed={statusFilter === 'all'} aria-controls="quizList" onClick={() => filterByStatus('all')}>
              Tất cả ({quizzes.length})
            </button>
          </div>
          <div className="ql-status-filters" role="group" aria-label="Lọc quiz theo trạng thái">
            {QUIZ_STATES.map((s) => (
              <button key={s.key} type="button" aria-pressed={statusFilter === s.key} aria-controls="quizList"
                className={`ql-status-filter ql-state-${s.key}${statusFilter === s.key ? ' active' : ''}`}
                onClick={() => filterByStatus(s.key)}>
                <span className="ql-filter-label"><span aria-hidden="true">{s.icon}</span> {s.label}</span>
                <strong className="ql-filter-count">{counts[s.key]}</strong>
                <span className="ql-filter-unit">quiz</span>
              </button>
            ))}
          </div>
          <p className="ql-filter-help">Chọn trạng thái để lọc bài. “Chưa nộp” là bài đã bắt đầu nhưng lượt làm đã kết thúc mà chưa nộp bài.</p>
          <p className="ql-result-count" role="status" aria-live="polite">
            Hiển thị {visibleQuizzes.length} / {quizzes.length} quiz{statusFilter !== 'all' ? ` · ${QUIZ_STATES.find((s) => s.key === statusFilter).label}` : ''}
          </p>
        </section>
      )}

      <div id="quizList" className="q-card-list">
        {quizzes === null && (
          <div style={{ textAlign: 'center', padding: '5rem 0' }}>
            <div className="spinner mb-4"></div>
            <p style={{ fontSize: '0.9rem', color: 'var(--s-text-muted)', fontWeight: 500 }}>
              Đang tải danh sách quiz...
            </p>
          </div>
        )}

        {quizzes !== null && quizzes.length === 0 && (
          <div className="s-empty">
            <div className="icon">📝</div>
            <h3>{loadError || 'Chưa có quiz nào'}</h3>
            {!loadError && !isManager && (
              <p style={{ color: 'var(--s-text-muted)' }}>
                Quiz của các khóa học bạn đã đăng ký sẽ hiện ở đây.{' '}
                <Link to="/student/courses">Khám phá khóa học →</Link>
              </p>
            )}
          </div>
        )}

        {!isManager && quizzes?.length > 0 && visibleQuizzes.length === 0 && (
          <div className="s-empty">
            <div className="icon" aria-hidden="true">📝</div>
            <h3>Không có quiz ở trạng thái này</h3>
            <p>Chọn trạng thái khác hoặc xem lại tất cả quiz.</p>
            <button type="button" className="s-btn s-btn-outline" onClick={() => filterByStatus('all')}>Xem tất cả quiz</button>
          </div>
        )}

        {quizzes !== null &&
          visibleQuizzes.map((q) => (
            <div key={q.id} className={`s-card ql-card${!isManager && stateOf(q) ? ` ql-state-${stateOf(q)}` : ''}`}>
              <div className="s-card-body ql-card-body">
                <div className="ql-card-content">
                  <h3 style={{ fontSize: '1.05rem', marginBottom: '.25rem', fontWeight: 700 }}>{q.title}</h3>
                  <span className="s-badge s-badge-blue">{q.question_count} câu hỏi</span>
                  {q.course_title && (
                    <span className="s-badge s-badge-green" style={{ marginLeft: '.5rem' }}>
                      {q.course_title}
                    </span>
                  )}
                  {(q.chapter_id || q.review_lesson_id) && (
                    <span className="s-badge s-badge-blue" style={{ marginLeft: '.5rem' }}>
                      {q.chapter_id ? 'Ôn tập chương' : 'Ôn tập bài'}
                    </span>
                  )}
                  {q.duration && (
                    <span className="s-badge s-badge-warn" style={{ marginLeft: '.5rem' }}>
                      ⏱ {q.duration} phút
                    </span>
                  )}
                  {q.max_attempts && (
                    <span className="s-badge s-badge-warn" style={{ marginLeft: '.5rem' }}>
                      🔁 Tối đa {q.max_attempts} lần
                    </span>
                  )}
                  <p style={{ marginTop: '.5rem', fontSize: '.875rem', color: 'var(--s-text-muted)' }}>
                    {q.description || ''}
                  </p>
                  {/* Học viên: tình trạng làm bài của mình */}
                  {q.my_status && (
                    <div className="ql-card-status">
                      <QuizStatus quiz={q} />
                    </div>
                  )}
                </div>
                <div className="ql-card-actions">
                  {actionOf(q, isManager).disabled ? (
                    <button type="button" className="s-btn s-btn-outline s-btn-sm" disabled>
                      {actionOf(q, isManager).label}
                    </button>
                  ) : (
                    <Link className="s-btn s-btn-primary s-btn-sm" to={`/quiz-show?id=${q.id}`}>
                      {actionOf(q, isManager).label}
                    </Link>
                  )}
                  {q.my_status?.submitted > 0 && (
                    <button
                      type="button"
                      className={`s-btn s-btn-sm ${historyId === q.id ? 's-btn-primary' : 's-btn-outline'}`}
                      aria-expanded={historyId === q.id}
                      onClick={() => setHistoryId(historyId === q.id ? null : q.id)}
                    >
                      📜 Lịch sử
                    </button>
                  )}
                  {isManager && (
                    <>
                      <Link className="s-btn s-btn-outline s-btn-sm" to={`/teacher/quizzes/${q.id}/questions`}>
                        Câu hỏi
                      </Link>
                      <button className="s-btn s-btn-danger s-btn-sm" onClick={() => handleDelete(q.id)}>
                        Xóa
                      </button>
                    </>
                  )}
                </div>
              </div>
              {/* Lịch sử làm bài của quiz này, mở ngay tại thẻ */}
              {historyId === q.id && <QuizHistoryPanel quizId={q.id} />}
            </div>
          ))}
      </div>
    </main>
  );
}
