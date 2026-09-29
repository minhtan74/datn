import { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { courseService } from '../services/courseService';
import { chapterService } from '../services/chapterService';
import { lessonService } from '../services/lessonService';
import '../assets/css/chapters.css';

/** Tương đương _legacy/pages/chapters.html (logic inline trong file đó, chapters.js là dead code) */
export default function Chapters() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const courseId = searchParams.get('course_id');

  const [course, setCourse] = useState(null);
  const [chapters, setChapters] = useState(null); // null = đang tải
  // Tập id các chương đang mở rộng (dạng accordion)
  const [openChapters, setOpenChapters] = useState(new Set());

  // Tải khóa học, các chương và bài học của từng chương (gọi song song); thiếu course_id thì quay về
  useEffect(() => {
    if (!courseId) {
      navigate('/student/my-courses', { replace: true });
      return;
    }

    let cancelled = false;
    setCourse(null);
    setChapters(null);
    setOpenChapters(new Set());

    (async () => {
      const courseRes = await courseService.getCourse(Number(courseId));
      if (!cancelled && courseRes?.ok && courseRes.data?.data) {
        setCourse(courseRes.data.data);
      }

      const chapRes = await chapterService.getChapters(Number(courseId));
      const chaps = chapRes?.data?.data || [];

      const lessonResults = await Promise.all(chaps.map((ch) => lessonService.getLessons(ch.id)));
      if (cancelled) return;

      const chaptersWithLessons = chaps.map((ch, idx) => ({
        ...ch,
        lessons: lessonResults[idx]?.data?.data || [],
      }));

      setChapters(chaptersWithLessons);
      if (chaptersWithLessons.length > 0) {
        setOpenChapters(new Set([chaptersWithLessons[0].id])); // mở chương đầu tiên mặc định
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [courseId, navigate]);

  useEffect(() => {
    if (course?.title) document.title = `${course.title} — StudyOnline`;
  }, [course]);

  // Mở / thu gọn 1 chương
  function toggleChapter(id) {
    setOpenChapters((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  // Tổng số bài học của khóa
  const totalLessons = chapters ? chapters.reduce((sum, c) => sum + c.lessons.length, 0) : 0;

  return (
    <main className="s-main">
      {/* Breadcrumb */}
      <nav className="chapters-breadcrumb" aria-label="Breadcrumb">
        <Link to="/student/dashboard">Dashboard</Link>
        <span className="sep">›</span>
        <Link to="/student/my-courses">Khóa học của tôi</Link>
        <span className="sep">›</span>
        <span id="bcCourse">{course?.title || 'Đang tải...'}</span>
      </nav>

      {/* Course Hero */}
      <div className="course-hero">
        <h1 id="courseTitle">{course?.title || 'Đang tải khóa học...'}</h1>
        <p id="courseDesc">{course?.description || 'Chọn chương để bắt đầu học'}</p>
        <div className="course-hero-meta">
          <span id="chapterCount">📂 {chapters ? chapters.length : '—'} chương</span>
          <span id="lessonCount">📖 {chapters ? totalLessons : '—'} bài học</span>
        </div>
      </div>

      <div id="alertBox"></div>

      <div id="chapterList">
        {chapters === null && (
          <div className="loading-spinner">
            <div className="spin"></div>
            <p>Đang tải nội dung khóa học...</p>
          </div>
        )}

        {chapters !== null && chapters.length === 0 && (
          <div className="s-empty">
            <div className="icon">📂</div>
            <h3>Chưa có chương nào</h3>
            <p>Khóa học này chưa có nội dung. Hãy quay lại sau nhé!</p>
          </div>
        )}

        {chapters !== null && chapters.length > 0 && (
          <div className="chapter-list">
            {chapters.map((ch, idx) => {
              const isOpen = openChapters.has(ch.id);
              return (
                <div key={ch.id} className={`chapter-item${isOpen ? ' open' : ''}`}>
                  <div className="chapter-header" onClick={() => toggleChapter(ch.id)}>
                    <div className="chapter-num">{idx + 1}</div>
                    <div className="chapter-info">
                      <h3>{ch.chapter_name || `Chương ${idx + 1}`}</h3>
                      <p>
                        {ch.lessons.length} bài học
                        {ch.review_question_count > 0 ? ` · ${ch.review_question_count} câu ôn tập` : ''}
                      </p>
                    </div>
                    <span className="chapter-arrow">▼</span>
                  </div>
                  <div className="lesson-list">
                    {ch.lessons.length === 0 ? (
                      <div style={{ padding: '1.25rem 2rem', fontSize: '.85rem', color: 'var(--s-text-muted)' }}>
                        📭 Chương này chưa có bài học.
                      </div>
                    ) : (
                      ch.lessons.map((lesson, li) => (
                        <Link key={lesson.id} className="lesson-row" to={`/lesson?id=${lesson.id}`}>
                          <div className="lesson-icon">{lesson.locked ? '🔒' : lesson.video_url ? '🎬' : '📄'}</div>
                          <div className="lesson-info">
                            <div className="title">{lesson.title || `Bài ${li + 1}`}</div>
                            <div className="desc">
                              {lesson.description
                                ? lesson.description.slice(0, 80) + (lesson.description.length > 80 ? '...' : '')
                                : 'Nhấn để xem bài học'}
                              {lesson.review_question_count > 0 ? ` · 📝 ${lesson.review_question_count} câu ôn tập` : ''}
                            </div>
                          </div>
                          <span className="lesson-cta">{lesson.locked ? '🔒 Cần đăng ký' : '▶ Xem bài'}</span>
                        </Link>
                      ))
                    )}
                    {/* Bộ câu hỏi ôn tập của chương (chỉ hiện khi giảng viên đã soạn câu hỏi) */}
                    {ch.review_question_count > 0 &&
                      (ch.lessons.some((l) => l.locked) ? (
                        <div className="lesson-row">
                          <div className="lesson-icon">🔒</div>
                          <div className="lesson-info">
                            <div className="title">Ôn tập chương</div>
                            <div className="desc">{ch.review_question_count} câu hỏi trắc nghiệm</div>
                          </div>
                          <span className="lesson-cta">🔒 Cần đăng ký</span>
                        </div>
                      ) : (
                        <Link className="lesson-row" to={`/quiz-show?id=${ch.review_quiz_id}`}>
                          <div className="lesson-icon">📝</div>
                          <div className="lesson-info">
                            <div className="title">Ôn tập chương</div>
                            <div className="desc">{ch.review_question_count} câu hỏi trắc nghiệm</div>
                          </div>
                          <span className="lesson-cta">✍️ Ôn tập</span>
                        </Link>
                      ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
