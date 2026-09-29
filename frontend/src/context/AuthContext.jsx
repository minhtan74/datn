import { createContext, useCallback, useMemo, useState } from 'react';
import { getStoredUser, getToken, setAuthStorage, clearAuthStorage } from '../api/axiosClient';
import { authService } from '../services/authService';

// Context chia sẻ trạng thái đăng nhập cho toàn bộ ứng dụng
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Khởi tạo từ localStorage để tải lại trang (F5) vẫn giữ đăng nhập
  const [token, setToken] = useState(getToken());
  const [user, setUser] = useState(getStoredUser());

  // Đăng nhập: lưu token + user vào localStorage và state
  const login = useCallback((newToken, newUser) => {
    setAuthStorage(newToken, newUser);
    setToken(newToken);
    setUser(newUser);
  }, []);

  // Đăng xuất: xóa phiên ở client rồi báo backend (lỗi cũng bỏ qua)
  const logout = useCallback(() => {
    clearAuthStorage();
    setToken(null);
    setUser(null);
    try {
      authService.logout();
    } catch {
      /* best-effort, giữ đúng hành vi bản gốc */
    }
  }, []);

  // Giá trị cung cấp cho các component (useMemo để tránh render lại không cần thiết)
  const value = useMemo(
    () => ({
      token,
      user,
      isLoggedIn: !!token,
      login,
      logout,
    }),
    [token, user, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
