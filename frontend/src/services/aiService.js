import axiosClient, { apiUrl, getToken, clearAuthStorage } from '../api/axiosClient';
import { readQuizStream } from './quizStream';

async function streamQuiz(payload, signal, onProgress) {
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, { once: true });
  if (signal?.aborted) controller.abort();
  let timedOut = false;
  const timer = setTimeout(() => { timedOut = true; controller.abort(); }, 180000);
  try {
    const token = getToken();
    const response = await fetch(apiUrl('/api/ai/generate-quiz/stream'), {
      method: 'POST', signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      if (response.status === 401) { clearAuthStorage(); window.location.href = '/login'; }
      const data = await response.json().catch(() => ({ success: false, message: 'Không sinh được câu hỏi.' }));
      return { ok: false, status: response.status, data };
    }
    return await readQuizStream(response, onProgress);
  } catch {
    const message = timedOut ? 'AI phản hồi quá lâu. Hãy giảm số câu hỏi mỗi lần sinh rồi thử lại.'
      : signal?.aborted ? 'Đã dừng chờ phản hồi.'
        : 'Kết nối AI bị gián đoạn. Các câu đã nhận được vẫn giữ trong bản nháp.';
    return { ok: false, status: 0, timedOut, cancelled: Boolean(signal?.aborted), data: { success: false, message } };
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
}

/** PHASE 6 — RAG AI Tutor. */
export const aiService = {
  // Trạng thái AI: LLM / model embedding đang dùng
  status() {
    return axiosClient.get('/api/ai/status');
  },

  // ── Hội thoại (học viên) ──────────────────────────────
  // Gửi câu hỏi cho AI Tutor (có conversationId thì hỏi tiếp cuộc trò chuyện cũ)
  chat({ courseId, lessonId = null, conversationId = null, message, signal }) {
    return axiosClient.post('/api/ai/chat', {
      course_id: courseId,
      lesson_id: lessonId,
      conversation_id: conversationId,
      message,
    }, { timeout: 120000, signal });
  },
  // Danh sách cuộc trò chuyện (lọc theo khóa nếu có)
  getConversations(courseId) {
    return axiosClient.get(courseId ? `/api/ai/conversations?course_id=${courseId}` : '/api/ai/conversations');
  },
  // Toàn bộ tin nhắn của 1 cuộc trò chuyện
  getConversation(id) {
    return axiosClient.get(`/api/ai/conversations/${id}`);
  },
  // Xóa cuộc trò chuyện
  deleteConversation(id) {
    return axiosClient.delete(`/api/ai/conversations/${id}`);
  },

  // ── Tài liệu (giảng viên) ─────────────────────────────
  // Danh sách tài liệu AI của giảng viên
  getDocuments(courseId) {
    return axiosClient.get(courseId ? `/api/ai/documents?course_id=${courseId}` : '/api/ai/documents');
  },
  // Tải tài liệu lên (multipart), báo % tiến trình qua onProgress
  uploadDocument({ file, courseId, lessonId = null, title = '' }, onProgress) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('course_id', courseId);
    if (lessonId) fd.append('lesson_id', lessonId);
    if (title) fd.append('title', title);
    return axiosClient.post('/api/ai/documents', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded / e.total) * 100));
      },
    });
  },
  // Xóa tài liệu AI
  deleteDocument(id) {
    return axiosClient.delete(`/api/ai/documents?id=${id}`);
  },

  // ── AI Quiz Generator (giảng viên) — PHASE 9 ─────────
  // Sinh bản nháp câu hỏi trắc nghiệm bằng AI
  // chapterId: sinh câu hỏi ôn tập bao quát cả chương
  // difficultyMix: { easy, medium, hard } = số câu mỗi mức độ khó (thay cho numberOfQuestions + difficulty)
  generateQuiz({ courseId, lessonId = null, chapterId = null, numberOfQuestions = 5, difficulty = 'medium', difficultyMix = null, signal, onProgress }) {
    const payload = {
      difficulty_mix: difficultyMix,
      course_id: courseId,
      lesson_id: lessonId,
      chapter_id: chapterId,
      number_of_questions: numberOfQuestions,
      difficulty,
    };
    if (onProgress) return streamQuiz(payload, signal, onProgress);
    return axiosClient.post('/api/ai/generate-quiz', payload, { timeout: 180000, signal });
  },
  // Lưu các câu hỏi đã duyệt thành quiz (có chapterId / reviewLessonId -> thêm vào bộ ôn tập của chương / bài)
  // duration / passing_score / max_attempts: cài đặt làm bài khi tạo quiz mới (null = không giới hạn)
  approveQuiz({
    courseId, lessonId = null, chapterId = null, reviewLessonId = null, title, description = '', questions,
    duration = null, passing_score = null, max_attempts = null, grading_method = null, source = 'ai',
  }) {
    return axiosClient.post('/api/ai/quiz/approve', {
      course_id: courseId,
      lesson_id: lessonId,
      chapter_id: chapterId,
      review_lesson_id: reviewLessonId,
      title,
      description,
      questions,
      duration,
      passing_score,
      max_attempts,
      grading_method,
      source,
    });
  },
};
