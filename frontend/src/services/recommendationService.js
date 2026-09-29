import axiosClient from '../api/axiosClient';

/** PHASE 5 — Rule-based Personalized Recommendation. */
export const recommendationService = {
  /** Gợi ý hiện tại (tính realtime) + lịch sử đã lưu. */
  get(courseId) {
    return axiosClient.get(courseId ? `/api/recommendations?course_id=${courseId}` : '/api/recommendations');
  },
  /** Tính lại từ dữ liệu mới nhất và lưu 1 dòng lịch sử. */
  refresh(courseId) {
    return axiosClient.post('/api/recommendations/refresh', courseId ? { course_id: courseId } : {});
  },
};
