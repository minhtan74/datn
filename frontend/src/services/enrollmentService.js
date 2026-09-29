import axiosClient from '../api/axiosClient';

export const enrollmentService = {
  // Danh sách ghi danh (admin/giảng viên: kèm tiến độ; học viên: khóa của tôi)
  getEnrollments() {
    return axiosClient.get('/api/enrollments');
  },
  // Chỉ lấy id các khóa đã ghi danh
  getEnrolledIds() {
    return axiosClient.get('/api/enrollments?ids_only=1');
  },
  // Kiểm tra đã ghi danh 1 khóa chưa
  checkEnrolled(courseId) {
    return axiosClient.get(`/api/enrollments?course_id=${courseId}`);
  },
  // Ghi danh khóa miễn phí
  enroll(courseId) {
    return axiosClient.post('/api/enrollments', { course_id: courseId });
  },
  // Hủy ghi danh
  unenroll(courseId) {
    return axiosClient.delete(`/api/enrollments?course_id=${courseId}`);
  },
};
