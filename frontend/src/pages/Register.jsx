import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

export default function Register() {
  const navigate = useNavigate();
  const [fullname, setFullname] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('student');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState(null);

  // Gửi thông tin đăng ký; thành công thì báo và sau 1.5 giây chuyển sang trang đăng nhập
  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setAlert(null);

    try {
      const res = await authService.register(
        fullname.trim(),
        email.trim(),
        password.trim(),
        confirmPassword.trim(),
      );

      if (res?.ok && res.data?.success) {
        setAlert({ type: 'success', message: 'Đăng ký thành công! Đang chuyển hướng...' });
        setTimeout(() => navigate('/login', { replace: true }), 1500);
        return;
      }

      setAlert({ type: 'danger', message: res?.data?.message || 'Đăng ký thất bại.' });
      setSubmitting(false);
    } catch {
      setAlert({ type: 'danger', message: 'Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.' });
      setSubmitting(false);
    }
  }

  return (
    <main className="flex-grow flex items-center justify-center py-16 px-4 bg-gradient-to-tr from-slate-50 via-blue-50/20 to-slate-50">
      <div className="w-full max-w-[440px]">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-xl p-8 sm:p-10 space-y-6">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-violet-600 rounded-2xl text-3xl shadow-md shadow-blue-200 mb-4 select-none">
              🎓
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Tạo tài khoản mới</h1>
            <p className="text-sm text-slate-500 mt-1">Đăng ký tham gia học tập miễn phí hôm nay</p>
          </div>

          <div id="alertBox">
            {alert && <div className={`alert alert-${alert.type}`}>{alert.message}</div>}
          </div>

          {/* Form đăng ký */}
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="fullname" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Họ và tên
              </label>
              <input
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all duration-200"
                type="text"
                id="fullname"
                name="fullname"
                placeholder="Nguyễn Văn A"
                required
                value={fullname}
                onChange={(e) => setFullname(e.target.value)}
              />
            </div>

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
              <label htmlFor="role" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Vai trò tài khoản
              </label>
              <div className="relative">
                {/* Lưu ý: vai trò chọn ở đây KHÔNG được gửi lên server — backend luôn tạo tài khoản học viên */}
                <select
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all duration-200 cursor-pointer appearance-none"
                  id="role"
                  name="role"
                  required
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="student">Học viên</option>
                  <option value="teacher">Giảng viên</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
                  ▾
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Mật khẩu
              </label>
              <input
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all duration-200"
                type="password"
                id="password"
                name="password"
                placeholder="Ít nhất 6 ký tự"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <div>
              <label
                htmlFor="confirm_password"
                className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2"
              >
                Xác nhận mật khẩu
              </label>
              <input
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10 transition-all duration-200"
                type="password"
                id="confirm_password"
                name="confirm_password"
                placeholder="Nhập lại mật khẩu mới"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-bold text-sm rounded-xl transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2 cursor-pointer mt-4"
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
                '🚀 Đăng ký ngay'
              )}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500">
            Đã có tài khoản?{' '}
            <Link to="/login" className="inline-block py-1 font-bold text-blue-600 hover:underline">
              Đăng nhập
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
