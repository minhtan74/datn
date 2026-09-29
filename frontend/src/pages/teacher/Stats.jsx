import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import { paymentService } from '../../services/paymentService';
import { monthlyBars } from '../../utils/monthlyBars';

/** Tương đương #statsView (view 7) của teacher/dashboard.html — renderStats() */
export default function TeacherStats() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [teacherCourses, setTeacherCourses] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [payments, setPayments] = useState([]);

  // Khi mở trang: tải song song khóa học, ghi danh và giao dịch (backend đã lọc theo giảng viên)
  useEffect(() => {
    let cancelled = false;
    async function loadData() {
      setLoading(true);
      const [coursesRes, enrollRes, payRes] = await Promise.all([
        courseService.getCourses(),
        enrollmentService.getEnrollments(),
        paymentService.getPayments(),
      ]);
      const allCourses = coursesRes?.ok ? coursesRes.data.data || [] : [];
      if (cancelled) return;
      setTeacherCourses(allCourses.filter((c) => c.teacher_id === user?.id || user?.role === 'admin'));
      setEnrollments(enrollRes?.ok ? enrollRes.data.data || [] : []);
      setPayments(payRes?.ok ? payRes.data.data || [] : []);
      setLoading(false);
    }
    loadData();
    return () => {
      cancelled = true;
    };
  }, [user]);

  // Tỷ lệ hoàn thành = tổng bài đã học xong / tổng bài phải học, cộng trên mọi lượt ghi danh
  const completionRate = useMemo(() => {
    let totalCompleted = 0;
    let totalLessons = 0;
    enrollments.forEach((e) => {
      totalCompleted += Number(e.completed_lessons || 0);
      totalLessons += Number(e.total_lessons || 0);
    });
    return totalLessons > 0 ? Math.round((totalCompleted / totalLessons) * 100) : 0;
  }, [enrollments]);

  // Tổng doanh thu (giao dịch thành công), hiển thị theo đơn vị triệu đồng
  const revenueDisplay = useMemo(() => {
    const totalRevenue = payments.filter((p) => p.status === 'completed').reduce((sum, p) => sum + Number(p.amount), 0);
    return (totalRevenue / 1000000).toFixed(1) + 'Mđ';
  }, [payments]);

  // Dữ liệu biểu đồ cột doanh thu theo tháng
  const revenueBars = useMemo(
    () =>
      monthlyBars(
        payments.filter((p) => p.status === 'completed'),
        (p) => p.paid_at,
        (p) => p.amount,
        (v) => Number(v).toLocaleString('vi-VN') + 'đ',
      ),
    [payments],
  );

  // Top 3 khóa học có nhiều học viên nhất
  const topCourses = useMemo(() => {
    const sorted = [...teacherCourses].sort((a, b) => {
      const countA = enrollments.filter((e) => e.course_id === a.id).length;
      const countB = enrollments.filter((e) => e.course_id === b.id).length;
      return countB - countA;
    });
    return sorted.slice(0, 3).map((c, i) => ({
      course: c,
      count: enrollments.filter((e) => e.course_id === c.id).length,
      rank: i + 1,
    }));
  }, [teacherCourses, enrollments]);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">📈 Thống kê &amp; Doanh thu</h1>
        <p className="page-subtitle">Đo lường mức độ hoàn thành và tăng trưởng thu nhập.</p>
      </div>

      {loading ? (
        <div className="loading-page">
          <div className="spinner" />
        </div>
      ) : (
        <>
          <div className="grid grid-2" style={{ marginBottom: '2rem' }}>
            <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
              <span style={{ fontSize: '2.5rem' }}>🎓</span>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--primary)', margin: '0.5rem 0' }}>{completionRate}%</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Tỷ lệ hoàn thành khóa học</p>
            </div>
            <div className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
              <span style={{ fontSize: '2.5rem' }}>💵</span>
              <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--success)', margin: '0.5rem 0' }}>{revenueDisplay}</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Doanh thu tạm tính</p>
            </div>
          </div>

          <div className="col-3-1">
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>📈 Doanh thu theo tháng (6 tháng gần nhất)</h3>
              <div className="bar-chart">
                {revenueBars.map((b) => (
                  <div className="bar-item" key={b.label}>
                    <div className="bar-value" style={{ height: `${b.height}%`, background: 'var(--success)' }} data-tooltip={b.tooltip}></div>
                    <span className="bar-label">{b.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '1.25rem' }}>🔥 Top khóa học phổ biến nhất</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {topCourses.length === 0 && (
                  <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem' }}>Chưa có khóa học.</p>
                )}
                {topCourses.map(({ course, count, rank }) => (
                  <div
                    key={course.id}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      borderBottom: '1px solid var(--border)',
                      paddingBottom: '0.5rem',
                    }}
                  >
                    <div>
                      <strong style={{ fontSize: '0.9rem' }}>{course.title}</strong>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {count} học viên đăng ký
                      </div>
                    </div>
                    <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                      Top {rank}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
