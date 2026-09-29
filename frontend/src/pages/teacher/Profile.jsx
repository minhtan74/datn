import { useEffect, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import { userService } from '../../services/userService';

// Chữ viết tắt làm avatar
function getInitials(fullname) {
  if (!fullname) return 'TC';
  return fullname
    .split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

// Tiểu sử lưu vào users.bio qua API; bảng users chưa có cột chuyên môn nên
// specialization vẫn chỉ lưu localStorage theo user id.
const specKey = (userId) => `profile_spec_${userId}`;

/** Tương đương #profileView (view 8) của teacher/dashboard.html */
export default function TeacherProfile() {
  const { user, token, login } = useAuth();
  const { showToast } = useToast();

  const [courseCount, setCourseCount] = useState(0);
  const [studentCount, setStudentCount] = useState(0);

  const [fullname, setFullname] = useState(user?.fullname || '');
  const [displayName, setDisplayName] = useState(user?.fullname || ''); // chỉ cập nhật khi lưu thành công
  const [specialization, setSpecialization] = useState('');
  const [biography, setBiography] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);

  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [changingPw, setChangingPw] = useState(false);

  // Khi mở trang: điền form từ thông tin đăng nhập, rồi tải số khóa học, số học viên và tiểu sử (bio) từ server
  useEffect(() => {
    if (!user) return;
    setFullname(user.fullname || '');
    setDisplayName(user.fullname || '');
    setSpecialization(localStorage.getItem(specKey(user.id)) || 'Giảng viên chuyên môn');

    let cancelled = false;
    async function loadCounts() {
      const [coursesRes, enrollRes, meRes] = await Promise.all([
        courseService.getCourses(),
        enrollmentService.getEnrollments(),
        userService.getUserById(user.id),
      ]);
      const allCourses = coursesRes?.ok ? coursesRes.data.data || [] : [];
      const enrollments = enrollRes?.ok ? enrollRes.data.data || [] : [];
      if (cancelled) return;
      setBiography(meRes?.ok ? meRes.data.data?.bio || '' : '');
      setCourseCount(allCourses.filter((c) => c.teacher_id === user.id || user.role === 'admin').length);
      setStudentCount(new Set(enrollments.map((e) => e.user_id)).size);
    }
    loadCounts();
    return () => {
      cancelled = true;
    };
  }, [user]);

  // Lưu hồ sơ: họ tên + tiểu sử lên server, chuyên môn lưu localStorage
  async function handleProfileUpdate(e) {
    e.preventDefault();
    setSavingProfile(true);
    const name = fullname.trim();

    const res = await userService.updateUser({
      id: user.id,
      fullname: name,
      email: user.email,
      role: user.role,
      bio: biography.trim(),
    });
    setSavingProfile(false);

    if (res?.ok && res.data?.success) {
      localStorage.setItem(specKey(user.id), specialization.trim());

      const updatedUser = { ...user, fullname: name };
      login(token, updatedUser);
      setDisplayName(name); // chỉ cập nhật hiển thị sau khi lưu thành công

      showToast('Cập nhật thông tin hồ sơ thành công!', 'success');
    } else {
      showToast(res?.data?.message || 'Không thể cập nhật thông tin.', 'error');
    }
  }

  // Đổi mật khẩu (kiểm tra phía client rồi gọi API, backend kiểm tra mật khẩu cũ)
  async function handleChangePassword(e) {
    e.preventDefault();

    if (newPassword.length < 6) {
      showToast('Mật khẩu mới phải từ 6 ký tự trở lên.', 'error');
      return;
    }
    if (newPassword !== confirmNewPassword) {
      showToast('Mật khẩu xác nhận không khớp.', 'error');
      return;
    }
    if (!oldPassword) {
      showToast('Vui lòng nhập mật khẩu hiện tại.', 'error');
      return;
    }

    setChangingPw(true);
    const res = await userService.changePassword(oldPassword, newPassword);
    setChangingPw(false);

    if (res?.ok && res.data?.success) {
      showToast('Đổi mật khẩu thành công!', 'success');
      setOldPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } else {
      showToast(res?.data?.message || 'Mật khẩu hiện tại không đúng.', 'error');
    }
  }

  const initials = getInitials(displayName);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">👤 Hồ sơ Giảng viên</h1>
        <p className="page-subtitle">Cập nhật thông tin giảng dạy, lịch sử chuyên môn.</p>
      </div>

      <div className="profile-hero">
        <div className="avatar avatar-xl" style={{ background: 'var(--primary)', boxShadow: 'var(--shadow-lg)' }}>
          {initials}
        </div>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>{displayName || 'Loading...'}</h2>
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>{specialization}</p>
          <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem' }}>
            <div>
              <strong>{courseCount}</strong> <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>Khóa học</span>
            </div>
            <div>
              <strong>{studentCount}</strong> <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>Học viên</span>
            </div>
          </div>
        </div>
      </div>

      <div className="col-3-1">
        <div className="card">
          <div className="card-header">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>👤 Thông tin chi tiết</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleProfileUpdate}>
              <div className="form-group">
                <label className="form-label">Họ và tên</label>
                <input type="text" className="form-control" required value={fullname} onChange={(e) => setFullname(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Địa chỉ Email</label>
                <input
                  type="email"
                  className="form-control"
                  readOnly
                  style={{ background: 'var(--surface-2)', cursor: 'not-allowed' }}
                  value={user?.email || ''}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Chuyên môn giảng dạy</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Ví dụ: Lập trình Web Fullstack, Lập trình Mobile..."
                  value={specialization}
                  onChange={(e) => setSpecialization(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Giới thiệu bản thân</label>
                <textarea
                  className="form-control"
                  rows={4}
                  placeholder="Chưa có tiểu sử — giới thiệu kinh nghiệm, kỹ năng và lịch sử giảng dạy..."
                  value={biography}
                  onChange={(e) => setBiography(e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-primary btn-sm" disabled={savingProfile}>
                Lưu thay đổi
              </button>
            </form>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>🔑 Đổi mật khẩu</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleChangePassword}>
              <div className="form-group">
                <label className="form-label">Mật khẩu hiện tại</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  placeholder="••••••••"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Mật khẩu mới</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  placeholder="Tối thiểu 6 ký tự"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Xác nhận mật khẩu mới</label>
                <input
                  type="password"
                  className="form-control"
                  required
                  placeholder="••••••••"
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                />
              </div>
              <button type="submit" className="btn btn-secondary btn-sm" style={{ width: '100%' }} disabled={changingPw}>
                {changingPw ? '⏳ Đang xử lý...' : 'Cập nhật mật khẩu'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
