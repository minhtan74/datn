import axios from 'axios';

// VITE_API_BASE_URL: URL tuyệt đối (dev) hoặc chuỗi rỗng "" (Docker — gọi cùng origin, Nginx proxy /api).
// Không đặt biến này → fallback về backend dev cục bộ.
const BASE_URL =
  import.meta.env.VITE_API_BASE_URL === undefined
    ? 'http://127.0.0.1:8080'
    : import.meta.env.VITE_API_BASE_URL;

// Đường dẫn tương đối của backend (vd "/uploads/images/quiz/a.png") -> URL đầy đủ để hiển thị
export function apiUrl(path) {
  return `${BASE_URL.replace(/\/$/, '')}${path}`;
}

// Tên key lưu token và thông tin user trong localStorage
export const TOKEN_KEY = 'token';
export const USER_KEY = 'user';

// Đọc token đăng nhập đã lưu
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

// Đọc thông tin user đã lưu (dữ liệu hỏng thì coi như chưa đăng nhập)
export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
  } catch {
    return null;
  }
}

// Lưu token + user sau khi đăng nhập thành công
export function setAuthStorage(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

// Xóa token + user khi đăng xuất hoặc token hết hạn
export function clearAuthStorage() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// Tạo instance axios dùng chung cho mọi lời gọi API
const axiosClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Trước mỗi request: tự gắn header "Authorization: Bearer <token>" nếu đã đăng nhập
axiosClient.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Chuẩn hoá response giống Api.request() cũ: { ok, status, data }.
// Không throw ở luồng thường để các trang xử lý res.ok như bản gốc.
axiosClient.interceptors.response.use(
  (res) => ({ ok: true, status: res.status, data: res.data, headers: res.headers }),
  (error) => {
    if (error.response) {
      const { status, data, config } = error.response;
      const path = config?.url || '';
      // Token hết hạn / không hợp lệ (401) ở API ngoài /api/auth -> xóa phiên và chuyển về trang đăng nhập
      if (status === 401 && !path.startsWith('/api/auth/')) {
        clearAuthStorage();
        window.location.href = '/login';
        return new Promise(() => {});
      }
      // Lỗi khác (400, 403, 404, 409...): trả về để trang tự hiển thị thông báo
      return { ok: false, status, data };
    }
    // Không nhận được phản hồi (server tắt / mất mạng)
    return {
      ok: false,
      status: 0,
      data: { success: false, message: 'Không thể kết nối tới máy chủ. Kiểm tra API server đang chạy.' },
    };
  },
);

export default axiosClient;
