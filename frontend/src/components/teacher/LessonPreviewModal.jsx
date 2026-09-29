import Modal from '../common/Modal.jsx';
import { isYoutubeUrl, getEmbedUrl } from '../../utils/videoUrl';

// Base path gốc dùng để phát video/tài liệu local — giữ nguyên chuỗi cứng từ
// bản gốc (previewLesson() trong teacher/dashboard.html) vì không có thông tin
// mới nào về nơi backend hiện phục vụ các file tĩnh này.
const LEGACY_VIDEO_BASE = '/studyonline/frontend/uploads/videos/';
const LEGACY_DOC_BASE = '/studyonline/frontend/uploads/documents/';

/**
 * Tương đương #lessonPreviewModal trong teacher/dashboard.html — dùng chung
 * cho cả view Chapters (nút "👀 Xem trước" trong tree lesson) và view Lessons
 * (nút "Xem trước" trong bảng), giống hệt bản gốc (1 modal preview duy nhất
 * cho toàn trang SPA).
 */
export default function LessonPreviewModal({ open, onClose, lesson }) {
  if (!lesson) return null;

  // *_src: link có chữ ký do API cấp cho file upload; *_url: giá trị gốc (YouTube, CDN, đường dẫn cũ).
  // Xác định link phát video: YouTube -> link embed; file upload -> link có chữ ký (video_src);
  // link tuyệt đối -> giữ nguyên; tên file cũ -> ghép với thư mục gốc cũ
  const isAbsolute = (u) => u.startsWith('http://') || u.startsWith('https://');
  const videoUrl = lesson.video_url;
  const isYoutube = isYoutubeUrl(videoUrl);
  const videoSrc = videoUrl
    ? isYoutube
      ? getEmbedUrl(videoUrl)
      : lesson.video_src || (isAbsolute(videoUrl) ? videoUrl : LEGACY_VIDEO_BASE + videoUrl)
    : null;

  // Link tài liệu PDF xác định theo cùng quy tắc
  const docUrl = lesson.document_url;
  const docHref = docUrl ? lesson.document_src || (isAbsolute(docUrl) ? docUrl : LEGACY_DOC_BASE + docUrl) : null;

  return (
    <Modal open={open} onClose={onClose}>
      <div
        className="card"
        style={{ width: '100%', maxWidth: 720, margin: '1.5rem', animation: 'modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="card-header">
          <h3>{lesson.title}</h3>
          <button className="btn-icon" onClick={onClose}>
            ✕
          </button>
        </div>
        <div className="card-body" style={{ padding: '1.5rem' }}>
          <div
            style={{
              width: '100%',
              height: 360,
              background: '#000',
              borderRadius: 12,
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
            }}
          >
            {!videoUrl && <p style={{ color: '#fff' }}>🚫 Không có tệp video gắn kèm.</p>}
            {videoUrl && isYoutube && (
              <iframe
                src={videoSrc}
                style={{ width: '100%', height: '100%', border: 'none' }}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                title={lesson.title}
              />
            )}
            {videoUrl && !isYoutube && (
              <video controls style={{ width: '100%', height: '100%', objectFit: 'contain' }}>
                <source src={videoSrc} type="video/mp4" />
                Trình duyệt của bạn không hỗ trợ phát video HTML5.
              </video>
            )}
          </div>
          <h4 style={{ fontWeight: 600, marginBottom: '0.75rem' }}>
            {lesson.description || 'Chưa có mô tả cho bài học này.'}
          </h4>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderTop: '1px solid var(--border)',
              paddingTop: '1rem',
              marginTop: '1rem',
            }}
          >
            {docHref ? (
              <a href={docHref} className="btn btn-outline btn-sm" target="_blank" rel="noreferrer">
                📎 Tải tài liệu PDF học tập
              </a>
            ) : (
              <span>Tài liệu: Không có</span>
            )}
            <button className="btn btn-secondary btn-sm" onClick={onClose}>
              Đóng xem trước
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
