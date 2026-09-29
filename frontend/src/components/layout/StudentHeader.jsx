import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useClickOutside } from '../../hooks/useClickOutside';

/** Tương đương <header class="s-header"> — avatar dropdown + toggle sidebar, dùng chung mọi trang student */
export default function StudentHeader({ onToggleSidebar }) {
  const { user } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const wrapRef = useRef(null);

  // Click ra ngoài thì đóng menu avatar
  useClickOutside(wrapRef, () => setDropdownOpen(false));

  // Avatar = chữ cái đầu của 2 từ cuối trong tên; tên hiển thị = từ cuối (tên gọi)
  const initials = user?.fullname
    ? user.fullname
      .split(' ')
      .map((w) => w[0])
      .slice(-2)
      .join('')
      .toUpperCase()
    : '?';
  const displayName = user?.fullname?.split(' ').pop() || 'Học viên';

  return (
    <header className="s-header">
      <button className="s-toggle-btn" id="sidebarToggle" title="Toggle sidebar" onClick={onToggleSidebar}>
        ☰
      </button>
      <div className="s-header-actions">
        <div
          className="s-avatar-wrap"
          id="avatarWrap"
          ref={wrapRef}
          onClick={(e) => {
            e.stopPropagation();
            setDropdownOpen((v) => !v);
          }}
        >
          <div className="s-avatar" id="headerAvatar">
            {initials}
          </div>
          <span className="s-avatar-name" id="headerName">
            {displayName}
          </span>
          <span style={{ color: 'var(--s-text-muted)', fontSize: '.8rem' }}>▾</span>
          <div className={`s-dropdown${dropdownOpen ? ' open' : ''}`} id="avatarDropdown">
            <Link to="/student/profile">👤 Hồ sơ</Link>
          </div>
        </div>
      </div>
    </header>
  );
}
