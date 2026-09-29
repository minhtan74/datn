import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { courseService } from '../../services/courseService';
import { userService } from '../../services/userService';
import { useToast } from '../../hooks/useToast';
import Modal from '../../components/common/Modal.jsx';
import CourseThumb from '../../components/common/CourseThumb.jsx';

const emptyForm = { id: '', title: '', description: '', thumbnail: '', price: '0', status: 'published', teacher_id: '' };

// Nhãn và màu hiển thị cho từng trạng thái khóa học
const COURSE_STATUS = {
  published: { label: 'Đã xuất bản', cls: 'badge-success' },
  draft: { label: 'Bản nháp', cls: 'badge-warning' },
  archived: { label: 'Lưu trữ', cls: 'badge-info' },
};

// Định dạng giá kiểu Việt Nam (1.500.000 ₫), giá 0 hiển thị "Miễn phí"
function fmtPrice(p) {
  return +p > 0 ? Number(p).toLocaleString('vi-VN') + ' ₫' : 'Miễn phí';
}

/** Tương đương #coursesView trong _legacy/pages/admin/dashboard.html. */
export default function AdminCourses() {
  const { showToast } = useToast();
  const [allCourses, setAllCourses] = useState(null); // null = đang tải
  const [teachers, setTeachers] = useState([]);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const isEditing = !!form.id;

  // Tải danh sách khóa học (admin thấy tất cả mọi trạng thái)
  async function loadCourses() {
    const res = await courseService.getCourses();
    if (res?.ok && res.data?.success) {
      setAllCourses(res.data.data || []);
    } else {
      setAllCourses([]);
    }
  }

  // Khi mở trang: tải khóa học + danh sách giảng viên đang hoạt động (để chọn người phụ trách)
  useEffect(() => {
    loadCourses();
    userService.getUsers().then((res) => {
      if (res?.ok && res.data?.success) {
        setTeachers((res.data.data || []).filter((u) => u.role === 'teacher' && u.is_active));
      }
    });
  }, []);

  // Lọc khóa học theo ô tìm kiếm tên
  const filtered = useMemo(() => {
    let list = allCourses || [];
    const q = search.toLowerCase().trim();
    if (q) list = list.filter((c) => c.title.toLowerCase().includes(q));
    return list;
  }, [allCourses, search]);

  // Mở form thêm khóa học mới
  function openCreateModal() {
    setForm(emptyForm);
    setModalOpen(true);
  }

  // Mở form sửa với dữ liệu khóa học hiện tại
  function openEditModal(c) {
    setForm({
      id: c.id,
      title: c.title,
      description: c.description || '',
      thumbnail: c.thumbnail || '',
      price: String(Number(c.price || 0)),
      status: c.status || 'published',
      teacher_id: String(c.teacher_id || ''),
    });
    setModalOpen(true);
  }

  // Lưu form: có id thì cập nhật, không thì tạo mới; chỉ gửi teacher_id khi admin có chọn giảng viên
  async function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      thumbnail: form.thumbnail.trim(),
      price: Number(form.price || 0),
      status: form.status,
      ...(form.teacher_id ? { teacher_id: Number(form.teacher_id) } : {}),
    };

    try {
      const res = isEditing
        ? await courseService.updateCourse({ id: form.id, ...payload })
        : await courseService.createCourse(payload);

      if (res?.ok && res.data?.success) {
        showToast(res.data.message || 'Thực hiện thành công', 'success');
        setModalOpen(false);
        loadCourses();
      } else {
        showToast(res?.data?.message || 'Có lỗi xảy ra', 'error');
      }
    } catch {
      showToast('Lỗi máy chủ', 'error');
    }
  }

  // Xóa khóa học (backend từ chối nếu đã có học viên / giao dịch -> nên chuyển sang Lưu trữ)
  async function handleDelete(id) {
    if (
      !window.confirm(
        'Xóa vĩnh viễn khóa học này cùng toàn bộ chương, bài học, quiz?\n' +
          '(Khóa đã có học viên hoặc giao dịch sẽ không xóa được — hãy chuyển sang "Lưu trữ".)',
      )
    )
      return;
    try {
      const res = await courseService.deleteCourse(id);
      if (res?.ok && res.data?.success) {
        showToast('Xóa khóa học thành công!', 'success');
        loadCourses();
      } else {
        showToast(res?.data?.message || 'Có lỗi xảy ra', 'error');
      }
    } catch {
      showToast('Lỗi máy chủ', 'error');
    }
  }

  return (
    <>
      <div className="page-header">
        <div className="breadcrumb">
          <Link to="/admin">Admin</Link> / <span>Quản lý Khóa học</span>
        </div>
        <h1 className="page-title">📚 Quản lý Khóa học</h1>
        <p className="page-subtitle">Thiết lập danh sách khóa học giảng dạy.</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>📚 Quản lý Khóa học</h3>
          <button className="btn btn-primary btn-sm" onClick={openCreateModal}>
            + Thêm Khóa học
          </button>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            <input
              type="text"
              className="form-control"
              placeholder="Tìm tên khóa học..."
              style={{ maxWidth: 300 }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="table-wrapper">
            {/* Bảng danh sách khóa học: ảnh, tên, giảng viên, giá, trạng thái, nút Sửa / Xóa */}
            <table>
              <thead>
                <tr>
                  <th>Thumbnail</th>
                  <th>Tên khóa học</th>
                  <th>Giảng viên phụ trách</th>
                  <th>Giá</th>
                  <th>Trạng thái</th>
                  <th style={{ textAlign: 'right' }}>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {allCourses === null && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                      Đang tải danh sách khóa học...
                    </td>
                  </tr>
                )}
                {allCourses !== null && filtered.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                      Không tìm thấy khóa học nào.
                    </td>
                  </tr>
                )}
                {filtered.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <div
                        style={{
                          width: 50,
                          height: 35,
                          borderRadius: 'var(--radius-sm)',
                          overflow: 'hidden',
                          background: 'var(--primary-light)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <CourseThumb src={c.thumbnail} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      </div>
                    </td>
                    <td>
                      <strong>{c.title}</strong>
                    </td>
                    <td>{c.teacher_name || 'Chưa phân công'}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>{fmtPrice(c.price)}</td>
                    <td>
                      {(() => {
                        const s = COURSE_STATUS[c.status] || { label: c.status || '—', cls: 'badge-primary' };
                        return (
                          <span className={`badge ${s.cls}`} style={{ whiteSpace: 'nowrap' }}>
                            {s.label}
                          </span>
                        );
                      })()}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-outline btn-sm"
                        style={{ padding: '0.25rem 0.5rem', marginRight: '0.25rem' }}
                        onClick={() => openEditModal(c)}
                      >
                        Sửa
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '0.25rem 0.5rem', background: 'var(--danger)' }}
                        onClick={() => handleDelete(c.id)}
                      >
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Hộp thoại thêm / sửa khóa học */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <div
          className="card modal-panel"
          style={{ width: '100%', maxWidth: 460, margin: '1.5rem', animation: 'modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="card-header">
            <h3>{isEditing ? 'Cập nhật khóa học' : 'Thêm khóa học mới'}</h3>
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
                  placeholder="Lập trình React JS"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Mô tả khóa học</label>
                <textarea
                  className="form-control"
                  rows={3}
                  placeholder="Mô tả tóm tắt..."
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Thumbnail URL</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="https://images.unsplash.com/..."
                  value={form.thumbnail}
                  onChange={(e) => setForm({ ...form, thumbnail: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Giảng viên phụ trách</label>
                <select
                  className="form-control"
                  value={form.teacher_id}
                  onChange={(e) => setForm({ ...form, teacher_id: e.target.value })}
                >
                  {!form.teacher_id && <option value="">— Tôi (Admin) —</option>}
                  {form.teacher_id && !teachers.some((t) => String(t.id) === form.teacher_id) && (
                    <option value={form.teacher_id}>(Giữ nguyên người hiện tại)</option>
                  )}
                  {teachers.map((t) => (
                    <option key={t.id} value={String(t.id)}>
                      {t.fullname} — {t.email}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Giá (VNĐ)</label>
                  <input
                    type="number"
                    min="0"
                    className="form-control"
                    placeholder="0 = miễn phí"
                    value={form.price}
                    onChange={(e) => setForm({ ...form, price: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Trạng thái</label>
                  <select
                    className="form-control"
                    value={form.status}
                    onChange={(e) => setForm({ ...form, status: e.target.value })}
                  >
                    <option value="published">Đã xuất bản</option>
                    <option value="draft">Bản nháp</option>
                    <option value="archived">Lưu trữ</option>
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.75rem' }}>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setModalOpen(false)}>
                  Hủy
                </button>
                <button type="submit" className="btn btn-primary btn-sm">
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
