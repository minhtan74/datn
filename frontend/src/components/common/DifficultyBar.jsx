// Các mức độ khó: nhãn tiếng Việt + màu hiển thị
export const DIFFICULTY_LEVELS = [
  { key: 'easy', label: 'Dễ', color: '#059669' },
  { key: 'medium', label: 'Trung bình', color: '#D97706' },
  { key: 'hard', label: 'Khó', color: '#DC2626' },
];

/**
 * Thanh phân bổ độ khó của một đề: thanh ngang chia theo tỉ lệ + chú thích số câu / % từng mức.
 * questions: mảng câu hỏi có trường difficulty ('easy' | 'medium' | 'hard' | rỗng = chưa gắn).
 */
export default function DifficultyBar({ questions }) {
  const total = questions.length;
  if (!total) return null;

  // Đếm số câu từng mức; câu chưa gắn độ khó gom vào nhóm riêng
  const counts = Object.fromEntries(DIFFICULTY_LEVELS.map((d) => [d.key, 0]));
  let unset = 0;
  questions.forEach((q) => {
    if (q.difficulty in counts) counts[q.difficulty] += 1;
    else unset += 1;
  });
  const segments = [
    ...DIFFICULTY_LEVELS.map((d) => ({ ...d, count: counts[d.key] })),
    { key: 'unset', label: 'Chưa gắn', color: '#94A3B8', count: unset },
  ].filter((s) => s.count > 0);
  const pct = (n) => Math.round((n / total) * 100);

  return (
    <div style={{ margin: '0.75rem 0 1.25rem' }}>
      <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.4rem' }}>
        Phân bổ độ khó ({total} câu)
      </div>
      <div
        style={{ display: 'flex', height: 10, borderRadius: 999, overflow: 'hidden', background: 'var(--border, #e2e8f0)' }}
        role="img"
        aria-label={segments.map((s) => `${s.label} ${s.count} câu`).join(', ')}
      >
        {segments.map((s) => (
          <div key={s.key} title={`${s.label}: ${s.count} câu`} style={{ width: `${pct(s.count)}%`, background: s.color }} />
        ))}
      </div>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.4rem', fontSize: '0.78rem' }}>
        {segments.map((s) => (
          <span key={s.key} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ width: 8, height: 8, borderRadius: 2, background: s.color, display: 'inline-block' }} />
            {s.label}: <strong>{s.count}</strong> ({pct(s.count)}%)
          </span>
        ))}
      </div>
    </div>
  );
}
