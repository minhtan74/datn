import { useEffect, useState } from 'react';
import { quizService } from '../../services/quizService';

// Share one outline request across all draft cards, with a short lifetime.
const requests = new Map();
function loadOutline(courseId) {
  const cached = requests.get(String(courseId));
  if (cached && Date.now() - cached.time < 30000) return cached.promise;
  const promise = quizService.getKnowledgeOutline(courseId);
  requests.set(String(courseId), { time: Date.now(), promise });
  return promise;
}

export default function KnowledgePicker({ courseId, chapterId, lessonId, lockedChapterId, lockedLessonId, onChange }) {
  const [outline, setOutline] = useState({ chapters: [], lessons: [] });
  const [error, setError] = useState('');
  useEffect(() => {
    let alive = true;
    setOutline({ chapters: [], lessons: [] });
    if (courseId) loadOutline(courseId).then((res) => {
      if (!alive) return;
      setOutline(res?.ok ? res.data.data : { chapters: [], lessons: [] });
      setError(res?.ok ? '' : 'Không tải được chương/bài. Hãy tải lại trang.');
    });
    return () => { alive = false; };
  }, [courseId]);
  const selectedLesson = lessonId || lockedLessonId || '';
  const lesson = outline.lessons.find((l) => String(l.id) === String(selectedLesson));
  const selectedChapter = chapterId || lockedChapterId || lesson?.chapter_id || '';
  return <div style={{ margin: '.6rem 0' }}>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: '.6rem' }}>
      <label>Chương kiến thức
        <select className="form-control" value={selectedChapter} disabled={Boolean(lockedChapterId || lockedLessonId)}
          onChange={(e) => onChange({ knowledge_chapter_id: Number(e.target.value) || null, knowledge_lesson_id: null })}>
          <option value="">Chưa phân loại chương</option>
          {outline.chapters.map((ch) => <option key={ch.id} value={ch.id}>{ch.chapter_name}</option>)}
        </select>
      </label>
      <label>Bài kiến thức
        <select className="form-control" value={selectedLesson} disabled={Boolean(lockedLessonId) || !selectedChapter}
          onChange={(e) => onChange({ knowledge_chapter_id: Number(selectedChapter) || null, knowledge_lesson_id: Number(e.target.value) || null })}>
          <option value="">Chưa xác định bài cụ thể</option>
          {outline.lessons.filter((l) => String(l.chapter_id) === String(selectedChapter)).map((l) => <option key={l.id} value={l.id}>{l.title}</option>)}
        </select>
      </label>
    </div>
    <small style={{ color: 'var(--text-muted,#64748b)' }}>{error || 'Chọn đúng chương và bài mà câu hỏi kiểm tra để gợi ý ôn tập chính xác. Kiểm tra lại phân loại do AI đề xuất.'}</small>
  </div>;
}
