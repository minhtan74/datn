import { useEffect, useRef, useState } from 'react';
import { aiService } from '../../services/aiService';
import { enrollmentService } from '../../services/enrollmentService';

/** PHASE 6 — AI Tutor (RAG): hỏi đáp dựa trên tài liệu khóa học, có trích dẫn nguồn. */
export default function AiTutor() {
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null); // id | null (mới)
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  // engine: thông tin LLM / embedding đang dùng (hiển thị cho người học biết AI chạy online hay offline)
  const [engine, setEngine] = useState(null);
  const threadRef = useRef(null);

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
    setMessages([]);
    (async () => {
      const res = await aiService.getConversations(courseId);
      setConversations(res?.data?.data || []);
    })();
  }, [courseId]);

  // Tự cuộn khung chat xuống tin nhắn mới nhất
  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, sending]);

  // Mở lại 1 cuộc trò chuyện cũ: tải toàn bộ tin nhắn
  async function openConversation(id) {
    setActiveConv(id);
    const res = await aiService.getConversation(id);
    setMessages(res?.data?.data?.messages || []);
  }

  // Bắt đầu cuộc trò chuyện mới (xóa khung chat)
  function newConversation() {
    setActiveConv(null);
    setMessages([]);
    setInput('');
  }

  // Gửi câu hỏi: hiện câu hỏi ngay, chờ AI trả lời kèm nguồn; lỗi thì hiện thông báo thành tin nhắn của AI
  async function send(e) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || !courseId || sending) return;
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: text, _local: true }]);
    setSending(true);
    const res = await aiService.chat({ courseId, conversationId: activeConv, message: text });
    setSending(false);
    const data = res?.data?.data;
    if (!res?.ok || !data) {
      setMessages((m) => [...m, { role: 'assistant', content: res?.data?.message || 'Có lỗi xảy ra, thử lại sau.' }]);
      return;
    }
    setMessages((m) => [...m, { role: 'assistant', content: data.answer, sources: data.sources }]);
    // Cuộc trò chuyện mới vừa được tạo -> nhớ id và tải lại danh sách hội thoại bên trái
    if (!activeConv && data.conversation_id) {
      setActiveConv(data.conversation_id);
      const conv = await aiService.getConversations(courseId);
      setConversations(conv?.data?.data || []);
    }
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
        Hỏi đáp dựa trên tài liệu của khóa học — câu trả lời luôn kèm nguồn trích dẫn.
      </div>

      <div className="ai-tutor-grid">
        {/* Cột trái: chọn khóa + danh sách hội thoại */}
        <div className="s-card" style={{ position: 'sticky', top: '1rem' }}>
          <div className="s-card-body" style={{ display: 'flex', flexDirection: 'column', gap: '.75rem' }}>
            <label style={{ fontSize: '.78rem', fontWeight: 700, color: 'var(--s-text-muted)' }}>KHÓA HỌC</label>
            <select
              className="s-input"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
              style={{ padding: '.5rem', borderRadius: 8, border: '1px solid var(--s-border)' }}
            >
              {courses.length === 0 && <option value="">— Chưa đăng ký khóa nào —</option>}
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>

            <button className="s-btn s-btn-primary s-btn-sm" onClick={newConversation}>
              + Cuộc trò chuyện mới
            </button>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '.35rem', marginTop: '.25rem' }}>
              {conversations.map((c) => (
                <div
                  key={c.id}
                  onClick={() => openConversation(c.id)}
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
                    onClick={(e) => removeConversation(c.id, e)}
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

            {sending && (
              <div style={{ alignSelf: 'flex-start', color: 'var(--s-text-muted)', fontSize: '.85rem' }}>
                🤖 Đang tìm trong tài liệu…
              </div>
            )}
          </div>

          <form
            onSubmit={send}
            style={{ borderTop: '1px solid var(--s-border)', padding: '.75rem', display: 'flex', gap: '.5rem' }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={courseId ? 'Nhập câu hỏi về khóa học…' : 'Hãy chọn/đăng ký một khóa học trước'}
              disabled={!courseId || sending}
              style={{ flex: 1, padding: '.6rem .8rem', borderRadius: 8, border: '1px solid var(--s-border)' }}
            />
            <button className="s-btn s-btn-primary" type="submit" disabled={!courseId || sending || !input.trim()}>
              Gửi
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
