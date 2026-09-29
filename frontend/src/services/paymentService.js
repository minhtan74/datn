import axiosClient from '../api/axiosClient';

export const paymentService = {
  // Lịch sử giao dịch (phạm vi theo vai trò)
  getPayments() {
    return axiosClient.get('/api/payments');
  },
  // Kiểm tra đã thanh toán / đã ghi danh khóa này chưa
  checkPayment(courseId) {
    return axiosClient.get(`/api/payments/check?course_id=${courseId}`);
  },
  // Thanh toán và ghi danh (khóa miễn phí thì chỉ ghi danh)
  pay(courseId, method, cardData = {}) {
    return axiosClient.post('/api/payments', { course_id: courseId, method, ...cardData });
  },
  // Tạo đơn hàng VNPay -> trả về payment_url để chuyển sang trang thanh toán VNPay
  createVnpay(courseId) {
    return axiosClient.post('/api/payments/vnpay/create', { course_id: courseId });
  },
  // Admin: danh sách giao dịch có phân trang + lọc (status, method, course_id, date_from, date_to, q)
  manage(params = {}) {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null));
    return axiosClient.get(`/api/payments/manage?${qs}`);
  },
  // Admin: đối soát 1 đơn đang chờ với VNPay / đối soát tất cả đơn đang chờ
  reconcile(id) {
    return axiosClient.post('/api/payments/reconcile', { id });
  },
  reconcileAll() {
    return axiosClient.post('/api/payments/reconcile-pending');
  },
  // Admin: hoàn tiền toàn phần 1 đơn (revokeAccess: thu hồi quyền học)
  refund(id, reason, revokeAccess) {
    return axiosClient.post('/api/payments/refund', { id, reason, revoke_access: revokeAccess });
  },
  // Trạng thái 1 đơn hàng theo mã giao dịch (dùng ở trang kết quả thanh toán)
  getStatus(ref) {
    return axiosClient.get(`/api/payments/status?ref=${encodeURIComponent(ref)}`);
  },
};
