// Kiểm tra danh sách quiz trên API/Vite local và DB backend/.env.
// Cần Playwright/Chromium; chỉ tạo dữ liệu trong khóa học tạm và tự dọn khi kết thúc.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const checks = [];
  const check = (label, value) => { assert.ok(value, label); checks.push(label); };
  async function call(method, url, auth, data) {
    const res = await api[method](url, { headers: auth ? { Authorization: `Bearer ${auth.token}` } : {}, data });
    const body = await res.json();
    assert.ok(res.ok(), `${method} ${url}: ${JSON.stringify(body)}`);
    return body;
  }
  const teacher = await call('post', '/api/auth/login', null, { email: 'an.nguyen@studyonline.vn', password: '123456' });
  const student = await call('post', '/api/auth/login', null, { email: 'em.hoang@gmail.com', password: '123456' });
  let course, browser;
  try {
    course = (await call('post', '/api/courses', teacher, { title: `PYTEST Quiz status ${Date.now()}`, price: 0 })).id;
    await call('post', '/api/enrollments', student, { course_id: course });
    async function quiz(title, settings = {}) {
      const id = (await call('post', '/api/quizzes', teacher, { course_id: course, title, ...settings })).id;
      await call('post', '/api/quizzes/questions', teacher, {
        quiz_id: id, content: '1 + 1 bằng bao nhiêu?', option_a: '2', option_b: '3', correct_answer: 'A',
      });
      return { id, title };
    }
    const untouched = await quiz('Bài chưa bắt đầu');
    const active = await quiz('Bài đang làm lượt cuối', { duration: 10, max_attempts: 1 });
    const passed = await quiz('Bài đã nộp và đạt', { passing_score: 70, max_attempts: 2 });
    const failed = await quiz('Bài đã nộp chưa đạt', { passing_score: 70, max_attempts: 1 });
    const redo = await quiz('Bài đang làm lại', { passing_score: 70, max_attempts: 2 });
    const expired = await quiz('Bài hết hạn chưa nộp', { duration: 1, max_attempts: 1 });
    browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined });
    async function pageFor(auth) {
      const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
      await ctx.addInitScript(a => { localStorage.setItem('token', a.token); localStorage.setItem('user', JSON.stringify(a.user)); }, auth);
      return ctx.newPage();
    }
    const page = await pageFor(student);
    const errors = [];
    let questions = 0;
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => { if (r.url().includes('/api/quizzes/questions?')) questions++; });
    const url = `http://127.0.0.1:5173/quiz?course_id=${course}`;
    const filter = key => page.locator(`.ql-status-filter.ql-state-${key}`);
    const card = title => page.locator('.ql-card').filter({ has: page.getByRole('heading', { name: title, exact: true }) });
    const count = key => filter(key).locator('.ql-filter-count').innerText();
    await page.goto(url); await page.locator('.ql-overview').waitFor();
    check('Bài chưa mở đều thuộc Chưa làm', await count('not_started') === '6' && await page.locator('.ql-card').count() === 6);
    await filter('submitted').click();
    await page.getByRole('heading', { name: 'Không có quiz ở trạng thái này' }).waitFor();
    check('Bộ lọc rỗng có lời giải thích và nút xem tất cả', await page.getByRole('button', { name: 'Xem tất cả quiz' }).isVisible());
    await page.getByRole('button', { name: 'Xem tất cả quiz' }).click();
    const open = async q => call('get', `/api/quizzes/questions?quiz_id=${q.id}`, student);
    async function submit(q, correct) {
      const started = await open(q);
      const row = started.data[0];
      const answer = ['A', 'B'].find(k => row[`option_${k.toLowerCase()}`] === (correct ? '2' : '3'));
      const result = await call('post', '/api/quizzes/submit', student, {
        quiz_id: q.id, answers: { [row.id]: answer }, attempt_token: started.attempt_token,
      });
      assert.equal(result.percent, correct ? 100 : 0);
    }
    await open(active); await submit(passed, true); await submit(failed, false); await submit(redo, true); await open(redo);
    const expiredAttempt = await open(expired);
    const aid = Number(expiredAttempt.attempt_token.split('.')[0]);
    const backend = path.resolve(__dirname, '../backend');
    execFileSync(path.join(backend, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python'), ['-c',
      `import time; from app.core.database import SessionLocal,execute; db=SessionLocal(); execute(db,'UPDATE quiz_attempts SET started_ts=:t WHERE id=:a AND quiz_id=:q',t=int(time.time())-122,a=${aid},q=${Number(expired.id)}); db.close()`], { cwd: backend, stdio: 'pipe' });
    await page.reload(); await page.locator('.ql-overview').waitFor();
    check('Số lượng bốn nhóm không trùng nhau', await count('not_started') === '1' && await count('in_progress') === '2' && await count('submitted') === '2' && await count('unfinished') === '1');
    check('Bài chưa làm có nút Làm bài', await card(untouched.title).getByRole('link', { name: 'Làm bài', exact: true }).isVisible());
    check('Lượt cuối đang dở vẫn cho tiếp tục', await card(active.title).getByRole('link', { name: 'Tiếp tục làm', exact: true }).isVisible());
    check('Bài đạt có điểm và nút Làm lại', (await card(passed.title).innerText()).includes('100%') && await card(passed.title).getByRole('link', { name: 'Làm lại', exact: true }).isVisible());
    check('Đã nộp không đồng nghĩa đạt', (await card(failed.title).innerText()).includes('Đã nộp') && (await card(failed.title).innerText()).includes('Chưa đạt'));
    check('Hết lượt vẫn xem được lịch sử', await card(failed.title).getByRole('button', { name: 'Hết lượt', exact: true }).isDisabled() && await card(failed.title).getByRole('button', { name: '📜 Lịch sử', exact: true }).isEnabled());
    check('Bài đang làm lại giữ điểm cũ và lịch sử', (await card(redo.title).innerText()).includes('100%') && (await card(redo.title).innerText()).includes('Đã nộp 1 lượt') && await card(redo.title).getByRole('link', { name: 'Tiếp tục làm', exact: true }).isVisible());
    check('Bài hết hạn chưa nộp không ghi Chưa làm', (await card(expired.title).locator('.ql-state-label').innerText()) === 'Chưa nộp' && await card(expired.title).getByRole('button', { name: 'Hết lượt', exact: true }).isDisabled());
    for (const [key, expected] of [['not_started', 1], ['in_progress', 2], ['submitted', 2], ['unfinished', 1]]) {
      await filter(key).click();
      check(`Lọc đúng nhóm ${key}`, await page.locator('.ql-card').count() === expected && await filter(key).getAttribute('aria-pressed') === 'true');
      assert.equal(new URL(page.url()).searchParams.get('course_id'), String(course));
    }
    await page.reload(); await page.locator('.ql-overview').waitFor();
    check('Tải lại giữ bộ lọc và khóa học trên URL', new URL(page.url()).searchParams.get('status') === 'unfinished' && await page.locator('.ql-card').count() === 1);
    await page.goBack(); await page.locator('.ql-overview').waitFor();
    check('Nút Back khôi phục bộ lọc trước đó', await filter('submitted').getAttribute('aria-pressed') === 'true' && await page.locator('.ql-card').count() === 2);
    await filter('not_started').focus(); await page.keyboard.press('Enter');
    check('Chọn bộ lọc bằng bàn phím', await filter('not_started').getAttribute('aria-pressed') === 'true');
    await page.getByRole('button', { name: 'Tất cả (6)', exact: true }).click();
    await card(redo.title).getByRole('button', { name: '📜 Lịch sử', exact: true }).click();
    await card(redo.title).locator('.qh-stats').waitFor();
    check('Lịch sử mở ngay trong thẻ quiz', (await card(redo.title).locator('.qh-stats').innerText()).includes('100%'));
    await card(redo.title).getByRole('button', { name: '📜 Lịch sử', exact: true }).click();
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(__dirname, 'quiz-status-list.png'), fullPage: true });
    for (const width of [900, 390, 320]) {
      await page.setViewportSize({ width, height: 844 });
      await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth);
      check(`Không tràn ngang ở ${width}px`, await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      if (width === 390) await page.screenshot({ path: path.join(__dirname, 'quiz-status-mobile.png'), fullPage: true });
    }
    const teacherPage = await pageFor(teacher);
    await teacherPage.goto(url + '&status=not_started'); await teacherPage.locator('.ql-card').first().waitFor();
    check('Giảng viên vẫn thấy đủ quiz và các nút quản lý', await teacherPage.locator('.ql-overview').count() === 0 && await teacherPage.locator('.ql-card').count() === 6 && await teacherPage.getByRole('link', { name: 'Câu hỏi', exact: true }).count() === 6);
    check('Lọc và xem lịch sử không mở lượt làm mới', questions === 0);
    check('Không có lỗi JavaScript', errors.length === 0);
    fs.writeFileSync(path.join(__dirname, 'quiz-status-check.json'), JSON.stringify({ passed: checks.length, checks, jsErrors: errors }, null, 2));
    console.log(JSON.stringify({ passed: checks.length, checks }, null, 2));
  } finally {
    if (browser) await browser.close();
    if (course) {
      await call('delete', `/api/enrollments?course_id=${course}`, student);
      await call('delete', `/api/courses?id=${course}`, teacher);
      console.log('Đã dọn dữ liệu kiểm thử.');
    }
    await api.dispose();
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
