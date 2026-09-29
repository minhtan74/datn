/** Thanh điểm 1 topic + nhãn trạng thái (Weak/Average/Good/Excellent). PHASE 4. */
// Màu chữ, màu nền và nhãn cho từng mức năng lực
const STATUS_STYLE = {
  Weak: { color: '#DC2626', bg: 'rgba(220,38,38,.12)', label: 'Yếu' },
  Average: { color: '#D97706', bg: 'rgba(217,119,6,.12)', label: 'Trung bình' },
  Good: { color: '#2563EB', bg: 'rgba(37,99,235,.12)', label: 'Khá' },
  Excellent: { color: '#059669', bg: 'rgba(5,150,105,.12)', label: 'Tốt' },
};

export default function TopicScoreBar({ topic, avgScore = 0, status = 'Average', answered = 0 }) {
  const s = STATUS_STYLE[status] || STATUS_STYLE.Average;
  // Giới hạn điểm trong khoảng 0–100 để vẽ thanh
  const pct = Math.max(0, Math.min(100, Math.round(avgScore)));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '.35rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '.75rem' }}>
        <span style={{ fontWeight: 600, fontSize: '.85rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {topic}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', flexShrink: 0 }}>
          <span style={{ fontSize: '.72rem', color: 'var(--s-text-muted)' }}>{answered} câu</span>
          <span
            style={{
              fontSize: '.68rem',
              fontWeight: 700,
              padding: '.1rem .45rem',
              borderRadius: 999,
              color: s.color,
              background: s.bg,
            }}
          >
            {s.label}
          </span>
          <span style={{ fontWeight: 800, color: s.color, minWidth: 38, textAlign: 'right' }}>{pct}%</span>
        </div>
      </div>
      <div className="s-progress">
        <div className="s-progress-bar" style={{ width: `${pct}%`, background: s.color }} />
      </div>
    </div>
  );
}
