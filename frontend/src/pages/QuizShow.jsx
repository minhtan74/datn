import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { quizService } from '../services/quizService';
import RichText from '../components/common/RichText.jsx';

// Các phương án trả lời của mỗi câu hỏi
const OPTION_KEYS = ['A', 'B', 'C', 'D'];

// Đáp án đang làm dở lưu theo lượt làm (token) -> tải lại trang vẫn giữ được bài đang làm
const draftKey = (token) => `quiz_draft_${token}`;
function loadDraft(token) {
  try {
    return JSON.parse(sessionStorage.getItem(draftKey(token)) || '{}') || {};
  } catch {
    return {};
  }
}
function saveDraft(token, answers) {
  try {
    sessionStorage.setItem(draftKey(token), JSON.stringify(answers));
  } catch {
    /* trình duyệt chặn lưu trữ -> bỏ qua, chỉ mất khả năng khôi phục khi tải lại */
  }
}
function clearDraft(token) {
  try {
    sessionStorage.removeItem(draftKey(token));
  } catch {
    /* bỏ qua */
  }
}

// Tự nộp khi hết giờ: thử lại tối đa 3 lần, mỗi lần cách 3 giây (server còn 60 giây ân hạn)
const AUTO_SUBMIT_TRIES = 3;
const AUTO_SUBMIT_DELAY_MS = 3000;

// Định dạng số giây còn lại thành mm:ss
function formatClock(sec) {
  const s = Math.max(0, sec);
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
}

/** Tương đương initQuizShow() trong _legacy/js/quiz.js + _legacy/pages/quiz-show.html */
export default function QuizShow() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  // Id quiz lấy từ URL: /quiz-show?id=X
  const quizId = searchParams.get('id');

  const [loading, setLoading] = useState(true);
  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // { [questionId]: 'A'|'B'|'C'|'D' }
  const [alertMsg, setAlertMsg] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  // Không mở được đề (chưa đăng ký / hết lượt làm) -> ẩn phần câu hỏi
  const [blocked, setBlocked] = useState(false);
  // Đề có giới hạn thời gian / số lượt: token của lượt đang làm do server cấp (mở lại đề vẫn là lượt cũ),
  // mốc hết giờ + số giây còn lại, số lượt đã dùng (tính cả lượt đang làm)
  const tokenRef = useRef(null);
  const [deadline, setDeadline] = useState(null);
  const [remaining, setRemaining] = useState(null);
  const [attemptsUsed, setAttemptsUsed] = useState(null);
  // Đã hết giờ: cho nộp dù còn câu trống (để nộp lại được nếu lần tự nộp bị lỗi mạng)
  const [timeUp, setTimeUp] = useState(false);
  // Giữ đáp án mới nhất và cờ đã nộp để tự nộp khi hết giờ không bị dùng dữ liệu cũ / nộp 2 lần
  const answersRef = useRef({});
  const submittedRef = useRef(false);

  // Tải thông tin quiz + danh sách câu hỏi song song (câu hỏi trả về đã ẩn đáp án)
  useEffect(() => {
    if (!quizId) return;
    let cancelled = false;
    setLoading(true);
    setAlertMsg(null);
    setAnswers({});
    setBlocked(false);
    tokenRef.current = null;
    setDeadline(null);
    setRemaining(null);
    setAttemptsUsed(null);
    setTimeUp(false);
    answersRef.current = {};
    submittedRef.current = false;

    (async () => {
      const [qRes, questionsRes] = await Promise.all([
        quizService.getQuiz(Number(quizId)),
        quizService.getQuestions(Number(quizId)),
      ]);
      if (cancelled) return;

      const quizData = qRes?.data?.data;
      const questionsData = questionsRes?.data?.data || [];

      if (quizData) document.title = `${quizData.title} — StudyOnline`;

      setQuiz(quizData || null);
      setQuestions(questionsData);
      if (questionsRes && !questionsRes.ok) {
        setBlocked(true);
        setAlertMsg({ type: 'danger', text: questionsRes.data?.message || 'Không thể tải câu hỏi.' });
      } else if (questionsRes?.data?.attempt_token) {
        const d = questionsRes.data;
        tokenRef.current = d.attempt_token;
        setAttemptsUsed(d.attempts_used ?? null);
        // Khôi phục đáp án đã chọn nếu đây là lượt đang làm dở (tải lại trang / mở lại đề)
        const draft = loadDraft(d.attempt_token);
        answersRef.current = draft;
        setAnswers(draft);
        if (d.time_limit_sec) {
          // Đếm ngược theo thời gian CÒN LẠI của lượt do server tính từ giờ mở đề lần đầu
          const left = d.remaining_sec ?? d.time_limit_sec;
          setDeadline(Date.now() + left * 1000);
          setRemaining(left);
        }
      }
      setLoading(false);
    })();

    return () => {
      cancelled = true;
    };
  }, [quizId]);

  // Ghi nhận đáp án người học chọn cho 1 câu
  function selectAnswer(questionId, key) {
    setAnswers((prev) => {
      const next = { ...prev, [questionId]: key };
      answersRef.current = next;
      if (tokenRef.current) saveDraft(tokenRef.current, next);
      return next;
    });
  }

  // Gửi bài lên server chấm rồi chuyển sang trang kết quả; trả về true nếu nộp thành công
  async function submitAnswers() {
    if (submittedRef.current) return true;
    submittedRef.current = true;
    setSubmitting(true);
    const res = await quizService.submitQuiz(Number(quizId), answersRef.current, tokenRef.current);
    setSubmitting(false);
    if (!(res?.ok && res.data?.success)) submittedRef.current = false;

    // Backend dùng array_merge nên data nằm ở root: { success, quiz, score, total, percent, details }
    if (res?.ok && res.data?.success) {
      if (tokenRef.current) clearDraft(tokenRef.current);
      // Lượt đã lưu có result_id trên URL -> tải lại trang kết quả vẫn xem được
      const rid = res.data.result_id;
      navigate(`/student/quiz-result${rid ? `?result_id=${rid}` : ''}`, { state: res.data });
      return true;
    }
    setAlertMsg({ type: 'danger', text: res?.data?.message || 'Có lỗi khi nộp bài. Vui lòng thử lại.' });
    return false;
  }

  // Hết giờ: tự nộp, lỗi (vd mất mạng) thì thử lại vài lần; vẫn lỗi thì để học viên bấm Nộp bài
  async function autoSubmit() {
    for (let i = 0; i < AUTO_SUBMIT_TRIES; i += 1) {
      if (i > 0) await new Promise((r) => setTimeout(r, AUTO_SUBMIT_DELAY_MS));
      if (await submitAnswers()) return;
    }
    setAlertMsg({
      type: 'danger',
      text: '⚠️ Tự nộp bài khi hết giờ bị lỗi. Kiểm tra kết nối mạng rồi bấm "Nộp bài" ngay để gửi lại.',
    });
  }

  // Nộp bài thủ công: bắt buộc trả lời đủ mọi câu (trừ khi đã hết giờ — lúc đó nộp ngay phần đã làm)
  function handleSubmit(e) {
    e.preventDefault();
    setAlertMsg(null);

    const unanswered = questions.filter((q) => !answers[q.id]);
    if (unanswered.length > 0 && !timeUp) {
      setAlertMsg({
        type: 'warning',
        text: `⚠️ Bạn còn ${unanswered.length} câu chưa trả lời. Vui lòng hoàn thành trước khi nộp bài.`,
      });
      return;
    }
    submitAnswers();
  }

  // Đếm ngược mỗi giây; hết giờ thì tự nộp bài (kể cả câu chưa trả lời)
  useEffect(() => {
    if (!deadline) return;
    const timer = setInterval(() => {
      const left = Math.round((deadline - Date.now()) / 1000);
      setRemaining(left);
      if (left <= 0) {
        clearInterval(timer);
        setTimeUp(true);
        setAlertMsg({ type: 'warning', text: '⏰ Hết giờ làm bài — hệ thống tự động nộp bài của bạn.' });
        autoSubmit();
      }
    }, 1000);
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deadline]);

  // Bộ ôn tập chương / bài -> nút quay lại dẫn về trang chương / bài học thay vì danh sách quiz
  const backTo = quiz?.chapter_id
    ? `/chapters?course_id=${quiz.course_id}`
    : quiz?.review_lesson_id
      ? `/lesson?id=${quiz.review_lesson_id}`
      : '/quiz';

  if (!quizId) {
    return (
      <main className="s-main q-container qh-page">
        <div className="alert alert-danger">Thiếu tham số quiz.</div>
      </main>
    );
  }

  return (
    <main className="s-main q-container qh-page">
      {/* Breadcrumb */}
      <nav className="q-breadcrumb" aria-label="Breadcrumb">
        <Link to="/student/dashboard">Dashboard</Link>
        <span className="q-breadcrumb-separator">›</span>
        <Link to={backTo}>
          {quiz?.chapter_id ? quiz.course_title : quiz?.review_lesson_id ? quiz.review_lesson_title : 'Danh sách Quiz'}
        </Link>
        <span className="q-breadcrumb-separator">›</span>
        <span className="q-breadcrumb-current">{quiz?.title || 'Làm bài Quiz'}</span>
      </nav>

      {/* Quiz Header */}
      <div className="q-header">
        <h1 className="q-title">{loading ? 'Đang tải...' : quiz?.title || 'Không tìm thấy quiz'}</h1>
        <p className="q-subtitle">
          {loading
            ? 'Vui lòng đợi trong giây lát...'
            : quiz
              ? `${questions.length} câu hỏi · ${quiz.course_title}`
              : ''}
        </p>
        {/* Cài đặt làm bài: thời gian, điểm đạt, số lượt đã dùng */}
        {quiz && (quiz.duration || quiz.passing_score || quiz.max_attempts) && (
          <p className="q-subtitle" style={{ marginTop: '0.35rem' }}>
            {quiz.duration ? `⏱ ${quiz.duration} phút` : ''}
            {quiz.passing_score ? ` · 🎯 Đạt từ ${quiz.passing_score}%` : ''}
            {quiz.max_attempts ? ` · 🔁 Lượt làm: ${attemptsUsed ?? quiz.my_attempts ?? 0}/${quiz.max_attempts}` : ''}
          </p>
        )}
        {remaining !== null && (
          <div
            style={{
              marginTop: '0.75rem',
              display: 'inline-block',
              padding: '0.35rem 0.9rem',
              borderRadius: 999,
              fontWeight: 800,
              fontVariantNumeric: 'tabular-nums',
              color: '#fff',
              background: remaining <= 60 ? 'var(--s-danger)' : 'var(--s-primary, #2563eb)',
            }}
          >
            ⏱ Còn lại {formatClock(remaining)}
          </div>
        )}
      </div>

      <div className="mb-4">
        {alertMsg && <div className={`alert alert-${alertMsg.type}`}>{alertMsg.text}</div>}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="space-y-6">
          {loading && (
            <div style={{ textAlign: 'center', padding: '5rem 0' }}>
              <div className="spinner mb-4"></div>
              <p style={{ fontSize: '0.9rem', color: 'var(--s-text-muted)', fontWeight: 500 }}>Đang tải câu hỏi...</p>
            </div>
          )}

          {!loading && !quiz && <div className="alert alert-danger">Không tìm thấy quiz.</div>}

          {!loading && quiz && !blocked && questions.length === 0 && (
            <div className="empty-state">
              <div className="icon">📝</div>
              <h3>Quiz chưa có câu hỏi</h3>
            </div>
          )}

          {!loading &&
            quiz &&
            questions.length > 0 &&
            questions.map((q, i) => (
              <div key={q.id} className="question-card">
                <div className="question-num">Câu {i + 1}</div>
                <div className="question-content" style={{ whiteSpace: 'pre-wrap' }}>
                  <RichText text={q.content} />
                </div>
                <ul className="option-list">
                  {/* Bỏ qua phương án C/D để trống (form câu hỏi cho phép chỉ nhập A, B) */}
                  {OPTION_KEYS.filter((k) => q[`option_${k.toLowerCase()}`]).map((k) => (
                    <li key={k} className="option-item">
                      <input
                        type="radio"
                        name={`answers[${q.id}]`}
                        id={`q${q.id}_${k}`}
                        value={k}
                        checked={answers[q.id] === k}
                        onChange={() => selectAnswer(q.id, k)}
                        required={!timeUp}
                      />
                      <label htmlFor={`q${q.id}_${k}`}>
                        <span className="option-key">{k}</span>
                        <span style={{ whiteSpace: 'pre-wrap' }}>
                          <RichText text={q[`option_${k.toLowerCase()}`]} imgMaxHeight={160} />
                        </span>
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
        </div>

        {!loading && quiz && questions.length > 0 && (
          <div className="q-footer-actions">
            <Link to={backTo} className="s-btn s-btn-outline">
              ← Quay lại
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--s-text-muted)', fontWeight: 500 }}>
                <span style={{ fontWeight: 700, color: 'var(--s-text)' }}>{questions.length}</span> câu hỏi
              </span>
              <button type="submit" className="s-btn s-btn-primary" disabled={submitting}>
                {submitting ? (
                  <>
                    <span className="spinner"></span> Đang chấm bài...
                  </>
                ) : (
                  '🚀 Nộp bài'
                )}
              </button>
            </div>
          </div>
        )}
      </form>
    </main>
  );
}
