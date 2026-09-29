import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { courseService } from '../services/courseService';

// Biểu tượng và màu nền trang trí cho thẻ khóa học
const DEMO_EMOJIS = ['💻', '🎨', '📊', '🌐', '📱', '🔐'];
const DEMO_COLORS = [
  '#2563EB,#8B5CF6',
  '#0F766E,#06B6D4',
  '#DC2626,#F59E0B',
  '#7C3AED,#EC4899',
  '#059669,#2563EB',
  '#D97706,#EF4444',
];
// Tên tiếng Việt của trình độ khóa học
const LEVEL_LABEL = { beginner: 'Cơ bản', intermediate: 'Trung cấp', advanced: 'Nâng cao' };

// Dữ liệu demo — hiển thị khi API chưa có khóa học nào (môi trường mới cài đặt).
const DEMO_FALLBACK = [
  {
    id: 'demo-1',
    title: 'Lập trình Python cho người mới bắt đầu',
    teacher_name: 'Giảng viên StudyOnline',
    description: 'Làm quen với Python: biến, vòng lặp, hàm và xây dựng dự án nhỏ đầu tiên.',
    price: 0,
    level: 'beginner',
  },
  {
    id: 'demo-2',
    title: 'ReactJS Chuyên Sâu',
    teacher_name: 'Giảng viên StudyOnline',
    description: 'Xây dựng ứng dụng thực tế với Hooks nâng cao, quản lý state và tối ưu hiệu năng.',
    price: 899000,
    level: 'advanced',
  },
  {
    id: 'demo-3',
    title: 'Thiết kế UI/UX căn bản',
    teacher_name: 'Giảng viên StudyOnline',
    description: 'Nguyên tắc thiết kế giao diện, trải nghiệm người dùng và công cụ Figma.',
    price: 499000,
    level: 'intermediate',
  },
  {
    id: 'demo-4',
    title: 'MySQL & Thiết Kế Cơ Sở Dữ Liệu',
    teacher_name: 'Giảng viên StudyOnline',
    description: 'Thiết kế cơ sở dữ liệu chuẩn hoá và viết truy vấn SQL hiệu quả với MySQL.',
    price: 499000,
    level: 'intermediate',
  },
];

// Hiển thị giá: 0 -> "Miễn phí", còn lại dạng 499.000đ
function formatPrice(price) {
  const p = Number(price);
  if (!p) return { text: 'Miễn phí', free: true };
  return { text: `${p.toLocaleString('vi-VN')}đ`, free: false };
}

export default function Home() {
  const [featured, setFeatured] = useState(null); // null = đang tải

  // Tải khóa học và lấy 4 khóa đầu làm "nổi bật"; chưa có khóa nào thì dùng dữ liệu demo
  useEffect(() => {
    let active = true;
    (async () => {
      const res = await courseService.getCourses();
      if (!active) return;
      const list = res?.ok ? res.data?.data || [] : [];
      setFeatured(list.length ? list.slice(0, 4) : DEMO_FALLBACK);
    })();
    return () => {
      active = false;
    };
  }, []);

  return (
    <>
      {/* HERO — Banner giới thiệu */}
      <section className="bg-gradient-to-br from-blue-600 via-violet-600 to-cyan-500 text-white py-24 text-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white to-transparent" />
        <div className="relative z-10 max-w-3xl mx-auto px-6">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-5 leading-tight">
            Học bất cứ điều gì,
            <br />
            mọi lúc mọi nơi 🚀
          </h1>
          <p className="text-lg opacity-85 mb-8 max-w-xl mx-auto">
            StudyOnline cung cấp hàng trăm khóa học chất lượng cao từ các giảng viên hàng đầu, giúp bạn nâng cao kỹ
            năng và phát triển sự nghiệp.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              to="/register"
              className="px-8 py-3.5 bg-white text-blue-600 font-bold rounded-xl hover:bg-blue-50 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-0.5"
            >
              Bắt đầu miễn phí
            </Link>
            <Link
              to="/courses"
              className="px-8 py-3.5 border-2 border-white/50 text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-300"
            >
              Xem khóa học
            </Link>
          </div>
        </div>
      </section>

      {/* STATS — Dải số liệu nổi bật */}
      <section className="bg-white border-b border-slate-200 py-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-extrabold text-blue-600">500+</div>
              <div className="text-slate-500 text-sm mt-1">Khóa học</div>
            </div>
            <div>
              <div className="text-4xl font-extrabold text-blue-600">10k+</div>
              <div className="text-slate-500 text-sm mt-1">Học viên</div>
            </div>
            <div>
              <div className="text-4xl font-extrabold text-blue-600">200+</div>
              <div className="text-slate-500 text-sm mt-1">Giảng viên</div>
            </div>
            <div>
              <div className="text-4xl font-extrabold text-blue-600">98%</div>
              <div className="text-slate-500 text-sm mt-1">Hài lòng</div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURED COURSES (demo) — Khóa học nổi bật */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-3">🔥 Khóa học nổi bật</h2>
            <p className="text-slate-500 max-w-xl mx-auto">
              Một vài khóa học tiêu biểu đang có trên StudyOnline — đăng ký ngay để bắt đầu học.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featured === null
              ? Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="bg-white rounded-2xl border border-slate-100 shadow-sm h-80 animate-pulse" />
                ))
              : featured.map((c, i) => {
                  const emoji = DEMO_EMOJIS[i % DEMO_EMOJIS.length];
                  const color = DEMO_COLORS[i % DEMO_COLORS.length];
                  const price = formatPrice(c.price);
                  const level = LEVEL_LABEL[c.level] || 'Cơ bản';
                  return (
                    <div
                      key={c.id}
                      className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col"
                    >
                      <div
                        className="h-36 flex items-center justify-center text-5xl"
                        style={{ background: `linear-gradient(135deg, ${color})` }}
                      >
                        {emoji}
                      </div>
                      <div className="p-5 flex flex-col flex-1">
                        <span className="text-xs font-semibold text-blue-600 mb-1.5">{level}</span>
                        <h3 className="font-bold text-slate-900 mb-1.5 leading-snug line-clamp-2">{c.title}</h3>
                        <p className="text-xs text-slate-500 mb-3">👨‍🏫 {c.teacher_name || 'Giảng viên StudyOnline'}</p>
                        <p className="text-sm text-slate-500 mb-4 line-clamp-2 flex-1">{c.description}</p>
                        <div className="flex items-center justify-between mt-auto pt-1">
                          <span className={`font-bold text-sm ${price.free ? 'text-emerald-600' : 'text-blue-600'}`}>
                            {price.free ? '🆓 Miễn phí' : price.text}
                          </span>
                          <Link to="/courses" className="inline-block py-1 text-sm font-semibold text-blue-600 hover:text-blue-700">
                            Xem thêm →
                          </Link>
                        </div>
                      </div>
                    </div>
                  );
                })}
          </div>

          <div className="text-center mt-10">
            <Link
              to="/courses"
              className="inline-block px-8 py-3 border-2 border-blue-600 text-blue-600 font-semibold rounded-xl hover:bg-blue-50 transition-all duration-300"
            >
              Xem tất cả khóa học →
            </Link>
          </div>
        </div>
      </section>

      {/* FEATURES — Lý do chọn StudyOnline */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-extrabold text-center mb-12 text-slate-900">Tại sao chọn StudyOnline?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 text-center hover:shadow-md hover:-translate-y-1 transition-all duration-300">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-lg font-bold mb-2">Học theo lộ trình</h3>
              <p className="text-slate-500 text-sm">
                Nội dung được sắp xếp khoa học từ cơ bản đến nâng cao, giúp bạn tiến bộ vững chắc.
              </p>
            </div>
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 text-center hover:shadow-md hover:-translate-y-1 transition-all duration-300">
              <div className="text-4xl mb-4">📱</div>
              <h3 className="text-lg font-bold mb-2">Học mọi thiết bị</h3>
              <p className="text-slate-500 text-sm">
                Giao diện responsive hoàn toàn, học trên máy tính, tablet hay điện thoại đều mượt mà.
              </p>
            </div>
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 text-center hover:shadow-md hover:-translate-y-1 transition-all duration-300">
              <div className="text-4xl mb-4">🏆</div>
              <h3 className="text-lg font-bold mb-2">Quiz kiểm tra</h3>
              <p className="text-slate-500 text-sm">
                Hệ thống bài thi trắc nghiệm giúp bạn kiểm tra kiến thức và theo dõi tiến độ học tập.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA — Lời kêu gọi đăng ký */}
      <section className="bg-gradient-to-r from-blue-600 to-violet-600 text-white text-center py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-extrabold mb-4">Sẵn sàng bắt đầu hành trình học tập?</h2>
          <p className="opacity-85 mb-8 text-lg">Đăng ký ngay hôm nay và trải nghiệm hơn 500 khóa học miễn phí.</p>
          <Link
            to="/register"
            className="inline-block px-10 py-4 bg-white text-blue-600 font-bold rounded-xl hover:bg-blue-50 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-0.5 text-base"
          >
            Đăng ký ngay — Miễn phí
          </Link>
        </div>
      </section>
    </>
  );
}
