import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext.jsx';

// Hook lấy trạng thái đăng nhập: { token, user, isLoggedIn, login, logout }
export function useAuth() {
  return useContext(AuthContext);
}
