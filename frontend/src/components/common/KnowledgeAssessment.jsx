import { Link } from 'react-router-dom';
import './KnowledgeAssessment.css';
import { formatStudyDate } from '../../utils/studyDate';

export default function KnowledgeAssessment({ data, title = 'Kết quả theo chương và bài học', showReview = false, answers = [], current = false, reviewOnly = false, onStudy, practiceItems = [] }) {
  if (!data) return null;
  const units = data.units || [];
  const chapters = units.filter((u) => u.kind === 'chapter');
  const multipleCourses = new Set(chapters.map((ch) => ch.course_id)).size > 1;
  const weakChapters = chapters.filter((unit) => unit.needs_review);
  const weakLessons = units.filter((unit) => unit.kind === 'lesson' && unit.needs_review);
  const uncertain = units.filter((unit) => !unit.sufficient_data);
  const lessonsFor = (chapter) => units.filter((unit) => unit.kind === 'lesson' && unit.course_id === chapter.course_id && unit.chapter_id === chapter.id);
  const needsAttention = (unit) => unit.needs_review || (!unit.sufficient_data && unit.correct < unit.answered);
  const rank = (unit) => unit.needs_review ? 0 : !unit.sufficient_data ? 1 : 2;
  const ordered = (list) => [...list].sort((a, b) => rank(a) - rank(b) || a.avg_score - b.avg_score);
  const attentionChapters = ordered(chapters.filter((chapter) => needsAttention(chapter) || lessonsFor(chapter).some(needsAttention)));
  const otherChapters = ordered(chapters.filter((chapter) => !attentionChapters.includes(chapter)));
  function unitSummary(unit, actionable = true) {
    const practice = practiceItems.find((item) => item.knowledge_evidence?.course_id === unit.course_id && item.knowledge_evidence?.kind === unit.kind && item.knowledge_evidence?.id === unit.id && item.practice_url);
    const wrongAnswers = answers.filter((answer) => !answer.is_right && (unit.question_ids || []).includes(answer.question_id));
    return <>
      <div className="knowledge-unit-row">
      <strong className="knowledge-unit-name">{unit.title}{unit.available === false ? ' (nội dung đã gỡ)' : ''}</strong>
      <span className="knowledge-unit-result">
        <span>Đúng {unit.correct}/{unit.answered} câu · {unit.avg_score}%</span>
        <strong className={`knowledge-status ${!unit.sufficient_data ? 'knowledge-status-insufficient' : unit.needs_review ? 'knowledge-status-review' : 'knowledge-status-good'}`}>{!unit.sufficient_data ? 'Chưa đủ dữ liệu' : unit.needs_review ? 'Cần củng cố' : 'Đạt ngưỡng'}</strong>
      </span>
      {actionable && needsAttention(unit) && <div className="knowledge-unit-actions">
        {unit.available !== false && <Link className="s-btn s-btn-primary s-btn-sm" onClick={onStudy ? (event) => onStudy(event, { knowledge_evidence: unit }, unit.kind === 'lesson' ? `/lesson?id=${unit.id}` : `/chapters?course_id=${unit.course_id}&chapter_id=${unit.id}`) : undefined} to={unit.kind === 'lesson' ? `/lesson?id=${unit.id}` : `/chapters?course_id=${unit.course_id}&chapter_id=${unit.id}`}>
          {unit.kind === 'lesson' ? 'Ôn bài học' : 'Ôn chương'}
        </Link>}
        {practice && <Link className="s-btn s-btn-outline s-btn-sm" to={practice.practice_url} onClick={onStudy ? (event) => onStudy(event, { knowledge_evidence: unit }, practice.practice_url) : undefined}>{practice.practice_label || 'Làm bài luyện'}</Link>}
        {wrongAnswers.length > 0 && <details>
          <summary style={{ cursor: 'pointer', padding: '.4rem 0', fontSize: '.85rem' }}>Xem {wrongAnswers.length} câu sai</summary>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '.5rem', padding: '.4rem 0' }}>{wrongAnswers.map((answer) => <a key={answer.question_id} href={`#quiz-question-${answer.question_id}`}>Câu {answers.indexOf(answer) + 1}</a>)}</div>
        </details>}
      </div>}
      </div>
      {current && needsAttention(unit) && <details className="knowledge-evidence">
        <summary style={{ cursor: 'pointer' }}>Vì sao cần ôn?</summary>
        <p>{unit.sufficient_data ? 'Đủ số câu làm căn cứ và tỷ lệ đúng dưới ngưỡng ôn tập.' : 'Có câu sai nhưng chưa đủ số câu để kết luận yếu.'}</p>
        <ul>{(unit.sources || []).map((source) => <li key={source.result_id}><Link to={`/student/quiz-result?result_id=${source.result_id}`}>{source.quiz_title}</Link> · {formatStudyDate(source.submitted_at)} · đúng {source.correct}/{source.answered} câu.</li>)}</ul>
      </details>}
    </>;
  }
  function chapterCard(chapter) {
    const lessons = ordered(lessonsFor(chapter));
    const attentionLessons = lessons.filter(needsAttention);
    const otherLessons = lessons.filter((unit) => !needsAttention(unit));
    return <div key={`${chapter.course_id}-${chapter.id}`} className="knowledge-chapter">
      {unitSummary(chapter, !attentionLessons.length)}
      {attentionLessons.length > 0 && <p style={{ marginTop: '.5rem', fontSize: '.85rem', fontWeight: 600 }}>Bài nên ôn ({attentionLessons.length})</p>}
      {!attentionLessons.length && needsAttention(chapter) && <p style={{ marginTop: '.5rem', fontSize: '.8rem', color: 'var(--s-text-muted)' }}>Nên ôn chương trước; chưa đủ căn cứ để chỉ ra bài cụ thể cần củng cố.</p>}
      {multipleCourses && <small>{chapter.course_title}</small>}
      {attentionLessons.length > 0 && <div className="knowledge-lesson-list">
        {attentionLessons.map((lesson) => <div className="knowledge-lesson" key={lesson.id}>{unitSummary(lesson)}</div>)}
      </div>}
      {!reviewOnly && otherLessons.length > 0 && <details style={{ marginTop: '.75rem', paddingLeft: '1rem' }}>
        <summary style={{ cursor: 'pointer', fontSize: '.85rem' }}>Bài đạt ngưỡng hoặc chưa ghi nhận câu sai ({otherLessons.length})</summary>
        {otherLessons.map((lesson) => <div key={lesson.id} style={{ marginTop: '.6rem' }}>{unitSummary(lesson, false)}</div>)}
      </details>}
    </div>;
  }
  function row(unit) {
    const isLesson = unit.kind === 'lesson';
    const url = isLesson ? `/lesson?id=${unit.id}` : `/chapters?course_id=${unit.course_id}&chapter_id=${unit.id}`;
    return <tr key={`${unit.course_id}-${unit.kind}-${unit.id}`}>
      <td style={{ padding: '.5rem', paddingLeft: isLesson ? '1.4rem' : '.5rem', fontWeight: isLesson ? 400 : 700 }}>
        {unit.available === false ? <span>{unit.title} (nội dung đã gỡ)</span> : <Link to={url}>{unit.title}</Link>}
        {!isLesson && multipleCourses && <small style={{ display: 'block', fontWeight: 400 }}>{unit.course_title}</small>}
      </td>
      <td style={{ padding: '.5rem', whiteSpace: 'nowrap' }}>{unit.correct}/{unit.answered} · {unit.avg_score}%</td>
      <td style={{ padding: '.5rem', color: unit.needs_review ? '#b45309' : 'inherit' }}>
        {!unit.sufficient_data ? 'Cần kiểm tra thêm' : unit.needs_review ? 'Cần củng cố' : 'Đạt ngưỡng ôn tập'}
      </td>
    </tr>;
  }
  return <section className="knowledge-assessment" style={{ marginBottom: '1rem' }} aria-label={title}>
    <h3 style={{ fontSize: '1rem', marginBottom: '.6rem' }}>{title}</h3>
    {showReview && chapters.length > 0 && <>
      <p style={{ fontSize: '.85rem', marginBottom: '.75rem' }}>{current ? 'Từ kết quả quiz gần nhất của từng bài trong khóa' : 'Riêng lượt quiz này'}: {weakChapters.length} chương và {weakLessons.length} bài cần củng cố. Ưu tiên ôn các bài bên dưới.</p>
      {attentionChapters.map(chapterCard)}
      {!attentionChapters.length && <p>Chưa ghi nhận phần cần ôn từ các câu đã kiểm tra trong lượt này.</p>}
      {!reviewOnly && otherChapters.length > 0 && <details style={{ marginBottom: '.75rem' }}>
        <summary style={{ cursor: 'pointer' }}>Các chương còn lại ({otherChapters.length})</summary>
        <div style={{ marginTop: '.75rem' }}>{otherChapters.map(chapterCard)}</div>
      </details>}
      {uncertain.length > 0 && <p style={{ fontSize: '.8rem', color: 'var(--s-text-muted)' }}>Các mục “Chưa đủ dữ liệu” cần thêm câu hỏi để đánh giá; có câu sai thì bạn vẫn có thể ôn lại.</p>}
    </>}
    {!chapters.length && <p>Chưa có câu hỏi được phân loại theo chương/bài trong dữ liệu này.</p>}
    {!reviewOnly && !!chapters.length && <details open={showReview ? undefined : true}><summary style={{ cursor: 'pointer', marginBottom: '.5rem' }}>Xem bảng kết quả chi tiết theo chương/bài</summary><div style={{ overflowX: 'auto' }}><table style={{ width: '100%', textAlign: 'left', fontSize: '.85rem', borderCollapse: 'collapse' }}>
      <thead><tr><th style={{ padding: '.5rem' }}>Phần kiến thức</th><th style={{ padding: '.5rem' }}>Số câu đúng</th><th style={{ padding: '.5rem' }}>Đánh giá</th></tr></thead>
      <tbody>{chapters.flatMap((ch) => [row(ch), ...units.filter((u) => u.kind === 'lesson' && u.course_id === ch.course_id && u.chapter_id === ch.id).map(row)])}</tbody>
    </table></div></details>}
    {data.unmapped_answers > 0 && <p style={{ fontSize: '.8rem' }}>{data.unmapped_answers} câu trả lời chưa xác định chương. Các câu này vẫn tính điểm tổng; giảng viên cần bổ sung phân loại để gợi ý cụ thể.</p>}
    {units.some((u) => u.reconstructed) && <p style={{ fontSize: '.78rem', color: 'var(--s-text-muted)' }}>Một phần phân loại dữ liệu cũ được khôi phục từ phạm vi đề và tên bài, chưa phải phân loại được lưu tại lúc nộp.</p>}
    <p style={{ fontSize: '.78rem', color: 'var(--s-text-muted)' }}>Cần ít nhất 5 câu khác nhau để phân loại; dưới 70% thì ưu tiên ôn. Đây là ngưỡng hỗ trợ học tập ban đầu.</p>
  </section>;
}
