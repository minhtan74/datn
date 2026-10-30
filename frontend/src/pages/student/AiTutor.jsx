import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { aiService } from '../../services/aiService';
import { enrollmentService } from '../../services/enrollmentService';
import { useAiChat } from '../../hooks/useAiChat';
import AiChatFeedback, { AiReplyLabel } from '../../components/ai/AiChatFeedback.jsx';

/** PHASE 6 — AI Tutor (RAG): hỏi đáp dựa trên tài liệu khóa học, có trích dẫn nguồn. */
export default function AiTutor() {
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null); // id | null (mới)
  const [activeLessonId, setActiveLessonId] = useState(null);
  const [openingConversation, setOpeningConversation] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  // engine: thông tin LLM / embedding đang dùng (hiển thị cho người học biết AI chạy online hay offline)
  const [engine, setEngine] = useState(null);
  const threadRef = useRef(null);
  const chat = useAiChat({ scopeKey: `course-${courseId}`, setMessages, onConversationId: setActiveConv });
  const { sending } = chat;

  // Tải khóa học đã đăng ký + trạng thái engine
  useEffect(() => {
    (async () => {
      const [enr, st] = await Promise.all([enrollmentService.getEnrollments(), aiService.status()]);
      const list = (enr?.data?.data || []).map((e) => ({
        id: e.course_id ?? e.id,
        title: e.title || e.course_title || `Khóa #${e.course_id}`,
      }));
      setCourses(list);
      if (list.length) setCourseId(String(list[0].id));
      setEngine(st?.data?.data || null);
    })();
  }, []);

  // Khi đổi khóa học -> tải danh sách hội thoại, mở về "cuộc trò chuyện mới"
  useEffect(() => {
    if (!courseId) return;
    setActiveConv(null);
    setActiveLessonId(null);
    setMessages([]);
    setInput('');
  }, [courseId]);

  useEffect(() => {
    if (!courseId) return;
    let cancelled = false;
    (async () => {
      const res = await aiService.getConversations(courseId);
      if (!cancelled) setConversations(res?.data?.data || []);
    })();
    return () => { cancelled = true; };
  }, [courseId, activeConv]);

  // Tự cuộn khung chat xuống tin nhắn mới nhất
  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, sending, chat.feedback]);

  // Mở lại 1 cuộc trò chuyện cũ: tải toàn bộ tin nhắn
  async function openConversation(id) {
    if (sending || openingConversation) return;
    setOpeningConversation(true);
    const res = await aiService.getConversation(id);
    setOpeningConversation(false);
    if (!res?.ok) return;
    setActiveConv(id);
    const lessonId = res.data?.data?.conversation?.lesson_id ?? null;
    setActiveLessonId(lessonId);
    chat.loadHistory(res?.data?.data?.messages || [], { courseId, lessonId, conversationId: id });
    setInput('');
  }

  // Bắt đầu cuộc trò chuyện mới (xóa khung chat)
  function newConversation() {
    chat.reset();
    setActiveConv(null);
    setActiveLessonId(null);
    setMessages([]);
    setInput('');
  }

  // Lỗi/chờ có vùng phản hồi riêng, không đưa lỗi dịch vụ vào câu trả lời kiến thức.
  function send(e) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || !courseId || sending || openingConversation) return;
    if (chat.sendMessage({ courseId, lessonId: activeLessonId, conversationId: activeConv, message: text })) setInput('');
  }

  // Xóa 1 cuộc trò chuyện (stopPropagation để không đồng thời mở nó ra)
  async function removeConversation(id, ev) {
    ev.stopPropagation();
    if (!window.confirm('Xóa cuộc trò chuyện này?')) return;
    await aiService.deleteConversation(id);
    setConversations((c) => c.filter((x) => x.id !== id));
    if (activeConv === id) newConversation();
  }

  return (
    <main className="s-main">
      <div className="s-page-title">🤖 AI Tutor</div>
      <div className="s-page-subtitle">
        Hỏi đáp dựa trên tài liệu của khóa học, có nguồn trích dẫn. AI sẽ hỏi thêm khi cần làm rõ câu hỏi.
      </div>

      <div className="ai-tutor-grid">
        {/* Cột trái: chọn khóa + danh sách hội thoại */}
        <div className="s-card" style={{ position: 'sticky', top: '1rem' }}>
          <div className="s-card-body" style={{ display: 'flex', flexDirection: 'column', gap: '.75rem' }}>
            <label htmlFor="ai-tutor-course" style={{ fontSize: '.78rem', fontWeight: 700, color: 'var(--s-text-muted)' }}>KHÓA HỌC</label>
            <select
              id="ai-tutor-course"
              className="s-input"
              value={courseId}
              disabled={sending || openingConversation}
              onChange={(e) => setCourseId(e.target.value)}
              style={{ padding: '.5rem', borderRadius: 8, border: '1px solid var(--s-border)' }}
            >
              {courses.length === 0 && <option value="">— Chưa đăng ký khóa nào —</option>}
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>

            <button className="s-btn s-btn-primary s-btn-sm" onClick={newConversation} disabled={sending || openingConversation}>
              + Cuộc trò chuyện mới
            </button>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '.35rem', marginTop: '.25rem' }}>
              {conversations.map((c) => (
                <div
                  key={c.id}
                  onClick={() => { if (!sending && !openingConversation) openConversation(c.id); }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '.4rem',
                    padding: '.5rem .6rem',
                    borderRadius: 8,
                    cursor: 'pointer',
                    fontSize: '.82rem',
                    background: activeConv === c.id ? 'var(--s-primary)' : 'var(--s-surface-2)',
                    color: activeConv === c.id ? '#fff' : 'inherit',
                    border: '1px solid var(--s-border)',
                  }}
                >
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    💬 {c.title}
                  </span>
                  <span
                    onClick={(e) => { if (!sending && !openingConversation) removeConversation(c.id, e); }}
                    title="Xóa"
                    style={{ flexShrink: 0, opacity: 0.7 }}
                  >
                    ✕
                  </span>
                </div>
              ))}
              {conversations.length === 0 && (
                <div style={{ fontSize: '.78rem', color: 'var(--s-text-muted)' }}>Chưa có cuộc trò chuyện.</div>
              )}
            </div>

            {engine && (
              <div style={{ fontSize: '.68rem', color: 'var(--s-text-muted)', marginTop: '.5rem', lineHeight: 1.5 }}>
                LLM: {engine.llm?.provider} / {engine.llm?.model}<br />
                Embedding: {engine.embedding?.model?.split('/').pop()}
              </div>
            )}
          </div>
        </div>

        {/* Cột phải: khung chat */}
        <div className="s-card ai-tutor-chat" style={{ display: 'flex', flexDirection: 'column', height: '70vh' }}>
          {activeLessonId && (
            <div className="ai-scope-note">
              Hội thoại này hỏi trong phạm vi tài liệu của bài học.{' '}
              <Link to={`/lesson?id=${activeLessonId}`}>Mở bài học</Link>
            </div>
          )}
          <div
            ref={threadRef}
            style={{ flex: 1, overflowY: 'auto', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}
          >
            {messages.length === 0 && !sending && (
              <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--s-text-muted)', maxWidth: 420 }}>
                <div style={{ fontSize: '2.5rem' }}>🤖</div>
                <p style={{ fontWeight: 700, marginTop: '.5rem' }}>Xin chào! Mình là trợ giảng AI.</p>
                <p style={{ fontSize: '.85rem' }}>
                  Hãy hỏi mình bất cứ điều gì về nội dung khóa học. Ví dụ: “HTTP là gì?”,
                  “Promise có những trạng thái nào?”. Mình chỉ trả lời dựa trên tài liệu của khóa.
                </p>
              </div>
            )}

            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '80%',
                }}
              >
                <div
                  style={{
                    padding: '.7rem .9rem',
                    borderRadius: 12,
                    fontSize: '.88rem',
                    lineHeight: 1.5,
                    whiteSpace: 'pre-wrap',
                    background: m.role === 'user' ? 'var(--s-primary)' : 'var(--s-surface-2)',
                    color: m.role === 'user' ? '#fff' : 'inherit',
                    border: m.role === 'user' ? 'none' : '1px solid var(--s-border)',
                  }}
                >
                  <AiReplyLabel message={m} />
                  {m.content}
                </div>
                {m.role === 'assistant' && Array.isArray(m.sources) && m.sources.length > 0 && (
                  <div style={{ marginTop: '.4rem', display: 'flex', flexWrap: 'wrap', gap: '.35rem' }}>
                    {m.sources.map((s, j) => (
                      <span
                        key={j}
                        style={{
                          fontSize: '.7rem',
                          padding: '.2rem .5rem',
                          borderRadius: 999,
                          background: 'rgba(37,99,235,.1)',
                          color: 'var(--s-primary)',
                          fontWeight: 600,
                        }}
                      >
                        📄 {s.document}{s.page ? ` — tr. ${s.page}` : ''}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            <AiChatFeedback sending={sending} elapsedSeconds={chat.elapsedSeconds} feedback={chat.feedback}
              onStop={chat.stop} onRetry={chat.retry} onEdit={setInput} />
          </div>

          <form
            onSubmit={send}
            style={{ borderTop: '1px solid var(--s-border)', padding: '.75rem', display: 'flex', gap: '.5rem' }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              aria-label="Câu hỏi cho AI Tutor"
              placeholder={courseId ? messages.at(-1)?.needs_clarification ? 'Bổ sung thông tin AI đang hỏi…' : 'Nhập câu hỏi về khóa học…' : 'Hãy chọn/đăng ký một khóa học trước'}
              disabled={!courseId || sending || openingConversation}
              style={{ flex: 1, minWidth: 0, padding: '.6rem .8rem', borderRadius: 8, border: '1px solid var(--s-border)' }}
            />
            <button className="s-btn s-btn-primary" type="submit" disabled={!courseId || sending || openingConversation || !input.trim()}>
              Gửi
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
