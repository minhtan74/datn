import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { aiService } from '../../services/aiService';
import { chapterService } from '../../services/chapterService';
import { courseService } from '../../services/courseService';
import { lessonService } from '../../services/lessonService';
import { quizService } from '../../services/quizService';
import DifficultyBar from '../../components/common/DifficultyBar.jsx';
import DraftQuestionCard from '../../components/teacher/DraftQuestionCard.jsx';
import { GRADING_METHODS } from '../../utils/quizGrading';

// Kiểm tra 1 câu trong bản nháp trước khi lưu -> lý do lỗi, hợp lệ thì null
function draftError(q) {
  if (!q.question?.trim()) return 'thiếu nội dung câu hỏi';
  if (!q.options.A?.trim() || !q.options.B?.trim()) return 'cần ít nhất phương án A và B';
  if (!q.options[q.correct_answer]?.trim()) return `đáp án ${q.correct_answer} đang để trống`;
  return null;
}

/**
 * Nhập bộ đề trắc nghiệm từ file Word (.docx): đọc file -> xem trước, sửa bản nháp -> duyệt & lưu
 * thành quiz mới hoặc thêm vào bộ ôn tập của chương / bài học. Không dùng AI.
 * onSaved: báo trang cha khi đã lưu quiz mới (để quay về danh sách và tải lại).
 */
export default function WordQuizImport({ onSaved }) {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const fileRef = useRef(null);

  // Khóa học + nơi lưu: 'new' = quiz mới, 'ch:<id>' = bộ ôn tập chương, 'ls:<id>' = bộ ôn tập bài
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [chapters, setChapters] = useState([]); // mỗi chương kèm lessons[]
  const [target, setTarget] = useState('new');

  // Kết quả đọc file: bản nháp câu hỏi (sửa được) + danh sách câu lỗi
  const [fileName, setFileName] = useState('');
  const [parsing, setParsing] = useState(false);
  const [result, setResult] = useState(null); // { found, errors, truncated }
  const [questions, setQuestions] = useState([]);

  // Cài đặt quiz mới
  const [title, setTitle] = useState('');
  const [settings, setSettings] = useState({ duration: '', passing_score: '', max_attempts: '' });
  const [grading, setGrading] = useState('highest');
  const [saving, setSaving] = useState(false);

  // Khóa học của giảng viên (admin thấy tất cả)
  useEffect(() => {
    (async () => {
      const res = await courseService.getCourses();
      const mine = (res?.data?.data || []).filter((c) => !user || c.teacher_id === user.id || user.role === 'admin');
      setCourses(mine);
      if (mine.length) setCourseId(String(mine[0].id));
    })();
  }, [user]);

  // Đổi khóa -> tải chương + bài để chọn bộ ôn tập; về lại "quiz mới"
  useEffect(() => {
    if (!courseId) return;
    let cancelled = false;
    (async () => {
      const res = await chapterService.getChapters(Number(courseId));
      const list = res?.ok ? res.data.data || [] : [];
      const lessonsRes = await Promise.all(list.map((ch) => lessonService.getLessons(ch.id)));
      if (cancelled) return;
      setChapters(list.map((ch, i) => ({ ...ch, lessons: lessonsRes[i]?.ok ? lessonsRes[i].data.data || [] : [] })));
      setTarget('new');
    })();
    return () => {
      cancelled = true;
    };
  }, [courseId]);

  // Tải file Word mẫu
  async function downloadTemplate() {
    const res = await quizService.downloadWordTemplate();
    if (!res?.ok) {
      showToast('Không tải được file mẫu.', 'error');
      return;
    }
    const url = URL.createObjectURL(res.data);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mau-de-trac-nghiem.docx';
    a.click();
    URL.revokeObjectURL(url);
  }

  // Chọn file -> gửi lên server đọc ngay thành bản nháp
  async function handleFile(e) {
    const file = e.target.files?.[0];
    e.target.value = ''; // chọn lại cùng file vẫn đọc lại được
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.docx')) {
      showToast('Chỉ nhận file .docx (file .doc: mở bằng Word rồi Lưu thành .docx).', 'error');
      return;
    }
    setParsing(true);
    setFileName(file.name);
    const res = await quizService.importWord(file);
    setParsing(false);
    if (!(res?.ok && res.data?.success)) {
      setResult(null);
      setQuestions([]);
      showToast(res?.data?.message || 'Không đọc được file.', 'error');
      return;
    }
    const data = res.data.data;
    setResult({
      found: data.found, errors: data.errors, truncated: data.truncated,
      ignored: data.ignored || [], ignoredCount: data.ignored_count || 0, drafted: data.questions.length,
    });
    setQuestions(data.questions);
    if (!title) setTitle(file.name.replace(/\.docx$/i, ''));
  }

  // Sửa 1 trường / 1 phương án / bỏ câu thứ i của bản nháp
  function patch(i, field, value) {
    setQuestions((qs) => qs.map((q, idx) => (idx === i ? { ...q, [field]: value } : q)));
  }
  function patchOption(i, letter, value) {
    setQuestions((qs) => qs.map((q, idx) => (idx === i ? { ...q, options: { ...q.options, [letter]: value } } : q)));
  }
  function removeQuestion(i) {
    setQuestions((qs) => qs.filter((_, idx) => idx !== i));
  }

  // Nơi lưu đang chọn
  const [kind, idRaw] = target.split(':');
  const targetId = idRaw ? Number(idRaw) : null;
  const targetLabel =
    kind === 'ch'
      ? chapters.find((c) => c.id === targetId)?.chapter_name
      : kind === 'ls'
        ? `bài "${chapters.flatMap((c) => c.lessons).find((l) => l.id === targetId)?.title || ''}"`
        : null;

  // Duyệt & lưu: kiểm tra từng câu trước, báo đúng câu đang lỗi
  async function save() {
    const bad = questions.map((q, i) => [i, draftError(q)]).find(([, err]) => err);
    if (bad) {
      showToast(`Câu ${bad[0] + 1}: ${bad[1]}.`, 'error');
      return;
    }
    if (!questions.length || (kind === 'new' && !title.trim())) {
      showToast('Cần tiêu đề quiz và ít nhất 1 câu hỏi.', 'error');
      return;
    }
    setSaving(true);
    const res = await aiService.approveQuiz({
      courseId: Number(courseId),
      chapterId: kind === 'ch' ? targetId : null,
      reviewLessonId: kind === 'ls' ? targetId : null,
      title: title.trim(),
      questions,
      source: 'word',
      ...(kind === 'new'
        ? {
            ...Object.fromEntries(Object.entries(settings).map(([k, v]) => [k, v === '' ? null : Number(v)])),
            grading_method: grading,
          }
        : {}),
    });
    setSaving(false);
    if (!(res?.ok && res.data?.success)) {
      showToast(res?.data?.message || 'Lưu thất bại.', 'error');
      return;
    }
    showToast(res.data.message || `Đã lưu ${res.data.data?.question_count} câu.`, 'success');
    setQuestions([]);
    setResult(null);
    setFileName('');
    setTitle('');
    if (kind === 'new' && onSaved) onSaved(res.data.data);
    else navigate(`/teacher/quizzes/${res.data.data.quiz_id}/questions`);
  }

  return (
    <>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0 0 1rem' }}>
        Nhập bộ đề có sẵn trong file Word — hệ thống đọc đúng từng câu (không dùng AI). Bạn xem lại, sửa rồi mới lưu.
      </p>

      <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div className="form-grid" style={{ alignItems: 'end' }}>
          <div className="form-group">
            <label className="form-label">Khóa học</label>
            <select className="form-control" value={courseId} onChange={(e) => setCourseId(e.target.value)}>
              {courses.length === 0 && <option value="">— Chưa có khóa học —</option>}
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Lưu vào</label>
            <select className="form-control" value={target} onChange={(e) => setTarget(e.target.value)}>
              <option value="new">Quiz mới</option>
              {chapters.map((ch) => (
                <optgroup key={ch.id} label={ch.chapter_name}>
                  <option value={`ch:${ch.id}`}>Bộ ôn tập cả chương</option>
                  {ch.lessons.map((l) => (
                    <option key={l.id} value={`ls:${l.id}`}>Bộ ôn tập bài: {l.title}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap', marginTop: '0.5rem' }}>
          <input ref={fileRef} type="file" accept=".docx" hidden onChange={handleFile} />
          <button className="btn btn-primary" onClick={() => fileRef.current?.click()} disabled={parsing || !courseId}>
            {parsing ? 'Đang đọc file…' : '📄 Chọn file Word (.docx)'}
          </button>
          <button type="button" className="btn btn-outline" onClick={downloadTemplate}>
            📥 Tải file Word mẫu
          </button>
          {fileName && <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{fileName}</span>}
        </div>

        {/* Định dạng file được hỗ trợ */}
        <details style={{ marginTop: '0.9rem', fontSize: '0.82rem' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 600 }}>Định dạng file Word được hỗ trợ</summary>
          <ul style={{ margin: '0.5rem 0 0', paddingLeft: '1.2rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
            <li>Mỗi câu bắt đầu bằng <code>Câu 1:</code>, <code>Câu 2.</code>, <code>Question 1:</code> (hoặc <code>1.</code>); nhãn mức độ <code>(NB)</code> <code>(TH)</code> <code>(VD)</code> ngay sau số câu được hiểu là độ khó.</li>
            <li>Phương án <code>A.</code> / <code>A)</code> / <code>(A)</code> … <code>D.</code>, mỗi phương án một dòng hoặc cùng một dòng. Tối thiểu A và B.</li>
            <li>Đáp án đúng: dòng <code>Đáp án: B</code> / <code>Chọn B</code>, <b>hoặc</b> in đậm / gạch chân / tô màu phương án đúng, <b>hoặc</b> dấu <code>*</code>, <b>hoặc</b> bảng đáp án cuối đề (dòng <code>1.B 2.C …</code> hay bảng Word <code>Câu | Đáp án</code>), <b>hoặc</b> <code>Chọn B</code> cuối lời giải.</li>
            <li><b>Đọc hiểu (Văn, Anh…)</b>: dòng <code>Đọc đoạn trích sau và trả lời câu 1 đến câu 5</code> / <code>Read the following passage … from 1 to 5</code> + đoạn văn → đoạn văn được gắn vào từng câu trong phạm vi.</li>
            <li><b>Đúng / sai nhiều ý (THPT 2025)</b>: các ý <code>a)</code> <code>b)</code> <code>c)</code> <code>d)</code> + <code>Đáp án: a) Đúng, b) Sai…</code> (hoặc <code>Đ S Đ S</code>) → tách thành từng câu Đúng / Sai.</li>
            <li><b>Có bao nhiêu phát biểu đúng (Sinh…)</b>: các ý a) b)… nằm trong đề, phương án A–D bên dưới.</li>
            <li>Giữ đúng <b>chỉ số trên / dưới</b> (H₂SO₄, m/s², 10⁻³), <b>phần gạch chân</b> của câu phát âm / trọng âm, <b>thụt lề code</b>, <b>bảng số liệu</b>, <b>hình ảnh</b> (PNG, JPG, GIF) và <b>công thức Equation của Word</b>.</li>
            <li>Tùy chọn: <code>Giải thích / Lời giải: …</code>, <code>Độ khó: Dễ / Trung bình / Khó</code>, <code>Chủ đề: …</code>.</li>
            <li>
              Chưa hỗ trợ: câu <b>trả lời ngắn</b> (THPT 2025 phần III), công thức <b>MathType / Equation 3.0</b>
              (MathType → Convert Equations → Office Math), ảnh EMF / WMF, danh sách đánh số tự động của Word.
            </li>
          </ul>
        </details>

        {/* Kết quả đọc file: số câu đọc được + từng câu lỗi kèm lý do */}
        {result && (
          <div style={{ marginTop: '1rem' }}>
            <p style={{ margin: 0, fontWeight: 600, color: result.errors.length ? 'var(--warning,#D97706)' : 'var(--success,#059669)' }}>
              {result.errors.length ? '⚠️' : '✓'} Đọc được {result.found - result.errors.length}/{result.found} câu
              {/* Câu đúng / sai nhiều ý được tách thành nhiều câu nên bản nháp có thể nhiều câu hơn */}
              {result.drafted !== result.found - result.errors.length ? ` → ${result.drafted} câu trong bản nháp` : ''}
              {result.errors.length ? ` · ${result.errors.length} câu lỗi (chưa đưa vào bản nháp)` : ''}
              {result.truncated ? ' · file quá 200 câu, chỉ đọc 200 câu đầu' : ''}
            </p>
            {result.errors.length > 0 && (
              <ul style={{ margin: '0.4rem 0 0', paddingLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--danger,#DC2626)' }}>
                {result.errors.map((e, i) => (
                  <li key={i}>
                    <strong>Câu {e.number}</strong> ({e.snippet || '—'}): {e.reason}
                  </li>
                ))}
              </ul>
            )}
            {/* Dòng nằm ngoài câu hỏi (tiêu đề đề thi, hướng dẫn...) -> cho giảng viên kiểm tra không sót nội dung */}
            {result.ignoredCount > 0 && (
              <details style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <summary style={{ cursor: 'pointer' }}>
                  Bỏ qua {result.ignoredCount} dòng không thuộc câu hỏi nào (tiêu đề, hướng dẫn…) — bấm để kiểm tra
                </summary>
                <ul style={{ margin: '0.3rem 0 0', paddingLeft: '1.2rem' }}>
                  {result.ignored.map((line, i) => (
                    <li key={i}>{line}</li>
                  ))}
                  {result.ignoredCount > result.ignored.length && <li>…</li>}
                </ul>
              </details>
            )}
          </div>
        )}
      </div>

      {questions.length > 0 && (
        <>
          <div className="card" style={{ padding: '1.25rem', marginBottom: '1rem', display: 'flex', gap: '1rem', alignItems: 'end', flexWrap: 'wrap' }}>
            {kind === 'new' ? (
              <>
                <div className="form-group" style={{ flex: 1, minWidth: 240 }}>
                  <label className="form-label">Tiêu đề quiz</label>
                  <input className="form-control" maxLength={255} value={title} onChange={(e) => setTitle(e.target.value)} />
                </div>
                {[
                  { key: 'duration', label: 'Thời gian (phút)', max: 600 },
                  { key: 'passing_score', label: 'Điểm đạt (%)', max: 100 },
                  { key: 'max_attempts', label: 'Số lần làm', max: 100 },
                ].map((f) => (
                  <div className="form-group" key={f.key} style={{ width: 130 }}>
                    <label className="form-label">{f.label}</label>
                    <input
                      className="form-control"
                      type="number"
                      min="0"
                      max={f.max}
                      placeholder="Không giới hạn"
                      value={settings[f.key]}
                      onChange={(e) => setSettings({ ...settings, [f.key]: e.target.value })}
                    />
                  </div>
                ))}
                <div className="form-group" style={{ width: 170 }}>
                  <label className="form-label">Tính điểm theo</label>
                  <select
                    className="form-control"
                    value={grading}
                    disabled={Number(settings.max_attempts) === 1}
                    onChange={(e) => setGrading(e.target.value)}
                  >
                    {GRADING_METHODS.map((m) => (
                      <option key={m.key} value={m.key}>{m.label}</option>
                    ))}
                  </select>
                </div>
              </>
            ) : (
              <p style={{ flex: 1, minWidth: 240, margin: 0 }}>
                Các câu sẽ được thêm vào bộ câu hỏi ôn tập của <strong>{targetLabel}</strong>.
              </p>
            )}
            <button className="btn btn-primary" onClick={save} disabled={saving}>
              {saving ? 'Đang lưu…' : `✓ Duyệt & Lưu (${questions.length} câu)`}
            </button>
          </div>

          <DifficultyBar questions={questions} />

          {questions.map((q, i) => (
            <DraftQuestionCard
              key={`${q.number}-${i}`}
              q={q}
              index={i}
              meta={[`câu ${q.number} trong file`, q.topic, q.answer_source ? `đáp án theo ${q.answer_source}` : null]
                .filter(Boolean)
                .join(' · ')}
              onPatch={(field, value) => patch(i, field, value)}
              onPatchOption={(L, value) => patchOption(i, L, value)}
              onRemove={() => removeQuestion(i)}
            />
          ))}
        </>
      )}
    </>
  );
}
