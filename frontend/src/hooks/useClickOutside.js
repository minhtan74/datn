import { useEffect } from 'react';

/** Đóng dropdown khi click ra ngoài — thay cho pattern lặp lại trong student-courses.js / student-dashboard.js */
export function useClickOutside(ref, onOutsideClick) {
  useEffect(() => {
    function handleClick() {
      onOutsideClick();
    }
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [ref, onOutsideClick]);
}
