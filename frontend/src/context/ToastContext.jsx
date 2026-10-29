import { createContext, useCallback, useEffect, useRef, useState } from 'react';
import './ToastContext.css';

export const ToastContext = createContext(null);
let idCounter = 0;
const TYPES = {
  success: { icon: '✓', label: 'Thành công' },
  error: { icon: '!', label: 'Có lỗi xảy ra' },
  info: { icon: 'i', label: 'Thông báo' },
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const timers = useRef(new Map());
  const dismissToast = useCallback((id) => {
    clearTimeout(timers.current.get(id));
    timers.current.delete(id);
    setToasts((previous) => previous.filter((toast) => toast.id !== id));
  }, []);
  const showToast = useCallback((message, type = 'success') => {
    const id = ++idCounter;
    const kind = TYPES[type] ? type : 'info';
    setToasts((previous) => [...previous, { id, message, type: kind }].slice(-4));
    timers.current.set(id, setTimeout(() => dismissToast(id), kind === 'error' ? 8000 : 6000));
    return id;
  }, [dismissToast]);
  useEffect(() => () => {
    timers.current.forEach((timer) => clearTimeout(timer));
    timers.current.clear();
  }, []);
  return <ToastContext.Provider value={{ showToast }}>
    {children}
    <div id="toastContainer" className="app-toast-container" aria-label="Thông báo">
      {toasts.map((toast) => <div key={toast.id} className={`app-toast app-toast-${toast.type}`} role={toast.type === 'error' ? 'alert' : 'status'} aria-atomic="true">
        <span className="app-toast-icon" aria-hidden="true">{TYPES[toast.type].icon}</span>
        <div className="app-toast-content"><strong>{TYPES[toast.type].label}</strong><p>{toast.message}</p></div>
        <button type="button" className="app-toast-close" aria-label="Đóng thông báo" onClick={() => dismissToast(toast.id)}>×</button>
      </div>)}
    </div>
  </ToastContext.Provider>;
}
