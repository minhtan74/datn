import { Routes, Route, Navigate, useLocation } from 'react-router-dom';

// Layout khung trang theo từng khu vực (công khai / học viên / admin / giảng viên)
import PublicLayout from '../layouts/PublicLayout.jsx';
import StudentLayout from '../layouts/StudentLayout.jsx';
import AdminLayout from '../layouts/AdminLayout.jsx';
import TeacherLayout from '../layouts/TeacherLayout.jsx';

// Các "cổng" kiểm tra đăng nhập và vai trò trước khi vào trang
import ProtectedRoute from './ProtectedRoute.jsx';
import PublicOnlyRoute from './PublicOnlyRoute.jsx';
import CoursesRedirect from './CoursesRedirect.jsx';

// Các trang công khai và trang học tập dùng chung
import Home from '../pages/Home.jsx';
import Login from '../pages/Login.jsx';
import Register from '../pages/Register.jsx';
import Chapters from '../pages/Chapters.jsx';
import Lesson from '../pages/Lesson.jsx';
import Quiz from '../pages/Quiz.jsx';
import QuizShow from '../pages/QuizShow.jsx';

// Trang của học viên
import StudentDashboard from '../pages/student/Dashboard.jsx';
import StudentCourses from '../pages/student/Courses.jsx';
import StudentMyCourses from '../pages/student/MyCourses.jsx';
import StudentProfile from '../pages/student/Profile.jsx';
import StudentProgress from '../pages/student/Progress.jsx';
import StudentQuizResult from '../pages/student/QuizResult.jsx';
import StudentQuizHistory from '../pages/student/QuizHistory.jsx';
import StudentAiTutor from '../pages/student/AiTutor.jsx';
import StudentPaymentResult from '../pages/student/PaymentResult.jsx';

// Trang của admin
import AdminOverview from '../pages/admin/Overview.jsx';
import AdminUsers from '../pages/admin/Users.jsx';
import AdminCourses from '../pages/admin/Courses.jsx';
import AdminReports from '../pages/admin/Reports.jsx';
import AdminPayments from '../pages/admin/Payments.jsx';

// Trang của giảng viên
import TeacherOverview from '../pages/teacher/Overview.jsx';
import TeacherCourses from '../pages/teacher/Courses.jsx';
import TeacherChapters from '../pages/teacher/Chapters.jsx';
import TeacherLessons from '../pages/teacher/Lessons.jsx';
import TeacherQuizzes from '../pages/teacher/Quizzes.jsx';
import TeacherQuizQuestions from '../pages/teacher/QuizQuestions.jsx';
import TeacherStudents from '../pages/teacher/Students.jsx';
import TeacherStats from '../pages/teacher/Stats.jsx';
import TeacherProfile from '../pages/teacher/Profile.jsx';
import TeacherDocuments from '../pages/teacher/Documents.jsx';

// Bảng định tuyến: đường dẫn URL -> trang tương ứng
// Đường dẫn cũ /teacher/ai-quiz?... -> tab AI của trang Quiz, giữ nguyên các tham số chọn sẵn khóa / chương / bài
function AiQuizRedirect() {
  const { search } = useLocation();
  const params = new URLSearchParams(search);
  params.set('tab', 'ai');
  return <Navigate to={`/teacher/quizzes?${params.toString()}`} replace />;
}

export default function AppRoutes() {
  return (
    <Routes>
      {/* Khu vực công khai: trang chủ; /login và /register chỉ dành cho người chưa đăng nhập */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<Home />} />
        <Route
          path="/login"
          element={
            <PublicOnlyRoute>
              <Login />
            </PublicOnlyRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicOnlyRoute>
              <Register />
            </PublicOnlyRoute>
          }
        />
      </Route>

      {/* /courses -> chuyển tới trang khóa học đúng với vai trò */}
      <Route path="/courses" element={<CoursesRedirect />} />

      <Route
        element={
          <ProtectedRoute>
            <StudentLayout />
          </ProtectedRoute>
        }
      >
        {/* Khu vực cần đăng nhập (mọi vai trò): học bài, làm quiz và các trang của học viên */}
        <Route path="/chapters" element={<Chapters />} />
        <Route path="/lesson" element={<Lesson />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/quiz-show" element={<QuizShow />} />
        <Route path="/student/dashboard" element={<StudentDashboard />} />
        <Route path="/student/courses" element={<StudentCourses />} />
        <Route path="/student/my-courses" element={<StudentMyCourses />} />
        <Route path="/student/profile" element={<StudentProfile />} />
        <Route path="/student/progress" element={<StudentProgress />} />
        <Route path="/student/quiz-result" element={<StudentQuizResult />} />
        <Route path="/student/quiz-history" element={<StudentQuizHistory />} />
        <Route path="/student/ai-tutor" element={<StudentAiTutor />} />
        {/* VNPay chuyển về đây (qua backend) sau khi thanh toán */}
        <Route path="/student/payment-result" element={<StudentPaymentResult />} />
      </Route>

      {/* Khu vực admin: chỉ vai trò admin */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute roles={['admin']} wrongRoleRedirect="/login" alertOnWrongRole="Bạn không có quyền truy cập trang này.">
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminOverview />} />
        {/* Quản lý User gồm 2 nhánh con: Teacher và Student */}
        <Route path="users" element={<AdminUsers roleFilter={null} />} />
        <Route path="users/teachers" element={<AdminUsers roleFilter="teacher" />} />
        <Route path="users/students" element={<AdminUsers roleFilter="student" />} />
        {/* Đường dẫn cũ -> chuyển sang đường dẫn mới nằm trong /admin/users */}
        <Route path="teachers" element={<Navigate to="/admin/users/teachers" replace />} />
        <Route path="students" element={<Navigate to="/admin/users/students" replace />} />
        <Route path="courses" element={<AdminCourses />} />
        <Route path="payments" element={<AdminPayments />} />
        <Route path="reports" element={<AdminReports />} />
      </Route>

      {/* Khu vực giảng viên: giảng viên (và admin) */}
      <Route
        path="/teacher"
        element={
          <ProtectedRoute
            roles={['teacher', 'admin']}
            wrongRoleRedirect="/login"
            alertOnWrongRole="Bạn không có quyền truy cập trang này."
          >
            <TeacherLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<TeacherOverview />} />
        <Route path="courses" element={<TeacherCourses />} />
        <Route path="chapters" element={<TeacherChapters />} />
        <Route path="lessons" element={<TeacherLessons />} />
        <Route path="quizzes" element={<TeacherQuizzes />} />
        <Route path="quizzes/:quizId/questions" element={<TeacherQuizQuestions />} />
        <Route path="students" element={<TeacherStudents />} />
        <Route path="stats" element={<TeacherStats />} />
        <Route path="profile" element={<TeacherProfile />} />
        <Route path="documents" element={<TeacherDocuments />} />
        {/* AI Quiz Generator đã gộp vào trang Quiz (tab "Tạo bằng AI"); giữ đường dẫn cũ để chuyển hướng */}
        <Route path="ai-quiz" element={<AiQuizRedirect />} />
      </Route>

      {/* Đường dẫn không tồn tại -> về trang chủ */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
