// API timestamps without an offset represent local database time in Vietnam.
export function formatStudyDate(value) {
  if (!value) return 'Chưa xác định';
  let input = String(value).trim().replace(' ', 'T');
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?$/.test(input)) input += '+07:00';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return 'Chưa xác định';
  return new Intl.DateTimeFormat('vi-VN', {
    timeZone: 'Asia/Ho_Chi_Minh', day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(date);
}
