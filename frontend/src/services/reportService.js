import axiosClient from '../api/axiosClient';

export const reportService = {
  /** GET /api/reports/summary?range=today|7d|30d|1y */
  getSummary(range = '7d') {
    return axiosClient.get(`/api/reports/summary?range=${range}`);
  },
  /** GET /api/reports/learning — quiz, hoàn thành bài, chủ đề yếu, AI Tutor */
  getLearning() {
    return axiosClient.get('/api/reports/learning');
  },
  /** Tải file CSV đầy đủ: type = payments | enrollments | courses | learning | topics */
  async exportCsv(type) {
    const res = await axiosClient.get(`/api/reports/export?type=${type}`, { responseType: 'blob' });
    if (!res?.ok) return false;
    // Lấy tên file từ header Content-Disposition (không có thì đặt tên mặc định)
    const disposition = res.headers?.['content-disposition'] || '';
    const match = disposition.match(/filename="?([^";]+)"?/);
    const filename = match ? match[1] : `bao-cao-${type}.csv`;
    const url = URL.createObjectURL(res.data);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return true;
  },
};
