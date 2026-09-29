import { useCallback, useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import StudentSidebar from '../components/layout/StudentSidebar.jsx';
import StudentHeader from '../components/layout/StudentHeader.jsx';

// Key localStorage nhớ trạng thái thu gọn sidebar giữa các lần mở trang
const COLLAPSED_KEY = 'sidebar_collapsed';

/** Tương đương shell chung .student-layout / .s-sidebar / .s-wrapper của mọi trang student cũ */
export default function StudentLayout() {
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem(COLLAPSED_KEY) === '1');
  const [mobileOpen, setMobileOpen] = useState(false);

  // body cần class 'student-layout' để CSS gốc (student.css) áp đúng layout
  useEffect(() => {
    document.body.classList.add('student-layout');
    return () => document.body.classList.remove('student-layout');
  }, []);

  // Thêm/bỏ class thu gọn sidebar trên body theo trạng thái
  useEffect(() => {
    document.body.classList.toggle('sidebar-collapsed', collapsed);
  }, [collapsed]);

  // Nút menu: trên điện thoại (<= 768px) thì mở/đóng sidebar trượt; trên máy tính thì thu gọn/mở rộng và ghi nhớ
  const toggleSidebar = useCallback(() => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
      setMobileOpen((v) => !v);
    } else {
      setCollapsed((v) => {
        const next = !v;
        localStorage.setItem(COLLAPSED_KEY, next ? '1' : '0');
        return next;
      });
    }
  }, []);

  return (
    <>
      {mobileOpen && (
        <div
          id="sidebarOverlay"
          className="active"
          style={{
            display: 'block',
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,.5)',
            zIndex: 150,
            transition: '.2s',
          }}
          onClick={() => setMobileOpen(false)}
        />
      )}

      <StudentSidebar collapsed={collapsed} mobileOpen={mobileOpen} />

      <div className="s-wrapper">
        <StudentHeader onToggleSidebar={toggleSidebar} />
        <Outlet />
      </div>
    </>
  );
}
