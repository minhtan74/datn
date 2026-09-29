import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { courseService } from '../../services/courseService';
import { chapterService } from '../../services/chapterService';
import { lessonService } from '../../services/lessonService';
import Modal from '../../components/common/Modal.jsx';
import LessonPreviewModal from '../../components/teacher/LessonPreviewModal.jsx';

const emptyForm = { chapter_name: '', order_index: 0 };

/**
 * Tương đương #chaptersView (view 3) của teacher/dashboard.html — tree view
 * Course -> Chapter -> Lesson, CRUD chương học.
 *
 * Đọc `?course_id=` từ query string để auto-chọn khóa học — thay cho dance
 * "hash '#chapters' + setTimeout 150ms + gán select.value" của bản gốc
 * (được kích hoạt khi điều hướng chéo trang từ courses.html cũ / nút "Quản lý").
 */
export default function TeacherChapters() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [teacherCourses, setTeacherCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [chapters, setChapters] = useState(null); // null = loading / chưa chọn khóa học
  const [lessonsByChapter, setLessonsByChapter] = useState({});

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const [previewLesson, setPreviewLesson] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  // Load danh sách khóa học của giảng viên, rồi auto-chọn theo ?course_id= nếu có
  useEffect(() => {
    let cancelled = false;
    async function loadCourses() {
      const res = await courseService.getCourses();
      const allCourses = res?.ok ? res.data.data || [] : [];
      const mine = allCourses.filter((c) => c.teacher_id === user?.id || user?.role === 'admin');
      if (cancelled) return;
      setTeacherCourses(mine);

      // Bản gốc populateCourseDropdowns() đổ toàn bộ <option> (không có option rỗng)
      // nên trình duyệt tự chọn option đầu tiên rồi bắn onChapterCourseChange() ngay —
      // giữ đúng hành vi: mặc định chọn khóa học đầu tiên nếu không có ?course_id=.
      const courseIdParam = searchParams.get('course_id');
      if (courseIdParam && mine.some((c) => String(c.id) === String(courseIdParam))) {
        setSelectedCourseId(String(courseIdParam));
      } else if (mine.length > 0) {
        setSelectedCourseId(String(mine[0].id));
      }
    }
    loadCourses();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Tải các chương của khóa học kèm danh sách bài học trong từng chương
  async function loadChapters(courseId) {
    if (!courseId) {
      setChapters(null);
      return;
    }
    setChapters(null);
    const chapRes = await chapterService.getChapters(Number(courseId));
    const chapterList = chapRes?.ok ? chapRes.data.data || [] : [];

    if (!chapterList.length) {
      setChapters([]);
      setLessonsByChapter({});
      return;
    }

    const lessonsResults = await Promise.all(chapterList.map((ch) => lessonService.getLessons(ch.id)));
    const map = {};
    chapterList.forEach((ch, idx) => {
      map[ch.id] = lessonsResults[idx]?.ok ? lessonsResults[idx].data.data || [] : [];
    });
    setLessonsByChapter(map);
    setChapters(chapterList);
  }

  // Đổi khóa học -> tải lại danh sách chương
  useEffect(() => {
    loadChapters(selectedCourseId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCourseId]);

  // Mở form thêm chương
  function openCreateModal() {
    if (!selectedCourseId) {
      showToast('Vui lòng chọn khóa học trước!', 'error');
      return;
    }
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  // Mở form sửa tên / thứ tự chương
  function openEditModal(ch) {
    setEditingId(ch.id);
    setForm({ chapter_name: ch.chapter_name || '', order_index: ch.order_index ?? 0 });
    setModalOpen(true);
  }

  // Lưu chương: có id thì cập nhật, không thì tạo mới
  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    const payload = {
      course_id: Number(selectedCourseId),
      chapter_name: form.chapter_name.trim(),
      order_index: Number(form.order_index || 0),
    };
    const res = editingId
      ? await chapterService.updateChapter({ id: Number(editingId), ...payload })
      : await chapterService.createChapter(payload);
    setSaving(false);

    if (res?.ok && res.data?.success) {
      showToast(editingId ? 'Cập nhật chương học thành công!' : 'Tạo chương học thành công!', 'success');
      setModalOpen(false);
      loadChapters(selectedCourseId);
    } else {
      showToast(res?.data?.message || 'Có lỗi xảy ra.', 'error');
    }
  }

  // Xóa chương (các bài học bên trong bị xóa theo)
  async function handleDelete(id) {
    if (!window.confirm('Xóa chương này sẽ xóa toàn bộ bài học bên trong. Bạn chắc chắn?')) return;
    const res = await chapterService.deleteChapter(id);
    if (res?.ok) {
      showToast('Đã xóa chương học!', 'success');
      loadChapters(selectedCourseId);
    } else {
      showToast(res?.data?.message || 'Không thể xóa.', 'error');
    }
  }

  // Mở bộ câu hỏi ôn tập của chương (chưa có thì tạo) rồi chuyển sang trang quản lý câu hỏi
  async function handleOpenReview(ch) {
    const res = await chapterService.openReview(ch.id);
    const quizId = res?.ok ? res.data?.data?.quiz_id : null;
    if (!quizId) {
      showToast(res?.data?.message || 'Không mở được bộ câu hỏi ôn tập.', 'error');
      return;
    }
    navigate(`/teacher/quizzes/${quizId}/questions`);
  }

  // Mở bộ câu hỏi ôn tập theo kiến thức của 1 bài học rồi chuyển sang trang quản lý câu hỏi
  async function handleOpenLessonReview(lesson) {
    const res = await lessonService.openReview(lesson.id);
    const quizId = res?.ok ? res.data?.data?.quiz_id : null;
    if (!quizId) {
      showToast(res?.data?.message || 'Không mở được bộ câu hỏi ôn tập.', 'error');
      return;
    }
    navigate(`/teacher/quizzes/${quizId}/questions`);
  }

  // Xem trước 1 bài học trong hộp thoại
  async function handlePreviewLesson(id) {
    const res = await lessonService.getLesson(id);
    const lesson = res?.ok ? res.data.data : null;
    if (!lesson) {
      showToast('Không tìm thấy thông tin bài học', 'error');
      return;
    }
    setPreviewLesson(lesson);
    setPreviewOpen(true);
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">📖 Quản lý Chương học</h1>
        <p className="page-subtitle">Xây dựng cấu trúc cây chương trình giảng dạy.</p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-body" style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 250 }}>
            <label className="form-label" style={{ marginBottom: '0.25rem' }}>
              Chọn khóa học cần quản lý chương:
            </label>
            <select className="form-control" value={selectedCourseId} onChange={(e) => setSelectedCourseId(e.target.value)}>
              {teacherCourses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" style={{ marginTop: '1.25rem' }} onClick={openCreateModal}>
            + Thêm Chương mới
          </button>
        </div>
      </div>

      {!selectedCourseId && (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Vui lòng chọn khóa học để hiển thị.
        </div>
      )}

      {selectedCourseId && chapters === null && (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <span
            className="spinner"
            style={{ width: 20, height: 20, border: '2px solid rgba(255,255,255,.3)', borderTopColor: 'var(--primary)' }}
          ></span>{' '}
          Đang tải chương học...
        </div>
      )}

      {selectedCourseId && chapters !== null && chapters.length === 0 && (
        <div className="card" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📂</div>
          <h3>Khóa học chưa có chương giảng dạy</h3>
          <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Hãy bấm nút Thêm Chương phía trên để thiết lập đề cương học tập.
          </p>
        </div>
      )}

      {selectedCourseId &&
        chapters !== null &&
        chapters.length > 0 &&
        chapters.map((ch, idx) => {
          const lessons = lessonsByChapter[ch.id] || [];
          return (
            <div className="tree-chapter" key={ch.id}>
              <div className="tree-chapter-header">
                <div className="tree-chapter-title">
                  <span>📁</span>
                  <span>{ch.chapter_name}</span>
                  <span className="badge badge-primary" style={{ fontSize: '0.65rem' }}>
                    {lessons.length} Bài giảng
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }} onClick={(e) => e.stopPropagation()}>
                  <button className="btn btn-outline btn-sm" onClick={() => handleOpenReview(ch)}>
                    📝 Câu hỏi ôn tập ({ch.review_question_count || 0})
                  </button>
                  <button className="btn btn-ghost btn-sm" onClick={() => openEditModal(ch)}>
                    ✏️ Sửa
                  </button>
                  <button className="btn btn-ghost btn-sm" style={{ color: 'var(--danger)' }} onClick={() => handleDelete(ch.id)}>
                    ✕ Xóa
                  </button>
                </div>
              </div>
              <div className="tree-lessons-list">
                {lessons.length > 0 ? (
                  lessons.map((l, i) => (
                    <div className="tree-lesson-item" key={l.id}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ color: 'var(--text-muted)' }}>🎥 Bài {i + 1}:</span>
                        <strong>{l.title}</strong>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button className="btn btn-outline btn-sm" onClick={() => handleOpenLessonReview(l)}>
                          📝 Ôn tập ({l.review_question_count || 0})
                        </button>
                        <button className="btn btn-ghost btn-sm" onClick={() => handlePreviewLesson(l.id)}>
                          👀 Xem trước
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '0.5rem 1rem' }}>
                    Chưa có bài học trong chương này.
                  </p>
                )}
              </div>
            </div>
          );
        })}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <div
          className="card modal-panel"
          style={{ width: '100%', maxWidth: 440, margin: '1.5rem', animation: 'modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="card-header">
            <h3>{editingId ? 'Sửa chương học' : 'Thêm chương học'}</h3>
            <button className="btn-icon" onClick={() => setModalOpen(false)}>
              ✕
            </button>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Tên chương học</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  placeholder="Chương 1: Giới thiệu căn bản"
                  value={form.chapter_name}
                  onChange={(e) => setForm({ ...form, chapter_name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Số thứ tự hiển thị</label>
                <input
                  type="number"
                  className="form-control"
                  value={form.order_index}
                  onChange={(e) => setForm({ ...form, order_index: e.target.value })}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setModalOpen(false)}>
                  Hủy
                </button>
                <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>
                  Lưu chương
                </button>
              </div>
            </form>
          </div>
        </div>
      </Modal>

      <LessonPreviewModal open={previewOpen} onClose={() => setPreviewOpen(false)} lesson={previewLesson} />
    </>
  );
}
