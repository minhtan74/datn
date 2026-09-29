import { useEffect, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { enrollmentService } from '../../services/enrollmentService';
import { userService } from '../../services/userService';

// Tên tiếng Việt của các vai trò
const ROLE_LABELS = { admin: 'Quản trị viên', teacher: 'Giảng viên', student: 'Học viên' };

/** Trang hồ sơ học viên (tương đương _legacy/pages/student/profile.html)
 * - Form "Lưu thay đổi" gọi PUT /api/users để cập nhật họ tên, rồi đồng bộ lại localStorage + context
 * - Form đổi mật khẩu gọi POST /api/auth/change-password (backend kiểm tra mật khẩu cũ)
 */
export default function Profile() {
  const { user, login, token } = useAuth();

  // State form thông tin cá nhân
  const [fullname, setFullname] = useState(user?.fullname || '');
  const [displayName, setDisplayName] = useState(user?.fullname || ''); // chỉ cập nhật khi lưu thành công
  const [infoAlert, setInfoAlert] = useState(null);
  const [coursesCount, setCoursesCount] = useState(null);
  const [savingInfo, setSavingInfo] = useState(false);

  // State form đổi mật khẩu
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [pwAlert, setPwAlert] = useState(null);
  const [changingPw, setChangingPw] = useState(false);

  useEffect(() => {
    (async () => {
      // Hiển thị số khóa học đã đăng ký
      const res = await enrollmentService.getEnrolledIds();
      setCoursesCount(res?.data?.data?.length ?? null);
    })();
  }, []);

  // Chữ cái đầu của 2 từ cuối trong tên, dùng làm avatar
  const initials = displayName
    ? displayName
        .split(' ')
        .map((w) => w[0])
        .slice(-2)
        .join('')
        .toUpperCase()
    : '?';

  // Lưu họ tên mới; thành công thì cập nhật luôn tên hiển thị trên header
  async function handleInfoSubmit(e) {
    e.preventDefault();
    const name = fullname.trim();
    if (!name) {
      setInfoAlert({ type: 'danger', text: 'Vui lòng nhập họ tên!' });
      return;
    }
    setSavingInfo(true);
    const res = await userService.updateUser({
      id: user.id,
      fullname: name,
      email: user.email,
      role: user.role,
    });
    setSavingInfo(false);

    if (res?.ok && res.data?.success) {
      const updated = { ...user, fullname: name };
      login(token, updated);
      setDisplayName(name); // chỉ cập nhật hiển thị sau khi lưu thành công
      setInfoAlert({ type: 'success', text: '✅ Cập nhật thành công!' });
    } else {
      setInfoAlert({ type: 'danger', text: res?.data?.message || 'Không thể cập nhật thông tin.' });
    }
    setTimeout(() => setInfoAlert(null), 3500);
  }

  // Đổi mật khẩu: kiểm tra phía client (>= 6 ký tự, xác nhận khớp, có mật khẩu cũ) rồi gọi API
  async function handlePwSubmit(e) {
    e.preventDefault();
    if (newPw.length < 6) {
      setPwAlert({ type: 'danger', text: 'Mật khẩu phải có ít nhất 6 ký tự!' });
      return;
    }
    if (newPw !== confirmPw) {
      setPwAlert({ type: 'danger', text: 'Mật khẩu xác nhận không khớp!' });
      return;
    }
    if (!currentPw) {
      setPwAlert({ type: 'danger', text: 'Vui lòng nhập mật khẩu hiện tại!' });
      return;
    }
    setChangingPw(true);
    const res = await userService.changePassword(currentPw, newPw);
    setChangingPw(false);

    if (res?.ok && res.data?.success) {
      setPwAlert({ type: 'success', text: '✅ Đổi mật khẩu thành công!' });
      setCurrentPw('');
      setNewPw('');
      setConfirmPw('');
    } else {
      setPwAlert({ type: 'danger', text: res?.data?.message || 'Mật khẩu hiện tại không đúng.' });
    }
    setTimeout(() => setPwAlert(null), 4000);
  }

  return (
    <main className="s-main">
      <div className="s-page-title">👤 Hồ sơ cá nhân</div>
      <div className="s-page-subtitle">Quản lý thông tin tài khoản của bạn</div>

      {/* Profile Hero */}
      <div className="s-profile-hero">
        <div className="s-profile-avatar-lg" id="profileAvatarLg">
          {initials}
        </div>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '.25rem' }} id="profileName">
            {displayName || '—'}
          </h2>
          <p style={{ opacity: 0.8, marginBottom: '1rem' }} id="profileEmail">
            {user?.email || '—'}
          </p>
          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800 }} id="profileCourses">
                {coursesCount ?? '—'}
              </div>
              <div style={{ fontSize: '.78rem', opacity: 0.7 }}>Khóa học</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800 }} id="profileJoined">
                {new Date().getFullYear()}
              </div>
              <div style={{ fontSize: '.78rem', opacity: 0.7 }}>Tham gia</div>
            </div>
          </div>
        </div>
      </div>

      <div className="s-grid-2">
        {/* Update Info */}
        <div className="s-card">
          <div className="s-card-header">
            <span className="s-card-title">✏️ Cập nhật thông tin</span>
          </div>
          <div className="s-card-body">
            <div id="infoAlert">{infoAlert && <div className={`s-alert s-alert-${infoAlert.type}`}>{infoAlert.text}</div>}</div>
            <form id="infoForm" onSubmit={handleInfoSubmit}>
              <div className="s-form-group">
                <label className="s-label">Họ và tên</label>
                <input
                  className="s-input"
                  type="text"
                  placeholder="Nhập họ tên..."
                  value={fullname}
                  onChange={(e) => setFullname(e.target.value)}
                />
              </div>
              <div className="s-form-group">
                <label className="s-label">Email</label>
                <input className="s-input" type="email" value={user?.email || ''} disabled style={{ opacity: 0.6 }} readOnly />
              </div>
              <div className="s-form-group">
                <label className="s-label">Vai trò</label>
                <input
                  className="s-input"
                  type="text"
                  value={ROLE_LABELS[user?.role] || user?.role || ''}
                  disabled
                  style={{ opacity: 0.6 }}
                  readOnly
                />
              </div>
              <button type="submit" className="s-btn s-btn-primary" style={{ width: '100%' }} disabled={savingInfo}>
                {savingInfo ? '⏳ Đang lưu...' : '💾 Lưu thay đổi'}
              </button>
            </form>
          </div>
        </div>

        {/* Change Password */}
        <div className="s-card">
          <div className="s-card-header">
            <span className="s-card-title">🔒 Đổi mật khẩu</span>
          </div>
          <div className="s-card-body">
            <div id="pwAlert">{pwAlert && <div className={`s-alert s-alert-${pwAlert.type}`}>{pwAlert.text}</div>}</div>
            <form id="pwForm" onSubmit={handlePwSubmit}>
              <div className="s-form-group">
                <label className="s-label">Mật khẩu hiện tại</label>
                <input
                  className="s-input"
                  type="password"
                  placeholder="Nhập mật khẩu hiện tại..."
                  value={currentPw}
                  onChange={(e) => setCurrentPw(e.target.value)}
                />
              </div>
              <div className="s-form-group">
                <label className="s-label">Mật khẩu mới</label>
                <input
                  className="s-input"
                  type="password"
                  placeholder="Ít nhất 8 ký tự..."
                  value={newPw}
                  onChange={(e) => setNewPw(e.target.value)}
                />
              </div>
              <div className="s-form-group">
                <label className="s-label">Xác nhận mật khẩu mới</label>
                <input
                  className="s-input"
                  type="password"
                  placeholder="Nhập lại mật khẩu mới..."
                  value={confirmPw}
                  onChange={(e) => setConfirmPw(e.target.value)}
                />
              </div>
              <button type="submit" className="s-btn s-btn-outline" style={{ width: '100%' }} disabled={changingPw}>
                {changingPw ? '⏳ Đang xử lý...' : '🔑 Đổi mật khẩu'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Avatar upload card */}
      <div className="s-card" style={{ marginTop: '1.25rem' }}>
        <div className="s-card-header">
          <span className="s-card-title">🖼 Ảnh đại diện</span>
        </div>
        <div className="s-card-body" style={{ display: 'flex', alignItems: 'center', gap: '2rem', flexWrap: 'wrap' }}>
          <div
            id="avatarPreview"
            style={{
              width: 90,
              height: 90,
              borderRadius: '50%',
              background: 'linear-gradient(135deg,var(--s-primary),#8B5CF6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2rem',
              fontWeight: 800,
              color: '#fff',
            }}
          >
            {initials}
          </div>
          <div>
            <p style={{ fontSize: '.875rem', color: 'var(--s-text-muted)', marginBottom: '1rem' }}>
              Chọn ảnh JPG, PNG hoặc GIF. Tối đa 2MB.
            </p>
            <div style={{ display: 'flex', gap: '.75rem' }}>
              <button className="s-btn s-btn-outline" onClick={() => window.alert('Tính năng đang phát triển!')}>
                📂 Chọn ảnh
              </button>
              <button className="s-btn s-btn-ghost" onClick={() => window.alert('Đã xóa ảnh!')}>
                🗑 Xóa
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
