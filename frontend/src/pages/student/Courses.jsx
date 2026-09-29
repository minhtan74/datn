import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import { paymentService } from '../../services/paymentService';
import { useToast } from '../../hooks/useToast';
import '../../assets/css/student-courses.css';

// Biểu tượng và màu nền trang trí thẻ khóa học (chọn theo id khóa)
const EMOJIS = ['🎨', '💻', '📊', '🔬', '🌐', '📱', '🎵', '✏️', '🧪', '📐', '🚀', '🔐'];
const COLORS = [
  '#2563EB,#8B5CF6',
  '#0F766E,#06B6D4',
  '#7C3AED,#EC4899',
  '#DC2626,#F59E0B',
  '#059669,#2563EB',
  '#D97706,#EF4444',
  '#1D4ED8,#06B6D4',
  '#7C3AED,#2563EB',
];
// Danh mục và trình độ dùng cho bộ lọc / nhãn hiển thị
const CATS = ['web', 'mobile', 'data', 'design', 'backend', 'other'];
const CAT_LABELS = ['🌐 Web', '📱 Mobile', '📊 Data', '🎨 Design', '⚙️ Backend', '📦 Khác'];
const LEVELS = ['Cơ bản', 'Trung cấp', 'Nâng cao'];
const LEVEL_DB = ['beginner', 'intermediate', 'advanced'];
const LEVEL_CLS = ['level-begin', 'level-mid', 'level-adv'];

// Các nút lọc theo danh mục
const CAT_PILLS = [
  { key: 'all', label: '🌟 Tất cả' },
  { key: 'web', label: '🌐 Web' },
  { key: 'mobile', label: '📱 Mobile' },
  { key: 'data', label: '📊 Data' },
  { key: 'design', label: '🎨 Design' },
  { key: 'backend', label: '⚙️ Backend' },
  { key: 'other', label: '📦 Khác' },
];

// courseMeta() — hàm deterministic theo course.id, giữ nguyên công thức gốc dù có vẻ "hack"
// (thay thế cho các trường lessons/hours/level/category chưa có thật ở backend)
function courseMeta(c, i) {
  const lessons = 5 + ((c.id || i) * 7) % 20;
  const hours = (lessons * 0.5).toFixed(0);
  const lvlIdx = LEVEL_DB.indexOf(c.level) >= 0 ? LEVEL_DB.indexOf(c.level) : (c.id || i) % 3;
  const catIdx = (c.id || i) % CATS.length;
  return { lessons, hours, lvlIdx, catIdx };
}

// Hiển thị giá: 0 -> "Miễn phí", còn lại dạng 499.000đ
function fmtPrice(p) {
  if (!p || p <= 0) return <span className="price-free">🆓 Miễn phí</span>;
  return <span className="price-paid">{Number(p).toLocaleString('vi-VN')}đ</span>;
}

/** Tương đương _legacy/pages/student/courses.html + _legacy/js/student-courses.js */
export default function Courses() {
  const { showToast } = useToast();

  const [allCourses, setAllCourses] = useState(null); // null = đang tải
  const [enrolledIds, setEnrolledIds] = useState(new Set());

  // Bộ lọc: từ khóa tìm kiếm, danh mục, cách sắp xếp
  const [searchVal, setSearchVal] = useState('');
  const [currentCat, setCurrentCat] = useState('all');
  const [currentSort, setCurrentSort] = useState('newest');

  // Hộp thoại chi tiết khóa học và hộp thoại xác nhận thanh toán VNPay
  const [detailCourse, setDetailCourse] = useState(null);
  const [paymentCourse, setPaymentCourse] = useState(null);
  const [payError, setPayError] = useState(null);
  const [paying, setPaying] = useState(false);

  // Khi mở trang: tải danh sách khóa học + id các khóa đã ghi danh (để hiện nút "Vào học" thay cho "Đăng ký")
  useEffect(() => {
    (async () => {
      const [coursesRes, enrollRes] = await Promise.allSettled([courseService.getCourses(), enrollmentService.getEnrolledIds()]);
      setAllCourses(coursesRes?.value?.data?.data || []);
      const rawIds = enrollRes?.value?.data?.data;
      setEnrolledIds(new Set(Array.isArray(rawIds) ? rawIds.map(Number) : []));
    })();
  }, []);

  // Khóa cuộn trang nền khi đang mở hộp thoại
  useEffect(() => {
    document.body.style.overflow = detailCourse || paymentCourse ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [detailCourse, paymentCourse]);

  // Lọc theo danh mục + từ khóa (tên hoặc mô tả), rồi sắp xếp theo lựa chọn (A-Z, Z-A, giá tăng/giảm)
  const filtered = useMemo(() => {
    if (!allCourses) return [];
    let list = allCourses.filter((c, i) => {
      const { catIdx } = courseMeta(c, i);
      const matchCat = currentCat === 'all' || CATS[catIdx] === currentCat;
      const q = searchVal.toLowerCase();
      const matchSearch = !q || (c.title || '').toLowerCase().includes(q) || (c.description || '').toLowerCase().includes(q);
      return matchCat && matchSearch;
    });
    if (currentSort === 'az') list = [...list].sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    if (currentSort === 'za') list = [...list].sort((a, b) => (b.title || '').localeCompare(a.title || ''));
    if (currentSort === 'price_asc') list = [...list].sort((a, b) => (+a.price || 0) - (+b.price || 0));
    if (currentSort === 'price_desc') list = [...list].sort((a, b) => (+b.price || 0) - (+a.price || 0));
    return list;
  }, [allCourses, currentCat, searchVal, currentSort]);

  // Mở / đóng hộp thoại chi tiết khóa học
  function openDetail(course) {
    setDetailCourse(course);
  }
  function closeDetail() {
    setDetailCourse(null);
  }

  // Mở / đóng hộp thoại xác nhận thanh toán
  function openPayment(course) {
    setPaymentCourse(course);
    setPayError(null);
    setPaying(false);
  }
  function closePayment() {
    if (!paying) setPaymentCourse(null);
  }

  // Bấm "Đăng ký": khóa có phí -> mở thanh toán; miễn phí -> ghi danh ngay
  function startEnroll(course) {
    if (+course.price > 0) {
      openPayment(course);
    } else {
      doFreeEnroll(course.id);
    }
  }

  // Ghi danh khóa miễn phí
  async function doFreeEnroll(courseId) {
    showToast('⏳ Đang đăng ký...', 'info');
    const res = await enrollmentService.enroll(courseId);
    if (res?.data?.success) {
      setEnrolledIds((prev) => new Set(prev).add(courseId));
      showToast('✅ Đăng ký khóa học thành công!', 'success');
    } else {
      showToast('❌ ' + (res?.data?.message || 'Đăng ký thất bại'), 'error');
    }
  }

  // Thanh toán qua VNPay: backend tạo đơn hàng (pending) rồi trả URL -> chuyển học viên sang trang VNPay.
  // Sau khi thanh toán, VNPay đưa học viên về /student/payment-result để xem kết quả.
  async function doPayment() {
    setPayError(null);
    setPaying(true);
    const res = await paymentService.createVnpay(paymentCourse.id);

    if (res?.data?.success && res.data.payment_url) {
      window.location.href = res.data.payment_url;
      return; // giữ trạng thái "đang chuyển" cho tới khi trang VNPay mở
    }
    setPaying(false);
    // Trường hợp khóa đã chuyển thành miễn phí: backend ghi danh luôn
    if (res?.data?.success && res.data.enrolled) {
      setEnrolledIds((prev) => new Set(prev).add(paymentCourse.id));
      setPaymentCourse(null);
      showToast('✅ Đăng ký khóa học thành công!', 'success');
      return;
    }
    setPayError('❌ ' + (res?.data?.message || 'Không thể tạo đơn thanh toán. Vui lòng thử lại.'));
  }

  return (
    <main className="s-main">
      {/* Hero */}
      <div className="explore-hero">
        <h1>🌐 Khám phá khóa học</h1>
        <p>Tìm kiếm và đăng ký hàng trăm khóa học chất lượng cao — học bất cứ lúc nào.</p>
        <div className="hero-search">
          <input
            type="text"
            id="heroSearch"
            placeholder="Tìm tên khóa học, chủ đề, kỹ năng..."
            autoComplete="off"
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
          />
          <button onClick={() => {}}>🔍 Tìm kiếm</button>
        </div>
        <div className="stats-row" id="statsRow">
          {allCourses === null ? (
            <span>⏳ Đang tải...</span>
          ) : (
            <>
              <span>📚 {allCourses.length} khóa học</span>
              <span>👨‍🏫 Nhiều giảng viên</span>
              <span>✅ {enrolledIds.size} đã đăng ký</span>
            </>
          )}
        </div>
      </div>

      {/* Category pills */}
      <div className="cat-pills" id="catPills">
        {CAT_PILLS.map((p) => (
          <button key={p.key} className={`cat-pill${currentCat === p.key ? ' active' : ''}`} onClick={() => setCurrentCat(p.key)}>
            {p.label}
          </button>
        ))}
      </div>

      {/* Sort bar */}
      <div className="sort-bar">
        <div className="count" id="countLabel">
          {allCourses === null ? (
            'Đang tải...'
          ) : (
            <>
              Hiển thị <strong>{filtered.length}</strong> / {allCourses.length} khóa học
            </>
          )}
        </div>
        <select id="sortSelect" value={currentSort} onChange={(e) => setCurrentSort(e.target.value)}>
          <option value="newest">Mới nhất</option>
          <option value="az">A → Z</option>
          <option value="za">Z → A</option>
          <option value="price_asc">Giá thấp → cao</option>
          <option value="price_desc">Giá cao → thấp</option>
        </select>
      </div>

      {/* Course Grid */}
      <div className="s-course-grid" id="courseGrid">
        {allCourses === null && (
          <>
            <div className="skeleton-card">
              <div className="sk sk-thumb"></div>
              <div className="sk-body">
                <div className="sk sk-line w80"></div>
                <div className="sk sk-line w60"></div>
                <div className="sk sk-line w40"></div>
              </div>
            </div>
            <div className="skeleton-card">
              <div className="sk sk-thumb"></div>
              <div className="sk-body">
                <div className="sk sk-line w80"></div>
                <div className="sk sk-line w60"></div>
                <div className="sk sk-line w40"></div>
              </div>
            </div>
            <div className="skeleton-card">
              <div className="sk sk-thumb"></div>
              <div className="sk-body">
                <div className="sk sk-line w80"></div>
                <div className="sk sk-line w60"></div>
                <div className="sk sk-line w40"></div>
              </div>
            </div>
          </>
        )}

        {allCourses !== null && filtered.length === 0 && (
          <div className="no-result">
            <div className="icon">🔎</div>
            <h3>Không tìm thấy khóa học</h3>
            <p>Thử từ khóa khác hoặc chọn danh mục khác nhé.</p>
          </div>
        )}

        {allCourses !== null &&
          filtered.map((c) => {
            const origIdx = allCourses.indexOf(c);
            const { lessons, hours, lvlIdx, catIdx } = courseMeta(c, origIdx);
            const emoji = EMOJIS[origIdx % EMOJIS.length];
            const color = COLORS[origIdx % COLORS.length];
            const isNew = origIdx < 3;
            const isEnrolled = enrolledIds.has(c.id);

            return (
              <div key={c.id} className="s-course-card" id={`card-${c.id}`}>
                <div className="s-course-thumb" style={{ background: `linear-gradient(135deg,${color})` }}>
                  {isNew && !isEnrolled && <span className="enroll-badge">🆕 Mới</span>}
                  {isEnrolled && <span className="enroll-badge enrolled-badge">✅ Đã đăng ký</span>}
                  <span style={{ fontSize: '2.5rem' }}>{emoji}</span>
                </div>
                <div className="s-course-body">
                  <h3>{c.title || 'Khóa học'}</h3>
                  <p className="teacher">👨‍🏫 {c.teacher_name || 'Giảng viên StudyOnline'}</p>
                  <div className="s-course-meta">
                    <span>📖 {lessons} bài</span>
                    <span>⏱ {hours}h</span>
                    <span>{CAT_LABELS[catIdx]}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto' }}>
                    <span className={`level-badge ${LEVEL_CLS[lvlIdx]}`}>{LEVELS[lvlIdx]}</span>
                    {fmtPrice(c.price)}
                  </div>
                </div>
                <div className="s-course-footer">
                  <button className="s-btn s-btn-outline s-btn-sm" onClick={() => openDetail(c)}>
                    🔍 Xem chi tiết
                  </button>
                  {isEnrolled ? (
                    <Link to={`/chapters?course_id=${c.id}`} className="s-btn s-btn-primary s-btn-sm">
                      ▶ Vào học
                    </Link>
                  ) : (
                    <button className="s-btn s-btn-primary s-btn-sm" onClick={() => startEnroll(c)}>
                      {+c.price > 0 ? '💳 Mua ngay' : '📥 Đăng ký'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
      </div>

      {/* Detail Modal */}
      {detailCourse &&
        (() => {
          const origIdx = allCourses.indexOf(detailCourse);
          const { lessons, hours, lvlIdx, catIdx } = courseMeta(detailCourse, origIdx);
          const color = COLORS[origIdx % COLORS.length];
          const isEnrolled = enrolledIds.has(detailCourse.id);
          return (
            <div className="modal-wrap open" id="detailModal">
              <div className="modal-backdrop" onClick={closeDetail}></div>
              <div className="modal-box">
                <div
                  className="modal-thumb"
                  style={{
                    background: `linear-gradient(135deg,${color})`,
                    height: 160,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '4rem',
                    borderRadius: '12px 12px 0 0',
                  }}
                >
                  {EMOJIS[origIdx % EMOJIS.length]}
                </div>
                <div className="modal-body">
                  <div style={{ display: 'flex', gap: '.5rem', flexWrap: 'wrap', marginBottom: '.75rem' }}>
                    <span className={`level-badge ${LEVEL_CLS[lvlIdx]}`}>{LEVELS[lvlIdx]}</span>
                    <span className="s-badge s-badge-blue">{CAT_LABELS[catIdx]}</span>
                  </div>
                  <h2 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '.5rem' }}>{detailCourse.title || 'Khóa học'}</h2>
                  <p style={{ fontSize: '.85rem', color: 'var(--s-text-muted)', marginBottom: '1rem', lineHeight: 1.6 }}>
                    {detailCourse.description || 'Chưa có mô tả.'}
                  </p>
                  <div className="detail-stats">
                    <div>
                      <strong>{lessons}</strong>
                      <span>Bài học</span>
                    </div>
                    <div>
                      <strong>{hours}h</strong>
                      <span>Thời lượng</span>
                    </div>
                    <div>
                      <strong>{LEVELS[lvlIdx]}</strong>
                      <span>Trình độ</span>
                    </div>
                    <div>
                      <strong>{+detailCourse.price > 0 ? Number(detailCourse.price).toLocaleString('vi-VN') + 'đ' : 'Miễn phí'}</strong>
                      <span>Học phí</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '.75rem', marginTop: '1.25rem' }}>
                    <button className="s-btn s-btn-ghost s-btn-sm" style={{ flex: 1 }} onClick={closeDetail}>
                      Đóng
                    </button>
                    {isEnrolled ? (
                      <Link
                        to={`/chapters?course_id=${detailCourse.id}`}
                        className="s-btn s-btn-primary"
                        style={{ flex: 2, justifyContent: 'center' }}
                      >
                        ▶ Vào học ngay
                      </Link>
                    ) : (
                      <button
                        className="s-btn s-btn-primary"
                        style={{ flex: 2 }}
                        onClick={() => {
                          const course = detailCourse;
                          closeDetail();
                          startEnroll(course);
                        }}
                      >
                        {+detailCourse.price > 0 ? '💳 Mua khóa học' : '📥 Đăng ký miễn phí'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })()}

      {/* Payment Modal */}
      {paymentCourse &&
        (() => {
          const origIdx = allCourses.indexOf(paymentCourse);
          const color = COLORS[origIdx % COLORS.length];
          return (
            <div className="modal-wrap open" id="paymentModal">
              <div className="modal-backdrop" onClick={closePayment}></div>
              <div className="modal-box" style={{ maxWidth: 480 }}>
                <div className="modal-body">
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      padding: '1rem',
                      background: 'var(--s-surface-2)',
                      borderRadius: '10px',
                      marginBottom: '1.25rem',
                    }}
                  >
                    <div
                      style={{
                        width: 48,
                        height: 48,
                        borderRadius: 10,
                        background: `linear-gradient(135deg,${color})`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.5rem',
                        flexShrink: 0,
                      }}
                    >
                      {EMOJIS[origIdx % EMOJIS.length]}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '.9rem' }}>{paymentCourse.title}</div>
                      <div style={{ fontSize: '.85rem', color: 'var(--s-text-muted)' }}>
                        Học phí: <strong style={{ color: 'var(--s-primary)' }}>{Number(paymentCourse.price).toLocaleString('vi-VN')}đ</strong>
                      </div>
                    </div>
                  </div>

                  <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>💳 Phương thức thanh toán</h3>
                  {/* Thanh toán qua cổng VNPay (Sandbox): thẻ ATM nội địa, thẻ quốc tế, QR ngân hàng */}
                  <div className="pay-method active" style={{ cursor: 'default' }}>
                    <span style={{ fontWeight: 800, color: '#005BAA' }}>VN</span>
                    <span style={{ fontWeight: 800, color: '#ED1C24', marginRight: 6 }}>PAY</span>
                    Thẻ ATM / Thẻ quốc tế / QR ngân hàng
                  </div>
                  <div
                    style={{
                      padding: '0.85rem 1rem',
                      background: 'var(--s-surface-2)',
                      borderRadius: '8px',
                      fontSize: '.82rem',
                      color: 'var(--s-text-muted)',
                      marginTop: '0.75rem',
                      lineHeight: 1.55,
                    }}
                  >
                    Bạn sẽ được chuyển sang trang thanh toán an toàn của <strong>VNPay</strong>. Sau khi thanh toán
                    thành công, khóa học sẽ được mở ngay. Đơn hàng hết hạn sau 15 phút.
                  </div>

                  {payError && (
                    <div id="payError" className="s-alert s-alert-danger">
                      {payError}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '.75rem', marginTop: '1.25rem' }}>
                    <button className="s-btn s-btn-ghost s-btn-sm" style={{ flex: 1 }} onClick={closePayment}>
                      Hủy
                    </button>
                    <button className="s-btn s-btn-primary" style={{ flex: 2 }} id="payBtn" disabled={paying} onClick={doPayment}>
                      {paying
                        ? '⏳ Đang chuyển sang VNPay...'
                        : `Thanh toán ${Number(paymentCourse.price).toLocaleString('vi-VN')}đ qua VNPay`}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })()}
    </main>
  );
}
