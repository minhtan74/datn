/**
 * videoUrl.js — Tiện ích xử lý URL video, đặc biệt là YouTube
 *
 * YouTube KHÔNG cho phép dùng URL thông thường trong <video> hay <iframe>.
 * Phải chuyển sang dạng embed: https://www.youtube.com/embed/VIDEO_ID
 */

/**
 * Kiểm tra xem URL có phải YouTube không (cả youtube.com và youtu.be)
 * @param {string} url
 * @returns {boolean}
 */
export function isYoutubeUrl(url) {
  if (!url) return false;
  return url.includes('youtube.com') || url.includes('youtu.be');
}

/**
 * Trích xuất Video ID từ mọi dạng URL YouTube phổ biến:
 *  - https://www.youtube.com/watch?v=VIDEO_ID
 *  - https://youtu.be/VIDEO_ID
 *  - https://www.youtube.com/embed/VIDEO_ID  (đã là embed rồi)
 *  - https://www.youtube.com/shorts/VIDEO_ID
 *  - https://www.youtube.com/watch?v=VIDEO_ID&t=30s  (có thêm params)
 * @param {string} url
 * @returns {string|null} Video ID hoặc null nếu không tìm được
 */
export function extractYoutubeVideoId(url) {
  if (!url) return null;
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.replace('www.', '');

    // Dạng rút gọn: youtu.be/VIDEO_ID
    if (host === 'youtu.be') {
      return parsed.pathname.slice(1).split('/')[0] || null;
    }

    if (host === 'youtube.com') {
      // Dạng embed: /embed/VIDEO_ID
      if (parsed.pathname.startsWith('/embed/')) {
        return parsed.pathname.split('/embed/')[1].split('/')[0] || null;
      }
      // Dạng shorts: /shorts/VIDEO_ID
      if (parsed.pathname.startsWith('/shorts/')) {
        return parsed.pathname.split('/shorts/')[1].split('/')[0] || null;
      }
      // Dạng thông thường: /watch?v=VIDEO_ID
      const v = parsed.searchParams.get('v');
      if (v) return v;
    }
  } catch {
    // URL không hợp lệ, thử regex
    const match = url.match(/(?:v=|\/embed\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  }
  return null;
}

/**
 * Chuyển đổi bất kỳ URL YouTube nào sang URL embed chuẩn.
 * Nếu không phải YouTube thì trả về URL gốc.
 * @param {string} url
 * @returns {string|null} URL embed hoặc URL gốc
 */
export function getEmbedUrl(url) {
  if (!url) return null;
  if (!isYoutubeUrl(url)) return url; // Không phải YT → trả về nguyên

  const videoId = extractYoutubeVideoId(url);
  if (!videoId) return url; // Không trích được ID → trả về nguyên (phòng trường hợp)

  return `https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1`;
}
