import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

// Thêm class "active" cho mục menu ứng với trang đang mở
const navClass = ({ isActive }) => 's-nav-item' + (isActive ? ' active' : '');

/** Tương đương <aside class="s-sidebar"> trong các trang student cũ */
export default function StudentSidebar({ collapsed, mobileOpen }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  // Đăng xuất rồi về trang chủ
  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <aside
      className={`s-sidebar${collapsed ? ' collapsed' : ''}${mobileOpen ? ' mobile-open' : ''}`}
      id="studentSidebar"
    >
      <Link className="s-sidebar-logo" to="/">
        <div className="logo-icon">🎓</div>
        <span className="logo-text">StudyOnline</span>
      </Link>
      <nav className="s-sidebar-nav">
        <NavLink className={navClass} to="/student/dashboard">
          <span className="nav-icon">📊</span>
          <span className="nav-label">Dashboard</span>
        </NavLink>
        <NavLink className={navClass} to="/student/my-courses">
          <span className="nav-icon">📚</span>
          <span className="nav-label">Khóa học của tôi</span>
        </NavLink>
        <NavLink className={navClass} to="/student/courses">
          <span className="nav-icon">🌐</span>
          <span className="nav-label">Khám phá</span>
        </NavLink>
        <NavLink className={navClass} to="/student/progress">
          <span className="nav-icon">📈</span>
          <span className="nav-label">Tiến độ học tập</span>
        </NavLink>
        <NavLink className={navClass} to="/quiz">
          <span className="nav-icon">📝</span>
          <span className="nav-label">Quiz</span>
        </NavLink>
        <NavLink className={navClass} to="/student/ai-tutor">
          <span className="nav-icon">🤖</span>
          <span className="nav-label">AI Tutor</span>
        </NavLink>
        <NavLink className={navClass} to="/student/profile">
          <span className="nav-icon">👤</span>
          <span className="nav-label">Hồ sơ cá nhân</span>
        </NavLink>
      </nav>

      <div className="s-sidebar-footer">
        <button className="s-nav-item s-logout" onClick={handleLogout}>
          <span className="nav-icon">🚪</span>
          <span className="nav-label">Đăng xuất</span>
        </button>
      </div>
    </aside>
  );
}
