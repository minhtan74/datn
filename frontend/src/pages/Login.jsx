import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useAuth } from '../hooks/useAuth';

// Trang chuyển tới sau khi đăng nhập, theo vai trò
const DASHBOARD_BY_ROLE = {
  admin: '/admin',
  teacher: '/teacher',
  student: '/student/dashboard',
};

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState(null);

  // Gửi email + mật khẩu; thành công thì lưu phiên đăng nhập và chuyển tới trang theo vai trò, sai thì hiện lỗi
  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setAlert(null);

    try {
      const res = await authService.login(email.trim(), password.trim());

      if (res?.ok && res.data?.success) {
        login(res.data.token, res.data.user);
        const role = res.data.user?.role;
        navigate(DASHBOARD_BY_ROLE[role] || '/student/dashboard', { replace: true });
        return;
      }

      setAlert(res?.data?.message || 'Đăng nhập thất bại.');
    } catch {
      setAlert('Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex-grow flex items-center justify-center py-16 px-4 bg-gradient-to-tr from-slate-50 via-blue-50/20 to-slate-50">
      <div className="w-full max-w-[420px]">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xl p-8 sm:p-10 space-y-6">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-violet-600 rounded-2xl text-3xl shadow-md shadow-blue-200 mb-4 select-none">
              🎓
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Chào mừng quay trở lại</h1>
            <p className="text-sm text-slate-500 mt-1">Đăng nhập vào tài khoản StudyOnline của bạn</p>
          </div>

          <div id="alertBox">
            {alert && <div className="alert alert-danger">{alert}</div>}
          </div>

          {/* Form đăng nhập */}
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Địa chỉ Email
              </label>
              <input
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all duration-200"
                type="email"
                id="email"
                name="email"
                placeholder="example@email.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="password" className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Mật khẩu
                </label>
                <a href="#" className="inline-block py-1 text-xs font-semibold text-blue-600 hover:underline">
                  Quên mật khẩu?
                </a>
              </div>
              <input
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all duration-200"
                type="password"
                id="password"
                name="password"
                placeholder="••••••••"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-bold text-sm rounded-xl transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2 cursor-pointer mt-2"
            >
              {submitting ? (
                <>
                  <span
                    className="spinner"
                    style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,.4)', borderTopColor: '#fff' }}
                  />{' '}
                  Đang xử lý...
                </>
              ) : (
                '🔑 Đăng nhập'
              )}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500">
            Chưa có tài khoản?{' '}
            <Link to="/register" className="inline-block py-1 font-bold text-blue-600 hover:underline">
              Đăng ký ngay
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
