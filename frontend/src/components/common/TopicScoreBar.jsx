import './TopicScoreBar.css';

const STATUS_STYLE = {
  Weak: { color: '#92400e', bg: '#fef3c7', label: 'Cần củng cố' },
  Average: { color: '#92400e', bg: '#fef3c7', label: 'Cần củng cố' },
  Good: { color: '#047857', bg: '#d1fae5', label: 'Đạt ngưỡng' },
  Excellent: { color: '#047857', bg: '#d1fae5', label: 'Đạt ngưỡng' },
  Insufficient: { color: '#64748b', bg: 'var(--s-surface-2)', label: 'Chưa đủ dữ liệu' },
};

export default function TopicScoreBar({ topic, avgScore, status = 'Insufficient', answered = 0, correct }) {
  const style = STATUS_STYLE[status] || STATUS_STYLE.Insufficient;
  const hasScore = answered > 0 && avgScore != null && Number.isFinite(Number(avgScore));
  const pct = hasScore ? Math.max(0, Math.min(100, Number(avgScore))) : null;
  const sufficient = hasScore && status !== 'Insufficient' && Boolean(STATUS_STYLE[status]);
  return <div className="topic-score">
    <div className="topic-score-row">
      <strong className="topic-score-name">{topic}</strong>
      <span className="topic-score-count">{correct != null ? `Đúng ${correct}/${answered} câu` : `${answered} câu đã trả lời`}</span>
      <span className="topic-score-status" style={{ color: style.color, background: style.bg }}>{style.label}</span>
      <span className="topic-score-percent">{pct == null ? '—' : `${pct.toLocaleString('vi-VN', { maximumFractionDigits: 1 })}%`}</span>
    </div>
    {sufficient && <div className="s-progress" aria-hidden="true"><div className="s-progress-bar" style={{ width: `${pct}%`, background: style.color }} /></div>}
  </div>;
}
