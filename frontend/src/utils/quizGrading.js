// Cách tính điểm khi học viên làm quiz nhiều lượt (khớp quizzes.grading_method ở backend)
export const GRADING_METHODS = [
  { key: 'highest', label: 'Lượt cao nhất', short: 'cao nhất' },
  { key: 'latest', label: 'Lượt làm cuối', short: 'lần cuối' },
  { key: 'first', label: 'Lượt làm đầu tiên', short: 'lần đầu' },
  { key: 'average', label: 'Trung bình các lượt', short: 'trung bình' },
];

// Tên ngắn của cách tính điểm (quiz cũ chưa có giá trị -> mặc định lượt cao nhất)
export function gradingShort(method) {
  return (GRADING_METHODS.find((m) => m.key === method) || GRADING_METHODS[0]).short;
}

// Định dạng số giây thành mm:ss
export function formatClock(sec) {
  const s = Math.max(0, sec || 0);
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
}
