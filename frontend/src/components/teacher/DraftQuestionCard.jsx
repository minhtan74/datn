import { DIFFICULTY_LEVELS } from '../common/DifficultyBar.jsx';
import RichText, { hasRichTokens } from '../common/RichText.jsx';

// Ký hiệu 4 phương án
const LETTERS = ['A', 'B', 'C', 'D'];

/**
 * Thẻ sửa 1 câu hỏi trong bản nháp (AI sinh hoặc nhập từ Word) trước khi duyệt & lưu:
 * nội dung, 4 phương án, đáp án đúng, độ khó, giải thích; nút bỏ câu.
 * q: { question, options: {A..D}, correct_answer, explanation, difficulty, verify?, verified? }
 * meta: dòng thông tin phụ cạnh số câu (chương / chủ đề / nguồn đáp án...)
 * onPatch(field, value) · onPatchOption(letter, value) · onRemove()
 */
export default function DraftQuestionCard({ q, index, meta, onPatch, onPatchOption, onRemove }) {
  // AI tự giải lại ra đáp án khác đáp án đang đánh (và chưa bấm "Giữ") -> cần xem lại
  const needsReview = Boolean(q.verify) && q.verify.answer !== q.correct_answer && !q.verify_dismissed;

  return (
    <div className="tq-question-card" style={{ marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="tq-question-num" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          Câu {index + 1}
          {meta ? ` · ${meta}` : ''} ·
          <select
            className="form-control"
            style={{ width: 'auto', padding: '0.15rem 0.5rem', fontSize: '0.75rem' }}
            value={q.difficulty || ''}
            onChange={(e) => onPatch('difficulty', e.target.value || null)}
          >
            {/* Đề nhập từ Word có thể chưa ghi độ khó */}
            {!q.difficulty && <option value="">Chưa đặt độ khó</option>}
            {DIFFICULTY_LEVELS.map((d) => (
              <option key={d.key} value={d.key}>{d.label}</option>
            ))}
          </select>
        </div>
        <button className="btn btn-ghost btn-sm" style={{ color: 'var(--danger,#DC2626)' }} onClick={onRemove}>✕ Xóa</button>
      </div>
      <textarea
        className="form-control"
        rows={2}
        value={q.question}
        onChange={(e) => onPatch('question', e.target.value)}
        style={{ margin: '.5rem 0', resize: 'vertical' }}
      />
      {/* Có ảnh / công thức: hiện bản xem trước như học viên sẽ thấy */}
      {[q.question, ...Object.values(q.options || {})].some(hasRichTokens) && (
        <div
          style={{
            margin: '0 0 .6rem', padding: '.6rem .75rem', borderRadius: 8, fontSize: '.9rem',
            background: 'var(--primary-light, #eff6ff)', whiteSpace: 'pre-wrap',
          }}
        >
          <div style={{ fontSize: '.7rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '.25rem' }}>
            XEM TRƯỚC
          </div>
          <RichText text={q.question} />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: '.35rem', marginTop: '.4rem' }}>
            {LETTERS.filter((L) => q.options[L]).map((L) => (
              <div key={L} style={{ color: q.correct_answer === L ? 'var(--success,#059669)' : undefined }}>
                <strong>{L}.</strong> <RichText text={q.options[L]} imgMaxHeight={120} />
              </div>
            ))}
          </div>
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: '.5rem' }}>
        {LETTERS.map((L) => (
          <label
            key={L}
            style={{
              display: 'flex', alignItems: 'center', gap: '.5rem',
              padding: '.4rem .5rem', borderRadius: 8,
              border: `1px solid ${q.correct_answer === L ? 'var(--success,#059669)' : 'var(--border,#e2e8f0)'}`,
              background: q.correct_answer === L ? 'rgba(5,150,105,.08)' : 'transparent',
            }}
          >
            {/* Phương án trống (đề Word chỉ có 2–3 phương án) thì không chọn làm đáp án được */}
            <input
              type="radio"
              name={`correct-${index}`}
              checked={q.correct_answer === L}
              disabled={!q.options[L]}
              onChange={() => onPatch('correct_answer', L)}
            />
            <strong>{L}.</strong>
            <input
              className="form-control"
              style={{ border: 'none', padding: 0, background: 'transparent' }}
              placeholder={L === 'A' || L === 'B' ? '' : '(để trống nếu không dùng)'}
              value={q.options[L] || ''}
              onChange={(e) => onPatchOption(L, e.target.value)}
            />
          </label>
        ))}
      </div>
      <input
        className="form-control"
        style={{ marginTop: '.5rem', fontSize: '.85rem' }}
        placeholder="Giải thích (tùy chọn)"
        value={q.explanation || ''}
        onChange={(e) => onPatch('explanation', e.target.value)}
      />
      {/* AI giải lại ra đáp án khác: hiện lý do, cho đổi nhanh hoặc giữ đáp án hiện tại */}
      {needsReview && (
        <div className="alert alert-warning" style={{ marginTop: '.5rem', marginBottom: 0, fontSize: '.82rem' }}>
          ⚠️ AI tự giải lại chọn <strong>{q.verify.answer}</strong>, khác đáp án đang đánh{' '}
          <strong>{q.correct_answer}</strong>.
          {q.verify.reason && <> Lý do: {q.verify.reason}</>}
          <div style={{ display: 'flex', gap: '.5rem', marginTop: '.4rem' }}>
            <button type="button" className="btn btn-primary btn-sm" onClick={() => onPatch('correct_answer', q.verify.answer)}>
              Đổi sang {q.verify.answer}
            </button>
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => onPatch('verify_dismissed', true)}>
              Giữ {q.correct_answer}
            </button>
          </div>
        </div>
      )}
      {q.verified && q.verified === q.correct_answer && (
        <div style={{ marginTop: '.35rem', fontSize: '.75rem', color: 'var(--success,#059669)' }}>✓ AI giải lại khớp đáp án</div>
      )}
    </div>
  );
}
