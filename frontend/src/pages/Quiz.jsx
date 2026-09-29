import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { quizService } from '../services/quizService';
import { formatClock, gradingShort } from '../utils/quizGrading';

/** Tình trạng làm bài của học viên với 1 quiz: chưa làm / đang làm dở / điểm được tính + đạt, số lượt còn lại */
function QuizStatus({ quiz }) {
  const s = quiz.my_status;
  if (!s) return null;
  if (s.in_progress) {
    return (
      <span className="s-badge s-badge-warn">
        ⏳ Đang làm dở{s.remaining_sec != null ? ` · còn ${formatClock(s.remaining_sec)}` : ''}
      </span>
    );
  }
  if (!s.submitted) return <span className="s-badge s-badge-gray">Chưa làm</span>;
  return (
    <>
      <span className="s-badge s-badge-blue" title={`Điểm tính theo ${gradingShort(quiz.grading_method)}`}>
        Điểm: {s.graded_percent}% ({gradingShort(quiz.grading_method)})
      </span>
      {s.passed === true && <span className="s-badge s-badge-green">✓ Đạt</span>}
      {s.passed === false && <span className="s-badge s-badge-warn">Chưa đạt</span>}
      <span style={{ fontSize: '0.8rem', color: 'var(--s-text-muted)' }}>
        Đã làm {s.submitted} lần{s.attempts_left != null ? ` · còn ${s.attempts_left} lượt` : ''}
      </span>
    </>
  );
}

// Nút chính theo tình trạng: tiếp tục lượt dở / làm lại / làm bài; hết lượt thì khóa
function actionOf(quiz) {
  const s = quiz.my_status;
  if (!s) return { label: 'Làm bài', disabled: false };
  if (s.in_progress) return { label: 'Tiếp tục làm', disabled: false };
  if (s.attempts_left === 0) return { label: 'Hết lượt', disabled: true };
  return { label: s.submitted ? 'Làm lại' : 'Làm bài', disabled: false };
}

/** Tương đương initQuizList() trong _legacy/js/quiz.js + _legacy/pages/quiz.html */
export default function Quiz() {
  const [searchParams] = useSearchParams();
  const courseId = searchParams.get('course_id');
  const { user } = useAuth();
  // Admin / giảng viên thấy thêm nút quản lý (sửa, xóa quiz)
  const isManager = user?.role === 'admin' || user?.role === 'teacher';

  const [quizzes, setQuizzes] = useState(null); // null = đang tải
  const [loadError, setLoadError] = useState(null);

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
    <main className="s-main q-container">
      <div className="q-header">
        <h1 className="q-title">📝 Danh sách Quiz</h1>
        <p className="q-subtitle">Chọn một bài tập trắc nghiệm dưới đây để kiểm tra và củng cố kiến thức học tập.</p>
      </div>

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

        {quizzes !== null &&
          quizzes.length > 0 &&
          quizzes.map((q) => (
            <div key={q.id} className="s-card" style={{ marginBottom: '1rem' }}>
              <div
                className="s-card-body"
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}
              >
                <div>
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
                    <div style={{ display: 'flex', gap: '.4rem', flexWrap: 'wrap', alignItems: 'center', marginTop: '.5rem' }}>
                      <QuizStatus quiz={q} />
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap' }}>
                  {actionOf(q).disabled ? (
                    <span className="s-btn s-btn-outline s-btn-sm" aria-disabled="true" style={{ opacity: 0.6, cursor: 'not-allowed' }}>
                      {actionOf(q).label}
                    </span>
                  ) : (
                    <Link className="s-btn s-btn-primary s-btn-sm" to={`/quiz-show?id=${q.id}`}>
                      {actionOf(q).label}
                    </Link>
                  )}
                  {q.my_status?.submitted > 0 && (
                    <Link className="s-btn s-btn-outline s-btn-sm" to={`/student/quiz-history?quiz_id=${q.id}`}>
                      Lịch sử
                    </Link>
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
            </div>
          ))}
      </div>
    </main>
  );
}
