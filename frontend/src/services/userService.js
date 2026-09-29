import axiosClient from '../api/axiosClient';

export const userService = {
  // Danh sách người dùng (chỉ admin)
  getUsers() {
    return axiosClient.get('/api/users');
  },
  // Thông tin 1 người dùng; create/update: admin tạo, sửa tài khoản (update cũng dùng cho sửa hồ sơ cá nhân)
  getUserById(id) {
    return axiosClient.get(`/api/users?id=${id}`);
  },
  createUser(data) {
    return axiosClient.post('/api/users', data);
  },
  updateUser(data) {
    return axiosClient.put('/api/users', data);
  },
  // Admin khóa / mở khóa tài khoản
  setUserStatus(id, isActive) {
    return axiosClient.put('/api/users/status', { id, is_active: isActive });
  },
  // Admin xóa tài khoản chưa có dữ liệu
  deleteUser(id) {
    return axiosClient.delete(`/api/users?id=${id}`);
  },
  // User tự đổi mật khẩu (phải nhập đúng mật khẩu cũ)
  changePassword(oldPassword, newPassword) {
    return axiosClient.post('/api/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};
