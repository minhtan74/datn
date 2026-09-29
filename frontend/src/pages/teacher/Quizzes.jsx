import { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { courseService } from '../../services/courseService';
import { quizService } from '../../services/quizService';
import Modal from '../../components/common/Modal.jsx';
import AiQuizGenerator from './AiQuizGenerator.jsx';
import WordQuizImport from './WordQuizImport.jsx';
import { GRADING_METHODS, gradingShort } from '../../utils/quizGrading';

// Giá trị rỗng của form quiz; để trống thời gian / điểm đạt / số lần làm = không giới hạn
const emptyForm = {
  course_id: '', title: '', description: '', duration: '', passing_score: '', max_attempts: '', grading_method: 'highest',
};
// Chuyển giá trị ô nhập sang số gửi lên API ('' -> null = không giới hạn)
const numOrNull = (v) => (v === '' || v === null || v === undefined ? null : Number(v));

/** Nhóm 3 ô cài đặt làm bài: thời gian, điểm đạt, số lần làm tối đa */
function QuizSettingsFields({ form, setForm }) {
  const fields = [
    { key: 'duration', label: 'Thời gian (phút)', max: 600 },
    { key: 'passing_score', label: 'Điểm đạt (%)', max: 100 },
    { key: 'max_attempts', label: 'Số lần làm tối đa', max: 100 },
  ];
  return (
    <>
      <div className="grid grid-3" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
        {fields.map((f) => (
          <div className="form-group" key={f.key}>
            <label className="form-label">{f.label}</label>
            <input
              type="number"
              className="form-control"
              min="0"
              max={f.max}
              placeholder="Không giới hạn"
              value={form[f.key]}
              onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
            />
          </div>
        ))}
      </div>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '-0.5rem' }}>
        Để trống hoặc 0 = không giới hạn thời gian / không xét đạt / làm lại không giới hạn.
      </p>
      {/* Học viên làm nhiều lượt thì lấy điểm lượt nào để tính điểm TB, đạt / chưa đạt, thống kê */}
      <div className="form-group">
        <label className="form-label">Cách tính điểm khi làm nhiều lượt</label>
        <select
          className="form-control"
          value={form.grading_method}
          disabled={Number(form.max_attempts) === 1}
          onChange={(e) => setForm({ ...form, grading_method: e.target.value })}
        >
          {GRADING_METHODS.map((m) => (
            <option key={m.key} value={m.key}>{m.label}</option>
          ))}
        </select>
        {Number(form.max_attempts) === 1 && (
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.25rem 0 0' }}>
            Chỉ cho làm 1 lần nên không cần chọn cách tính.
          </p>
        )}
      </div>
    </>
  );
}

/** Tương đương #quizzesView (view 5) của teacher/dashboard.html — CRUD quiz */
export default function TeacherQuizzes() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [teacherCourses, setTeacherCourses] = useState([]);
  const [quizzes, setQuizzes] = useState(null); // null = loading

  const [modalOpen, setModalOpen] = useState(false);
  // Bảng chọn cách tạo quiz mới: thủ công / nhập Word / sinh bằng AI
  const [chooseOpen, setChooseOpen] = useState(false);
  // Quiz đang sửa (null = đang tạo mới); cần cả object để biết quiz đã có lượt làm / là bộ ôn tập
  const [editingQuiz, setEditingQuiz] = useState(null);
  const editingId = editingQuiz?.id ?? null;
  const editingAttempts = editingQuiz?.attempt_count || 0;
  const editingIsReview = Boolean(editingQuiz?.chapter_id || editingQuiz?.review_lesson_id);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  // Tab đang mở: danh sách quiz / AI Quiz Generator (?tab=ai) / nhập từ Word (?tab=word) — giữ được khi tải lại
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = ['ai', 'word'].includes(searchParams.get('tab')) ? searchParams.get('tab') : 'list';
  // Chỉ dựng tab AI / Word lần đầu khi mở tới, sau đó giữ nguyên (ẩn đi) để không mất bản nháp khi chuyển tab
  const [aiMounted, setAiMounted] = useState(tab === 'ai');
  const [wordMounted, setWordMounted] = useState(tab === 'word');
  useEffect(() => {
    if (tab === 'ai') setAiMounted(true);
    if (tab === 'word') setWordMounted(true);
  }, [tab]);

  // Chuyển tab: về danh sách thì bỏ luôn các tham số chọn sẵn phạm vi của AI
  function switchTab(next) {
    setSearchParams(next === 'list' ? {} : { tab: next });
  }

  // AI / nhập Word lưu xong quiz mới -> quay về danh sách và tải lại để thấy quiz vừa tạo
  function handleAiSaved() {
    switchTab('list');
    loadQuizzes();
  }

  // Tải các khóa học của giảng viên (để chọn khóa khi tạo quiz)
  async function loadCourses() {
    const res = await courseService.getCourses();
    const allCourses = res?.ok ? res.data.data || [] : [];
    setTeacherCourses(allCourses.filter((c) => c.teacher_id === user?.id || user?.role === 'admin'));
  }

  // Tải danh sách quiz (backend tự lọc: giảng viên chỉ thấy quiz khóa của mình)
  async function loadQuizzes() {
    setQuizzes(null);
    const res = await quizService.getQuizzes();
    setQuizzes(res?.ok ? res.data.data || [] : []);
  }

  useEffect(() => {
    loadCourses();
    loadQuizzes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Mở form thêm quiz, chọn sẵn khóa học đầu tiên
  function openCreateModal() {
    setEditingQuiz(null);
    setForm({ ...emptyForm, course_id: teacherCourses.length > 0 ? String(teacherCourses[0].id) : '' });
    setModalOpen(true);
  }

  // Mở form sửa với dữ liệu quiz hiện tại
  function openEditModal(q) {
    setEditingQuiz(q);
    setForm({
      course_id: String(q.course_id),
      title: q.title || '',
      description: q.description || '',
      duration: q.duration ?? '',
      passing_score: q.passing_score ?? '',
      max_attempts: q.max_attempts ?? '',
      grading_method: q.grading_method || 'highest',
    });
    setModalOpen(true);
  }

  // Lưu quiz: có editingId thì cập nhật, không thì tạo mới
  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    const payload = {
      course_id: Number(form.course_id),
      title: form.title.trim(),
      description: form.description.trim(),
      duration: numOrNull(form.duration),
      passing_score: numOrNull(form.passing_score),
      max_attempts: numOrNull(form.max_attempts),
      grading_method: form.grading_method,
    };
    const res = editingId
      ? await quizService.updateQuiz({ id: Number(editingId), ...payload })
      : await quizService.createQuiz(payload);
    setSaving(false);

    if (res?.ok && res.data?.success) {
      setModalOpen(false);
      // Tạo mới: chuyển thẳng tới trang soạn câu hỏi (quiz chưa có câu hỏi thì học viên chưa nhìn thấy)
      if (!editingId && res.data.id) {
        showToast('Tạo đề thi thành công! Hãy thêm câu hỏi cho đề.', 'success');
        navigate(`/teacher/quizzes/${res.data.id}/questions`);
        return;
      }
      showToast(editingId ? 'Cập nhật đề thi thành công!' : 'Tạo đề thi thành công!', 'success');
      loadQuizzes();
    } else {
      showToast(res?.data?.message || 'Có lỗi xảy ra.', 'error');
    }
  }

  // Xóa quiz (backend từ chối nếu đã có học viên làm bài)
  async function handleDelete(id) {
    if (
      !window.confirm(
        'Xóa đề thi này cùng tất cả câu hỏi?\n(Quiz đã có học viên làm bài sẽ không xóa được, để giữ điểm và dữ liệu phân tích.)',
      )
    )
      return;
    const res = await quizService.deleteQuiz(id);
    if (res?.ok) {
      showToast('Đã xóa Quiz thành công!', 'success');
      loadQuizzes();
    } else {
      showToast(res?.data?.message || 'Không thể xóa.', 'error');
    }
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">📝 Bài thi Trắc nghiệm</h1>
        <p className="page-subtitle">Biên soạn đề thi, theo dõi kết quả tự động.</p>
      </div>

      {/* Đang ở màn AI / Word (mở từ bảng chọn "+ Tạo Quiz mới") -> chỉ hiện nút quay lại danh sách */}
      {tab !== 'list' && (
        <button
          type="button"
          className="btn btn-ghost btn-sm"
          style={{ marginBottom: '1rem' }}
          onClick={() => switchTab('list')}
        >
          ← Quay lại danh sách
        </button>
      )}

      {/* AI Quiz Generator: giữ trong DOM sau lần mở đầu để bản nháp không bị mất */}
      {aiMounted && (
        <div hidden={tab !== 'ai'}>
          <AiQuizGenerator embedded onSaved={handleAiSaved} />
        </div>
      )}

      {/* Nhập bộ đề từ file Word */}
      {wordMounted && (
        <div hidden={tab !== 'word'}>
          <WordQuizImport onSaved={handleAiSaved} />
        </div>
      )}

      <div hidden={tab !== 'list'}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', gap: '0.5rem', flexWrap: 'wrap' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>📝 Quản lý Quiz trắc nghiệm</h3>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {/* Chưa có khóa học thì chưa tạo được quiz (quiz luôn thuộc 1 khóa) */}
          <button
            className="btn btn-primary"
            onClick={() => setChooseOpen(true)}
            disabled={teacherCourses.length === 0}
            title={teacherCourses.length === 0 ? 'Bạn cần tạo khóa học trước khi tạo quiz.' : undefined}
          >
            + Tạo Quiz mới
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-body" style={{ padding: 0 }}>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Khóa học</th>
                  <th>Tên Quiz</th>
                  <th>Số câu hỏi</th>
                  <th>Thời gian</th>
                  <th>Điểm đạt</th>
                  <th>Lượt làm</th>
                  <th style={{ textAlign: 'right' }}>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {quizzes === null && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: '2rem' }}>
                      <span
                        className="spinner"
                        style={{ width: 20, height: 20, border: '2px solid rgba(255,255,255,.3)', borderTopColor: 'var(--primary)' }}
                      ></span>{' '}
                      Đang tải danh sách Quiz...
                    </td>
                  </tr>
                )}
                {quizzes !== null && quizzes.length === 0 && (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                      Hệ thống chưa có đề thi trắc nghiệm. Bấm Tạo Quiz mới để tự biên soạn, hoặc Tạo bằng AI để AI sinh câu hỏi.
                    </td>
                  </tr>
                )}
                {quizzes?.map((q) => (
                  <tr key={q.id}>
                    <td>
                      <strong>{q.course_title || 'Chưa phân loại'}</strong>
                    </td>
                    <td>
                      <strong>{q.title}</strong>
                      {(q.chapter_id || q.review_lesson_id) && (
                        <span className="badge badge-primary" style={{ marginLeft: '0.5rem', fontSize: '0.65rem' }}>
                          {q.chapter_id ? 'Ôn tập chương' : 'Ôn tập bài'}
                        </span>
                      )}
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{q.description || '—'}</div>
                    </td>
                    <td>
                      <span className="badge badge-primary">{q.question_count || 0} câu hỏi</span>
                      {/* Quiz rỗng bị ẩn khỏi danh sách của học viên cho tới khi có câu hỏi */}
                      {!q.question_count && (
                        <div style={{ fontSize: '0.7rem', color: 'var(--warning, #D97706)', marginTop: '0.25rem' }}>
                          Chưa hiện cho học viên
                        </div>
                      )}
                    </td>
                    <td>{q.duration ? `${q.duration} phút` : 'Không giới hạn'}</td>
                    <td>{q.passing_score ? `${q.passing_score}%` : '—'}</td>
                    <td>
                      {q.max_attempts ? `${q.max_attempts} lần` : 'Không giới hạn'}
                      {q.max_attempts !== 1 && (
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Tính điểm: {gradingShort(q.grading_method)}</div>
                      )}
                      {q.attempt_count > 0 && (
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Đã có {q.attempt_count} lượt làm</div>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <div style={{ display: 'inline-flex', gap: '0.25rem', justifyContent: 'flex-end', alignItems: 'center' }}>
                        <Link
                          className="btn btn-outline btn-sm"
                          style={{ padding: '0.25rem 0.5rem' }}
                          to={`/teacher/quizzes/${q.id}/questions`}
                        >
                          Câu hỏi
                        </Link>
                        <button className="btn btn-ghost btn-sm" style={{ padding: '0.25rem 0.5rem' }} onClick={() => openEditModal(q)}>
                          ✏️
                        </button>
                        <button className="btn btn-ghost btn-sm" style={{ padding: '0.25rem 0.5rem', color: 'var(--danger)' }} onClick={() => handleDelete(q.id)}>
                          ✕
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      </div>

      {/* Chọn cách tạo quiz mới: thủ công / nhập Word / sinh bằng AI */}
      <Modal open={chooseOpen} onClose={() => setChooseOpen(false)}>
        <div
          className="card modal-panel"
          style={{ width: '100%', maxWidth: 420, margin: '1.5rem', animation: 'modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="card-header">
            <h3>Tạo Quiz mới bằng cách nào?</h3>
            <button className="btn-icon" onClick={() => setChooseOpen(false)}>
              ✕
            </button>
          </div>
          <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <button
              type="button"
              className="btn btn-outline"
              style={{ justifyContent: 'flex-start', textAlign: 'left', padding: '0.85rem 1rem' }}
              onClick={() => {
                setChooseOpen(false);
                openCreateModal();
              }}
            >
              ✍️ <strong style={{ marginLeft: '0.5rem' }}>Tạo thủ công</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Tự đặt tiêu đề, cài đặt làm bài rồi tự soạn từng câu hỏi.
              </div>
            </button>
            <button
              type="button"
              className="btn btn-outline"
              style={{ justifyContent: 'flex-start', textAlign: 'left', padding: '0.85rem 1rem' }}
              onClick={() => {
                setChooseOpen(false);
                switchTab('word');
              }}
            >
              📄 <strong style={{ marginLeft: '0.5rem' }}>Nhập từ file Word</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Tải lên file .docx đã soạn sẵn câu hỏi theo mẫu.
              </div>
            </button>
            <button
              type="button"
              className="btn btn-outline"
              style={{ justifyContent: 'flex-start', textAlign: 'left', padding: '0.85rem 1rem' }}
              onClick={() => {
                setChooseOpen(false);
                switchTab('ai');
              }}
            >
              ✨ <strong style={{ marginLeft: '0.5rem' }}>Tạo bằng AI</strong>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                AI sinh câu hỏi từ tài liệu khóa học, bạn chỉnh sửa & duyệt trước khi lưu.
              </div>
            </button>
          </div>
        </div>
      </Modal>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <div
          className="card modal-panel"
          style={{ width: '100%', maxWidth: 460, margin: '1.5rem', animation: 'modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="card-header">
            <h3>{editingId ? 'Chỉnh sửa đề thi' : 'Tạo bài thi Quiz'}</h3>
            <button className="btn-icon" onClick={() => setModalOpen(false)}>
              ✕
            </button>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              {/* Quiz đã có lượt làm: đổi cài đặt chỉ áp dụng cho các lượt sau, kết quả cũ giữ nguyên */}
              {editingAttempts > 0 && (
                <div className="alert alert-warning" style={{ fontSize: '0.8rem', marginBottom: '1rem' }}>
                  ⚠️ Quiz đã có <strong>{editingAttempts}</strong> lượt làm bài. Thay đổi thời gian / điểm đạt / số lượt chỉ áp dụng
                  cho các lượt làm sau — kết quả đạt / chưa đạt của các lượt cũ được giữ nguyên.
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Thuộc khóa học</label>
                {/* Không cho chuyển khóa khi quiz đã có lượt làm (điểm sẽ tính nhầm sang khóa mới) hoặc là bộ ôn tập */}
                <select
                  className="form-control"
                  required
                  value={form.course_id}
                  disabled={editingAttempts > 0 || editingIsReview}
                  onChange={(e) => setForm({ ...form, course_id: e.target.value })}
                >
                  {teacherCourses.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.title}
                    </option>
                  ))}
                </select>
                {(editingAttempts > 0 || editingIsReview) && (
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.25rem 0 0' }}>
                    {editingIsReview
                      ? 'Bộ câu hỏi ôn tập gắn với chương / bài học nên không đổi được khóa học.'
                      : 'Quiz đã có lượt làm bài nên không đổi được khóa học.'}
                  </p>
                )}
              </div>
              <div className="form-group">
                <label className="form-label">Tiêu đề Quiz</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  maxLength={255}
                  placeholder="Kiểm tra kiến thức Chương 1"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Mô tả ngắn</label>
                <textarea
                  className="form-control"
                  rows={2}
                  placeholder="Giới thiệu nội dung bài test..."
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <QuizSettingsFields form={form} setForm={setForm} />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setModalOpen(false)}>
                  Hủy
                </button>
                <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>
                  Lưu lại
                </button>
              </div>
            </form>
          </div>
        </div>
      </Modal>

    </>
  );
}
