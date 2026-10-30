import { useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function PasswordRecovery({ reset = false }) {
  useEffect(() => {
    if (window.location.hash) window.history.replaceState(null, '', window.location.pathname);
  }, []);
  return <main className="flex-grow flex items-center justify-center py-16 px-4 bg-gradient-to-tr from-slate-50 via-blue-50/20 to-slate-50">
    <div className="w-full max-w-[460px] bg-white border border-slate-200 rounded-2xl shadow-xl p-8 sm:p-10 space-y-6">
      <h1 className="text-2xl font-extrabold text-slate-900 text-center">Quên mật khẩu?</h1>
      <p className="text-sm leading-6 text-slate-600">Vui lòng liên hệ Admin quản lý hệ thống để xác minh tài khoản và được cấp lại mật khẩu.</p>
      {reset && <p role="status" className="text-sm rounded-xl p-4 bg-amber-50 text-amber-800">Website không sử dụng liên kết đặt lại mật khẩu qua email. Hãy liên hệ Admin để được hỗ trợ.</p>}
      <ol className="list-decimal pl-5 space-y-3 text-sm leading-6 text-slate-600">
        <li>Cung cấp email đã đăng ký, họ tên và thông tin xác minh theo hướng dẫn của Admin.</li>
        <li>Admin kiểm tra thông tin và cấp mật khẩu mới qua kênh liên hệ đã xác minh.</li>
        <li>Đăng nhập bằng mật khẩu được cấp và đổi mật khẩu tại Hồ sơ cá nhân.</li>
      </ol>
      <p className="text-xs leading-6 text-slate-500">Không gửi mật khẩu hiện tại, mã OTP hoặc thông tin ngân hàng khi yêu cầu hỗ trợ.</p>
      <Link to="/login" className="block text-center text-sm font-semibold text-blue-600 hover:underline">Quay lại đăng nhập</Link>
    </div>
  </main>;
}
