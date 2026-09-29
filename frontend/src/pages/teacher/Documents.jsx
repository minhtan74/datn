import { useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { aiService } from '../../services/aiService';
import { courseService } from '../../services/courseService';

// Nhãn + màu cho trạng thái lập chỉ mục của tài liệu
const STATUS = {
  indexed: { text: 'Đã lập chỉ mục', color: 'var(--success, #059669)' },
  pending: { text: 'Đang xử lý', color: 'var(--warning, #D97706)' },
  failed: { text: 'Thất bại', color: 'var(--danger, #DC2626)' },
};

/** PHASE 6 — Quản lý tài liệu cho AI Tutor (RAG). Giảng viên tải PDF/DOCX/TXT theo khóa. */
export default function TeacherDocuments() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const fileRef = useRef(null);

  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [title, setTitle] = useState('');
  const [docs, setDocs] = useState(null); // null = loading
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  // Khi mở trang: tải các khóa học của giảng viên, chọn sẵn khóa đầu tiên
  useEffect(() => {
    (async () => {
      const res = await courseService.getCourses();
      const mine = (res?.data?.data || []).filter(
        (c) => !user || c.teacher_id === user.id || user.role === 'admin',
      );
      setCourses(mine);
      if (mine.length) setCourseId(String(mine[0].id));
    })();
  }, [user]);

  // Tải danh sách tài liệu AI của khóa đang chọn
  async function loadDocs() {
    if (!courseId) return;
    setDocs(null);
    const res = await aiService.getDocuments(courseId);
    setDocs(res?.data?.data || []);
  }

  // Đổi khóa học -> tải lại danh sách tài liệu
  useEffect(() => {
    loadDocs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId]);

  // Tải tài liệu lên (hiện % tiến trình); backend lập chỉ mục ngay, xong thì tải lại danh sách
  async function handleUpload(e) {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file || !courseId) return;
    setUploading(true);
    setProgress(0);
    const res = await aiService.uploadDocument(
      { file, courseId, title: title.trim() },
      setProgress,
    );
    setUploading(false);
    if (res?.ok && res.data?.success) {
      showToast(res.data.message || 'Đã tải tài liệu.', 'success');
      setTitle('');
      if (fileRef.current) fileRef.current.value = '';
      loadDocs();
    } else {
      showToast(res?.data?.message || 'Tải tài liệu thất bại.', 'error');
    }
  }

  // Xóa tài liệu khỏi AI Tutor (kèm các đoạn vector)
  async function handleDelete(id) {
    if (!window.confirm('Xóa tài liệu này khỏi AI Tutor?')) return;
    const res = await aiService.deleteDocument(id);
    if (res?.ok) {
      showToast('Đã xóa.', 'success');
      loadDocs();
    }
  }

  // Tổng số đoạn (chunk) đã lập chỉ mục của khóa
  const totalChunks = useMemo(
    () => (docs || []).reduce((s, d) => s + (Number(d.chunk_count) || 0), 0),
    [docs],
  );

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ fontSize: '1.6rem', fontWeight: 800 }}>
            🤖 Tài liệu AI Tutor
          </h1>
          <p className="page-subtitle" style={{ marginTop: '0.25rem', fontSize: '0.88rem' }}>
            Tải tài liệu (PDF, DOCX, TXT) để trợ giảng AI trả lời câu hỏi của học viên dựa trên đó.
          </p>
        </div>
      </div>

      <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <form onSubmit={handleUpload} style={{ display: 'grid', gap: '1rem' }}>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Khóa học</label>
              <select className="form-control" value={courseId} onChange={(e) => setCourseId(e.target.value)}>
                {courses.length === 0 && <option value="">— Chưa có khóa học —</option>}
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>{c.title}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Tiêu đề (tùy chọn)</label>
              <input
                className="form-control"
                type="text"
                placeholder="VD: Giáo trình chương 1"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Tệp tài liệu (.pdf, .docx, .txt — tối đa 20MB)</label>
            <input ref={fileRef} className="form-control" type="file" accept=".pdf,.docx,.txt,.md" required />
          </div>
          {uploading && (
            <div className="s-progress" style={{ height: 8 }}>
              <div className="s-progress-bar" style={{ width: `${progress}%` }} />
            </div>
          )}
          <div>
            <button className="btn btn-primary" type="submit" disabled={uploading || !courseId}>
              {uploading ? `Đang tải & lập chỉ mục… ${progress}%` : '⬆ Tải lên & lập chỉ mục'}
            </button>
          </div>
        </form>
      </div>

      <div className="card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <strong>Tài liệu của khóa</strong>
          <span style={{ fontSize: '.8rem', color: 'var(--text-muted, #64748b)' }}>
            {docs ? `${docs.length} tài liệu · ${totalChunks} đoạn đã lập chỉ mục` : '…'}
          </span>
        </div>

        {docs === null && (
          <div className="loading-page"><div className="spinner" /></div>
        )}
        {docs !== null && docs.length === 0 && (
          <div className="empty-state">
            <div className="icon">📄</div>
            <h3>Chưa có tài liệu nào</h3>
            <p>Tải lên tài liệu đầu tiên để kích hoạt AI Tutor cho khóa học này.</p>
          </div>
        )}
        {docs !== null && docs.length > 0 && (
          <div className="table-wrapper">
            {/* Bảng tài liệu: tên, bài học, trạng thái, số trang, số đoạn, nút xóa */}
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '.88rem' }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--text-muted, #64748b)' }}>
                  <th style={{ padding: '.5rem' }}>Tiêu đề</th>
                  <th style={{ padding: '.5rem' }}>Loại</th>
                  <th style={{ padding: '.5rem' }}>Trạng thái</th>
                  <th style={{ padding: '.5rem' }}>Đoạn</th>
                  <th style={{ padding: '.5rem' }}>Trang</th>
                  <th style={{ padding: '.5rem' }} />
                </tr>
              </thead>
              <tbody>
                {docs.map((d) => {
                  const st = STATUS[d.status] || STATUS.pending;
                  return (
                    <tr key={d.id} style={{ borderTop: '1px solid var(--border, #e2e8f0)' }}>
                      <td style={{ padding: '.6rem .5rem', fontWeight: 600 }}>
                        {d.title}
                        {d.status === 'failed' && d.error && (
                          <div style={{ fontSize: '.72rem', color: 'var(--danger,#DC2626)', fontWeight: 400 }}>{d.error}</div>
                        )}
                      </td>
                      <td style={{ padding: '.6rem .5rem', textTransform: 'uppercase' }}>{d.file_type}</td>
                      <td style={{ padding: '.6rem .5rem', color: st.color, fontWeight: 700 }}>{st.text}</td>
                      <td style={{ padding: '.6rem .5rem' }}>{d.chunk_count}</td>
                      <td style={{ padding: '.6rem .5rem' }}>{d.pages ?? '—'}</td>
                      <td style={{ padding: '.6rem .5rem', textAlign: 'right' }}>
                        <button className="btn btn-ghost btn-sm" style={{ color: 'var(--danger,#DC2626)' }} onClick={() => handleDelete(d.id)}>
                          ✕ Xóa
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
