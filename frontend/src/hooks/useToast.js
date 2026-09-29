import { useContext } from 'react';
import { ToastContext } from '../context/ToastContext.jsx';

// Hook lấy hàm showToast để hiện thông báo
export function useToast() {
  return useContext(ToastContext);
}
