import { useEffect, useRef } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Thay cho requireLogin() + IIFE kiểm tra role trong các trang admin/teacher/quiz-questions cũ.
 * - Chưa đăng nhập -> /login
 * - Sai role -> wrongRoleRedirect (mặc định /login, giống bản gốc)
 */
export default function ProtectedRoute({ roles, wrongRoleRedirect = '/login', alertOnWrongRole, children }) {
  const { isLoggedIn, user } = useAuth();
  const location = useLocation();
  const wrongRole = isLoggedIn && roles && roles.length > 0 && !roles.includes(user?.role);

  // Báo sai vai trò trong effect (không gọi alert lúc render) và chỉ 1 lần:
  // StrictMode ở chế độ dev render / chạy effect 2 lần nên trước đây thông báo hiện 2 lần
  const alerted = useRef(false);
  useEffect(() => {
    if (wrongRole && alertOnWrongRole && !alerted.current) {
      alerted.current = true;
      window.alert(alertOnWrongRole);
    }
  }, [wrongRole, alertOnWrongRole]);

  // Chưa đăng nhập -> về trang đăng nhập, nhớ trang đang muốn vào để quay lại sau khi đăng nhập
  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Sai vai trò (vd học viên vào /admin) -> chuyển hướng (thông báo do effect ở trên hiện)
  if (wrongRole) {
    return <Navigate to={wrongRoleRedirect} replace />;
  }

  // Hợp lệ -> hiển thị trang con
  return children ?? <Outlet />;
}
