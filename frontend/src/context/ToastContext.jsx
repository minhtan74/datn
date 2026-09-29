import { createContext, useCallback, useRef, useState } from 'react';

// Context hiển thị thông báo nhanh (toast) ở góc màn hình, gọi bằng showToast(message, type)
export const ToastContext = createContext(null);

let idCounter = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const timers = useRef({});

  // Thêm 1 toast mới; type: success (xanh lá) / error (đỏ) / info (xanh dương)
  const showToast = useCallback((message, type = 'success') => {
    const id = ++idCounter;
    setToasts((prev) => [...prev, { id, message, type, show: false }]);

    // enter animation, tương đương setTimeout(10ms) của bản gốc
    setTimeout(() => {
      setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, show: true } : t)));
    }, 10);

    // Sau 3.5 giây: ẩn toast (hiệu ứng mờ dần 350ms) rồi xóa khỏi danh sách
    timers.current[id] = setTimeout(() => {
      setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, show: false } : t)));
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 350);
    }, 3500);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {/* Vùng chứa các toast; màu viền trái theo loại thông báo */}
      <div id="toastContainer" className="toast-container">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`toast-item${t.show ? ' toast-show' : ''}`}
            style={{
              borderLeft: `4px solid ${
                t.type === 'error' ? '#EF4444' : t.type === 'info' ? '#2563EB' : '#10B981'
              }`,
            }}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
