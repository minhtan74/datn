import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { recommendationService } from '../../services/recommendationService';

/** PHASE 5 — Thẻ "Gợi ý học tập cá nhân hoá" (rule-based). Tự tải dữ liệu + có nút cập nhật. */

// Tên + màu của các mức năng lực
const LEVEL = {
  Weak: { text: 'Yếu', color: '#DC2626' },
  Average: { text: 'Trung bình', color: '#D97706' },
  Good: { text: 'Khá', color: '#2563EB' },
  Excellent: { text: 'Tốt', color: '#059669' },
};

// Biểu tượng cho từng loại gợi ý (hoàn thành bài, ôn chủ đề, bài tiếp theo, làm lại quiz, lời khuyên)
const ICON = {
  finish_lessons: '📋',
  review_topic: '🔁',
  next_lesson: '▶️',
  retake_quiz: '📝',
  advice: '💡',
};

export default function RecommendationCard({ courseId = null, compact = false }) {
  const [rec, setRec] = useState(null); // current recommendation
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [updatedAt, setUpdatedAt] = useState(null);

  // Tải gợi ý hiện tại (backend tính trực tiếp từ dữ liệu học tập mới nhất)
  const load = useCallback(async () => {
    const res = await recommendationService.get(courseId);
    setRec(res?.data?.data?.current || null);
    setLoading(false);
  }, [courseId]);

  useEffect(() => {
    load();
  }, [load]);

  // Bấm "Cập nhật": tính lại gợi ý, lưu vào lịch sử và hiển thị kết quả mới
  async function handleRefresh() {
    setRefreshing(true);
    const res = await recommendationService.refresh(courseId);
    if (res?.ok && res.data?.data) {
      setRec({
        level: res.data.data.level,
        summary: res.data.data.summary,
        items: res.data.data.items || [],
        based_on: res.data.data.based_on,
      });
      setUpdatedAt(new Date());
    }
    setRefreshing(false);
  }

  const lv = rec?.level ? LEVEL[rec.level] : null;
  // Chế độ gọn (compact) chỉ hiện 3 gợi ý đầu
  const items = (rec?.items || []).slice(0, compact ? 3 : 99);

  return (
    <div className="s-card">
      <div className="s-card-header">
        <span className="s-card-title">🎯 Gợi ý học tập cho bạn</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '.6rem' }}>
          {lv && (
            <span
              className="s-badge"
              style={{ color: lv.color, background: `${lv.color}1f`, fontWeight: 700 }}
            >
              {lv.text}
            </span>
          )}
          <button
            className="s-btn s-btn-ghost s-btn-sm"
            onClick={handleRefresh}
            disabled={refreshing || loading}
            title="Tính lại gợi ý từ kết quả học tập mới nhất"
          >
            {refreshing ? 'Đang cập nhật…' : '↻ Cập nhật'}
          </button>
        </div>
      </div>
      <div className="s-card-body">
        {loading && <div style={{ color: 'var(--s-text-muted)', fontSize: '.875rem' }}>Đang tải gợi ý…</div>}

        {!loading && !rec && (
          <div style={{ color: 'var(--s-text-muted)', fontSize: '.875rem' }}>Chưa có gợi ý.</div>
        )}

        {!loading && rec && (
          <>
            <p style={{ fontWeight: 700, marginBottom: '.85rem' }}>{rec.summary}</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '.6rem' }}>
              {items.map((it, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '.6rem',
                    padding: '.6rem .75rem',
                    border: '1px solid var(--s-border)',
                    borderRadius: 8,
                    background: 'var(--s-surface-2)',
                  }}
                >
                  <span style={{ fontSize: '1rem', lineHeight: 1.4 }}>{ICON[it.type] || '•'}</span>
                  <span style={{ flex: 1, fontSize: '.86rem', lineHeight: 1.45 }}>{it.text}</span>
                  {it.action_url && (
                    <Link to={it.action_url} className="s-btn s-btn-primary s-btn-sm" style={{ flexShrink: 0 }}>
                      Đi tới
                    </Link>
                  )}
                </div>
              ))}
            </div>
            {updatedAt && (
              <p style={{ fontSize: '.72rem', color: 'var(--s-text-muted)', marginTop: '.75rem' }}>
                Đã cập nhật lúc {updatedAt.toLocaleTimeString('vi-VN')} — gợi ý sẽ thay đổi theo kết quả học tập mới của bạn.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
