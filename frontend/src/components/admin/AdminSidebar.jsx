import { useEffect, useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

/**
 * Tương đương <aside class="sidebar"> trong _legacy/pages/admin/dashboard.html.
 * Thay cho switchView()/hashchange thủ công cũ, active state của menu giờ do
 * <NavLink> tự xử lý (thêm class "active" khi route khớp) — khớp với
 * `.sidebar-menu a.active` đã có sẵn trong studyonline.css.
 */
export default function AdminSidebar({ mobileOpen, onNavigate }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  // Đang ở trong khu Quản lý User (/admin/users/...) thì tự mở menu con Teacher / Student
  const inUsers = pathname.startsWith('/admin/users');
  const [usersOpen, setUsersOpen] = useState(inUsers);
  useEffect(() => {
    if (inUsers) setUsersOpen(true);
  }, [inUsers]);

  const fullname = user?.fullname || 'Admin';
  // Cùng quy ước initials/tên hiển thị với phần còn lại của app (vd StudentHeader.jsx):
  // initials = chữ cái đầu của 2 từ cuối cùng, tên hiển thị = từ cuối cùng.
  const initials = fullname
    .split(' ')
    .map((w) => w[0])
    .slice(-2)
    .join('')
    .toUpperCase();

  // Đăng xuất rồi về trang chủ
  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <aside className={`sidebar${mobileOpen ? ' active' : ''}`} onClick={(e) => {
      // Đóng sidebar mobile khi bấm 1 link điều hướng (không ảnh hưởng desktop)
      if (e.target.closest('a')) onNavigate?.();
    }}>
      <div className="sidebar-brand">
        <div className="brand-icon">🎓</div>
        <div className="brand-text">
          <div className="brand-name">StudyOnline</div>
          <div className="brand-sub">Hệ thống Quản lý</div>
        </div>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-label">Bảng điều khiển</div>
        <nav className="sidebar-menu">
          <NavLink to="/admin" end>
            <span className="menu-icon">📊</span> Dashboard
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-label">Quản trị hệ thống</div>
        <nav className="sidebar-menu">
          {/* Nhóm Quản lý User: mục cha (tất cả user) + nút mở/đóng menu con Teacher / Student */}
          <div className={`sidebar-group${inUsers ? ' current' : ''}`}>
            <NavLink to="/admin/users" end onClick={() => setUsersOpen(true)}>
              <span className="menu-icon">👥</span> Quản lý User
            </NavLink>
            <button
              type="button"
              className="sidebar-group-toggle"
              aria-label={usersOpen ? 'Thu gọn' : 'Mở rộng'}
              aria-expanded={usersOpen}
              onClick={() => setUsersOpen((v) => !v)}
            >
              {usersOpen ? '▾' : '▸'}
            </button>
          </div>
          {usersOpen && (
            <div className="sidebar-submenu">
              <NavLink to="/admin/users/teachers">
                <span className="menu-icon">👨‍🏫</span> Teacher
              </NavLink>
              <NavLink to="/admin/users/students">
                <span className="menu-icon">🎒</span> Student
              </NavLink>
            </div>
          )}
          <NavLink to="/admin/courses">
            <span className="menu-icon">📚</span> Quản lý Khóa học
          </NavLink>
          <NavLink to="/admin/payments">
            <span className="menu-icon">💳</span> Quản lý Giao dịch
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-label">Báo cáo &amp; Cấu hình</div>
        <nav className="sidebar-menu">

          <NavLink to="/admin/reports">
            <span className="menu-icon">📄</span> Báo cáo
          </NavLink>

        </nav>
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="avatar avatar-sm" style={{ background: 'var(--accent)' }}>
            {initials}
          </div>
          <div className="user-info">
            <div className="sidebar-user-name">{fullname}</div>
            <div className="sidebar-user-role">Super Admin</div>
          </div>
        </div>
        <button className="sidebar-logout" onClick={handleLogout}>
          🚪 Đăng xuất
        </button>
      </div>
    </aside>
  );
}
