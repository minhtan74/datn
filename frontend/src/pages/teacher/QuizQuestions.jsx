import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useToast } from '../../hooks/useToast';
import { quizService } from '../../services/quizService';
import Modal from '../../components/common/Modal.jsx';
import DifficultyBar from '../../components/common/DifficultyBar.jsx';
import RichText, { hasRichTokens } from '../../components/common/RichText.jsx';

// Giá trị rỗng của form câu hỏi (mặc định đáp án đúng là A)
const emptyForm = {
  content: '',
  option_a: '',
  option_b: '',
  option_c: '',
  option_d: '',
  correct_answer: 'A',
  order_index: 0,
  topic: '',
  difficulty: '',
  explanation: '',
};

// Tên tiếng Việt của mức độ khó
const DIFFICULTY_LABELS = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' };

/**
 * Port của _legacy/pages/teacher/quiz-questions.html + initQuizQuestions()
 * (_legacy/js/quiz.js, dòng 318-438).
 *
 * Bản gốc là 1 trang riêng dùng navbar public thông thường (không có sidebar
 * dashboard) và đọc `?quiz_id=` từ query string. Theo quyết định đã duyệt cho
 * bản React, trang này giờ nằm trong TeacherLayout như mọi trang teacher khác
 * và đọc `quizId` từ route param (`/teacher/quizzes/:quizId/questions`).
 */
export default function TeacherQuizQuestions() {
  const { quizId } = useParams();
  const { showToast } = useToast();

  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState(null); // null = loading

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  // Tải thông tin quiz (tiêu đề, chương nếu là bộ ôn tập) để hiển thị trên đầu trang
  useEffect(() => {
    let cancelled = false;
    async function loadQuiz() {
      const res = await quizService.getQuiz(Number(quizId));
      const data = res?.ok ? res.data.data : null;
      if (!cancelled && data) setQuiz(data);
    }
    loadQuiz();
    return () => {
      cancelled = true;
    };
  }, [quizId]);

  // Tải danh sách câu hỏi (chủ khóa học nhận kèm đáp án)
  async function loadQuestions() {
    setQuestions(null);
    const res = await quizService.getQuestions(Number(quizId));
    setQuestions(res?.ok ? res.data.data || [] : []);
  }

  // Đổi quiz -> tải lại câu hỏi
  useEffect(() => {
    loadQuestions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [quizId]);

  // Mở form thêm câu hỏi
  function openCreateModal() {
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  // Mở form sửa: tải chi tiết câu hỏi từ server rồi điền vào form
  async function openEditModal(id) {
    setEditingId(id);
    const res = await quizService.getQuestion(id);
    if (!res?.ok) return;
    const q = res.data.data;
    setForm({
      content: q.content || '',
      option_a: q.option_a || '',
      option_b: q.option_b || '',
      option_c: q.option_c || '',
      option_d: q.option_d || '',
      correct_answer: q.correct_answer || 'A',
      order_index: q.order_index ?? 0,
      topic: q.topic || '',
      difficulty: q.difficulty || '',
      explanation: q.explanation || '',
    });
    setModalOpen(true);
  }

  // Lưu câu hỏi: có editingId thì cập nhật, không thì thêm mới vào quiz
  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    const payload = {
      quiz_id: Number(quizId),
      content: form.content.trim(),
      option_a: form.option_a.trim(),
      option_b: form.option_b.trim(),
      option_c: form.option_c.trim(),
      option_d: form.option_d.trim(),
      correct_answer: form.correct_answer,
      order_index: Number(form.order_index || 0),
      topic: form.topic.trim(),
      difficulty: form.difficulty,
      explanation: form.explanation.trim(),
    };
    const res = editingId
      ? await quizService.updateQuestion({ id: editingId, ...payload })
      : await quizService.createQuestion(payload);
    setSaving(false);

    if (res?.ok && res.data?.success) {
      setModalOpen(false);
      showToast('Thành công!', 'success');
      loadQuestions();
    } else {
      showToast(res?.data?.message || 'Lỗi.', 'error');
    }
  }

  // Xóa câu hỏi (backend từ chối nếu đã có học viên trả lời)
  async function handleDelete(id) {
    if (!window.confirm('Xóa câu hỏi này? (Câu hỏi đã có học viên trả lời sẽ không xóa được.)')) return;
    const res = await quizService.deleteQuestion(id);
    if (res?.ok) {
      showToast('Đã xóa!', 'success');
      loadQuestions();
    } else {
      showToast(res?.data?.message || 'Không thể xóa câu hỏi.', 'error');
    }
  }

  // Bộ câu hỏi ôn tập của chương / bài học: breadcrumb quay về trang Chương, có nút sinh câu hỏi bằng AI
  const isReview = Boolean(quiz?.chapter_id || quiz?.review_lesson_id);
  const reviewName = quiz?.chapter_id ? quiz.chapter_name : `Bài: ${quiz?.review_lesson_title}`;
  const aiLink = quiz?.chapter_id
    ? `/teacher/quizzes?tab=ai&course_id=${quiz.course_id}&chapter_id=${quiz.chapter_id}`
    : `/teacher/quizzes?tab=ai&course_id=${quiz?.course_id}&lesson_id=${quiz?.review_lesson_id}`;

  return (
    <>
      <div className="breadcrumb">
        {isReview ? (
          <Link to={`/teacher/chapters?course_id=${quiz.course_id}`}>📖 Quản lý Chương</Link>
        ) : (
          <Link to="/teacher/quizzes">📚 Quản lý Quiz</Link>
        )}
        <span className="sep">›</span>
        <span>{quiz?.title || 'Câu hỏi'}</span>
      </div>

      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ fontSize: '1.6rem', fontWeight: 800 }}>
            {isReview ? `📝 Câu hỏi ôn tập — ${reviewName}` : '❓ Quản lý Câu hỏi'}
          </h1>
          <p className="page-subtitle" style={{ marginTop: '0.25rem', fontSize: '0.88rem' }}>
            {isReview
              ? `Học viên dùng bộ câu hỏi này để ôn lại kiến thức sau khi học xong ${quiz.chapter_id ? 'chương' : 'bài'}.`
              : 'Biên soạn nội dung trắc nghiệm và đáp án đúng cho bài kiểm tra.'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {isReview && (
            <Link
              className="btn btn-outline"
              style={{ padding: '0.6rem 1.25rem' }}
              to={aiLink}
            >
              ✨ Sinh bằng AI
            </Link>
          )}
          <button className="btn btn-primary" style={{ padding: '0.6rem 1.25rem' }} onClick={openCreateModal}>
            + Thêm câu hỏi mới
          </button>
        </div>
      </div>

      {questions === null && (
        <div className="loading-page">
          <div className="spinner" />
        </div>
      )}

      {questions !== null && questions.length === 0 && (
        <div className="empty-state">
          <div className="icon">❓</div>
          <h3>Chưa có câu hỏi nào</h3>
        </div>
      )}

      {/* Thống kê phân bổ độ khó của đề */}
      {questions !== null && <DifficultyBar questions={questions} />}

      {questions !== null &&
        questions.length > 0 &&
        questions.map((q, i) => (
          <div className="tq-question-card" key={q.id}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1.5rem', flexWrap: 'wrap' }}>
              <div style={{ flex: 1 }}>
                <div className="tq-question-num">
                  Câu hỏi {i + 1}
                  {q.topic ? ` · ${q.topic}` : ' · ⚠️ chưa gắn chủ đề'}
                  {q.difficulty ? ` · ${DIFFICULTY_LABELS[q.difficulty] || q.difficulty}` : ''}
                </div>
                <div className="tq-question-content" style={{ whiteSpace: 'pre-wrap' }}>
                  <RichText text={q.content} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.75rem', marginTop: '1.25rem' }}>
                  {['A', 'B', 'C', 'D'].map((k) => {
                    const text = q[`option_${k.toLowerCase()}`];
                    if (!text && (k === 'C' || k === 'D')) return null;
                    const isCorrect = k === q.correct_answer;
                    return (
                      <div className={`tq-option-item${isCorrect ? ' correct' : ''}`} key={k}>
                        <span className="tq-option-icon">{isCorrect ? '✅' : '⬜'}</span>
                        <span>
                          <strong>{k}.</strong> <RichText text={text} imgMaxHeight={140} />
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                <button className="btn btn-outline btn-sm" onClick={() => openEditModal(q.id)}>
                  ✏️ Sửa
                </button>
                <button className="btn btn-ghost btn-sm" style={{ color: 'var(--danger)' }} onClick={() => handleDelete(q.id)}>
                  ✕ Xóa
                </button>
              </div>
            </div>
          </div>
        ))}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <div className="tq-modal-box" onClick={(e) => e.stopPropagation()}>
          <div className="tq-modal-header">
            <h3>{editingId ? 'Sửa câu hỏi' : 'Thêm câu hỏi'}</h3>
            <button className="tq-modal-close" onClick={() => setModalOpen(false)}>
              ✕
            </button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">
                Nội dung câu hỏi <span style={{ color: 'var(--danger)' }}>*</span>
              </label>
              <textarea
                className="form-control"
                rows={3}
                placeholder="Nhập nội dung câu hỏi..."
                required
                style={{ resize: 'vertical', minHeight: 80 }}
                value={form.content}
                onChange={(e) => setForm({ ...form, content: e.target.value })}
              />
              {/* Câu nhập từ Word có ảnh / công thức: xem trước như học viên sẽ thấy */}
              {[form.content, form.option_a, form.option_b, form.option_c, form.option_d].some(hasRichTokens) && (
                <div
                  style={{
                    marginTop: '0.5rem', padding: '0.6rem 0.75rem', borderRadius: 8, fontSize: '0.9rem',
                    background: 'var(--primary-light, #eff6ff)', whiteSpace: 'pre-wrap',
                  }}
                >
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                    XEM TRƯỚC · ảnh [[img:…]] và công thức [[math:LaTeX]] được hiển thị cho học viên như sau
                  </div>
                  <RichText text={form.content} />
                  {['a', 'b', 'c', 'd'].filter((k) => form[`option_${k}`]).map((k) => (
                    <div key={k} style={{ marginTop: '0.25rem' }}>
                      <strong>{k.toUpperCase()}.</strong> <RichText text={form[`option_${k}`]} imgMaxHeight={120} />
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">
                  Đáp án A <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <input
                  className="form-control"
                  type="text"
                  placeholder="Nập đáp án A"
                  required
                  value={form.option_a}
                  onChange={(e) => setForm({ ...form, option_a: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">
                  Đáp án B <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <input
                  className="form-control"
                  type="text"
                  placeholder="Nhập đáp án B"
                  required
                  value={form.option_b}
                  onChange={(e) => setForm({ ...form, option_b: e.target.value })}
                />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Đáp án C</label>
                <input
                  className="form-control"
                  type="text"
                  placeholder="Nhập đáp án C (tùy chọn)"
                  value={form.option_c}
                  onChange={(e) => setForm({ ...form, option_c: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Đáp án D</label>
                <input
                  className="form-control"
                  type="text"
                  placeholder="Nhập đáp án D (tùy chọn)"
                  value={form.option_d}
                  onChange={(e) => setForm({ ...form, option_d: e.target.value })}
                />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">
                  Đáp án đúng <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <select
                  className="form-control"
                  required
                  value={form.correct_answer}
                  onChange={(e) => setForm({ ...form, correct_answer: e.target.value })}
                >
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Thứ tự hiển thị</label>
                <input
                  className="form-control"
                  type="number"
                  min="0"
                  value={form.order_index}
                  onChange={(e) => setForm({ ...form, order_index: e.target.value })}
                />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Chủ đề</label>
                <input
                  className="form-control"
                  type="text"
                  maxLength={100}
                  placeholder="VD: Hàm (Functions), DOM..."
                  value={form.topic}
                  onChange={(e) => setForm({ ...form, topic: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Độ khó</label>
                <select
                  className="form-control"
                  value={form.difficulty}
                  onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
                >
                  <option value="">— Chưa chọn —</option>
                  <option value="easy">Dễ</option>
                  <option value="medium">Trung bình</option>
                  <option value="hard">Khó</option>
                </select>
              </div>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '-0.5rem' }}>
              Chủ đề dùng cho trang Phân tích học tập và Gợi ý cá nhân hóa của học viên (điểm mạnh/yếu theo chủ đề).
            </p>

            <div className="form-group">
              <label className="form-label">Giải thích đáp án</label>
              <textarea
                className="form-control"
                rows={2}
                placeholder="Vì sao đáp án này đúng (tùy chọn)"
                value={form.explanation}
                onChange={(e) => setForm({ ...form, explanation: e.target.value })}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '2rem', borderTop: '1px solid var(--border)', paddingTop: '1.25rem' }}>
              <button type="button" className="btn btn-ghost" onClick={() => setModalOpen(false)}>
                Hủy bỏ
              </button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                Lưu câu hỏi
              </button>
            </div>
          </form>
        </div>
      </Modal>
    </>
  );
}
