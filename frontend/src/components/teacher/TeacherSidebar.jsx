import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

// Tương đương document.querySelectorAll('.sidebar-menu a').active của bản gốc:
// NavLink v6 không tự thêm class 'active', phải tính thủ công.
const navLinkClass = ({ isActive }) => (isActive ? 'active' : undefined);

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

/** Tương đương <aside class="sidebar"> của teacher/dashboard.html cũ */
export default function TeacherSidebar({ mobileOpen, onNavigate }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Đăng xuất rồi về trang chủ
  function doTeacherLogout() {
    logout();
    navigate('/');
  }

  const name = user?.fullname || 'Instructor';
  const initials = getInitials(name);

  return (
    <aside className={`sidebar${mobileOpen ? ' active' : ''}`} onClick={(e) => {
      // Đóng sidebar mobile khi bấm 1 link điều hướng (không ảnh hưởng desktop)
      if (e.target.closest('a')) onNavigate?.();
    }}>
      <div className="sidebar-brand">
        <div className="brand-icon">🎓</div>
        <div className="brand-text">
          <div className="brand-name">StudyOnline</div>
          <div className="brand-sub">Instructor Panel</div>
        </div>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-label">Giảng dạy</div>
        <nav className="sidebar-menu">
          <NavLink to="/teacher" end className={navLinkClass}>
            <span className="menu-icon">📊</span> Dashboard
          </NavLink>
          <NavLink to="/teacher/courses" className={navLinkClass}>
            <span className="menu-icon">📚</span> Khóa học của tôi
          </NavLink>
          <NavLink to="/teacher/chapters" className={navLinkClass}>
            <span className="menu-icon">📖</span> Chương học
          </NavLink>
          <NavLink to="/teacher/lessons" className={navLinkClass}>
            <span className="menu-icon">🎥</span> Bài học
          </NavLink>
          <NavLink to="/teacher/quizzes" className={navLinkClass}>
            <span className="menu-icon">📝</span> Quiz trắc nghiệm
          </NavLink>
          <NavLink to="/teacher/documents" className={navLinkClass}>
            <span className="menu-icon">🤖</span> Tài liệu AI Tutor
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-section-label">Quản lý &amp; Báo cáo</div>
        <nav className="sidebar-menu">
          <NavLink to="/teacher/students" className={navLinkClass}>
            <span className="menu-icon">👨‍🎓</span> Học viên
          </NavLink>
          <NavLink to="/teacher/stats" className={navLinkClass}>
            <span className="menu-icon">📈</span> Thống kê
          </NavLink>
          <NavLink to="/teacher/profile" className={navLinkClass}>
            <span className="menu-icon">👤</span> Hồ sơ cá nhân
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="avatar avatar-sm" style={{ background: 'var(--accent)' }}>
            {initials}
          </div>
          <div className="user-info">
            <div className="sidebar-user-name">{name}</div>
            <div className="sidebar-user-role">Giảng viên</div>
          </div>
        </div>
        <button className="sidebar-logout" onClick={doTeacherLogout}>
          🚪 Đăng xuất
        </button>
      </div>
    </aside>
  );
}
