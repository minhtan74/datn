import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { courseService } from '../services/courseService';
import { chapterService } from '../services/chapterService';
import { lessonService } from '../services/lessonService';
import { progressService } from '../services/progressService';
import { aiService } from '../services/aiService';
import { isYoutubeUrl, getEmbedUrl, isUsableMediaUrl } from '../utils/videoUrl';

/** Tương đương _legacy/pages/lesson.html (logic inline trong file đó, lessons.js là dead code) */
export default function Lesson() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  // Id bài học lấy từ URL: /lesson?id=X
  const lessonId = searchParams.get('id');

  // Dữ liệu bài học, chương, khóa, mục lục và tiến độ
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [chapter, setChapter] = useState(null);
  const [course, setCourse] = useState(null);
  const [chaptersWithLessons, setChaptersWithLessons] = useState([]);
  const [completedIds, setCompletedIds] = useState(new Set());
  const [prevLesson, setPrevLesson] = useState(null);
  const [nextLesson, setNextLesson] = useState(null);
  const [activeTab, setActiveTab] = useState('desc');
  const [markingDone, setMarkingDone] = useState(false);

  // Trạng thái khung chat "Hỏi AI" trong bài học
  const [aiOpen, setAiOpen] = useState(false);
  const [aiMessages, setAiMessages] = useState([]);
  const [aiInput, setAiInput] = useState('');
  const [aiSending, setAiSending] = useState(false);
  const [aiConvId, setAiConvId] = useState(null);

  // Đang xem video hay tài liệu PDF (khi bài có cả hai)
  const [playerTab, setPlayerTab] = useState('video');

  // videoRef: thẻ <video>; lastSavedSecRef: giây đã lưu gần nhất (để 10 giây mới lưu 1 lần)
  const videoRef = useRef(null);
  const lastSavedSecRef = useRef(0);
  const aiThreadRef = useRef(null);

  // Tải dữ liệu mỗi khi đổi bài học (id trên URL đổi); không có id thì về "Khóa học của tôi"
  useEffect(() => {
    if (!lessonId) {
      navigate('/student/my-courses', { replace: true });
      return;
    }

    let cancelled = false;
    // Đặt lại trạng thái trang và khung chat AI cho bài mới
    setLoading(true);
    setErrorMsg(null);
    setActiveTab('desc');
    lastSavedSecRef.current = 0;
    setAiOpen(false);
    setAiMessages([]);
    setAiInput('');
    setAiConvId(null);

    (async () => {
      const id = Number(lessonId);

      // 1. Bài học
      const res = await lessonService.getLesson(id);
      if (!res?.ok || !res.data?.data) {
        if (!cancelled) {
          setErrorMsg(
            res?.status === 403
              ? res.data?.message
              : 'Không tìm thấy bài học hoặc có lỗi xảy ra. Vui lòng kiểm tra lại.',
          );
          setLoading(false);
        }
        return;
      }
      const lessonData = res.data.data;

      // 2. Chương
      const chapterRes = await chapterService.getChapter(lessonData.chapter_id);
      const currentChapter = chapterRes?.data?.data;
      if (!currentChapter) {
        if (!cancelled) {
          setErrorMsg('Không tìm thấy thông tin chương học.');
          setLoading(false);
        }
        return;
      }

      // 3. Khóa học
      const courseRes = await courseService.getCourse(currentChapter.course_id);
      const courseData = courseRes?.data?.data;
      if (!courseData) {
        if (!cancelled) {
          setErrorMsg('Không tìm thấy thông tin khóa học.');
          setLoading(false);
        }
        return;
      }

      // 5. Chương + bài học
      const chaptersRes = await chapterService.getChapters(currentChapter.course_id);
      const chaptersList = chaptersRes?.data?.data || [];
      const chaptersFull = await Promise.all(
        chaptersList.map(async (chap) => {
          const lessonsRes = await lessonService.getLessons(chap.id);
          return { ...chap, lessons: lessonsRes?.data?.data || [] };
        }),
      );

      // 6. Tiến độ hiện có
      const progressRes = await progressService.getProgressByCourse(currentChapter.course_id);
      const doneSet = new Set();
      if (progressRes?.ok && Array.isArray(progressRes.data?.data)) {
        progressRes.data.data.forEach((lid) => doneSet.add(lid));
      }

      // 7. Prev / next
      const allLessons = chaptersFull.flatMap((chap) => chap.lessons);
      const currentIdx = allLessons.findIndex((l) => l.id === lessonData.id);
      const prev = currentIdx > 0 ? allLessons[currentIdx - 1] : null;
      const next = currentIdx >= 0 && currentIdx < allLessons.length - 1 ? allLessons[currentIdx + 1] : null;

      // Người dùng đã chuyển sang bài khác trong lúc đang tải -> bỏ kết quả cũ
      if (cancelled) return;

      document.title = `${lessonData.title} — StudyOnline`;
      // Mở tab có nội dung dùng được: ưu tiên video, video chưa có file thật mà có tài liệu thì mở tài liệu
      const videoOk = isUsableMediaUrl(lessonData.video_src || lessonData.video_url);
      setPlayerTab(videoOk || !lessonData.document_url ? 'video' : 'doc');
      setLesson(lessonData);
      setChapter(currentChapter);
      setCourse(courseData);
      setChaptersWithLessons(chaptersFull);
      setCompletedIds(doneSet);
      setPrevLesson(prev);
      setNextLesson(next);
      setLoading(false);
    })();

    // Dọn dẹp: đánh dấu hủy khi rời trang / đổi bài
    return () => {
      cancelled = true;
    };
  }, [lessonId, navigate]);

  // Scroll sidebar active item vào view
  useEffect(() => {
    if (!loading && lesson) {
      const t = setTimeout(() => {
        document.querySelector('.active-sidebar-item')?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }, 150);
      return () => clearTimeout(t);
    }
  }, [loading, lesson]);

  // Gửi tiến độ lên server: số giây đã xem + đã hoàn thành (1) hay chưa (0)
  async function saveProgress(watchedSec, isCompleted) {
    if (!lesson) return;
    await progressService.updateProgress(lesson.id, Math.floor(watchedSec), isCompleted ? 1 : 0);
  }

  // Khi video đang phát: cứ tua thêm 10 giây thì lưu vị trí 1 lần (không đánh dấu hoàn thành)
  function handleTimeUpdate() {
    const videoEl = videoRef.current;
    if (!videoEl) return;
    const sec = Math.floor(videoEl.currentTime);
    if (sec - lastSavedSecRef.current >= 10) {
      lastSavedSecRef.current = sec;
      saveProgress(sec, false);
    }
  }

  // Video phát hết -> lưu hoàn thành và tick ✓ bài học trên mục lục
  async function handleEnded() {
    const videoEl = videoRef.current;
    await saveProgress(videoEl?.duration || 0, true);
    setCompletedIds((prev) => new Set(prev).add(lesson.id));
  }

  // Người học bấm "Đánh dấu hoàn thành"
  async function markDone() {
    setMarkingDone(true);
    const videoEl = videoRef.current;
    const watchedSec = videoEl ? Math.floor(videoEl.currentTime) : 0;
    await saveProgress(watchedSec, true);
    setCompletedIds((prev) => new Set(prev).add(lesson.id));
    setMarkingDone(false);
  }

  // Tự cuộn khung chat AI xuống tin nhắn mới nhất
  useEffect(() => {
    aiThreadRef.current?.scrollTo({ top: aiThreadRef.current.scrollHeight, behavior: 'smooth' });
  }, [aiMessages, aiSending]);

  // Gửi câu hỏi cho AI (chỉ tìm trong tài liệu của bài học này); hiện câu hỏi ngay, chờ câu trả lời + nguồn
  async function sendAiMessage(e) {
    e?.preventDefault();
    const text = aiInput.trim();
    if (!text || aiSending) return;
    setAiInput('');
    setAiMessages((m) => [...m, { role: 'user', content: text }]);
    setAiSending(true);
    const res = await aiService.chat({
      courseId: course.id,
      lessonId: lesson.id,
      conversationId: aiConvId,
      message: text,
    });
    setAiSending(false);
    const data = res?.data?.data;
    if (!res?.ok || !data) {
      setAiMessages((m) => [...m, { role: 'assistant', content: res?.data?.message || 'Có lỗi xảy ra, thử lại sau.' }]);
      return;
    }
    setAiMessages((m) => [...m, { role: 'assistant', content: data.answer, sources: data.sources }]);
    // Lần hỏi đầu tiên: nhớ id cuộc trò chuyện để các câu sau hỏi tiếp cùng ngữ cảnh
    if (!aiConvId && data.conversation_id) setAiConvId(data.conversation_id);
  }

  // Đang tải -> hiện vòng xoay; có lỗi (vd chưa ghi danh) -> hiện thông báo
  if (loading) {
    return (
      <main className="s-main">
        <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '5rem 0' }}>
          <div className="spinner mb-4"></div>
          <p style={{ fontSize: '0.95rem', color: 'var(--s-text-muted)', fontWeight: 500 }}>
            Đang tải nội dung bài học...
          </p>
        </div>
      </main>
    );
  }

  if (errorMsg) {
    return (
      <main className="s-main">
        <div className="alert alert-danger" role="alert">
          ❌ {errorMsg}
        </div>
      </main>
    );
  }

  // Tiến độ khóa học: số bài đã xong / tổng số bài
  const totalCount = chaptersWithLessons.reduce((sum, c) => sum + c.lessons.length, 0);
  const doneCount = completedIds.size;
  const pct = totalCount > 0 ? Math.round((doneCount / totalCount) * 100) : 0;
  const isCompleted = completedIds.has(lesson.id);
  // Link dùng được để nhúng; đường dẫn mẫu chưa có file thật (vd "docs/py_02.pdf") thì hiện thông báo thay vì nhúng nhầm trang web
  const docSrc = isUsableMediaUrl(lesson.document_src || lesson.document_url) ? lesson.document_src || lesson.document_url : null;
  const videoSrc = isUsableMediaUrl(lesson.video_src || lesson.video_url) ? lesson.video_src || lesson.video_url : null;

  return (
    <main className="s-main">
      {/* Breadcrumb */}
      <nav className="q-breadcrumb" aria-label="Breadcrumb">
        <Link to="/student/dashboard">Dashboard</Link>
        <span className="q-breadcrumb-separator">›</span>
        <Link to="/student/my-courses">Khóa học của tôi</Link>
        <span className="q-breadcrumb-separator">›</span>
        <Link to={`/chapters?course_id=${course.id}`}>{course.title}</Link>
        <span className="q-breadcrumb-separator">›</span>
        <span>{chapter.chapter_name}</span>
        <span className="q-breadcrumb-separator">›</span>
        <span className="q-breadcrumb-current">{lesson.title}</span>
      </nav>

      <div id="lessonWorkspace" className="l-workspace">
        {/* Main Column */}
        <div className="l-main-col">
          {/* Chuyển đổi Video / Tài liệu */}
          {lesson.video_url && lesson.document_url && (
            <div className="l-player-switch">
              <button
                type="button"
                onClick={() => setPlayerTab('video')}
                className={`l-player-switch-btn${playerTab === 'video' ? ' active' : ''}`}
              >
                🎬 Video bài giảng
              </button>
              <button
                type="button"
                onClick={() => setPlayerTab('doc')}
                className={`l-player-switch-btn${playerTab === 'doc' ? ' active' : ''}`}
              >
                📄 Tài liệu PDF
              </button>
            </div>
          )}

          {/* Video / Tài liệu / Placeholder */}
          <div
            className="l-video-container"
            style={playerTab === 'doc' && docSrc ? { aspectRatio: 'auto', height: 'min(85vh, 950px)' } : undefined}
          >
            {playerTab === 'doc' && lesson.document_url ? (
              docSrc ? (
                <iframe
                  src={`${docSrc}#view=FitH`}
                  title={`Tài liệu — ${lesson.title}`}
                  style={{ width: '100%', height: '100%', border: 'none', background: '#fff', display: 'block' }}
                />
              ) : (
                <div className="l-video-placeholder">
                  <span className="icon">📄</span>
                  <p>Tài liệu PDF của bài này chưa được tải lên</p>
                  <span>Giảng viên sẽ bổ sung sớm. Bạn có thể đọc phần mô tả bên dưới.</span>
                </div>
              )
            ) : lesson.video_url && !videoSrc ? (
              <div className="l-video-placeholder">
                <span className="icon">🎬</span>
                <p>Video của bài này chưa được tải lên</p>
                <span>Giảng viên sẽ bổ sung sớm. Bạn có thể đọc phần mô tả bên dưới.</span>
              </div>
            ) : lesson.video_url ? (
              isYoutubeUrl(lesson.video_url) ? (
                /* ── YouTube: dùng iframe với URL embed đã chuẩn hoá ── */
                <iframe
                  id="lessonVideo"
                  src={getEmbedUrl(lesson.video_url)}
                  title={lesson.title}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                  style={{ width: '100%', height: '100%', border: 'none', borderRadius: '12px' }}
                />
              ) : (
                /* ── Video local / CDN: dùng thẻ <video> HTML5 ── */
                <video
                  id="lessonVideo"
                  ref={videoRef}
                  controls
                  src={videoSrc}
                  onTimeUpdate={handleTimeUpdate}
                  onEnded={handleEnded}
                >
                  Trình duyệt của bạn không hỗ trợ phát video.
                </video>
              )
            ) : (
              <div className="l-video-placeholder">
                <span className="icon">📄</span>
                <p>Bài học này không có video</p>
                <span>Hãy đọc mô tả bên dưới.</span>
              </div>
            )}
          </div>

          {/* Lesson Info */}
          <div className="s-card s-card-body">
            <div>
              <div
                className="lesson-tags"
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}
              >
                <span className={`s-badge ${lesson.video_url ? 's-badge-blue' : 's-badge-warn'}`}>
                  {lesson.video_url ? '🎬 Bài học Video' : '📎 Bài học Văn bản'}
                </span>
                <span
                  className="s-badge"
                  style={{ background: 'var(--s-surface-2)', color: 'var(--s-text-muted)', border: 'none' }}
                >
                  {chapter.chapter_name}
                </span>
                {isCompleted && (
                  <span id="completedBadge" className="s-badge s-badge-green">
                    ✅ Đã hoàn thành
                  </span>
                )}
              </div>
              <h1 className="q-title" style={{ margin: '0.5rem 0 1.5rem 0' }}>
                {lesson.title}
              </h1>
            </div>

            {/* Tabs */}
            <div className="l-tabs-bar">
              <button
                id="tabDescBtn"
                onClick={() => setActiveTab('desc')}
                className={`l-tab-btn${activeTab === 'desc' ? ' active' : ''}`}
              >
                Mô tả bài học
              </button>
              {lesson.document_url && (
                <button
                  id="tabDocBtn"
                  onClick={() => setActiveTab('doc')}
                  className={`l-tab-btn${activeTab === 'doc' ? ' active' : ''}`}
                >
                  Tài liệu đính kèm
                </button>
              )}
            </div>

            {/* Tab Panels */}
            <div style={{ marginTop: '1.25rem' }}>
              <div
                id="panelDesc"
                className={`l-tab-panel whitespace-pre-line${activeTab !== 'desc' ? ' hidden' : ''}`}
              >
                {lesson.description || <p className="text-slate-400 italic">Bài học này chưa có phần mô tả.</p>}
              </div>
              {lesson.document_url && (
                <div id="panelDoc" className={`l-tab-panel${activeTab !== 'doc' ? ' hidden' : ''}`}>
                  <div className="l-doc-download">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: 0 }}>
                      <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>📎</span>
                      <div style={{ minWidth: 0 }}>
                        <p
                          className="truncate"
                          style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--s-text)', margin: 0 }}
                        >
                          {lesson.document_url.split('/').pop()}
                        </p>
                        <p style={{ fontSize: '0.75rem', color: 'var(--s-text-muted)', margin: '0.15rem 0 0 0' }}>
                          Tài liệu học tập đính kèm
                        </p>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                      {docSrc && lesson.video_url && (
                        <button
                          type="button"
                          onClick={() => {
                            setPlayerTab('doc');
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                          }}
                          className="s-btn s-btn-sm"
                          style={{ background: 'var(--s-surface)', border: '1px solid var(--s-border)', color: 'var(--s-text)' }}
                        >
                          👁 Xem ở trên
                        </button>
                      )}
                      {docSrc ? (
                        <a href={docSrc} target="_blank" rel="noreferrer" download className="s-btn s-btn-primary s-btn-sm">
                          📥 Tải xuống
                        </a>
                      ) : (
                        <span className="s-badge s-badge-warn">Chưa có file</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

          </div>

          {/* Thanh hành động: hoàn thành + điều hướng bài học */}
          <div className="l-action-bar">
            {isCompleted ? (
              <span className="l-action-done">✅ Đã hoàn thành bài học</span>
            ) : (
              <button
                id="markDoneBtn"
                onClick={markDone}
                disabled={markingDone}
                className="s-btn s-btn-primary"
                style={{ background: 'var(--s-success)', borderColor: 'var(--s-success)', color: '#fff' }}
              >
                {markingDone ? '⏳ Đang lưu...' : '✅ Đánh dấu hoàn thành'}
              </button>
            )}

            <div className="l-action-bar-nav">
              {/* Bộ câu hỏi ôn tập theo kiến thức của bài (khi giảng viên đã soạn) */}
              {lesson.review_question_count > 0 && (
                <Link
                  to={`/quiz-show?id=${lesson.review_quiz_id}`}
                  className="s-btn s-btn-outline s-btn-sm"
                  title="Làm bài ôn tập kiến thức của bài học này"
                >
                  📝 Ôn tập bài này ({lesson.review_question_count} câu)
                </Link>
              )}
              {prevLesson && (
                <Link
                  to={`/lesson?id=${prevLesson.id}`}
                  className="l-nav-btn-sm l-nav-btn-sm-prev"
                  title={prevLesson.title}
                >
                  ← Bài trước
                </Link>
              )}
              {nextLesson && (
                <Link
                  to={`/lesson?id=${nextLesson.id}`}
                  className="l-nav-btn-sm l-nav-btn-sm-next"
                  title={nextLesson.title}
                >
                  Bài tiếp theo →
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar: Curriculum */}
        <div className="l-curriculum-card">
          <div className="l-curriculum-header">
            <p>Chương trình học</p>
            <h2>{course.title}</h2>
            <div className="l-progress-info">
              <span>{totalCount} bài học</span>
              <span id="progressPct" style={{ color: 'var(--s-primary)' }}>
                {pct}% Hoàn thành
              </span>
            </div>
            <div className="l-progress-bar-wrap">
              <div className="l-progress-bar-fill" id="progressBar" style={{ width: `${pct}%` }}></div>
            </div>
          </div>

          <div className="l-chapters-list custom-scrollbar">
            {chaptersWithLessons.map((chap, chapIdx) => (
              <div key={chap.id} className="l-chapter-item">
                <div className="l-chapter-title-row">
                  <span
                    className="truncate"
                    style={{
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      color: 'var(--s-text)',
                      cursor: 'default',
                      lineHeight: 1.4,
                    }}
                  >
                    {chapIdx + 1}. {chap.chapter_name}
                  </span>
                  <span
                    className="s-badge"
                    style={{
                      background: 'var(--s-surface-2)',
                      color: 'var(--s-text-muted)',
                      border: 'none',
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      flexShrink: 0,
                    }}
                  >
                    {chap.lessons.length} bài
                  </span>
                </div>
                <div className="l-lessons-sublist">
                  {chap.lessons.map((l) => {
                    const isActive = l.id === lesson.id;
                    const isDone = completedIds.has(l.id);
                    const icon = isDone ? '✅' : l.video_url ? '🎬' : '📎';
                    return (
                      <Link
                        key={l.id}
                        to={`/lesson?id=${l.id}`}
                        data-lesson-id={l.id}
                        className={`l-lesson-link${isActive ? ' active active-sidebar-item' : ''}${isDone ? ' lesson-done' : ''}`}
                      >
                        <span className="lesson-icon" style={{ flexShrink: 0, fontSize: '0.9rem' }}>
                          {icon}
                        </span>
                        <span className="truncate" style={{ flexGrow: 1 }}>
                          {l.title}
                        </span>
                        {isActive && (
                          <span
                            className="s-badge s-badge-blue"
                            style={{ fontSize: '0.65rem', padding: '0.1rem 0.35rem', flexShrink: 0 }}
                          >
                            Đang học
                          </span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Nút nổi "Hỏi AI" (chỉ hiện khi bài học có tài liệu PDF) */}
      {lesson.document_url && !aiOpen && (
        <button
          type="button"
          onClick={() => setAiOpen(true)}
          title="Hỏi AI về bài học"
          style={{
            position: 'fixed',
            right: '1.5rem',
            bottom: '1.5rem',
            width: 56,
            height: 56,
            borderRadius: '50%',
            border: 'none',
            background: 'var(--s-primary)',
            color: '#fff',
            fontSize: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(0,0,0,0.25)',
            cursor: 'pointer',
            zIndex: 40,
          }}
        >
          🤖
        </button>
      )}

      {/* Khung chat AI Tutor của bài học */}
      {lesson.document_url && aiOpen && (
        <div
          className="s-card"
          style={{
            position: 'fixed',
            right: '1.5rem',
            bottom: '1.5rem',
            width: 420,
            maxWidth: 'calc(100vw - 2rem)',
            height: 620,
            maxHeight: 'calc(100vh - 3rem)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 40,
            boxShadow: '0 8px 30px rgba(0,0,0,0.25)',
          }}
        >
          <div
            style={{
              padding: '0.85rem 1rem',
              borderBottom: '1px solid var(--s-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexShrink: 0,
            }}
          >
            <div style={{ minWidth: 0 }}>
              <p style={{ margin: 0, fontWeight: 700, fontSize: '0.9rem' }}>🤖 Hỏi AI về bài học</p>
              <p
                className="truncate"
                style={{ margin: '0.15rem 0 0 0', fontSize: '0.7rem', color: 'var(--s-text-muted)' }}
              >
                Trả lời dựa trên tài liệu PDF của bài "{lesson.title}"
              </p>
            </div>
            <button
              type="button"
              onClick={() => setAiOpen(false)}
              className="s-btn s-btn-sm"
              style={{ background: 'transparent', border: 'none', fontSize: '1.1rem', flexShrink: 0 }}
            >
              ✕
            </button>
          </div>

          <div
            ref={aiThreadRef}
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.8rem',
            }}
          >
            {aiMessages.length === 0 && !aiSending && (
              <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--s-text-muted)', maxWidth: 280 }}>
                <div style={{ fontSize: '1.75rem' }}>🤖</div>
                <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
                  Hỏi bất cứ điều gì về nội dung tài liệu PDF đính kèm bài học này.
                </p>
              </div>
            )}

            {aiMessages.map((m, i) => (
              <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '88%' }}>
                <div
                  style={{
                    padding: '0.55rem 0.75rem',
                    borderRadius: 12,
                    fontSize: '0.8rem',
                    lineHeight: 1.5,
                    whiteSpace: 'pre-wrap',
                    background: m.role === 'user' ? 'var(--s-primary)' : 'var(--s-surface-2)',
                    color: m.role === 'user' ? '#fff' : 'inherit',
                    border: m.role === 'user' ? 'none' : '1px solid var(--s-border)',
                  }}
                >
                  {m.content}
                </div>
                {m.role === 'assistant' && Array.isArray(m.sources) && m.sources.length > 0 && (
                  <div style={{ marginTop: '0.3rem', display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                    {m.sources.map((s, j) => (
                      <span
                        key={j}
                        style={{
                          fontSize: '0.65rem',
                          padding: '0.15rem 0.4rem',
                          borderRadius: 999,
                          background: 'rgba(37,99,235,.1)',
                          color: 'var(--s-primary)',
                          fontWeight: 600,
                        }}
                      >
                        📄 {s.document}{s.page ? ` — tr. ${s.page}` : ''}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {aiSending && (
              <div style={{ alignSelf: 'flex-start', color: 'var(--s-text-muted)', fontSize: '0.78rem' }}>
                🤖 Đang tìm trong tài liệu…
              </div>
            )}
          </div>

          <form
            onSubmit={sendAiMessage}
            style={{
              borderTop: '1px solid var(--s-border)',
              padding: '0.6rem',
              display: 'flex',
              gap: '0.4rem',
              flexShrink: 0,
            }}
          >
            <input
              value={aiInput}
              onChange={(e) => setAiInput(e.target.value)}
              placeholder="Nhập câu hỏi…"
              disabled={aiSending}
              style={{ flex: 1, padding: '0.5rem 0.65rem', borderRadius: 8, border: '1px solid var(--s-border)', minWidth: 0 }}
            />
            <button
              className="s-btn s-btn-primary s-btn-sm"
              type="submit"
              disabled={aiSending || !aiInput.trim()}
            >
              Gửi
            </button>
          </form>
        </div>
      )}

    </main>
  );
}
