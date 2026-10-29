import { useEffect, useState } from 'react';
import { formatStudyDate } from '../../utils/studyDate';
import { recommendationService } from '../../services/recommendationService';

export default function StudyProgressPanel({ refreshKey, courseId = null }) {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState('');
  useEffect(() => {
    let alive = true;
    setRows([]);
    setError('');
    recommendationService.progress(courseId).then((res) => {
      if (!alive) return;
      setRows(res?.data?.data || []);
      setError(res?.ok ? '' : 'Không tải được lịch sử ôn tập.');
    });
    return () => { alive = false; };
  }, [refreshKey, courseId]);
  return <details style={{ marginTop: '1rem' }}>
    <summary style={{ cursor: 'pointer', fontWeight: 600 }}>Kết quả trước/sau khi mở gợi ý ôn ({rows.length})</summary>
    {error && <p role="alert">{error}</p>}
    {!error && !rows.length && <p style={{ fontSize: '.8rem' }}>Bấm Ôn bài học hoặc Làm bài luyện trong gợi ý để ghi nhận mốc. Sau khi nộp bài mới, bấm Cập nhật để xem thay đổi.</p>}
    {rows.map((r) => <div key={`${r.checkpoint_kind || 'topic'}-${r.id}`} style={{ marginTop: '.75rem', borderTop: '1px solid var(--s-border)', paddingTop: '.75rem', fontSize: '.8rem' }}>
      <strong>{r.topic} · {r.course_title}</strong>
      <p>Mở gợi ý lúc {formatStudyDate(r.started_at)}.</p>
      <div style={{ overflowX: 'auto' }}><table style={{ width: '100%', textAlign: 'left' }}>
        <thead><tr><th>Mốc</th><th>Số câu đúng</th><th>Tỷ lệ đúng</th></tr></thead>
        <tbody><tr><td>Trước</td><td>{r.before.correct}/{r.before.answered}</td><td>{r.before.avg_score}%</td></tr>
          <tr><td>Sau</td><td>{r.after ? `${r.after.correct}/${r.after.answered}` : 'Chờ bài làm mới'}</td><td>{r.after ? `${r.after.avg_score}%` : '—'}</td></tr></tbody>
      </table></div>
      {r.after && <>
        <p>Chênh lệch: {r.difference_pct > 0 ? '+' : ''}{r.difference_pct} điểm phần trăm.
          {!r.sufficient_data && ' Một trong hai mốc chưa đủ 5 câu; chỉ tham khảo.'}</p>
        <p style={{ color: 'var(--s-text-muted)' }}>{r.note}</p>
      </>}
    </div>)}
  </details>;
}
