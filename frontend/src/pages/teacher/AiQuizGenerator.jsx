import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { aiService } from '../../services/aiService';
import { chapterService } from '../../services/chapterService';
import { courseService } from '../../services/courseService';
import { lessonService } from '../../services/lessonService';
import DifficultyBar, { DIFFICULTY_LEVELS } from '../../components/common/DifficultyBar.jsx';
import { GRADING_METHODS } from '../../utils/quizGrading';
import DraftQuestionCard from '../../components/teacher/DraftQuestionCard.jsx';

// Mẫu tỉ lệ % độ khó hay dùng (Dễ / Trung bình / Khó)
const PCT_PRESETS = [
  { label: 'Cơ bản', pct: { easy: 50, medium: 40, hard: 10 } },
  { label: 'Cân bằng', pct: { easy: 30, medium: 50, hard: 20 } },
  { label: 'Nâng cao', pct: { easy: 20, medium: 40, hard: 40 } },
];

// Quy tỉ lệ % ra số câu mỗi mức: làm tròn xuống rồi chia phần dư cho mức có phần lẻ lớn nhất,
// để tổng số câu luôn đúng bằng total (vd 10 câu, 33/33/34% -> 3/3/4)
function splitByPercent(total, pct) {
  const raw = DIFFICULTY_LEVELS.map((d) => ({ key: d.key, exact: (total * (Number(pct[d.key]) || 0)) / 100 }));
  const counts = Object.fromEntries(raw.map((r) => [r.key, Math.floor(r.exact)]));
  let rest = total - Object.values(counts).reduce((a, b) => a + b, 0);
  [...raw]
    .sort((a, b) => (b.exact - Math.floor(b.exact)) - (a.exact - Math.floor(a.exact)))
    .forEach((r) => {
      if (rest > 0 && r.exact > 0) {
        counts[r.key] += 1;
        rest -= 1;
      }
    });
  return counts;
}

// Đề cuối khóa tối đa 60 câu (đề thường / ôn tập tối đa 30); mỗi mức của 1 chương tối đa 20 câu (giới hạn API)
const MAX_EXAM_TOTAL = 60;
const MAX_SINGLE_TOTAL = 30;

// Kiểm tra tổng số câu + tỉ lệ % -> trả lý do lỗi, hợp lệ thì null
function pctErrorOf(total, pct, maxTotal) {
  const pctSum = DIFFICULTY_LEVELS.reduce((sum, d) => sum + (Number(pct[d.key]) || 0), 0);
  if (pctSum !== 100) return `Tổng tỉ lệ đang là ${pctSum}%, cần đúng 100%.`;
  if (total < 1 || total > maxTotal) return `Tổng số câu phải từ 1 đến ${maxTotal}.`;
  return null;
}

// Chia đều n câu cho các chương (theo thứ tự chương), phần dư dồn cho các chương đầu: 7 câu / 3 chương -> 3/2/2
function splitEvenly(n, ids) {
  const out = Object.fromEntries(ids.map((id) => [id, Math.floor(n / ids.length)]));
  ids.slice(0, n % ids.length).forEach((id) => {
    out[id] += 1;
  });
  return out;
}

// Phân ngẫu nhiên n câu vào các chương (mỗi câu bốc 1 chương bất kỳ), mỗi chương tối đa 20 câu / mức
function splitRandomly(n, ids) {
  const out = Object.fromEntries(ids.map((id) => [id, 0]));
  for (let i = 0; i < n; i += 1) {
    const free = ids.filter((id) => out[id] < 20);
    const pick = (free.length ? free : ids)[Math.floor(Math.random() * (free.length || ids.length))];
    out[pick] += 1;
  }
  return out;
}

// Số câu còn thiếu từng mức = yêu cầu - hiện có (không âm)
function missingOf(requested, have) {
  return Object.fromEntries(
    DIFFICULTY_LEVELS.map((d) => [d.key, Math.max(0, (requested[d.key] || 0) - (have[d.key] || 0))]),
  );
}
const sumMix = (m) => DIFFICULTY_LEVELS.reduce((sum, d) => sum + (m[d.key] || 0), 0);

// Chuẩn hóa nội dung câu hỏi để loại câu trùng giữa các chương
const normText = (t) => (t || '').trim().toLowerCase().replace(/\s+/g, ' ');

/**
 * PHASE 9 — AI Quiz Generator: sinh → giảng viên chỉnh/duyệt → lưu. AI KHÔNG tự lưu.
 * Được nhúng làm tab trong trang Quiz trắc nghiệm (embedded = ẩn tiêu đề trang riêng;
 * onSaved = báo trang cha khi đã lưu quiz mới để quay về danh sách và tải lại).
 */
export default function AiQuizGenerator({ embedded = false, onSaved }) {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  // Phạm vi chọn sẵn khi mở từ trang câu hỏi ôn tập (?chapter_id= / ?lesson_id=) — chỉ áp dụng lần tải đầu
  const initialScope = useRef(
    searchParams.get('lesson_id')
      ? `ls:${searchParams.get('lesson_id')}`
      : searchParams.get('chapter_id')
        ? `ch:${searchParams.get('chapter_id')}`
        : '',
  );

  // Tham số sinh câu hỏi: khóa học, phạm vi ('multi' = đề cuối khóa, 'ch:<id>' = ôn tập chương, 'ls:<id>' = ôn tập bài,
  // '' = theo tài liệu khóa — chỉ dùng khi khóa chưa có chương),
  // số câu, độ khó, tiêu đề quiz
  const [courses, setCourses] = useState([]);
  const [courseId, setCourseId] = useState('');
  const [chapters, setChapters] = useState([]); // mỗi chương kèm lessons[]
  const [scope, setScope] = useState('');
  // Phân bổ độ khó theo tỉ lệ %: tổng số câu + % từng mức -> quy ra số câu mỗi mức
  const [total, setTotal] = useState(10);
  const [pct, setPct] = useState(PCT_PRESETS[1].pct);
  const totalNum = Number(total) || 0;
  const mix = splitByPercent(totalNum, pct);

  // Đề cuối khóa: mỗi mức độ khó lấy câu từ những chương nào { easy: [chapterId...], medium: [...], hard: [...] }
  const [levelChapters, setLevelChapters] = useState({ easy: [], medium: [], hard: [] });
  // Tiến độ khi sinh lần lượt từng chương
  const [progress, setProgress] = useState(null);
  // Kế hoạch phân bổ chốt lúc sinh: [{ key, chapterId, lessonId, name, requested:{easy,medium,hard}, error }]
  // (đề cuối khóa: mỗi chương 1 phần; các phạm vi khác: 1 phần). So với bản nháp hiện tại để biết còn thiếu gì.
  const [plan, setPlan] = useState([]);
  const [title, setTitle] = useState('');
  // Cài đặt làm bài cho quiz mới (để trống = không giới hạn); đề cuối khóa được điền sẵn gợi ý
  const [quizSettings, setQuizSettings] = useState({ duration: '', passing_score: '', max_attempts: '' });
  // Cách tính điểm khi học viên làm nhiều lượt (quiz mới)
  const [grading, setGrading] = useState('highest');

  // Trạng thái xử lý và bản nháp câu hỏi AI trả về (meta: thông tin model, số câu yêu cầu/nhận được...)
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [meta, setMeta] = useState(null);
  const [questions, setQuestions] = useState([]); // [{question, options:{A..D}, correct_answer, explanation, difficulty, topic}]
  // Đích lưu của bản nháp, chốt lúc bấm Sinh: đổi khóa / phạm vi sau đó không làm câu hỏi bị lưu nhầm chỗ
  // { courseId, chapterId, lessonId, label } — label có giá trị = thêm vào bộ ôn tập, null = tạo quiz mới
  const [draftTarget, setDraftTarget] = useState(null);

  // Khi mở trang: tải các khóa học của giảng viên đang đăng nhập (admin thấy tất cả)
  useEffect(() => {
    (async () => {
      const res = await courseService.getCourses();
      const mine = (res?.data?.data || []).filter(
        (c) => !user || c.teacher_id === user.id || user.role === 'admin',
      );
      setCourses(mine);
      // Ưu tiên khóa học truyền qua ?course_id=, không có thì chọn khóa đầu tiên
      const fromParam = mine.find((c) => String(c.id) === searchParams.get('course_id'));
      if (fromParam) setCourseId(String(fromParam.id));
      else if (mine.length) setCourseId(String(mine[0].id));
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Đổi khóa học -> tải chương + bài học của từng chương để chọn phạm vi ôn tập
  useEffect(() => {
    if (!courseId) return;
    let cancelled = false;
    (async () => {
      const res = await chapterService.getChapters(Number(courseId));
      const list = res?.ok ? res.data.data || [] : [];
      const lessonsRes = await Promise.all(list.map((ch) => lessonService.getLessons(ch.id)));
      if (cancelled) return;
      const full = list.map((ch, i) => ({ ...ch, lessons: lessonsRes[i]?.ok ? lessonsRes[i].data.data || [] : [] }));
      setChapters(full);
      // Mặc định không chọn chương nào -> mọi mức lấy ngẫu nhiên lẫn lộn từ các chương
      setLevelChapters({ easy: [], medium: [], hard: [] });
      // Chỉ giữ phạm vi truyền qua URL nếu chương / bài đó thuộc khóa đang chọn
      const wanted = initialScope.current;
      initialScope.current = '';
      const valid = full.some(
        (ch) => `ch:${ch.id}` === wanted || ch.lessons.some((l) => `ls:${l.id}` === wanted),
      );
      // Không truyền phạm vi -> mặc định đề kiểm tra cuối khóa; khóa chưa có chương thì chỉ còn cách sinh theo tài liệu
      setScope(valid ? wanted : full.length ? 'multi' : '');
    })();
    return () => {
      cancelled = true;
    };
  }, [courseId]);

  // Phạm vi đang chọn: chương hoặc bài học cần sinh câu ôn tập (lưu vào bộ ôn tập thay vì tạo quiz mới)
  const [scopeKind, scopeIdRaw] = scope.split(':');
  const scopeId = scopeIdRaw ? Number(scopeIdRaw) : null;
  const chapter = scopeKind === 'ch' ? chapters.find((ch) => ch.id === scopeId) : null;
  const lesson = scopeKind === 'ls' ? chapters.flatMap((ch) => ch.lessons).find((l) => l.id === scopeId) : null;
  const reviewTarget = chapter ? chapter.chapter_name : lesson ? `bài "${lesson.title}"` : null;
  // Đích lưu tương ứng với phạm vi đang chọn (chốt vào draftTarget khi bấm Sinh)
  const currentTarget = {
    courseId,
    chapterId: chapter ? chapter.id : null,
    lessonId: lesson ? lesson.id : null,
    label: reviewTarget,
  };
  // Phạm vi / khóa trên form đã khác đích của bản nháp đang có
  const scopeChanged =
    questions.length > 0 &&
    draftTarget &&
    (draftTarget.courseId !== currentTarget.courseId ||
      draftTarget.chapterId !== currentTarget.chapterId ||
      draftTarget.lessonId !== currentTarget.lessonId ||
      Boolean(draftTarget.label) !== Boolean(currentTarget.label));
  const isMulti = scope === 'multi';

  // Mức không chọn chương: phân ngẫu nhiên vào mọi chương. Giữ nguyên kết quả bốc giữa các lần render,
  // chỉ bốc lại khi đổi số câu / danh sách chương hoặc bấm "Xáo lại" (shuffleSeed)
  const [shuffleSeed, setShuffleSeed] = useState(0);
  const chapterIdsKey = chapters.map((ch) => ch.id).join(',');
  const randomAlloc = useMemo(
    () =>
      Object.fromEntries(
        DIFFICULTY_LEVELS.map((d) => [d.key, chapters.length ? splitRandomly(mix[d.key], chapters.map((ch) => ch.id)) : {}]),
      ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [mix.easy, mix.medium, mix.hard, chapterIdsKey, shuffleSeed],
  );

  // Đề cuối khóa: mức có chọn chương -> chia đều cho các chương đó; không chọn -> dùng kết quả phân ngẫu nhiên
  const perLevel = Object.fromEntries(
    DIFFICULTY_LEVELS.map((d) => {
      const ids = chapters.map((ch) => ch.id).filter((id) => levelChapters[d.key].includes(id));
      return [d.key, ids.length ? splitEvenly(mix[d.key], ids) : randomAlloc[d.key] || {}];
    }),
  );
  const hasRandomLevel = DIFFICULTY_LEVELS.some((d) => mix[d.key] > 0 && !levelChapters[d.key].length);
  const examRows = chapters
    .map((ch) => {
      const rowMix = Object.fromEntries(DIFFICULTY_LEVELS.map((d) => [d.key, perLevel[d.key][ch.id] || 0]));
      return { ch, rowMix, rowTotal: rowMix.easy + rowMix.medium + rowMix.hard };
    })
    .filter((r) => r.rowTotal > 0);

  // Lỗi cấu hình (nếu có) -> khóa nút sinh và hiện lý do
  const overloaded = examRows.find((r) => Object.values(r.rowMix).some((c) => c > 20));
  const mixError = isMulti
    ? pctErrorOf(totalNum, pct, MAX_EXAM_TOTAL) ||
      (overloaded
        ? `${overloaded.ch.chapter_name} bị dồn quá 20 câu ở một mức — hãy chọn thêm chương hoặc giảm số câu.`
        : null)
    : pctErrorOf(totalNum, pct, MAX_SINGLE_TOTAL) ||
      (Object.values(mix).some((c) => c > 20) ? 'Mỗi mức độ khó tối đa 20 câu.' : null);

  // Số câu hiện có trong bản nháp của 1 phần (đề cuối khóa: đếm theo chương; phạm vi khác: cả bản nháp).
  // Giảng viên xóa câu hoặc đổi độ khó thì phần thiếu cập nhật theo -> "Sinh bù" lấp đúng chỗ đó.
  function haveOf(part) {
    const have = { easy: 0, medium: 0, hard: 0 };
    questions
      .filter((q) => q.plan_key === part.key)
      .forEach((q) => {
        if (q.difficulty in have) have[q.difficulty] += 1;
      });
    return have;
  }
  const planStatus = plan.map((part) => {
    const have = haveOf(part);
    return { ...part, have, missing: missingOf(part.requested, have) };
  });
  const missingTotal = planStatus.reduce((sum, p) => sum + sumMix(p.missing), 0);

  // Câu AI tự giải ra đáp án khác đáp án đang đánh (và giảng viên chưa bấm "Giữ đáp án") -> cần xem lại
  const needsReview = (q) => Boolean(q.verify) && q.verify.answer !== q.correct_answer && !q.verify_dismissed;
  const flaggedCount = questions.filter(needsReview).length;
  const verifiedCount = questions.filter((q) => q.verified && q.verified === q.correct_answer).length;

  // Bật / tắt 1 chương cho 1 mức độ khó
  function toggleLevelChapter(level, chId) {
    setLevelChapters((prev) => ({
      ...prev,
      [level]: prev[level].includes(chId) ? prev[level].filter((id) => id !== chId) : [...prev[level], chId],
    }));
  }
  // Chọn tất cả chương (chia đều) / bỏ chọn (quay về lấy ngẫu nhiên) cho 1 mức
  function setLevelAll(level, on) {
    setLevelChapters((prev) => ({ ...prev, [level]: on ? chapters.map((ch) => ch.id) : [] }));
  }

  // Đề cuối khóa: gọi AI lần lượt từng chương (tránh 1 request quá lâu), gom câu hỏi và báo cáo từng chương
  async function generateMulti() {
    setDraftTarget({ ...currentTarget, label: null });
    setGenerating(true);
    setQuestions([]);
    setMeta(null);
    const parts = examRows.map((r) => ({
      key: `ch:${r.ch.id}`, chapterId: r.ch.id, lessonId: null, name: r.ch.chapter_name, requested: r.rowMix, error: null,
    }));
    setPlan(parts);
    const all = [];
    const seen = new Set();
    for (const [i, r] of examRows.entries()) {
      setProgress(`Đang sinh chương ${i + 1}/${examRows.length}: ${r.ch.chapter_name}…`);
      const res = await aiService.generateQuiz({ courseId, chapterId: r.ch.id, difficultyMix: r.rowMix });
      const data = res?.ok ? res.data?.data : null;
      (data?.questions || []).forEach((q) => {
        if (seen.has(normText(q.question))) return;
        seen.add(normText(q.question));
        // Gắn tên chương + phần kế hoạch để hiển thị và tính phần thiếu; chủ đề trống thì lấy tên chương
        all.push({ ...q, chapter_name: r.ch.chapter_name, plan_key: parts[i].key, topic: q.topic || r.ch.chapter_name });
      });
      parts[i].error = data ? null : res?.data?.message || 'Lỗi';
      setQuestions([...all]);
      setPlan([...parts]);
    }
    setProgress(null);
    setGenerating(false);
    if (!all.length) {
      showToast('Không sinh được câu hỏi nào.', 'error');
      return;
    }
    if (!title) {
      const c = courses.find((x) => String(x.id) === String(courseId));
      setTitle(`Kiểm tra cuối khóa - ${c?.title || 'Khóa học'}`);
      // Gợi ý cho đề cuối khóa: ~1.5 phút / câu, đạt 50%, làm 1 lần (giảng viên sửa được trước khi duyệt)
      setQuizSettings({ duration: Math.max(15, Math.ceil(all.length * 1.5)), passing_score: 50, max_attempts: 1 });
    }
  }

  // Gọi AI sinh bản nháp; lần đầu thì tự đặt tiêu đề quiz theo tên khóa học
  async function generate() {
    if (!courseId) return;
    if (isMulti) {
      generateMulti();
      return;
    }
    setDraftTarget(currentTarget);
    setGenerating(true);
    setQuestions([]);
    setMeta(null);
    const part = {
      key: 'single', chapterId: currentTarget.chapterId, lessonId: currentTarget.lessonId, name: null, requested: mix, error: null,
    };
    setPlan([part]);
    const res = await aiService.generateQuiz({
      courseId,
      chapterId: chapter ? chapter.id : null,
      lessonId: lesson ? lesson.id : null,
      difficultyMix: mix,
    });
    setGenerating(false);
    if (res?.ok && res.data?.data) {
      setQuestions((res.data.data.questions || []).map((q) => ({ ...q, plan_key: 'single' })));
      setMeta(res.data.data.meta || null);
      if (!title) {
        const c = courses.find((x) => String(x.id) === String(courseId));
        setTitle(`Quiz AI - ${c?.title || 'Khóa học'}`);
      }
    } else {
      showToast(res?.data?.message || 'Không sinh được câu hỏi.', 'error');
    }
  }

  // Sinh bù: gọi AI lại chỉ cho số câu còn thiếu của từng phần, thêm vào cuối bản nháp (loại câu trùng)
  async function fillMissing() {
    const todo = planStatus.filter((p) => sumMix(p.missing) > 0);
    if (!todo.length || !draftTarget) return;
    setGenerating(true);
    const all = [...questions];
    const seen = new Set(all.map((q) => normText(q.question)));
    const parts = plan.map((p) => ({ ...p }));
    let added = 0;
    for (const [i, p] of todo.entries()) {
      setProgress(`Đang sinh bù ${i + 1}/${todo.length}${p.name ? `: ${p.name}` : ''} (${sumMix(p.missing)} câu)…`);
      const res = await aiService.generateQuiz({
        courseId: draftTarget.courseId,
        chapterId: p.chapterId,
        lessonId: p.lessonId,
        difficultyMix: p.missing,
      });
      const data = res?.ok ? res.data?.data : null;
      (data?.questions || []).forEach((q) => {
        if (seen.has(normText(q.question))) return;
        seen.add(normText(q.question));
        added += 1;
        all.push({ ...q, plan_key: p.key, ...(p.name ? { chapter_name: p.name, topic: q.topic || p.name } : {}) });
      });
      const idx = parts.findIndex((x) => x.key === p.key);
      parts[idx].error = data ? null : res?.data?.message || 'Lỗi';
      setQuestions([...all]);
      setPlan([...parts]);
    }
    setProgress(null);
    setGenerating(false);
    showToast(added ? `Đã sinh bù ${added} câu.` : 'AI chưa sinh bù được câu nào, hãy thử lại.', added ? 'success' : 'error');
  }

  // Giảng viên sửa 1 trường của câu hỏi thứ i trong bản nháp
  function patch(i, field, value) {
    setQuestions((qs) => qs.map((q, idx) => (idx === i ? { ...q, [field]: value } : q)));
  }
  // Sửa nội dung 1 phương án (A–D) của câu hỏi thứ i
  function patchOption(i, letter, value) {
    setQuestions((qs) =>
      qs.map((q, idx) => (idx === i ? { ...q, options: { ...q.options, [letter]: value } } : q)),
    );
  }
  // Bỏ câu hỏi thứ i khỏi bản nháp
  function removeQuestion(i) {
    setQuestions((qs) => qs.filter((_, idx) => idx !== i));
  }

  // Duyệt và lưu: quiz mới cần tiêu đề; ôn tập chương / bài thì thêm vào bộ ôn tập rồi mở trang câu hỏi của bộ đó
  async function approve() {
    const target = draftTarget || currentTarget;
    if ((!target.label && !title.trim()) || questions.length === 0) {
      showToast('Cần tiêu đề và ít nhất 1 câu hỏi.', 'error');
      return;
    }
    // Còn câu AI giải ra đáp án khác -> hỏi lại trước khi lưu
    if (
      flaggedCount > 0 &&
      !window.confirm(
        `Còn ${flaggedCount} câu AI tự giải ra đáp án KHÁC đáp án đang đánh (đánh dấu ⚠️).
` +
          'Nên kiểm tra lại trước khi lưu. Bấm OK để vẫn lưu.',
      )
    )
      return;
    // Đề còn thiếu so với phân bổ đã đặt -> hỏi lại trước khi lưu
    if (
      missingTotal > 0 &&
      !window.confirm(
        `Bản nháp còn thiếu ${missingTotal} câu so với phân bổ độ khó đã đặt.\n` +
          'Bấm "Sinh bù" để AI sinh thêm, hoặc OK để vẫn lưu với số câu hiện có.',
      )
    )
      return;
    setSaving(true);
    // Lưu theo đích đã chốt lúc sinh, không theo ô phạm vi hiện tại
    const res = await aiService.approveQuiz({
      courseId: target.courseId,
      chapterId: target.chapterId,
      reviewLessonId: target.lessonId,
      lessonId: target.lessonId,
      title: title.trim(),
      questions,
      // Cài đặt làm bài chỉ áp dụng khi tạo quiz mới (bộ ôn tập giữ cài đặt riêng)
      ...(target.label
        ? {}
        : {
            ...Object.fromEntries(
              Object.entries(quizSettings).map(([k, v]) => [k, v === '' || v === null ? null : Number(v)]),
            ),
            grading_method: grading,
          }),
    });
    setSaving(false);
    if (res?.ok && res.data?.success) {
      showToast(res.data.message || `Đã lưu quiz (${res.data.data?.question_count} câu).`, 'success');
      // Nhúng trong trang Quiz: xóa bản nháp đã lưu rồi để trang cha chuyển về danh sách quiz
      if (!target.label && onSaved) {
        setQuestions([]);
        setPlan([]);
        setMeta(null);
        setTitle('');
        setDraftTarget(null);
        onSaved(res.data.data);
        return;
      }
      navigate(target.label ? `/teacher/quizzes/${res.data.data.quiz_id}/questions` : '/teacher/quizzes');
    } else {
      showToast(res?.data?.message || 'Lưu quiz thất bại.', 'error');
    }
  }

  return (
    <>
      {/* Mở riêng thì có tiêu đề trang; nhúng trong trang Quiz thì chỉ hiện dòng mô tả ngắn */}
      {embedded ? (
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0 0 1rem' }}>
          AI sinh câu hỏi từ tài liệu khóa học. Bạn chỉnh sửa & duyệt trước khi lưu — AI không tự lưu.
        </p>
      ) : (
        <div className="page-header">
          <div>
            <h1 className="page-title" style={{ fontSize: '1.6rem', fontWeight: 800 }}>✨ AI Quiz Generator</h1>
            <p className="page-subtitle" style={{ marginTop: '0.25rem', fontSize: '0.88rem' }}>
              AI sinh câu hỏi từ tài liệu khóa học. Bạn chỉnh sửa & duyệt trước khi lưu — AI không tự lưu.
            </p>
          </div>
        </div>
      )}

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
            <label className="form-label">Phạm vi</label>
            <select className="form-control" value={scope} onChange={(e) => setScope(e.target.value)}>
              {/* Khóa chưa có chương: dự phòng sinh quiz từ tài liệu AI Tutor của khóa */}
              {chapters.length === 0 && <option value="">Theo tài liệu khóa học (khóa chưa có chương)</option>}
              {chapters.length > 0 && <option value="multi">Đề kiểm tra cuối khóa (chọn chương cho từng mức độ khó)</option>}
              {chapters.map((ch) => (
                <optgroup key={ch.id} label={ch.chapter_name}>
                  <option value={`ch:${ch.id}`}>Ôn tập cả chương</option>
                  {ch.lessons.map((l) => (
                    <option key={l.id} value={`ls:${l.id}`}>Ôn tập bài: {l.title}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Tổng số câu</label>
            <input
              className="form-control"
              type="number"
              min="1"
              max={isMulti ? MAX_EXAM_TOTAL : MAX_SINGLE_TOTAL}
              value={total}
              onChange={(e) => setTotal(e.target.value)}
            />
          </div>
          {/* Phân bổ độ khó: nhập tỉ lệ % từng mức, hiện số câu tương ứng */}
          <div className="form-group">
            <div className="form-label" style={{ display: 'flex', justifyContent: 'space-between', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span>Tỉ lệ độ khó (%)</span>
              <span style={{ display: 'inline-flex', gap: '0.35rem' }}>
                {PCT_PRESETS.map((p) => (
                  <button
                    key={p.label}
                    type="button"
                    className="btn btn-ghost btn-sm"
                    style={{ padding: '0 0.4rem', fontSize: '0.7rem' }}
                    title={`${p.pct.easy}% / ${p.pct.medium}% / ${p.pct.hard}%`}
                    onClick={() => setPct(p.pct)}
                  >
                    {p.label}
                  </button>
                ))}
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
              {DIFFICULTY_LEVELS.map((d) => (
                <label key={d.key} style={{ fontSize: '0.75rem', fontWeight: 600, color: d.color }}>
                  {d.label} · {mix[d.key]} câu
                  <input
                    className="form-control"
                    type="number"
                    min="0"
                    max="100"
                    value={pct[d.key]}
                    onChange={(e) => setPct({ ...pct, [d.key]: e.target.value })}
                  />
                </label>
              ))}
            </div>
            <div style={{ fontSize: '0.75rem', marginTop: '0.3rem', color: mixError ? 'var(--danger,#DC2626)' : 'var(--text-muted,#64748b)' }}>
              {mixError || `= ${mix.easy} dễ + ${mix.medium} trung bình + ${mix.hard} khó`}
            </div>
          </div>
        </div>

        {/* Đề cuối khóa: mỗi mức độ khó chọn lấy câu từ chương nào */}
        {isMulti && (
          <div style={{ marginTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <div>
                <strong style={{ fontSize: '0.85rem' }}>Mỗi mức độ khó lấy câu từ chương nào?</strong>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted,#64748b)' }}>
                  Không chọn chương = lấy ngẫu nhiên lẫn lộn từ các chương. Chọn chương = chỉ chia đều vào những chương đó.
                </div>
              </div>
              {hasRandomLevel && (
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShuffleSeed((x) => x + 1)}>
                  🎲 Xáo lại
                </button>
              )}
            </div>
            {DIFFICULTY_LEVELS.map((d) => (
              <div
                key={d.key}
                role="group"
                aria-label={`Chương cho mức ${d.label}`}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', padding: '0.6rem 0', borderBottom: '1px solid var(--border,#e2e8f0)' }}
              >
                <span style={{ width: 150, fontWeight: 700, fontSize: '0.8rem', color: d.color }}>
                  {d.label} · {mix[d.key]} câu
                  {mix[d.key] > 0 && !levelChapters[d.key].length && (
                    <span style={{ display: 'block', fontWeight: 500, fontSize: '0.7rem', color: 'var(--text-muted,#64748b)' }}>
                      🎲 ngẫu nhiên các chương
                    </span>
                  )}
                </span>
                {chapters.map((ch) => {
                  const on = levelChapters[d.key].includes(ch.id);
                  return (
                    <button
                      key={ch.id}
                      type="button"
                      aria-pressed={on}
                      onClick={() => toggleLevelChapter(d.key, ch.id)}
                      style={{
                        padding: '0.3rem 0.7rem',
                        borderRadius: 999,
                        fontSize: '0.78rem',
                        cursor: 'pointer',
                        border: `1px solid ${on ? d.color : 'var(--border,#e2e8f0)'}`,
                        background: on ? `${d.color}1A` : 'transparent',
                        color: on ? d.color : 'var(--text-muted,#64748b)',
                        fontWeight: on ? 700 : 500,
                      }}
                    >
                      {on ? '✓ ' : ''}
                      {ch.chapter_name}
                      {on ? ` (${perLevel[d.key][ch.id] || 0})` : ''}
                    </button>
                  );
                })}
                <span style={{ marginLeft: 'auto', display: 'inline-flex', gap: '0.25rem' }}>
                  <button type="button" className="btn btn-ghost btn-sm" style={{ fontSize: '0.7rem' }} onClick={() => setLevelAll(d.key, true)}>
                    Tất cả
                  </button>
                  <button type="button" className="btn btn-ghost btn-sm" style={{ fontSize: '0.7rem' }} onClick={() => setLevelAll(d.key, false)}>
                    Bỏ chọn
                  </button>
                </span>
              </div>
            ))}

            {/* Xem trước: số câu từng mức của từng chương sẽ được sinh */}
            {examRows.length > 0 && (
              <div className="table-wrapper" style={{ marginTop: '0.75rem' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Chương</th>
                      {DIFFICULTY_LEVELS.map((d) => (
                        <th key={d.key} style={{ color: d.color }}>{d.label}</th>
                      ))}
                      <th>Tổng</th>
                    </tr>
                  </thead>
                  <tbody>
                    {examRows.map((r) => (
                      <tr key={r.ch.id}>
                        <td>{r.ch.chapter_name}</td>
                        {DIFFICULTY_LEVELS.map((d) => (
                          <td key={d.key}>{r.rowMix[d.key] || '—'}</td>
                        ))}
                        <td><strong>{r.rowTotal}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Nút sinh đặt cuối phần cấu hình: chọn xong khóa, phạm vi, số câu, độ khó (và chương) rồi mới bấm */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
          <button
            className="btn btn-primary"
            onClick={generate}
            disabled={generating || !courseId || Boolean(mixError)}
            title={mixError || undefined}
          >
            {generating ? 'Đang sinh…' : '⚡ Sinh câu hỏi bằng AI'}
          </button>
        </div>

        {/* Tiến độ sinh + kết quả từng chương (yêu cầu -> nhận được) */}
        {progress && <p style={{ fontSize: '.8rem', marginTop: '.75rem' }}>⏳ {progress}</p>}
        {planStatus.length > 0 && (planStatus.length > 1 || missingTotal > 0 || planStatus.some((p) => p.error)) && (
          <ul style={{ fontSize: '.78rem', marginTop: '.5rem', paddingLeft: '1.1rem', color: 'var(--text-muted,#64748b)' }}>
            {planStatus.map((p) => (
              <li key={p.key}>
                <strong>{p.name || 'Bản nháp'}</strong>:{' '}
                {DIFFICULTY_LEVELS.filter((d) => p.requested[d.key] > 0).map((d, i, arr) => (
                  <span key={d.key} style={{ color: p.missing[d.key] > 0 ? 'var(--danger,#DC2626)' : undefined }}>
                    {d.label} {Math.min(p.have[d.key], p.requested[d.key])}/{p.requested[d.key]}
                    {i < arr.length - 1 ? ' · ' : ''}
                  </span>
                ))}
                {p.error && <span style={{ color: 'var(--danger,#DC2626)' }}> — {p.error}</span>}
              </li>
            ))}
          </ul>
        )}
        {/* Còn thiếu so với phân bổ đã đặt (AI sinh hụt, hoặc giảng viên xóa / đổi độ khó câu) -> sinh bù đúng phần thiếu */}
        {missingTotal > 0 && questions.length > 0 && !generating && (
          <button type="button" className="btn btn-outline btn-sm" style={{ marginTop: '.5rem' }} onClick={fillMissing}>
            🔁 Sinh bù {missingTotal} câu còn thiếu
          </button>
        )}
        {/* Thông tin lần sinh: model đã dùng, số câu nhận được, số đoạn ngữ liệu */}
        {meta && (
          <p style={{ fontSize: '.78rem', color: 'var(--text-muted,#64748b)', marginTop: '.5rem' }}>
            Nguồn sinh: <strong>{meta.generated_by}</strong> · {meta.returned}/{meta.requested} câu ·
            {' '}{meta.context_chunks} đoạn ngữ cảnh
          </p>
        )}
      </div>

      {questions.length > 0 && (
        <>
          <div className="card" style={{ padding: '1.25rem', marginBottom: '1rem', display: 'flex', gap: '1rem', alignItems: 'end', flexWrap: 'wrap' }}>
            {draftTarget?.label ? (
              <p style={{ flex: 1, minWidth: 260, margin: 0 }}>
                Các câu đã duyệt sẽ được thêm vào bộ câu hỏi ôn tập của <strong>{draftTarget?.label}</strong>.
              </p>
            ) : (
              <>
                <div className="form-group" style={{ flex: 1, minWidth: 260 }}>
                  <label className="form-label">Tiêu đề quiz</label>
                  <input className="form-control" maxLength={255} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="VD: Kiểm tra chương 1" />
                </div>
                {/* Cài đặt làm bài của quiz mới: để trống = không giới hạn / không xét đạt */}
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
                      value={quizSettings[f.key]}
                      onChange={(e) => setQuizSettings({ ...quizSettings, [f.key]: e.target.value })}
                    />
                  </div>
                ))}
                {/* Làm nhiều lượt thì lấy điểm lượt nào (chỉ 1 lượt thì không cần chọn) */}
                <div className="form-group" style={{ width: 170 }}>
                  <label className="form-label">Tính điểm theo</label>
                  <select
                    className="form-control"
                    value={grading}
                    disabled={Number(quizSettings.max_attempts) === 1}
                    onChange={(e) => setGrading(e.target.value)}
                  >
                    {GRADING_METHODS.map((m) => (
                      <option key={m.key} value={m.key}>{m.label}</option>
                    ))}
                  </select>
                </div>
              </>
            )}
            <button className="btn btn-primary" onClick={approve} disabled={saving}>
              {saving
                ? 'Đang lưu…'
                : draftTarget?.label
                  ? `✓ Duyệt & Thêm vào bộ ôn tập (${questions.length} câu)`
                  : `✓ Duyệt & Lưu Quiz (${questions.length} câu)`}
            </button>
          </div>

          {/* Đã đổi khóa / phạm vi sau khi sinh: nhắc rằng bản nháp vẫn lưu theo phạm vi cũ */}
          {scopeChanged && (
            <div className="alert alert-warning" style={{ marginBottom: '1rem', fontSize: '0.85rem' }}>
              ⚠️ Bạn đã đổi khóa học / phạm vi sau khi sinh. Bản nháp này vẫn được lưu theo phạm vi lúc sinh
              {draftTarget?.label ? <> (bộ ôn tập của <strong>{draftTarget.label}</strong>)</> : ' (quiz mới)'} — bấm “Sinh câu hỏi” lại nếu muốn sinh cho phạm vi mới.
            </div>
          )}
          <DifficultyBar questions={questions} />
          {/* Kết quả AI tự giải lại đề để bắt câu đánh sai đáp án */}
          {(verifiedCount > 0 || questions.some((q) => q.verify)) && (
            <p style={{ fontSize: '0.8rem', margin: '-0.5rem 0 1rem', color: flaggedCount ? 'var(--danger,#DC2626)' : 'var(--success,#059669)' }}>
              🔎 AI tự giải lại đề: {verifiedCount} câu khớp đáp án
              {flaggedCount > 0 ? ` · ${flaggedCount} câu ra đáp án khác, cần bạn kiểm tra (đánh dấu ⚠️)` : ''}
            </p>
          )}

          {/* Danh sách câu hỏi nháp: sửa nội dung, phương án, đáp án đúng, độ khó, giải thích; có nút bỏ câu */}
          {questions.map((q, i) => (
            <DraftQuestionCard
              key={i}
              q={q}
              index={i}
              meta={[q.chapter_name, q.topic !== q.chapter_name ? q.topic : null].filter(Boolean).join(' · ')}
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
