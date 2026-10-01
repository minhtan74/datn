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
// Trình độ dùng cho nhãn hiển thị
const LEVELS = ['Cơ bản', 'Trung cấp', 'Nâng cao'];
const LEVEL_DB = ['beginner', 'intermediate', 'advanced'];
const LEVEL_CLS = ['level-begin', 'level-mid', 'level-adv'];

// courseMeta() — hàm deterministic theo course.id, giữ nguyên công thức gốc dù có vẻ "hack"
// (thay thế cho các trường lessons/hours/level chưa có thật ở backend)
function courseMeta(c, i) {
  const lessons = 5 + ((c.id || i) * 7) % 20;
  const hours = (lessons * 0.5).toFixed(0);
  const lvlIdx = LEVEL_DB.indexOf(c.level) >= 0 ? LEVEL_DB.indexOf(c.level) : (c.id || i) % 3;
  return { lessons, hours, lvlIdx };
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

  // Bộ lọc: từ khóa tìm kiếm, cách sắp xếp
  const [searchVal, setSearchVal] = useState('');
  const [currentSort, setCurrentSort] = useState('newest');

  // Hộp thoại chi tiết khóa học và hộp thoại xác nhận thanh toán VNPay
  const [detailCourse, setDetailCourse] = useState(null);
  const [paymentCourse, setPaymentCourse] = useState(null);
  const [payError, setPayError] = useState(null);
  const [paying, setPaying] = useState(false);

  // Khi mở trang: tải danh sách khóa học + id các khóa đã ghi danh (để ẩn các khóa đã đăng ký)
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

  // Khóa chưa đăng ký: trang Khám phá chỉ hiện các khóa này (khóa đã đăng ký nằm ở "Khóa học của tôi")
  const available = useMemo(
    () => (allCourses ? allCourses.filter((c) => !enrolledIds.has(Number(c.id))) : []),
    [allCourses, enrolledIds],
  );

  // Lọc theo từ khóa (tên hoặc mô tả), rồi sắp xếp theo lựa chọn (A-Z, Z-A, giá tăng/giảm)
  const filtered = useMemo(() => {
    const q = searchVal.toLowerCase();
    let list = available.filter(
      (c) => !q || (c.title || '').toLowerCase().includes(q) || (c.description || '').toLowerCase().includes(q),
    );
    if (currentSort === 'az') list = [...list].sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    if (currentSort === 'za') list = [...list].sort((a, b) => (b.title || '').localeCompare(a.title || ''));
    if (currentSort === 'price_asc') list = [...list].sort((a, b) => (+a.price || 0) - (+b.price || 0));
    if (currentSort === 'price_desc') list = [...list].sort((a, b) => (+b.price || 0) - (+a.price || 0));
    return list;
  }, [available, searchVal, currentSort]);

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
      setEnrolledIds((prev) => new Set(prev).add(Number(courseId)));
      showToast('✅ Đăng ký thành công! Khóa học đã chuyển sang "Khóa học của tôi".', 'success');
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
      setEnrolledIds((prev) => new Set(prev).add(Number(paymentCourse.id)));
      setPaymentCourse(null);
      showToast('✅ Đăng ký thành công! Khóa học đã chuyển sang "Khóa học của tôi".', 'success');
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
              <span>📚 {available.length} khóa học chưa đăng ký</span>
              <span>👨‍🏫 Nhiều giảng viên</span>
              <span>✅ {enrolledIds.size} đã đăng ký</span>
            </>
          )}
        </div>
      </div>

      {/* Sort bar */}
      <div className="sort-bar">
        <div className="count" id="countLabel">
          {allCourses === null ? (
            'Đang tải...'
          ) : (
            <>
              Hiển thị <strong>{filtered.length}</strong> / {available.length} khóa học
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
          // Đã đăng ký hết mọi khóa -> báo riêng, khác với trường hợp lọc không ra kết quả
          <div className="no-result">
            {allCourses.length > 0 && available.length === 0 ? (
              <>
                <div className="icon">🎉</div>
                <h3>Bạn đã đăng ký tất cả khóa học</h3>
                <p>
                  Tiếp tục học tại <Link to="/student/my-courses">Khóa học của tôi</Link>.
                </p>
              </>
            ) : (
              <>
                <div className="icon">🔎</div>
                <h3>Không tìm thấy khóa học</h3>
                <p>Thử từ khóa khác nhé.</p>
              </>
            )}
          </div>
        )}

        {allCourses !== null &&
          filtered.map((c) => {
            const origIdx = allCourses.indexOf(c);
            const { lessons, hours, lvlIdx } = courseMeta(c, origIdx);
            const emoji = EMOJIS[origIdx % EMOJIS.length];
            const color = COLORS[origIdx % COLORS.length];
            const isNew = origIdx < 3;

            return (
              <div key={c.id} className="s-course-card" id={`card-${c.id}`}>
                <div className="s-course-thumb" style={{ background: `linear-gradient(135deg,${color})` }}>
                  {isNew && <span className="enroll-badge">🆕 Mới</span>}
                  <span style={{ fontSize: '2.5rem' }}>{emoji}</span>
                </div>
                <div className="s-course-body">
                  <h3>{c.title || 'Khóa học'}</h3>
                  <p className="teacher">👨‍🏫 {c.teacher_name || 'Giảng viên StudyOnline'}</p>
                  <div className="s-course-meta">
                    <span>📖 {lessons} bài</span>
                    <span>⏱ {hours}h</span>
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
                  <button className="s-btn s-btn-primary s-btn-sm" onClick={() => startEnroll(c)}>
                    {+c.price > 0 ? '💳 Mua ngay' : '📥 Đăng ký'}
                  </button>
                </div>
              </div>
            );
          })}
      </div>

      {/* Detail Modal */}
      {detailCourse &&
        (() => {
          const origIdx = allCourses.indexOf(detailCourse);
          const { lessons, hours, lvlIdx } = courseMeta(detailCourse, origIdx);
          const color = COLORS[origIdx % COLORS.length];
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
