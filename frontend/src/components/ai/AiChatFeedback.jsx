export default function AiChatFeedback({ sending, elapsedSeconds, feedback, onStop, onRetry, onEdit }) {
  if (sending) {
    const message = elapsedSeconds >= 45 ? 'AI đang mất nhiều thời gian hơn thường lệ. Bạn có thể dừng chờ; câu hỏi vẫn được giữ.'
      : elapsedSeconds >= 15 ? 'AI vẫn đang xử lý. Một số câu hỏi cần thêm thời gian.' : 'AI đang xử lý câu hỏi của bạn…';
    return (
      <div className="ai-chat-feedback ai-chat-waiting">
        <p role="status" aria-live="polite"><span className="spinner" aria-hidden="true" /> {message}</p>
        <div className="ai-chat-feedback-actions">
          <span>Đã chờ {Math.floor(elapsedSeconds / 60)}:{String(elapsedSeconds % 60).padStart(2, '0')} · Tối đa 2 phút</span>
          <button type="button" className="s-btn s-btn-outline s-btn-sm" onClick={onStop}>Dừng chờ</button>
        </div>
      </div>
    );
  }
  if (!feedback) return null;
  return (
    <div className={`ai-chat-feedback${feedback.kind === 'stopped' ? '' : ' ai-chat-failed'}`}
      role={feedback.kind === 'stopped' ? 'status' : 'alert'}>
      <strong>{feedback.kind === 'stopped' ? 'Đã dừng chờ' : feedback.kind === 'timeout' ? 'AI phản hồi quá lâu' : 'Chưa nhận được câu trả lời'}</strong>
      <p>{feedback.message}</p>
      <blockquote>{feedback.question}</blockquote>
      {feedback.mayFinish && <p className="ai-chat-feedback-note">AI có thể vẫn hoàn tất và lưu câu trả lời vào lịch sử. Bạn có thể kiểm tra lịch sử trước khi gửi lại.</p>}
      <div className="ai-chat-feedback-actions">
        {feedback.retryable && <button type="button" className="s-btn s-btn-primary s-btn-sm" onClick={onRetry}>Thử lại</button>}
        <button type="button" className="s-btn s-btn-outline s-btn-sm" onClick={() => onEdit(feedback.question)}>Sửa câu hỏi</button>
      </div>
    </div>
  );
}

export function AiReplyLabel({ message }) {
  if (message.response_status === 'error') return <span className="ai-reply-error-label">Thông báo lỗi — chưa có câu trả lời</span>;
  if (message.response_status === 'fallback') return <span className="ai-clarification-label">Trích đoạn tài liệu dự phòng — AI đang gián đoạn</span>;
  if (message.needs_clarification) return <span className="ai-clarification-label">AI cần thêm thông tin</span>;
  return null;
}
