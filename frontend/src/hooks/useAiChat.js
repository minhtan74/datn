import { useCallback, useEffect, useRef, useState } from 'react';
import { aiService } from '../services/aiService';

const UNAVAILABLE = 'AI hiện chưa thể trả lời. Bạn có thể thử lại sau; câu hỏi của bạn vẫn được giữ.';
const isOldError = (text) => String(text || '').startsWith('[Lỗi gọi LLM');

// Dùng chung ở AI Tutor và bài học: mỗi trang chỉ có một lượt đang chờ, phản hồi cũ không ghi đè trang mới.
export function useAiChat({ scopeKey, setMessages, onConversationId }) {
  const [sending, setSending] = useState(false);
  const [startedAt, setStartedAt] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const activeRef = useRef(null);
  const lastAttemptRef = useRef(null);
  const turnRef = useRef(0);
  const scopeRef = useRef(scopeKey);
  const optionsRef = useRef({ setMessages, onConversationId });
  scopeRef.current = scopeKey;
  optionsRef.current = { setMessages, onConversationId };

  const invalidate = useCallback(() => {
    const active = activeRef.current;
    activeRef.current = null;
    active?.controller.abort();
  }, []);

  const reset = useCallback(() => {
    invalidate();
    lastAttemptRef.current = null;
    setSending(false);
    setStartedAt(null);
    setElapsedSeconds(0);
    setFeedback(null);
  }, [invalidate]);

  useEffect(() => {
    reset();
    return invalidate;
  }, [scopeKey, reset, invalidate]);

  useEffect(() => {
    if (startedAt == null) return;
    const tick = () => setElapsedSeconds(Math.max(0, Math.floor((Date.now() - startedAt) / 1000)));
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [startedAt]);

  const run = useCallback((attempt) => {
    if (activeRef.current) return false;
    const active = { controller: new AbortController(), scope: scopeRef.current, attempt };
    activeRef.current = active;
    lastAttemptRef.current = attempt;
    setSending(true);
    setStartedAt(Date.now());
    setElapsedSeconds(0);
    setFeedback(null);
    optionsRef.current.setMessages((prev) => prev.some((m) => m._turnId === attempt.turnId) ? prev
      : [...prev, { role: 'user', content: attempt.payload.message, _turnId: attempt.turnId }]);

    void (async () => {
      let res;
      try {
        res = await aiService.chat({ ...attempt.payload, signal: active.controller.signal });
      } catch {
        res = { ok: false, status: 0 };
      }
      if (activeRef.current !== active || scopeRef.current !== active.scope) return;
      const data = res?.data?.data;
      if (data?.conversation_id) {
        attempt.payload = { ...attempt.payload, conversationId: data.conversation_id };
        optionsRef.current.onConversationId?.(data.conversation_id);
      }
      activeRef.current = null;
      setSending(false);
      setStartedAt(null);

      if (!res?.ok || res?.data?.success === false || !data?.answer || data.response_status === 'error' || isOldError(data.answer)) {
        const timedOut = res?.timedOut || res?.status === 504;
        let message = timedOut ? 'Đã hết thời gian chờ AI. Câu hỏi vẫn được giữ để bạn thử lại.'
          : res?.status === 0 || !res ? 'Không thể kết nối tới AI. Bạn kiểm tra kết nối mạng rồi thử lại nhé.'
            : res?.status >= 500 || data?.response_status === 'error' || isOldError(data?.answer) ? UNAVAILABLE
              : res?.data?.message || 'Chưa nhận được câu trả lời. Bạn có thể sửa câu hỏi hoặc thử lại.';
        if (isOldError(message)) message = UNAVAILABLE;
        setFeedback({ kind: timedOut ? 'timeout' : res?.status === 0 || !res ? 'network' : 'error', message,
          question: attempt.payload.message, retryable: data?.retryable ?? (!res || res.status === 0 || res.status >= 500 || res.ok),
          mayFinish: !!timedOut || res?.status === 0 });
        return;
      }
      lastAttemptRef.current = null;
      optionsRef.current.setMessages((prev) => [...prev, { role: 'assistant', content: data.answer,
        sources: data.sources || [], needs_clarification: data.needs_clarification,
        response_status: data.response_status || (data.answer.includes('đây là nội dung trích trực tiếp') ? 'fallback' : 'ok') }]);
    })();
    return true;
  }, []);

  const sendMessage = useCallback((payload) => {
    if (activeRef.current || !payload.message?.trim()) return false;
    return run({ turnId: ++turnRef.current, payload: { ...payload, message: payload.message.trim() } });
  }, [run]);

  const retry = useCallback(() => {
    if (lastAttemptRef.current) return run(lastAttemptRef.current);
    return false;
  }, [run]);

  const stop = useCallback(() => {
    const active = activeRef.current;
    if (!active) return;
    invalidate();
    setSending(false);
    setStartedAt(null);
    setFeedback({ kind: 'stopped', message: 'Bạn đã dừng chờ. Câu hỏi vẫn được giữ để sửa hoặc gửi lại.',
      question: active.attempt.payload.message, retryable: true, mayFinish: true });
  }, [invalidate]);

  const loadHistory = useCallback((rows, payload) => {
    reset();
    const saved = [...rows];
    const last = saved.at(-1);
    if (last?.role === 'assistant' && (last.response_status === 'error' || isOldError(last.content))) {
      const questionIndex = saved.findLastIndex((m) => m.role === 'user');
      if (questionIndex >= 0) {
        const turnId = ++turnRef.current;
        saved[questionIndex] = { ...saved[questionIndex], _turnId: turnId };
        lastAttemptRef.current = { turnId, payload: { ...payload, message: saved[questionIndex].content } };
        saved.pop();
        setFeedback({ kind: 'error', message: UNAVAILABLE, question: saved[questionIndex].content, retryable: last.retryable !== false });
      }
    }
    optionsRef.current.setMessages(saved);
  }, [reset]);

  return { sending, elapsedSeconds, feedback, sendMessage, retry, stop, reset, loadHistory };
}
