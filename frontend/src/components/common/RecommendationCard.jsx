import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { recommendationService } from '../../services/recommendationService';
import StudyProgressPanel from './StudyProgressPanel.jsx';
import KnowledgeAssessment from './KnowledgeAssessment.jsx';
import { formatStudyDate } from '../../utils/studyDate';
import { useToast } from '../../hooks/useToast';

/** PHASE 5 — Thẻ "Gợi ý học tập cá nhân hoá" (rule-based). Tự tải dữ liệu + có nút cập nhật. */

// Tên + màu của các mức năng lực
const LEVEL = {
  Weak: { text: 'Yếu', color: '#DC2626' },
  Average: { text: 'Trung bình', color: '#D97706' },
  Good: { text: 'Khá', color: '#2563EB' },
  Excellent: { text: 'Tốt', color: '#059669' },
  Insufficient: { text: 'Chưa đủ dữ liệu', color: '#64748B' },
  ContentBased: { text: 'Theo kiến thức', color: '#2563EB' },
};

// Biểu tượng cho từng loại gợi ý (hoàn thành bài, ôn chủ đề, bài tiếp theo, làm lại quiz, lời khuyên)
const ICON = {
  finish_lessons: '📋',
  review_topic: '🔁',
  review_knowledge: '📖',
  practice_topic: '🔎',
  next_lesson: '▶️',
  retake_quiz: '📝',
  advice: '💡',
};

export default function RecommendationCard({ courseId = null, compact = false, title = 'Gợi ý học tập cho bạn' }) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [rec, setRec] = useState(null); // current recommendation
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [updatedAt, setUpdatedAt] = useState(null);
  const [expanded, setExpanded] = useState(false);
  const [actionBusy, setActionBusy] = useState(false);
  const [actionError, setActionError] = useState('');
  async function openStudy(e, item, url) {
    if ((!item.topic_id && !item.knowledge_evidence) || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    if (actionBusy) return;
    setActionBusy(true); setActionError('');
    const res = item.knowledge_evidence
      ? await recommendationService.startKnowledgeStudy(item.knowledge_evidence)
      : await recommendationService.startStudy(item.topic_id);
    setActionBusy(false);
    if (!res?.ok) showToast('Chưa ghi được mốc so sánh ôn tập. Bạn vẫn có thể mở nội dung học.', 'info');
    navigate(url);
  }

  // Tải gợi ý hiện tại (backend tính trực tiếp từ dữ liệu học tập mới nhất)
  const load = useCallback(async (isCurrent = () => true) => {
    setLoading(true);
    setLoadError('');
    setRec(null);
    const res = await recommendationService.get(courseId);
    if (!isCurrent()) return;
    if (res?.ok) setRec(res.data?.data?.current || null);
    else setLoadError('Không tải được gợi ý học tập. Vui lòng thử lại.');
    setLoading(false);
  }, [courseId]);

  useEffect(() => {
    let active = true;
    setExpanded(false);
    setUpdatedAt(null);
    load(() => active);
    return () => { active = false; };
  }, [load]);

  // Bấm "Cập nhật": tính lại gợi ý, lưu vào lịch sử và hiển thị kết quả mới
  async function handleRefresh() {
    setRefreshing(true);
    setActionError('');
    const res = await recommendationService.refresh(courseId);
    if (res?.ok && res.data?.data) {
      setRec({
        level: res.data.data.level,
        summary: res.data.data.summary,
        items: res.data.data.items || [],
        based_on: res.data.data.based_on,
      });
      setUpdatedAt(new Date());
    } else {
      setActionError(res?.data?.message || 'Không cập nhật được gợi ý. Vui lòng thử lại.');
    }
    setRefreshing(false);
  }

  const lv = rec?.level ? LEVEL[rec.level] : null;
  // Chế độ gọn (compact) chỉ hiện 3 gợi ý đầu
  const knowledgeData = rec?.based_on?.knowledge;
  const hasKnowledge = knowledgeData?.units?.some((unit) => unit.kind === 'chapter');
  const allItems = (rec?.items || []).filter((item) => !hasKnowledge || item.type !== 'review_knowledge');
  const items = compact && !expanded ? allItems.slice(0, 3) : allItems;

  return (
    <div className="s-card">
      <div className="s-card-header" style={{ flexWrap: 'wrap', gap: '.75rem' }}>
        <span className="s-card-title">🎯 {title}</span>
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

        {!loading && loadError && <div role="alert">
          <p>{loadError}</p>
          <button type="button" className="s-btn s-btn-outline s-btn-sm" onClick={() => load()}>Thử lại</button>
        </div>}
        {!loading && !loadError && !rec && (
          <div style={{ color: 'var(--s-text-muted)', fontSize: '.875rem' }}>Chưa có gợi ý.</div>
        )}

        {!loading && rec && (
          <>
            <p style={{ fontWeight: 700, marginBottom: '.85rem' }}>{rec.summary}</p>
            <p style={{ fontSize: '.78rem', color: 'var(--s-text-muted)', marginBottom: '.85rem' }}>
              Dựa trên kết quả theo chương, bài học và chủ đề. Kết quả mới thay thế căn cứ cũ của cùng bài học; cần ít nhất {rec.based_on?.min_topic_questions ?? 5} câu khác nhau để phân loại.
            </p>
            {hasKnowledge && <KnowledgeAssessment data={knowledgeData} title="Chương cần ôn và các bài nên ôn" showReview current reviewOnly onStudy={openStudy} practiceItems={rec.items || []} />}
            {actionError && <p role="alert" style={{ color: '#DC2626' }}>{actionError}</p>}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '.6rem' }}>
              {items.map((it, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    alignItems: 'flex-start',
                    gap: '.6rem',
                    padding: '.6rem .75rem',
                    border: '1px solid var(--s-border)',
                    borderRadius: 8,
                    background: 'var(--s-surface-2)',
                    borderLeft: i === 0 && it.type !== 'advice' ? '3px solid var(--s-primary, #2563eb)' : undefined,
                  }}
                >
                  <span style={{ fontSize: '1rem', lineHeight: 1.4 }}>{ICON[it.type] || '•'}</span>
                  <div style={{ flex: '1 1 220px', minWidth: 0, fontSize: '.86rem', lineHeight: 1.45 }}>
                    {i === 0 && it.type !== 'advice' && <span className="s-badge" style={{ marginBottom: '.35rem' }}>Ưu tiên trước</span>}
                    {(it.knowledge_evidence || it.evidence) ? (() => {
                      const evidence = it.knowledge_evidence || it.evidence;
                      return <>
                        <strong style={{ display: 'block', fontSize: '.95rem' }}>{evidence.kind === 'chapter' ? 'Chương: ' : evidence.kind === 'lesson' ? 'Bài học: ' : ''}{evidence.title || evidence.topic || it.topic}</strong>
                        {evidence.kind === 'lesson' && <small style={{ display: 'block' }}>Thuộc {evidence.chapter_name}</small>}
                        <span style={{ display: 'block', color: 'var(--s-text-muted)', margin: '.2rem 0' }}>{evidence.course_title}</span>
                        <span>Đúng {evidence.correct}/{evidence.answered} câu · {evidence.avg_score}%</span>
                        <span style={{ display: 'block', fontWeight: 600, color: evidence.sufficient_data ? '#b45309' : 'var(--s-text-muted)' }}>
                          {evidence.sufficient_data ? 'Cần củng cố' : 'Cần luyện thêm để đủ dữ liệu'}
                        </span>
                      </>;
                    })() : <span>{it.text}</span>}
                    <details style={{ marginTop: '.4rem' }}>
                      <summary style={{ cursor: 'pointer', color: 'var(--s-primary,#2563eb)' }}>Vì sao có gợi ý này?</summary>
                      {it.evidence ? <>
                        <p>Đúng {it.evidence.correct}/{it.evidence.answered} câu khác nhau ({it.evidence.avg_score}%).
                          {it.evidence.sufficient_data ? ' Đã đủ số câu theo quy tắc ban đầu.' : ' Chưa đủ 5 câu để phân loại.'}</p>
                        <p>{it.evidence.confirmed ? 'Liên kết ôn tập đã được giảng viên xác nhận.' : 'Chưa có bài ôn được liên kết riêng cho chủ đề này.'}</p>
                        {it.evidence.catalog_name && it.evidence.catalog_name !== it.evidence.topic && <p>Tên hiện tại trong danh mục: {it.evidence.catalog_name}. Căn cứ giữ tên đã lưu trong bài làm.</p>}
                        <ul>{(it.evidence.sources || []).map((s) => <li key={s.result_id}>
                          <Link to={`/student/quiz-result?result_id=${s.result_id}`}>{s.quiz_title}</Link>: đúng {s.correct}/{s.answered} câu chủ đề này, nộp {formatStudyDate(s.submitted_at)}.
                          {' '}Phân loại lưu trong bài: {s.topic_name}.
                          {s.reconstructed && ' Phân loại của dữ liệu cũ được khôi phục từ câu hỏi tại thời điểm cập nhật hệ thống.'}
                        </li>)}</ul>
                        <p style={{ color: 'var(--s-text-muted)' }}>Mốc 5 câu và 70% là quy tắc hỗ trợ ôn tập ban đầu, chưa phải chứng nhận mức thành thạo.</p>
                      </> : it.grade_evidence ? <>
                        <p>Đề lấy điểm {it.grade_evidence.method}: {it.grade_evidence.score}%.
                          {it.grade_evidence.passed === false ? ' Chưa đạt yêu cầu đề.' : ' Tỷ lệ đúng dưới ngưỡng luyện tập 70%.'}</p>
                        <p>Đã dùng {it.grade_evidence.attempts_used} lượt, gồm cả lượt bỏ dở.
                          {it.grade_evidence.attempts_left === null ? ' Không giới hạn lượt.' : ` Còn ${it.grade_evidence.attempts_left} lượt mới.`}</p>
                        <ul>{it.grade_evidence.sources.map((s) => <li key={s.result_id}>
                          <Link to={`/student/quiz-result?result_id=${s.result_id}`}>Xem kết quả</Link> · {formatStudyDate(s.submitted_at)}
                        </li>)}</ul>
                      </> : it.knowledge_evidence ? <>
                        <p>Đúng {it.knowledge_evidence.correct}/{it.knowledge_evidence.answered} câu ({it.knowledge_evidence.avg_score}%).
                          {it.knowledge_evidence.sufficient_data ? ' Đủ số câu theo quy tắc ban đầu; dưới 70% thì ưu tiên ôn.' : ' Chưa đủ 5 câu; chưa kết luận yếu cả phần kiến thức.'}</p>
                        <p>Lấy kết quả mới nhất của từng bài học qua các đề. Khi luyện lại, căn cứ cũ của bài đó được thay thế; các bài khác giữ căn cứ gần nhất.</p>
                        <ul>{it.knowledge_evidence.sources.map((s) => <li key={s.result_id}>
                          <Link to={`/student/quiz-result?result_id=${s.result_id}`}>{s.quiz_title}</Link>: đúng {s.correct}/{s.answered} câu, nộp {formatStudyDate(s.submitted_at)}.
                        </li>)}</ul>
                        {it.knowledge_evidence.reconstructed && <p>Phân loại dữ liệu cũ được khôi phục từ phạm vi đề hoặc tên bài khớp rõ ràng.</p>}
                        <p>Nên luyện thêm câu tương đương để hạn chế ảnh hưởng của việc nhớ đáp án.</p>
                      </> : <p>{it.reason || it.text}</p>}
                    </details>
                  </div>
                  {it.action_url && (
                    <Link to={it.action_url} onClick={(e) => openStudy(e, it, it.action_url)} aria-disabled={actionBusy} className="s-btn s-btn-primary s-btn-sm" style={{ flexShrink: 0 }}>
                      {it.action_label || 'Đi tới'}
                    </Link>
                  )}
                  {it.practice_url && <Link to={it.practice_url} onClick={(e) => openStudy(e, it, it.practice_url)} aria-disabled={actionBusy} className="s-btn s-btn-outline s-btn-sm">{it.practice_label || 'Làm bài luyện'}</Link>}
                </div>
              ))}
            </div>
            {compact && allItems.length > 3 && (
              <button type="button" className="s-btn s-btn-ghost s-btn-sm" onClick={() => setExpanded((value) => !value)}>
                {expanded ? 'Thu gọn' : `Xem tất cả ${allItems.length} gợi ý`}
              </button>
            )}
            {updatedAt && (
              <p style={{ fontSize: '.72rem', color: 'var(--s-text-muted)', marginTop: '.75rem' }}>
                Đã cập nhật lúc {updatedAt.toLocaleTimeString('vi-VN')} — gợi ý sẽ thay đổi theo kết quả học tập mới của bạn.
              </p>
            )}
            {rec.based_on?.knowledge && <details style={{ marginTop: '1rem' }}>
              <summary style={{ cursor: 'pointer' }}>Xem kết quả kiến thức hiện tại theo chương/bài</summary>
              <KnowledgeAssessment data={rec.based_on.knowledge} title="Căn cứ mới nhất theo chương/bài" />
            </details>}
            <StudyProgressPanel courseId={courseId} refreshKey={updatedAt?.getTime()} />
          </>
        )}
      </div>
    </div>
  );
}
