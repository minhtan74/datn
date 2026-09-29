import axiosClient from '../api/axiosClient';

export const quizService = {
  // Danh sách quiz (theo khóa, hoặc theo vai trò nếu không truyền khóa)
  getQuizzes(courseId) {
    return courseId ? axiosClient.get(`/api/quizzes?course_id=${courseId}`) : axiosClient.get('/api/quizzes');
  },
  // Chi tiết 1 quiz; create/update/delete: quản lý quiz (giảng viên)
  getQuiz(id) {
    return axiosClient.get(`/api/quizzes?id=${id}`);
  },
  createQuiz(data) {
    return axiosClient.post('/api/quizzes', data);
  },
  updateQuiz(data) {
    return axiosClient.put('/api/quizzes', data);
  },
  deleteQuiz(id) {
    return axiosClient.delete(`/api/quizzes?id=${id}`);
  },

  // Câu hỏi của quiz (học viên nhận bản đã ẩn đáp án); các hàm sau: thêm / sửa / xóa câu hỏi
  getQuestions(quizId) {
    return axiosClient.get(`/api/quizzes/questions?quiz_id=${quizId}`);
  },
  getQuestion(id) {
    return axiosClient.get(`/api/quizzes/questions?id=${id}`);
  },
  createQuestion(data) {
    return axiosClient.post('/api/quizzes/questions', data);
  },
  updateQuestion(data) {
    return axiosClient.put('/api/quizzes/questions', data);
  },
  deleteQuestion(id) {
    return axiosClient.delete(`/api/quizzes/questions?id=${id}`);
  },

  // Nộp bài: answers dạng { [questionId]: 'A' | 'B' | 'C' | 'D' }; attemptToken bắt buộc với đề có giới hạn thời gian
  submitQuiz(quizId, answers, attemptToken = null) {
    return axiosClient.post('/api/quizzes/submit', { quiz_id: quizId, answers, attempt_token: attemptToken });
  },

  // Lịch sử làm bài của học viên (mới nhất trước), truyền quizId để lọc 1 quiz
  getResults(quizId = null) {
    return axiosClient.get(quizId ? `/api/quizzes/results?quiz_id=${quizId}` : '/api/quizzes/results');
  },
  // Xem lại 1 lượt đã nộp (cùng dạng dữ liệu với kết quả nộp bài)
  getResult(id) {
    return axiosClient.get(`/api/quizzes/results?id=${id}`);
  },

  // Đọc file Word (.docx) thành bản nháp câu hỏi (chưa lưu) — giảng viên
  importWord(file) {
    const formData = new FormData();
    formData.append('file', file);
    return axiosClient.post('/api/quizzes/import-word', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  // Tải file Word mẫu (trả về Blob)
  downloadWordTemplate() {
    return axiosClient.get('/api/quizzes/import-word/template', { responseType: 'blob' });
  },
};
