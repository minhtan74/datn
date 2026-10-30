import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { quizService } from '../services/quizService';
import RichText from '../components/common/RichText.jsx';
import { GRADING_METHODS } from '../utils/quizGrading';
import '../assets/css/quiz-taking.css';

// Các phương án trả lời của mỗi câu hỏi
const OPTION_KEYS = ['A', 'B', 'C', 'D'];

// Đáp án đang làm dở & cờ đánh dấu lưu theo lượt làm (token) -> tải lại trang vẫn giữ được bài đang làm
const draftKey = (token) => `quiz_draft_${token}`;
const flagsKey = (token) => `quiz_flags_${token}`;

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
    /* trình duyệt chặn lưu trữ -> bỏ qua */
  }
}

function clearDraft(token) {
  try {
    sessionStorage.removeItem(draftKey(token));
  } catch {
    /* bỏ qua */
  }
}

function loadFlags(token) {
  try {
    return JSON.parse(sessionStorage.getItem(flagsKey(token)) || '{}') || {};
  } catch {
    return {};
  }
}

function saveFlags(token, flags) {
  try {
    sessionStorage.setItem(flagsKey(token), JSON.stringify(flags));
  } catch {
    /* bỏ qua */
  }
}

function clearFlags(token) {
  try {
    sessionStorage.removeItem(flagsKey(token));
  } catch {
    /* bỏ qua */
  }
}

// Tự nộp khi hết giờ: thử lại tối đa 3 lần, mỗi lần cách 3 giây (server còn 60 giây ân hạn)
const AUTO_SUBMIT_TRIES = 3;
const AUTO_SUBMIT_DELAY_MS = 3000;

// Định dạng số giây còn lại thành mm:ss (hoặc hh:mm:ss nếu > 1 giờ)
function formatClock(sec) {
  const s = Math.max(0, sec || 0);
  const hours = Math.floor(s / 3600);
  const minutes = Math.floor((s % 3600) / 60);
  const seconds = s % 60;
  if (hours > 0) {
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

export default function QuizShow() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  // Id quiz lấy từ URL: /quiz-show?id=X
  const quizId = searchParams.get('id');

  const [loading, setLoading] = useState(true);
  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // { [questionId]: 'A'|'B'|'C'|'D' }
  const [flags, setFlags] = useState({}); // { [questionId]: boolean }
  const [currentIndex, setCurrentIndex] = useState(0);
  const [viewMode, setViewMode] = useState('single'); // 'single' | 'all'
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showExitModal, setShowExitModal] = useState(false);
  const [showMobilePalette, setShowMobilePalette] = useState(false);

  const [alertMsg, setAlertMsg] = useState(null);
  const alertRef = useRef(null);
  const [submitting, setSubmitting] = useState(false);
  const [started, setStarted] = useState(false);
  const [starting, setStarting] = useState(false);
  const openingRef = useRef(false);
  const pageRef = useRef(null);
  const [introRemaining, setIntroRemaining] = useState(null);

  // Đề có giới hạn thời gian / số lượt
  const tokenRef = useRef(null);
  const [deadline, setDeadline] = useState(null);
  const [remaining, setRemaining] = useState(null);
  const [attemptsUsed, setAttemptsUsed] = useState(null);
  const [timeUp, setTimeUp] = useState(false);

  // Giữ đáp án mới nhất và cờ đã nộp để tự nộp khi hết giờ không bị dùng dữ liệu cũ / nộp 2 lần
  const answersRef = useRef({});
  const submittedRef = useRef(false);

  // Chỉ xem thông tin: chưa tải câu hỏi, chưa tạo lượt và chưa bắt đầu đồng hồ.
  useEffect(() => {
    if (!quizId) return;
    let cancelled = false;
    const page = {};
    pageRef.current = page;
    openingRef.current = false;
    setLoading(true);
    setQuiz(null);
    setQuestions([]);
    setAlertMsg(null);
    setAnswers({});
    setFlags({});
    setCurrentIndex(0);
    setStarted(false);
    setStarting(false);
    tokenRef.current = null;
    setDeadline(null);
    setRemaining(null);
    setAttemptsUsed(null);
    setTimeUp(false);
    answersRef.current = {};
    submittedRef.current = false;

    (async () => {
      const qRes = await quizService.getQuiz(Number(quizId));
      if (cancelled) return;
      const quizData = qRes?.data?.data;

      if (quizData) document.title = `${quizData.title} — StudyOnline`;

      setQuiz(quizData || null);
      if (!qRes?.ok) {
        setAlertMsg({ type: 'danger', text: qRes?.data?.message || 'Không thể tải thông tin quiz.' });
      }
      setLoading(false);
    })();

    return () => {
      cancelled = true;
      if (pageRef.current === page) pageRef.current = null;
    };
  }, [quizId]);

  // Lượt đang dở vẫn chạy thời gian khi người học quay về màn hình giới thiệu.
  useEffect(() => {
    const left = quiz?.my_status?.remaining_sec;
    setIntroRemaining(left ?? null);
    if (left == null || started) return;
    const end = Date.now() + left * 1000;
    const timer = setInterval(() => setIntroRemaining(Math.max(0, Math.ceil((end - Date.now()) / 1000))), 1000);
    return () => clearInterval(timer);
  }, [quiz, started]);

  async function startAttempt() {
    if (openingRef.current || started) return;
    openingRef.current = true;
    setStarting(true);
    setAlertMsg(null);
    const page = pageRef.current;
    const res = await quizService.getQuestions(Number(quizId), { resumeOnly: !!quiz.my_status?.in_progress });
    if (pageRef.current !== page) return;
    if (!res?.ok) {
      setAlertMsg({ type: 'danger', text: res?.data?.message || 'Không thể tải câu hỏi. Vui lòng thử lại.' });
      const refreshed = await quizService.getQuiz(Number(quizId));
      if (pageRef.current !== page) return;
      if (refreshed?.ok) setQuiz(refreshed.data.data);
    } else {
      const d = res.data;
      const rows = d.data || [];
      setQuestions(rows);
      setQuiz((prev) => ({ ...prev, question_count: rows.length }));
      if (rows.length) {
        tokenRef.current = d.attempt_token || null;
        setAttemptsUsed(d.attempts_used ?? null);
        const draft = d.attempt_token ? loadDraft(d.attempt_token) : {};
        const savedFlags = d.attempt_token ? loadFlags(d.attempt_token) : {};
        answersRef.current = draft;
        setAnswers(draft);
        setFlags(savedFlags);
        setStarted(true);
        setCurrentIndex(0);
        if (d.time_limit_sec) {
          const left = d.remaining_sec ?? d.time_limit_sec;
          setDeadline(Date.now() + left * 1000);
          setRemaining(left);
        }
      }
    }
    openingRef.current = false;
    setStarting(false);
  }

  // Ghi nhận đáp án người học chọn cho 1 câu
  function selectAnswer(questionId, key) {
    setAnswers((prev) => {
      const next = { ...prev, [questionId]: key };
      answersRef.current = next;
      if (tokenRef.current) saveDraft(tokenRef.current, next);
      return next;
    });
  }

  // Xóa đáp án đã chọn (bỏ chọn)
  function clearAnswer(questionId) {
    setAnswers((prev) => {
      const next = { ...prev };
      delete next[questionId];
      answersRef.current = next;
      if (tokenRef.current) saveDraft(tokenRef.current, next);
      return next;
    });
  }

  // Đánh dấu / Bỏ đánh dấu xem lại câu hỏi
  function toggleFlag(questionId) {
    setFlags((prev) => {
      const next = { ...prev, [questionId]: !prev[questionId] };
      if (tokenRef.current) saveFlags(tokenRef.current, next);
      return next;
    });
  }

  // Gửi bài lên server chấm rồi chuyển sang trang kết quả; trả về true nếu nộp thành công
  async function submitAnswers() {
    if (submittedRef.current) return true;
    submittedRef.current = true;
    setSubmitting(true);
    setShowSubmitModal(false);
    const res = await quizService.submitQuiz(Number(quizId), answersRef.current, tokenRef.current);
    setSubmitting(false);
    if (!(res?.ok && res.data?.success)) submittedRef.current = false;

    if (res?.ok && res.data?.success) {
      if (tokenRef.current) {
        clearDraft(tokenRef.current);
        clearFlags(tokenRef.current);
      }
      const rid = res.data.result_id;
      navigate(`/student/quiz-result${rid ? `?result_id=${rid}` : ''}`, { state: res.data });
      return true;
    }
    setAlertMsg({ type: 'danger', text: res?.data?.message || 'Có lỗi khi nộp bài. Vui lòng thử lại.' });
    return false;
  }

  // Hết giờ: tự nộp, lỗi (vd mất mạng) thì thử lại vài lần
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

  // Đếm ngược mỗi giây; hết giờ thì tự nộp bài
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

  // Phím tắt bàn phím (A, B, C, D hoặc 1, 2, 3, 4; Mũi tên trái/phải; F để gắn cờ)
  useEffect(() => {
    if (!started || submitting || showSubmitModal || showExitModal) return;

    function handleKeyDown(e) {
      if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

      const key = e.key;
      const currentQ = questions[currentIndex];

      const optionMap = {
        '1': 'A', 'a': 'A', 'A': 'A',
        '2': 'B', 'b': 'B', 'B': 'B',
        '3': 'C', 'c': 'C', 'C': 'C',
        '4': 'D', 'd': 'D', 'D': 'D',
      };

      if (optionMap[key] && currentQ) {
        const optKey = optionMap[key];
        if (currentQ[`option_${optKey.toLowerCase()}`]) {
          selectAnswer(currentQ.id, optKey);
        }
        return;
      }

      if (key.toLowerCase() === 'f' && currentQ) {
        toggleFlag(currentQ.id);
        return;
      }

      if (viewMode === 'single') {
        if (key === 'ArrowRight' && currentIndex < questions.length - 1) {
          setCurrentIndex((i) => i + 1);
        } else if (key === 'ArrowLeft' && currentIndex > 0) {
          setCurrentIndex((i) => i - 1);
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [started, submitting, showSubmitModal, showExitModal, currentIndex, questions, viewMode]);

  // Nhảy tới câu hỏi theo index
  function goToQuestion(index) {
    setCurrentIndex(index);
    if (viewMode === 'all') {
      const el = document.getElementById(`qz-q-${index}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.classList.add('qz-highlight-flash');
        setTimeout(() => el.classList.remove('qz-highlight-flash'), 1200);
      }
    }
    if (showMobilePalette) {
      setShowMobilePalette(false);
    }
  }

  // Chuyển tới câu chưa làm tiếp theo
  function jumpToNextUnanswered() {
    const nextUnanswered = questions.findIndex((q) => !answers[q.id]);
    if (nextUnanswered !== -1) {
      goToQuestion(nextUnanswered);
    }
  }

  // Thống kê tiến độ
  const totalCount = questions.length;
  const answeredCount = Object.keys(answers).filter((id) => answers[id]).length;
  const answeredList = questions
    .map((q, idx) => ({ ...q, index: idx }))
    .filter((q) => Boolean(answers[q.id]));
  const unansweredList = questions
    .map((q, idx) => ({ ...q, index: idx }))
    .filter((q) => !answers[q.id]);
  const unansweredCount = unansweredList.length;
  const flaggedCount = Object.values(flags).filter(Boolean).length;
  const percentDone = totalCount > 0 ? Math.round((answeredCount / totalCount) * 100) : 0;

  const timerStatus =
    remaining === null
      ? 'normal'
      : remaining <= 60
        ? 'critical'
        : remaining <= 300
          ? 'warning'
          : 'normal';

  // Bộ ôn tập chương / bài
  const backTo = quiz?.chapter_id
    ? `/chapters?course_id=${quiz.course_id}`
    : quiz?.review_lesson_id
      ? `/lesson?id=${quiz.review_lesson_id}`
      : '/quiz';
  const inProgress = !!quiz?.my_status?.in_progress;
  const exhausted = !inProgress && quiz?.my_status?.attempts_left === 0;
  const gradingLabel = (GRADING_METHODS.find((m) => m.key === quiz?.grading_method) || GRADING_METHODS[0]).label;

  // Render câu hỏi đơn lẻ (tái sử dụng trong cả 2 chế độ single & all)
  function renderQuestionCard(q, idx, isSingle = true) {
    const isAnswered = Boolean(answers[q.id]);
    const isFlagged = Boolean(flags[q.id]);

    return (
      <div key={q.id} id={`qz-q-${idx}`} className="qz-card">
        {/* Header câu hỏi */}
        <div className="qz-card-header">
          <div className="qz-card-tags">
            <span className="qz-num-badge">
              {isSingle ? `Câu ${idx + 1} / ${totalCount}` : `Câu ${idx + 1}`}
            </span>
            <span className={`qz-status-badge ${isAnswered ? 'qz-status-answered' : 'qz-status-unanswered'}`}>
              {isAnswered ? '✓ Đã trả lời' : '○ Chưa trả lời'}
            </span>
          </div>

          <button
            type="button"
            className={`qz-flag-toggle ${isFlagged ? 'flagged' : ''}`}
            onClick={() => toggleFlag(q.id)}
            title="Đánh dấu câu hỏi này để xem lại trước khi nộp bài"
          >
            <span>🚩</span>
            <span>{isFlagged ? 'Đã đánh dấu' : 'Đánh dấu xem lại'}</span>
          </button>
        </div>

        {/* Nội dung câu hỏi */}
        <div className="qz-card-body">
          <div className="qz-question-text">
            <RichText text={q.content} />
          </div>

          {/* Danh sách các lựa chọn */}
          <ul className="qz-options-list">
            {OPTION_KEYS.filter((k) => q[`option_${k.toLowerCase()}`]).map((k) => {
              const isSelected = answers[q.id] === k;
              return (
                <li key={k} className="qz-option-row">
                  <input
                    type="radio"
                    name={`answers[${q.id}]`}
                    id={`q${q.id}_${k}`}
                    value={k}
                    checked={isSelected}
                    onChange={() => selectAnswer(q.id, k)}
                    className="qz-option-input"
                  />
                  <label htmlFor={`q${q.id}_${k}`} className="qz-option-label">
                    <span className="qz-option-key">{k}</span>
                    <div className="qz-option-content">
                      <RichText text={q[`option_${k.toLowerCase()}`]} imgMaxHeight={160} />
                    </div>
                    <span className="qz-option-radio-dot" />
                  </label>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Footer câu hỏi */}
        <div className="qz-card-footer">
          {isAnswered ? (
            <button
              type="button"
              className="qz-clear-btn"
              onClick={() => clearAnswer(q.id)}
              title="Xóa lựa chọn cho câu này"
            >
              ✕ Bỏ chọn đáp án này
            </button>
          ) : (
            <span />
          )}

          {isSingle && (
            <div className="qz-card-nav-btns">
              <button
                type="button"
                className="qz-btn-prev"
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
              >
                ← Câu trước
              </button>

              {currentIndex < totalCount - 1 && (
                <button
                  type="button"
                  className="qz-btn-next"
                  onClick={() => setCurrentIndex((i) => Math.min(totalCount - 1, i + 1))}
                >
                  Câu tiếp theo →
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Render nội dung Palette trong Sidebar & Mobile Drawer
  function renderPaletteContent() {
    return (
      <div className="qz-sidebar-box">
        {/* Đồng hồ to */}
        {remaining !== null && (
          <div className={`qz-sidebar-timer is-${timerStatus}`}>
            <div className="qz-sidebar-timer-label">⏱ Thời gian còn lại</div>
            <div className="qz-sidebar-timer-val">{formatClock(remaining)}</div>
          </div>
        )}

        {/* Tổng quan số lượng */}
        <div className="qz-box-counts">
          <div className="qz-count-item answered">
            <span className="qz-count-dot answered" />
            <span>Đã làm: <strong>{answeredCount}</strong></span>
          </div>
          <div className="qz-count-item unanswered">
            <span className="qz-count-dot unanswered" />
            <span>Chưa làm: <strong>{unansweredCount}</strong></span>
          </div>
        </div>

        {/* Danh sách các số câu hỏi đã làm và chưa làm */}
        <div className="qz-question-lists">
          {/* Nhóm Đã làm */}
          <div className="qz-list-group">
            <div className="qz-list-label is-answered">
              <span>✓ Đã làm ({answeredCount})</span>
            </div>
            <div className="qz-chips-container">
              {answeredList.length > 0 ? (
                answeredList.map((q) => (
                  <button
                    key={q.id}
                    type="button"
                    className={`qz-chip-btn answered ${currentIndex === q.index ? 'active' : ''}`}
                    onClick={() => goToQuestion(q.index)}
                    title={`Câu ${q.index + 1} - Đã chọn (${answers[q.id]})`}
                  >
                    {q.index + 1}
                  </button>
                ))
              ) : (
                <span className="qz-empty-text">(Chưa có câu nào)</span>
              )}
            </div>
          </div>

          {/* Nhóm Chưa làm */}
          <div className="qz-list-group">
            <div className="qz-list-label is-unanswered">
              <span>○ Chưa làm ({unansweredCount})</span>
            </div>
            <div className="qz-chips-container">
              {unansweredList.length > 0 ? (
                unansweredList.map((q) => (
                  <button
                    key={q.id}
                    type="button"
                    className={`qz-chip-btn unanswered ${currentIndex === q.index ? 'active' : ''}`}
                    onClick={() => goToQuestion(q.index)}
                    title={`Câu ${q.index + 1} - Chưa trả lời`}
                  >
                    {q.index + 1}
                  </button>
                ))
              ) : (
                <span className="qz-empty-text success">🎉 Đã hoàn thành tất cả!</span>
              )}
            </div>
          </div>
        </div>

        {/* Nút nộp bài */}
        <button
          type="button"
          className="qz-sidebar-submit-btn"
          disabled={submitting}
          onClick={() => setShowSubmitModal(true)}
        >
          {submitting ? (
            <>
              <span className="spinner" /> Đang chấm bài...
            </>
          ) : (
            <>🚀 Nộp bài thi</>
          )}
        </button>

        {unansweredCount > 0 && (
          <button type="button" className="qz-jump-unanswered-link" onClick={jumpToNextUnanswered}>
            Đi tới câu chưa làm tiếp theo →
          </button>
        )}
      </div>
    );
  }

  if (!quizId) {
    return (
      <main className="s-main q-container qh-page">
        <div className="alert alert-danger">Thiếu tham số quiz.</div>
      </main>
    );
  }

  return (
    <main className="s-main qz-page-wrap">
      {/* =========================================================================
          TRƯỜNG HỢP 1: ĐANG LÀM BÀI (STARTED = TRUE)
          ========================================================================= */}
      {started && questions.length > 0 && (
        <>
          {/* Sticky Topbar */}
          <header className="qz-exam-topbar">
            <div className="qz-topbar-inner">
              <div className="qz-topbar-left">
                <button type="button" className="qz-exit-btn" onClick={() => setShowExitModal(true)}>
                  ← Thoát bài
                </button>
                <div className="qz-exam-info">
                  <h1 className="qz-exam-title">{quiz?.title}</h1>
                  <div className="qz-exam-sub">
                    <span>{quiz?.course_title || 'Khóa học'}</span>
                    <span>•</span>
                    <span>
                      Đã làm {answeredCount}/{totalCount} câu
                    </span>
                  </div>
                </div>
              </div>

              {/* View Switch */}
              <div className="qz-topbar-center">
                <div className="qz-view-switch" role="tablist">
                  <button
                    type="button"
                    className={`qz-view-tab ${viewMode === 'single' ? 'active' : ''}`}
                    onClick={() => setViewMode('single')}
                  >
                    📄 Từng câu
                  </button>
                  <button
                    type="button"
                    className={`qz-view-tab ${viewMode === 'all' ? 'active' : ''}`}
                    onClick={() => setViewMode('all')}
                  >
                    📜 Tất cả
                  </button>
                </div>
              </div>

              {/* Topbar Right: Timer */}
              <div className="qz-topbar-right">
                {remaining !== null && (
                  <div className={`qz-timer-badge qz-timer-${timerStatus}`}>
                    ⏱ {formatClock(remaining)}
                  </div>
                )}
              </div>
            </div>
          </header>

          {/* Thông báo lỗi nếu có */}
          {alertMsg && (
            <div style={{ maxWidth: 1280, margin: '0 auto 1.5rem', padding: '0 1.5rem' }} ref={alertRef}>
              <div role="alert" className={`alert alert-${alertMsg.type}`}>
                {alertMsg.text}
              </div>
            </div>
          )}

          {/* Không gian làm bài 2 cột */}
          <div className="qz-workspace">
            {/* Cột trái: Khu vực câu hỏi */}
            <div className="qz-content-col">
              {viewMode === 'single' ? (
                <>
                  {renderQuestionCard(questions[currentIndex], currentIndex, true)}
                  <div className="qz-keyboard-hint">
                    <span>💡 Phím tắt nhanh:</span>
                    <span>
                      <kbd className="qz-kbd">A</kbd> <kbd className="qz-kbd">B</kbd> <kbd className="qz-kbd">C</kbd>{' '}
                      <kbd className="qz-kbd">D</kbd> chọn đáp án • <kbd className="qz-kbd">←</kbd>{' '}
                      <kbd className="qz-kbd">→</kbd> chuyển câu • <kbd className="qz-kbd">F</kbd> cờ xem lại
                    </span>
                  </div>
                </>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  {questions.map((q, idx) => renderQuestionCard(q, idx, false))}
                </div>
              )}
            </div>

            {/* Cột phải: Sticky Sidebar (Thời gian & Nộp bài) */}
            <aside className="qz-sidebar-col">{renderPaletteContent()}</aside>
          </div>

          {/* Modal Xác nhận Nộp bài */}
          {showSubmitModal && (
            <div className="qz-modal-backdrop" onClick={() => setShowSubmitModal(false)}>
              <div className="qz-modal-box" onClick={(e) => e.stopPropagation()}>
                <div className={`qz-modal-icon ${unansweredCount === 0 ? 'ready' : 'warning'}`}>
                  {unansweredCount === 0 ? '🎉' : '⚠️'}
                </div>

                <h3 className="qz-modal-title">
                  {unansweredCount === 0 ? 'Sẵn sàng nộp bài?' : 'Bạn còn câu chưa trả lời'}
                </h3>

                <p className="qz-modal-desc">
                  {unansweredCount === 0
                    ? 'Bạn đã hoàn thành tất cả câu hỏi trong bài thi! Bạn có chắc chắn muốn nộp để hệ thống chấm điểm?'
                    : `Bạn còn ${unansweredCount} câu chưa chọn đáp án. Bạn có muốn hoàn thành trước khi nộp không?`}
                </p>

                <div className="qz-modal-stats">
                  <div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#2563eb' }}>{totalCount}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--s-text-muted)' }}>Tổng số câu</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#10b981' }}>{answeredCount}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--s-text-muted)' }}>Đã làm</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f59e0b' }}>{flaggedCount}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--s-text-muted)' }}>Đánh dấu</div>
                  </div>
                </div>

                {unansweredCount > 0 && (
                  <div className="qz-modal-unanswered-list">
                    <div className="qz-modal-unanswered-title">Các câu hỏi còn trống (bấm để làm ngay):</div>
                    <div className="qz-unanswered-pills">
                      {unansweredList.slice(0, 15).map((q) => (
                        <button
                          key={q.id}
                          type="button"
                          className="qz-pill-btn"
                          onClick={() => {
                            setShowSubmitModal(false);
                            goToQuestion(q.index);
                          }}
                        >
                          Câu {q.index + 1}
                        </button>
                      ))}
                      {unansweredList.length > 15 && (
                        <span style={{ fontSize: '0.75rem', color: '#9f1239', alignSelf: 'center' }}>
                          +{unansweredList.length - 15} câu khác
                        </span>
                      )}
                    </div>
                  </div>
                )}

                <div className="qz-modal-actions">
                  <button type="button" className="qz-btn-modal-cancel" onClick={() => setShowSubmitModal(false)}>
                    Tiếp tục làm bài
                  </button>

                  <button
                    type="button"
                    className="qz-btn-modal-submit"
                    disabled={submitting || (unansweredCount > 0 && !timeUp)}
                    onClick={submitAnswers}
                    style={{
                      opacity: unansweredCount > 0 && !timeUp ? 0.6 : 1,
                      cursor: unansweredCount > 0 && !timeUp ? 'not-allowed' : 'pointer',
                    }}
                    title={
                      unansweredCount > 0 && !timeUp
                        ? 'Cần hoàn thành tất cả các câu trước khi nộp'
                        : 'Xác nhận nộp bài'
                    }
                  >
                    {submitting ? 'Đang chấm điểm...' : 'Xác nhận nộp bài'}
                  </button>
                </div>

                {unansweredCount > 0 && !timeUp && (
                  <p style={{ textAlign: 'center', fontSize: '0.75rem', color: '#e11d48', margin: 0 }}>
                    * Hệ thống yêu cầu hoàn thành đủ các câu hỏi trước khi nộp bài (hoặc tự nộp khi hết giờ).
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Modal Xác nhận Thoát bài */}
          {showExitModal && (
            <div className="qz-modal-backdrop" onClick={() => setShowExitModal(false)}>
              <div className="qz-modal-box" onClick={(e) => e.stopPropagation()}>
                <div className="qz-modal-icon warning">⚠️</div>
                <h3 className="qz-modal-title">Bạn có chắc muốn rời khỏi bài thi?</h3>
                <p className="qz-modal-desc">
                  Bài làm của bạn đang được tự động lưu tạm thời. Tuy nhiên, thời gian làm bài vẫn tiếp tục đếm ngược.
                  Bạn có chắc muốn quay về danh sách bài học không?
                </p>
                <div className="qz-modal-actions">
                  <button type="button" className="qz-btn-modal-cancel" onClick={() => setShowExitModal(false)}>
                    Ở lại làm tiếp
                  </button>
                  <Link
                    to={backTo}
                    className="qz-btn-modal-submit"
                    style={{
                      background: '#ef4444',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      textDecoration: 'none',
                    }}
                  >
                    Thoát bài thi
                  </Link>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* =========================================================================
          TRƯỜNG HỢP 2: TRƯỚC KHI LÀM BÀI (MÀN HÌNH GIỚI THIỆU HOẶC ĐANG TẢI)
          ========================================================================= */}
      {!started && (
        <div className="q-container qh-page" style={{ maxWidth: 960, margin: '0 auto', padding: '1.5rem' }}>
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
          <div className="q-header" style={{ marginBottom: '1.5rem' }}>
            <h1 className="q-title">{loading ? 'Đang tải...' : quiz?.title || 'Không tìm thấy quiz'}</h1>
            <p className="q-subtitle">
              {loading
                ? 'Vui lòng đợi trong giây lát...'
                : quiz
                  ? `${quiz.question_count} câu hỏi · ${quiz.course_title}`
                  : ''}
            </p>
          </div>

          <div className="mb-4" ref={alertRef}>
            {alertMsg && (
              <div role="alert" className={`alert alert-${alertMsg.type}`}>
                {alertMsg.text}
              </div>
            )}
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: '5rem 0' }}>
              <div className="spinner mb-4" />
              <p style={{ fontSize: '0.9rem', color: 'var(--s-text-muted)', fontWeight: 500 }}>
                Đang tải thông tin quiz...
              </p>
            </div>
          )}

          {!loading && !quiz && <div className="alert alert-danger">Không tìm thấy quiz.</div>}

          {!loading && quiz && (
            <section className="qz-intro-box" aria-labelledby="quiz-intro-title" aria-busy={starting}>
              <div className="qz-intro-header">
                <div className="qz-intro-icon">📝</div>
                <div className="qz-intro-title-wrap">
                  <h2 id="quiz-intro-title">{inProgress ? 'Tiếp tục bài đang làm' : 'Thông tin trước khi làm bài'}</h2>
                  <span style={{ fontSize: '0.85rem', color: 'var(--s-text-muted)' }}>
                    Hãy kiểm tra kỹ thông tin và chuẩn bị đường truyền mạng ổn định trước khi bắt đầu.
                  </span>
                </div>
              </div>

              {quiz.description && (
                <div className="qz-intro-desc">
                  <RichText text={quiz.description} />
                </div>
              )}

              <div className="qz-facts-grid">
                <div className="qz-fact-card">
                  <div className="qz-fact-label">📝 Số câu hỏi</div>
                  <div className="qz-fact-value">{quiz.question_count} câu</div>
                </div>

                <div className="qz-fact-card">
                  <div className="qz-fact-label">⏱ Thời gian</div>
                  <div className="qz-fact-value">{quiz.duration ? `${quiz.duration} phút` : 'Không giới hạn'}</div>
                </div>

                <div className="qz-fact-card">
                  <div className="qz-fact-label">🎯 Điểm đạt</div>
                  <div className="qz-fact-value">{quiz.passing_score ? `Từ ${quiz.passing_score}%` : 'Không quy định'}</div>
                </div>

                <div className="qz-fact-card">
                  <div className="qz-fact-label">⭐ Cách tính điểm</div>
                  <div className="qz-fact-value">{gradingLabel}</div>
                </div>

                <div className="qz-fact-card">
                  <div className="qz-fact-label">🔁 Số lượt tối đa</div>
                  <div className="qz-fact-value">{quiz.max_attempts || 'Không giới hạn'}</div>
                </div>

                <div className="qz-fact-card">
                  <div className="qz-fact-label">📊 Lượt đã dùng</div>
                  <div className="qz-fact-value">
                    {quiz.is_preview
                      ? 'Không ghi nhận'
                      : `${quiz.my_attempts ?? 0}${quiz.max_attempts ? ` / ${quiz.max_attempts}` : ''}`}
                  </div>
                  {!quiz.is_preview && quiz.my_status?.attempts_left != null && (
                    <div className="qz-fact-sub">Còn {quiz.my_status.attempts_left} lượt mới</div>
                  )}
                </div>
              </div>

              <div className="qz-intro-notice" role="status">
                <span style={{ fontSize: '1.25rem' }}>ℹ️</span>
                <div>
                  {quiz.is_preview
                    ? 'Bạn đang làm thử. Hệ thống không ghi nhận lượt làm hoặc lưu điểm của bạn.'
                    : !quiz.can_attempt
                      ? 'Bạn chưa có quyền làm quiz này. Học viên cần đăng ký khóa học; giảng viên chỉ làm thử quiz của khóa mình phụ trách.'
                      : !quiz.question_count
                        ? 'Quiz chưa có câu hỏi. Vui lòng quay lại sau.'
                        : inProgress
                          ? `Bạn có một lượt đang làm dở${introRemaining !== null ? `, còn ${formatClock(introRemaining)}` : ''}. Bấm “Tiếp tục làm bài” để khôi phục bài trong cùng phiên trình duyệt. Thời gian vẫn chạy khi rời trang; tiếp tục không tốn lượt mới.`
                          : exhausted
                            ? 'Bạn đã dùng hết lượt làm cho quiz này.'
                            : `Chỉ khi bấm “Bắt đầu làm bài”, hệ thống mới ghi nhận một lượt${quiz.duration ? ' và bắt đầu đếm giờ. Hết giờ, bài được tự động nộp nếu trang làm bài đang mở' : ''}. Rời trang sau khi bắt đầu vẫn tính lượt đã dùng${quiz.duration ? ' và thời gian vẫn tiếp tục chạy' : ''}.`}
                </div>
              </div>

              <div className="qz-intro-actions">
                <Link to={backTo} className="s-btn s-btn-outline">
                  ← Quay lại
                </Link>

                <button
                  type="button"
                  className="qz-btn-start"
                  onClick={startAttempt}
                  disabled={starting || !quiz.can_attempt || !quiz.question_count || exhausted}
                >
                  {starting
                    ? 'Đang mở bài...'
                    : quiz.is_preview
                      ? 'Làm thử quiz'
                      : inProgress
                        ? 'Tiếp tục làm bài →'
                        : exhausted
                          ? 'Đã hết lượt làm'
                          : 'Bắt đầu làm bài →'}
                </button>
              </div>
            </section>
          )}
        </div>
      )}
    </main>
  );
}
