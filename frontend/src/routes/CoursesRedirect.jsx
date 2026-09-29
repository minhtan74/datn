import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const COURSES_BY_ROLE = {
  admin: '/admin/courses',
  teacher: '/teacher/courses',
  student: '/student/courses',
};

/** /courses (link ở trang chủ, footer) -> trang khóa học đúng vai trò; khách -> đăng nhập. */
export default function CoursesRedirect() {
  const { isLoggedIn, user } = useAuth();
  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: { pathname: '/student/courses' } }} replace />;
  }
  return <Navigate to={COURSES_BY_ROLE[user?.role] || '/student/courses'} replace />;
}
