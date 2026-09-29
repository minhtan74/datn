import axiosClient from '../api/axiosClient';

// Gọi API khóa học: lấy danh sách (lọc theo quyền ở backend), lấy 1 khóa, thêm / sửa / xóa
export const courseService = {
  getCourses() {
    return axiosClient.get('/api/courses');
  },
  getCourse(id) {
    return axiosClient.get(`/api/courses?id=${id}`);
  },
  createCourse(data) {
    return axiosClient.post('/api/courses', data);
  },
  updateCourse(data) {
    return axiosClient.put('/api/courses', data);
  },
  deleteCourse(id) {
    return axiosClient.delete(`/api/courses?id=${id}`);
  },
};
