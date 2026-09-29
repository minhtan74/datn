import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import AdminSidebar from '../components/admin/AdminSidebar.jsx';
import AdminTopbar from '../components/admin/AdminTopbar.jsx';
import '../assets/css/admin.css';

/**
 * Tương đương <body> của _legacy/pages/admin/dashboard.html (sidebar + main-wrapper).
 * Auth/role guard đã được xử lý ở router (ProtectedRoute roles=['admin']),
 * nên component này không cần lặp lại IIFE kiểm tra quyền của bản gốc.
 * Hash-router (#dashboard/#users/...) cũ được thay bằng route lồng nhau thật + <Outlet/>.
 *
 * `sidebarOpen` (fix giao diện): studyonline.css ẩn .sidebar dưới 992px nhưng
 * bản gốc không có cơ chế nào để mở lại — thêm state + nút toggle (AdminTopbar)
 * + overlay đóng khi bấm ra ngoài, không đổi hành vi/route nào khác.
 */
export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      <div
        className={`sidebar-overlay${sidebarOpen ? ' active' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />
      <AdminSidebar mobileOpen={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />
      <div className="main-wrapper">
        <AdminTopbar onToggleSidebar={() => setSidebarOpen((v) => !v)} />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </>
  );
}
