import axiosClient from '../api/axiosClient';
const requests = new Map();
export const topicService = {
  get(courseId) {
    const key = Number(courseId);
    const cached = requests.get(key);
    if (cached && Date.now() - cached.time < 10000) return cached.promise;
    const promise = axiosClient.get(`/api/topics?course_id=${key}`);
    requests.set(key, { time: Date.now(), promise });
    return promise;
  },
  invalidate(courseId) { requests.delete(Number(courseId)); },
  create(courseId, name) { return axiosClient.post('/api/topics', { course_id: Number(courseId), name }); },
};
