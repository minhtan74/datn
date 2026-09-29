import axiosClient from '../api/axiosClient';

// Gọi API chương học: lấy danh sách theo khóa, lấy 1 chương, thêm / sửa / xóa
export const chapterService = {
  getChapters(courseId) {
    return axiosClient.get(`/api/chapters?course_id=${courseId}`);
  },
  getChapter(id) {
    return axiosClient.get(`/api/chapters?id=${id}`);
  },
  createChapter(data) {
    return axiosClient.post('/api/chapters', data);
  },
  updateChapter(data) {
    return axiosClient.put('/api/chapters', data);
  },
  deleteChapter(id) {
    return axiosClient.delete(`/api/chapters?id=${id}`);
  },
  // Mở bộ câu hỏi ôn tập của chương (chưa có thì backend tạo mới) -> { quiz_id }
  openReview(chapterId) {
    return axiosClient.post('/api/chapters/review', { chapter_id: chapterId });
  },
};
