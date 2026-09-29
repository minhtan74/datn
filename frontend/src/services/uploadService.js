import axiosClient from '../api/axiosClient';

/**
 * Upload file video hoặc PDF lên server.
 * @param {File} file - File object từ <input type="file">
 * @param {'video'|'document'} type - Loại file
 * @param {function} onProgress - callback(percent: number)
 * @returns {Promise} axios response
 */
export function uploadFile(file, type = 'document', onProgress) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', type);

  return axiosClient.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        const pct = Math.round((event.loaded / event.total) * 100);
        onProgress(pct);
      }
    },
  });
}
