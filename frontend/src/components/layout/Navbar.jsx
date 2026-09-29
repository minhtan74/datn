import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

// Nút "vào trang quản lý" trên navbar, theo vai trò của người đang đăng nhập
const PANEL_BY_ROLE = {
  admin: { to: '/admin', label: 'Admin Panel' },
  teacher: { to: '/teacher', label: 'Teacher Panel' },
  student: { to: '/student/dashboard', label: 'Dashboard' },
};

/** Tương đương renderNavbar() (bản Tailwind) trong api.js — dùng cho Home/Login/Register/Courses */
export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const panel = user?.role ? PANEL_BY_ROLE[user.role] : null;

  // Đăng xuất rồi về trang chủ
  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <nav id="navbar" className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16 gap-2">
        <div className="flex items-center gap-1 min-w-0">
          <Link to="/" className="text-blue-600 font-extrabold text-lg sm:text-xl flex items-center gap-2 whitespace-nowrap">
            🎓 <span className="text-slate-900">StudyOnline</span>
          </Link>
          {/* Trên điện thoại logo đã dẫn về trang chủ -> ẩn link này để các nút bên phải không bị cắt */}
          <Link
            to="/"
            className="hidden sm:inline-block ml-4 text-slate-600 hover:text-blue-600 font-medium text-sm px-3 py-2 rounded-lg hover:bg-slate-100 transition-all"
          >
            Trang chủ
          </Link>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {panel && (
            <Link
              to={panel.to}
              className="whitespace-nowrap text-slate-600 hover:text-blue-600 font-medium text-sm px-2 sm:px-3 py-2 rounded-lg hover:bg-slate-100 transition-all"
            >
              {panel.label}
            </Link>
          )}
          {user ? (
            <button
              onClick={handleLogout}
              className="whitespace-nowrap px-3 sm:px-4 py-2 border border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white font-semibold text-sm rounded-lg transition-all"
            >
              Đăng xuất<span className="hidden sm:inline"> ({user.fullname?.split(' ').pop()})</span>
            </button>
          ) : (
            <>
              <Link
                to="/login"
                className="whitespace-nowrap px-3 sm:px-4 py-2 border border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold text-sm rounded-lg transition-all"
              >
                Đăng nhập
              </Link>
              <Link
                to="/register"
                className="whitespace-nowrap px-3 sm:px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 font-semibold text-sm rounded-lg transition-all shadow-sm"
              >
                Đăng ký
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
