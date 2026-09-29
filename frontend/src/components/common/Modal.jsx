/**
 * Wrapper hành vi dùng chung cho mọi modal CRUD (đóng khi click ra ngoài / nút đóng).
 * Không áp class mặc định cứng để từng trang có thể tái dùng đúng style gốc của trang đó.
 */
export default function Modal({ open, onClose, children, overlayClassName }) {
  // Đóng thì không render gì; click vào vùng nền tối bên ngoài nội dung sẽ gọi onClose
  if (!open) return null;

  return (
    <div
      className={
        overlayClassName ||
        'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 overflow-y-auto p-4 md:p-10'
      }
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="flex min-h-full items-start md:items-center justify-center"
        onClick={(e) => {
          if (e.target === e.currentTarget) onClose();
        }}
      >
        {children}
      </div>
    </div>
  );
}

