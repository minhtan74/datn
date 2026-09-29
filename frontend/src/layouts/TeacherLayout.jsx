import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import '../assets/css/teacher.css';
import TeacherSidebar from '../components/teacher/TeacherSidebar.jsx';
import TeacherTopbar from '../components/teacher/TeacherTopbar.jsx';

/**
 * Shell chung cho toàn bộ khu vực /teacher/* — tương đương <aside class="sidebar">
 * + <div class="main-wrapper"> (topbar + main-content) của teacher/dashboard.html cũ.
 *
 * Bản gốc dùng URL-hash routing (#dashboard, #courses, ...) với switchView() +
 * một inline <script> duy nhất render 8 "view-panel" ẩn/hiện trong cùng 1 trang.
 * Ở bản React, mỗi view cũ giờ là 1 route con thật (index, courses, chapters, ...)
 * render qua <Outlet/> — mechanism hash-routing cũ được thay hoàn toàn.
 *
 * `sidebarOpen` (fix giao diện): studyonline.css ẩn .sidebar dưới 992px nhưng
 * bản gốc không có cơ chế nào để mở lại — thêm state + nút toggle (TeacherTopbar)
 * + overlay đóng khi bấm ra ngoài, không đổi hành vi/route nào khác.
 */
export default function TeacherLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      <div
        className={`sidebar-overlay${sidebarOpen ? ' active' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />
      <TeacherSidebar mobileOpen={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />
      <div className="main-wrapper">
        <TeacherTopbar onToggleSidebar={() => setSidebarOpen((v) => !v)} />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </>
  );
}
