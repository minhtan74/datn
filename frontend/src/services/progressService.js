import axiosClient from '../api/axiosClient';

export const progressService = {
  /** GET /api/progress — tổng hợp tiến độ tất cả khóa học của user (bulk, 1 request) */
  getProgress() {
    return axiosClient.get('/api/progress');
  },
  // Id các bài đã hoàn thành trong 1 khóa
  getProgressByCourse(courseId) {
    return axiosClient.get(`/api/progress?course_id=${courseId}`);
  },
  // Số bài hoàn thành mỗi ngày trong 7 ngày qua (biểu đồ tuần)
  getWeeklyProgress() {
    return axiosClient.get('/api/progress?weekly=1');
  },
  /** GET /api/progress?recent=1 — danh sách bài học đã hoàn thành gần nhất (kèm tên bài, tên khóa, thời gian) */
  getRecentActivities() {
    return axiosClient.get('/api/progress?recent=1');
  },
  // Lưu số giây đã xem / đánh dấu hoàn thành bài học
  updateProgress(lessonId, watchedSec, isCompleted) {
    return axiosClient.post('/api/progress', {
      lesson_id: lessonId,
      watched_sec: watchedSec,
      is_completed: isCompleted,
    });
  },
};
