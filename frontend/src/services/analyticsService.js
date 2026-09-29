import axiosClient from '../api/axiosClient';

/** PHASE 4 — Learning Analytics (dữ liệu học tập của học viên đang đăng nhập). */
export const analyticsService = {
  /** Tổng quan: điểm quiz TB, mức năng lực, tỷ lệ hoàn thành, thời gian học, số lần làm quiz. */
  getOverview(courseId) {
    return axiosClient.get(courseId ? `/api/analytics/overview?course_id=${courseId}` : '/api/analytics/overview');
  },
  /** Điểm theo topic + phân loại mạnh/yếu. */
  getTopics(courseId) {
    return axiosClient.get(courseId ? `/api/analytics/topics?course_id=${courseId}` : '/api/analytics/topics');
  },
  /** So sánh các lần làm cùng một quiz (dùng cho vòng lặp cá nhân hoá). */
  getQuizProgress(quizId) {
    return axiosClient.get(`/api/analytics/quiz-progress?quiz_id=${quizId}`);
  },
};
