import { useAuth } from '../../hooks/useAuth';

// Thanh trên cùng chứa menu và tài khoản; breadcrumb nằm ở đầu nội dung mỗi trang.

export default function AdminTopbar({ onToggleSidebar }) {
  const { user } = useAuth();

  const fullname = user?.fullname || 'Admin';
  const initials = fullname
    .split(' ')
    .map((w) => w[0])
    .slice(-2)
    .join('')
    .toUpperCase();
  const displayName = fullname.split(' ').pop() || 'Admin';

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
          <h2 className="topbar-title">Hệ thống Quản trị</h2>
          <span className="topbar-sub">Xin chào, {displayName}!</span>
        </div>
      </div>
      <div className="topbar-right">
        <div className="topbar-avatar">{initials}</div>
      </div>
    </header>
  );
}
