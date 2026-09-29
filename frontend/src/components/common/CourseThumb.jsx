import { useEffect, useState } from 'react';

/**
 * Ảnh bìa khóa học có dự phòng: không có ảnh hoặc ảnh lỗi (đường dẫn hỏng, file đã xóa)
 * thì hiện `fallback` thay cho biểu tượng ảnh vỡ của trình duyệt.
 * fallback là URL ảnh -> hiện ảnh đó; là chữ / emoji / JSX -> hiện nguyên như vậy.
 */
export default function CourseThumb({ src, alt = '', fallback = '📘', style, className }) {
  const [broken, setBroken] = useState(false);

  // Đổi ảnh (vd sửa khóa học) -> thử tải lại ảnh mới
  useEffect(() => {
    setBroken(false);
  }, [src]);

  if (!src || broken) {
    if (typeof fallback === 'string' && /^https?:\/\//.test(fallback)) {
      return <img src={fallback} alt={alt} style={style} className={className} />;
    }
    return fallback;
  }
  return <img src={src} alt={alt} style={style} className={className} onError={() => setBroken(true)} />;
}
