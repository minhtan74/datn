import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import Modal from '../../components/common/Modal.jsx';
import { uploadFile } from '../../services/uploadService';
import CourseThumb from '../../components/common/CourseThumb.jsx';

const emptyForm = { title: '', description: '', thumbnail: '', price: '', status: 'published' };

// Tên tiếng Việt của trạng thái khóa học
const STATUS_LABELS = { published: 'Đã xuất bản', draft: 'Bản nháp', archived: 'Lưu trữ' };

/** Tương đương #coursesView (view 2) của teacher/dashboard.html — CRUD khóa học của giảng viên */
export default function TeacherCourses() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [teacherCourses, setTeacherCourses] = useState([]);
  const [enrollments, setEnrollments] = useState([]);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [thumbUploading, setThumbUploading] = useState(false);
  const [thumbPct, setThumbPct] = useState(0);

  // Tải ảnh bìa khóa học lên server (hiện % tiến trình), xong thì điền URL ảnh vào form
  async function handleThumbUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = '';
    setThumbUploading(true);
    setThumbPct(0);
    try {
      const res = await uploadFile(file, 'image', (pct) => setThumbPct(pct));
      if (res?.data?.success && res.data?.url) {
        setForm((prev) => ({ ...prev, thumbnail: res.data.url }));
        showToast('Upload ảnh thành công!', 'success');
      } else {
        showToast(res?.data?.message || 'Upload thất bại.', 'error');
      }
    } catch {
      showToast('Lỗi kết nối khi upload ảnh.', 'error');
    } finally {
      setThumbUploading(false);
      setThumbPct(0);
    }
  }

  // Tải khóa học của giảng viên (admin thấy tất cả) + danh sách ghi danh để đếm học viên mỗi khóa
  async function loadData() {
    setLoading(true);
    const [coursesRes, enrollRes] = await Promise.all([courseService.getCourses(), enrollmentService.getEnrollments()]);
    const allCourses = coursesRes?.ok ? coursesRes.data.data || [] : [];
    setTeacherCourses(allCourses.filter((c) => c.teacher_id === user?.id || user?.role === 'admin'));
    setEnrollments(enrollRes?.ok ? enrollRes.data.data || [] : []);
    setLoading(false);
  }

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Lọc khóa học theo ô tìm kiếm
  const filteredCourses = useMemo(() => {
    let list = teacherCourses;
    const q = search.toLowerCase().trim();
    if (q) list = list.filter((c) => c.title.toLowerCase().includes(q));
    if (statusFilter !== 'all') list = list.filter((c) => c.status === statusFilter);
    return list;
  }, [teacherCourses, search, statusFilter]);

  // Mở form thêm khóa học
  function openCreateModal() {
    setEditingId(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  // Mở form sửa với dữ liệu khóa học hiện tại
  function openEditModal(c) {
    setEditingId(c.id);
    setForm({
      title: c.title || '',
      description: c.description || '',
      thumbnail: c.thumbnail || '',
      price: c.price ?? 0,
      status: c.status || 'published',
    });
    setModalOpen(true);
  }

  // Lưu khóa học: có id thì cập nhật, không thì tạo mới
  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      thumbnail: form.thumbnail.trim(),
      price: Number(form.price || 0),
      status: form.status,
    };
    const res = editingId
      ? await courseService.updateCourse({ id: Number(editingId), ...payload })
      : await courseService.createCourse(payload);
    setSaving(false);

    if (res?.ok && res.data?.success) {
      showToast(editingId ? 'Cập nhật khóa học thành công!' : 'Tạo khóa học thành công!', 'success');
      setModalOpen(false);
      loadData();
    } else {
      showToast(res?.data?.message || 'Lỗi thao tác.', 'error');
    }
  }

  // Xóa khóa học (backend từ chối nếu đã có học viên / giao dịch)
  async function handleDelete(id) {
    if (
      !window.confirm(
        'Xóa vĩnh viễn khóa học này cùng toàn bộ chương và bài học?\n' +
          '(Khóa đã có học viên hoặc giao dịch sẽ không xóa được — hãy chuyển sang "Lưu trữ".)',
      )
    )
      return;
    const res = await courseService.deleteCourse(id);
    if (res?.ok) {
      showToast('Xóa khóa học thành công!', 'success');
      loadData();
    } else {
      showToast(res?.data?.message || 'Không thể xóa khóa học.', 'error');
    }
  }

  // Chuyển sang trang quản lý chương của khóa học
  function manageCourseChapters(courseId) {
    navigate(`/teacher/chapters?course_id=${courseId}`);
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">📚 Khóa học của tôi</h1>
        <p className="page-subtitle">Quản lý thông tin chi tiết, trạng thái kích hoạt khóa học.</p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', flex: '1 1 320px', maxWidth: 500, flexWrap: 'wrap' }}>
          <input
            type="text"
            className="form-control"
            style={{ flex: '1 1 200px', minWidth: 0 }}
            placeholder="Tìm tên khóa học..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="form-control"
            style={{ flex: '0 1 180px', minWidth: 150 }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="published">Đã xuất bản</option>
            <option value="draft">Bản nháp</option>
            <option value="archived">Lưu trữ</option>
          </select>
        </div>
        <button className="btn btn-primary" onClick={openCreateModal}>
          + Thêm Khóa học
        </button>
      </div>

      {loading ? (
        <div className="loading-page">
          <div className="spinner" />
        </div>
      ) : (
        <div className="course-card-grid">
          {filteredCourses.length === 0 && (
            <div className="card" style={{ gridColumn: '1/-1', padding: '3rem', textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📚</div>
              <h3>Không tìm thấy khóa học nào</h3>
            </div>
          )}
          {filteredCourses.map((c) => {
            const studentCount = enrollments.filter((e) => e.course_id === c.id).length;
            const courseEnrolled = enrollments.filter((e) => e.course_id === c.id);
            const avgProgress =
              courseEnrolled.length > 0
                ? Math.round(
                    courseEnrolled.reduce((sum, e) => {
                      const total = Number(e.total_lessons || 0);
                      const completed = Number(e.completed_lessons || 0);
                      return sum + (total > 0 ? (completed / total) * 100 : 0);
                    }, 0) / courseEnrolled.length,
                  )
                : 0;

            return (
              <div className="course-dash-card" key={c.id}>
                <div className="course-dash-thumb">
                  <CourseThumb src={c.thumbnail} fallback="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=320&auto=format&fit=crop" alt={c.title} />
                  <span className="course-dash-badge">{STATUS_LABELS[c.status] || c.status}</span>
                </div>
                <div className="course-dash-body">
                  <h3 className="course-dash-title">{c.title}</h3>
                  <p className="course-dash-desc">{c.description || 'Chưa có mô tả ngắn...'}</p>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.75rem' }}>
                    {Number(c.price || 0).toLocaleString()} VNĐ
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span>Tiến độ học viên TB</span>
                    <span>{avgProgress}%</span>
                  </div>
                  <div className="course-progress-bar" style={{ marginTop: 0 }}>
                    <div className="course-progress-fill" style={{ width: `${avgProgress}%` }}></div>
                  </div>

                  <div className="course-dash-meta">
                    <span>👥 {studentCount} Học viên</span>
                    <div style={{ display: 'flex', gap: '0.25rem' }}>
                      <button className="btn btn-outline btn-sm" style={{ padding: '0.25rem 0.5rem' }} onClick={() => manageCourseChapters(c.id)}>
                        Quản lý
                      </button>
                      <button className="btn btn-ghost btn-sm" style={{ padding: '0.25rem 0.5rem' }} onClick={() => openEditModal(c)}>
                        ✏️
                      </button>
                      <button
                        className="btn btn-ghost btn-sm"
                        style={{ padding: '0.25rem 0.5rem', color: 'var(--danger)' }}
                        onClick={() => handleDelete(c.id)}
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <div
          className="card modal-panel"
          style={{ width: '100%', maxWidth: 480, margin: '1.5rem', animation: 'modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="card-header">
            <h3>{editingId ? 'Chỉnh sửa khóa học' : 'Tạo khóa học mới'}</h3>
            <button className="btn-icon" onClick={() => setModalOpen(false)}>
              ✕
            </button>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Tên khóa học</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  placeholder="Lập trình React JS nâng cao"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Mô tả ngắn</label>
                <textarea
                  className="form-control"
                  rows={3}
                  required
                  placeholder="Mô tả tóm tắt nội dung..."
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Thumbnail URL</label>
                {/* Preview */}
                {form.thumbnail && (
                  <div style={{ marginBottom: '0.5rem', borderRadius: 8, overflow: 'hidden', height: 100, background: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <img src={form.thumbnail} alt="preview" style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'cover', width: '100%' }} />
                  </div>
                )}
                <input
                  type="text"
                  className="form-control"
                  placeholder="https://images.unsplash.com/..."
                  value={form.thumbnail}
                  onChange={(e) => setForm({ ...form, thumbnail: e.target.value })}
                />
                {/* Upload từ máy */}
                <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <label
                    style={{
                      display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
                      padding: '0.3rem 0.75rem', borderRadius: 6, cursor: 'pointer',
                      background: 'var(--surface-2,#1e293b)', border: '1px solid var(--border,#334155)',
                      fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap',
                      opacity: thumbUploading ? 0.5 : 1,
                      pointerEvents: thumbUploading ? 'none' : 'auto',
                    }}
                  >
                    🖼️ Chọn ảnh từ máy
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/gif,image/webp"
                      style={{ display: 'none' }}
                      onChange={handleThumbUpload}
                    />
                  </label>
                  {thumbUploading && (
                    <div style={{ flex: 1, height: 6, background: 'var(--border,#334155)', borderRadius: 99, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${thumbPct}%`, background: 'var(--primary)', transition: 'width 0.2s' }} />
                    </div>
                  )}
                  {thumbUploading && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', flexShrink: 0 }}>{thumbPct}%</span>
                  )}
                </div>
              </div>
              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Giá bán (VNĐ)</label>
                  <input
                    type="number"
                    min="0"
                    className="form-control"
                    required
                    placeholder="0 = miễn phí"
                    value={form.price}
                    onChange={(e) => setForm({ ...form, price: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Trạng thái</label>
                  <select className="form-control" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                    <option value="published">Đã xuất bản — học viên thấy & đăng ký được</option>
                    <option value="draft">Bản nháp — chỉ bạn thấy</option>
                    <option value="archived">Lưu trữ — ngừng nhận học viên mới</option>
                  </select>
                </div>
              </div>
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
