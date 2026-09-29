import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { courseService } from '../../services/courseService';
import { chapterService } from '../../services/chapterService';
import { lessonService } from '../../services/lessonService';
import { quizService } from '../../services/quizService';
import { enrollmentService } from '../../services/enrollmentService';
import { paymentService } from '../../services/paymentService';
import { monthlyBars } from '../../utils/monthlyBars';
import CourseThumb from '../../components/common/CourseThumb.jsx';

// Chữ viết tắt làm avatar: 2 ký tự đầu của từ cuối trong tên
function initialsOf(name) {
  return name ? name.split(' ').pop().slice(0, 2).toUpperCase() : 'U';
}

export default function TeacherOverview() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [teacherCourses, setTeacherCourses] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [stats, setStats] = useState({ courses: 0, students: 0, lessons: 0, quizzes: 0, views: 0, revenue: 0 });

  // Khi mở trang: tải khóa học, quiz, ghi danh, giao dịch rồi tính các số liệu tổng quan của giảng viên
  useEffect(() => {
    let cancelled = false;

    async function fetchAllDashboardData() {
      setLoading(true);
      try {
        // 1. Courses
        const coursesRes = await courseService.getCourses();
        const allCourses = coursesRes?.ok ? coursesRes.data.data || [] : [];
        const myCourses = allCourses.filter((c) => c.teacher_id === user?.id || user?.role === 'admin');

        // 2. Quizzes
        const quizzesRes = await quizService.getQuizzes();
        const allQuizzes = quizzesRes?.ok ? quizzesRes.data.data || [] : [];

        // 3. Enrollments
        const enrollRes = await enrollmentService.getEnrollments();
        const allEnrollments = enrollRes?.ok ? enrollRes.data.data || [] : [];

        // 4. Payments
        const payRes = await paymentService.getPayments();
        const allPayments = payRes?.ok ? payRes.data.data || [] : [];

        // Stat: học viên (unique theo user_id trong enrollments)
        const enrolledStudentIds = [...new Set(allEnrollments.map((e) => e.user_id))];

        // Stat: quiz thuộc các khóa học của giảng viên
        const teacherCourseIds = myCourses.map((c) => c.id);
        const teacherQuizzes = allQuizzes.filter((q) => teacherCourseIds.includes(q.course_id));

        // Stat: tổng số bài học — lặp course -> chapter -> lesson (giữ nguyên
        // cách gọi tuần tự của bản gốc, không tối ưu song song).
        let totalLessonsCount = 0;
        for (const course of myCourses) {
          const chaptersRes = await chapterService.getChapters(course.id);
          const chapters = chaptersRes?.ok ? chaptersRes.data.data || [] : [];
          for (const chap of chapters) {
            const lessonsRes = await lessonService.getLessons(chap.id);
            const count = (lessonsRes?.ok ? lessonsRes.data.data || [] : []).length;
            totalLessonsCount += count;
          }
        }

        // Stat: lượt xem = tổng completed_lessons trên tất cả enrollments
        const totalCompletedLessons = allEnrollments.reduce((sum, e) => sum + Number(e.completed_lessons || 0), 0);

        // Stat: doanh thu = tổng amount của các payment đã completed
        const totalRevenue = allPayments
          .filter((p) => p.status === 'completed')
          .reduce((sum, p) => sum + Number(p.amount), 0);

        if (cancelled) return;
        setTeacherCourses(myCourses);
        setEnrollments(allEnrollments);
        setStats({
          courses: myCourses.length,
          students: enrolledStudentIds.length,
          lessons: totalLessonsCount,
          quizzes: teacherQuizzes.length,
          views: totalCompletedLessons || 0,
          revenue: totalRevenue,
        });
      } catch (err) {
        console.error('Error fetching teacher data:', err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchAllDashboardData();
    return () => {
      cancelled = true;
    };
  }, [user]);

  const recentCourses = teacherCourses.slice(0, 3);
  const recentEnrollments = enrollments.slice(0, 3);
  const courseViews = teacherCourses.slice(0, 4);
  const enrollmentBars = monthlyBars(enrollments, (e) => e.enroll_date, () => 1, (v) => `${v} lượt đăng ký`);
  const draftCount = teacherCourses.filter((c) => c.status === 'draft').length;
  const publishedCount = teacherCourses.filter((c) => c.status === 'published').length;

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Dashboard Giảng viên</h1>
        <p className="page-subtitle">Xem nhanh thông số lớp học và tiến độ đào tạo của bạn.</p>
      </div>

      {loading ? (
        <div className="loading-page">
          <div className="spinner" />
        </div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon-wrap" style={{ background: 'rgba(37,99,235,0.1)', color: 'var(--primary)' }}>
                📚
              </div>
              <div>
                <div className="stat-label">Tổng khóa học</div>
                <div className="stat-value">{stats.courses}</div>
                <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>
                  {publishedCount} xuất bản · {draftCount} bản nháp
                </span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon-wrap" style={{ background: 'rgba(16,185,129,0.1)', color: 'var(--success)' }}>
                👨‍🎓
              </div>
              <div>
                <div className="stat-label">Tổng học viên</div>
                <div className="stat-value">{stats.students}</div>
                <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>
                  {enrollments.length} lượt đăng ký
                </span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon-wrap" style={{ background: 'rgba(139,92,246,0.1)', color: 'var(--accent)' }}>
                🎥
              </div>
              <div>
                <div className="stat-label">Tổng bài học</div>
                <div className="stat-value">{stats.lessons}</div>
                <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>Trên {stats.courses} khóa học</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon-wrap" style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--warning)' }}>
                📝
              </div>
              <div>
                <div className="stat-label">Tổng Quiz</div>
                <div className="stat-value">{stats.quizzes}</div>
                <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>Bài kiểm tra trắc nghiệm</span>
              </div>
            </div>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon-wrap" style={{ background: 'rgba(6,182,212,0.1)', color: 'var(--info)' }}>
                👁️
              </div>
              <div>
                <div className="stat-label">Bài học đã hoàn thành</div>
                <div className="stat-value">{stats.views}</div>
                <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>Tổng của mọi học viên</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon-wrap" style={{ background: 'rgba(16,185,129,0.1)', color: 'var(--success)' }}>
                💵
              </div>
              <div>
                <div className="stat-label">Doanh thu tạm tính</div>
                <div className="stat-value">{stats.revenue.toLocaleString('vi-VN')}đ</div>
                <span className="stat-trend" style={{ color: 'var(--text-muted)' }}>Từ các giao dịch thành công</span>
              </div>
            </div>
          </div>

          <div className="col-3-1" style={{ marginBottom: '2rem' }}>
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>📈 Lượt đăng ký theo tháng (6 tháng gần nhất)</h3>
              <div className="bar-chart">
                {enrollmentBars.map((b) => (
                  <div className="bar-item" key={b.label}>
                    <div className="bar-value" style={{ height: `${b.height}%` }} data-tooltip={b.tooltip}></div>
                    <span className="bar-label">{b.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '1.25rem' }}>📊 Bài học đã hoàn thành theo khóa</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
                {courseViews.length > 0 ? (
                  courseViews.map((c) => {
                    const completedForCourse = enrollments
                      .filter((e) => e.course_id === c.id)
                      .reduce((sum, e) => sum + Number(e.completed_lessons || 0), 0);
                    const width = completedForCourse ? Math.min(100, completedForCourse * 10) : 0;
                    return (
                      <div key={c.id}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                          <span
                            style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 200 }}
                          >
                            {c.title}
                          </span>
                          <strong>{completedForCourse} bài hoàn thành</strong>
                        </div>
                        <div className="course-progress-bar" style={{ margin: 0 }}>
                          <div className="course-progress-fill" style={{ width: `${width}%`, background: 'var(--accent)' }}></div>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <p style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)', padding: '1rem' }}>
                    Không có dữ liệu lượt xem.
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="col-3-1">
            <div className="card">
              <div className="card-header">
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>📚 Khóa học mới đăng</h3>
                <Link to="/teacher/courses" className="btn btn-ghost btn-sm">
                  Xem tất cả
                </Link>
              </div>
              <div className="card-body" style={{ padding: 0 }}>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Thumbnail</th>
                        <th>Tên khóa học</th>
                        <th>Học viên</th>
                        <th>Giá tiền</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentCourses.length === 0 && (
                        <tr>
                          <td colSpan={4} style={{ textAlign: 'center', padding: '1rem', color: 'var(--text-muted)' }}>
                            Bạn chưa đăng khóa học nào.
                          </td>
                        </tr>
                      )}
                      {recentCourses.map((c) => {
                        const count = enrollments.filter((e) => e.course_id === c.id).length;
                        return (
                          <tr key={c.id}>
                            <td>
                              <div style={{ width: 44, height: 32, borderRadius: 'var(--radius-sm)', overflow: 'hidden', background: 'var(--primary-light)' }}>
                                <CourseThumb
                                  src={c.thumbnail}
                                  fallback="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=80&auto=format&fit=crop"
                                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                  alt={c.title}
                                />
                              </div>
                            </td>
                            <td>
                              <strong>{c.title}</strong>
                            </td>
                            <td>
                              <span className="badge badge-primary">{count} Học viên</span>
                            </td>
                            <td>
                              <strong>{Number(c.price || 0).toLocaleString()}đ</strong>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>👨‍🎓 Học viên mới đăng ký</h3>
                <Link to="/teacher/students" className="btn btn-ghost btn-sm">
                  Tất cả
                </Link>
              </div>
              <div className="card-body" style={{ padding: '1.25rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {recentEnrollments.length === 0 ? (
                    <p style={{ textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)', padding: '1rem' }}>
                      Chưa có học viên đăng ký.
                    </p>
                  ) : (
                    recentEnrollments.map((e, idx) => (
                      <div
                        key={e.id ?? idx}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.75rem',
                          paddingBottom: idx < recentEnrollments.length - 1 ? '1rem' : '0',
                          borderBottom: idx < recentEnrollments.length - 1 ? '1px solid var(--border)' : 'none',
                        }}
                      >
                        <div
                          className="avatar avatar-sm"
                          style={{
                            flexShrink: 0,
                            background: 'linear-gradient(135deg, var(--primary), var(--accent))',
                            fontWeight: 700,
                          }}
                        >
                          {initialsOf(e.user_name)}
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
                            <strong
                              style={{
                                fontSize: '0.875rem',
                                color: 'var(--text)',
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                              }}
                            >
                              {e.user_name}
                            </strong>
                          </div>
                          <p
                            style={{
                              fontSize: '0.75rem',
                              color: 'var(--text-muted)',
                              margin: '0.1rem 0 0.25rem 0',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                            }}
                          >
                            {e.user_email}
                          </p>
                          <span
                            className="badge badge-success"
                            style={{
                              fontSize: '0.7rem',
                              padding: '0.15rem 0.5rem',
                              textTransform: 'none',
                              letterSpacing: 'normal',
                              display: 'inline-block',
                              maxWidth: '100%',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {e.course_title}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
