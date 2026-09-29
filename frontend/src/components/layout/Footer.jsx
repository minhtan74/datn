import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          <div>
            <h4 className="text-white font-bold text-base mb-3">🎓 StudyOnline</h4>
            <p className="text-sm leading-relaxed">Nền tảng học tập trực tuyến cho sinh viên và người đi làm.</p>
          </div>
          <div>
            <h4 className="text-white font-bold text-base mb-3">Liên kết</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="inline-block py-1 hover:text-white transition-colors">
                  Trang chủ
                </Link>
              </li>
              <li>
                <Link to="/courses" className="inline-block py-1 hover:text-white transition-colors">
                  Khóa học
                </Link>
              </li>
              <li>
                <Link to="/login" className="inline-block py-1 hover:text-white transition-colors">
                  Đăng nhập
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold text-base mb-3">Liên hệ</h4>
            <p className="text-sm">Email: support@studyonline.com</p>
            <p className="text-sm mt-1">Hotline: 1900 xxxx</p>
          </div>
        </div>
        <div className="border-t border-slate-800 pt-6 text-center text-xs">
          © 2026 StudyOnline. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
