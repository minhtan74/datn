import axiosClient from '../api/axiosClient';

// Gọi API bài học: lấy danh sách theo chương, lấy 1 bài (kèm link video có chữ ký), thêm / sửa / xóa
export const lessonService = {
  getLessons(chapterId) {
    return axiosClient.get(`/api/lessons?chapter_id=${chapterId}`);
  },
  getLesson(id) {
    return axiosClient.get(`/api/lessons?id=${id}`);
  },
  createLesson(data) {
    return axiosClient.post('/api/lessons', data);
  },
  updateLesson(data) {
    return axiosClient.put('/api/lessons', data);
  },
  deleteLesson(id) {
    return axiosClient.delete(`/api/lessons?id=${id}`);
  },
  // Mở bộ câu hỏi ôn tập của bài học (chưa có thì backend tạo mới) -> { quiz_id }
  openReview(lessonId) {
    return axiosClient.post('/api/lessons/review', { lesson_id: lessonId });
  },
};
