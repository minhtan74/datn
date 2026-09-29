import { useAuth } from '../../hooks/useAuth';

// Chữ viết tắt làm avatar: chữ cái đầu của 2 từ đầu trong tên
function getInitials(fullname) {
  if (!fullname) return 'TC';
  return fullname
    .split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

/** Tương đương <header class="topbar"> của teacher/dashboard.html cũ */
export default function TeacherTopbar({ onToggleSidebar }) {
  const { user } = useAuth();

  const name = user?.fullname || 'Instructor';
  const initials = getInitials(name);

  return (
    <header className="topbar">
      <div className="topbar-left" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.75rem' }}>
        <button
          type="button"
          className="btn-icon sidebar-toggle-btn"
          onClick={onToggleSidebar}
          aria-label="Mở/đóng menu"
        >
          ☰
        </button>
        <div>
          <h2 className="topbar-title">Hệ thống Giảng viên</h2>
          <span className="topbar-sub">Xin chào, {name}!</span>
        </div>
      </div>
      <div className="topbar-right">
        <div className="topbar-avatar">{initials}</div>
      </div>
    </header>
  );
}
