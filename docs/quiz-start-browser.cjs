// Cần Playwright, Chromium và API/Vite đang chạy. Chỉ tạo/xóa khóa học kiểm thử riêng.
// Có thể đặt PLAYWRIGHT_MODULE và PLAYWRIGHT_CHROMIUM_EXECUTABLE để dùng bản đã cài.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

(async () => {
  const api = await request.newContext({ baseURL: process.env.TEST_API_URL || 'http://127.0.0.1:8080' });
  const web = process.env.TEST_WEB_URL || 'http://127.0.0.1:5173';
  const checks = [];
  const check = (name, condition) => { assert.ok(condition, name); checks.push(name); };
  async function call(method, url, auth, data) {
    const res = await api[method](url, { headers: auth ? { Authorization: `Bearer ${auth.token}` } : {}, data });
    const body = await res.json();
    assert.ok(res.ok(), `${method} ${url}: ${JSON.stringify(body)}`);
    return body;
  }
  const teacher = await call('post', '/api/auth/login', null, {
    email: process.env.TEST_TEACHER_EMAIL || 'an.nguyen@studyonline.vn', password: process.env.TEST_TEACHER_PASSWORD || '123456',
  });
  const student = await call('post', '/api/auth/login', null, {
    email: process.env.TEST_STUDENT_EMAIL || 'em.hoang@gmail.com', password: process.env.TEST_STUDENT_PASSWORD || '123456',
  });
  let course, browser;
  try {
    course = (await call('post', '/api/courses', teacher, { title: `PYTEST Quiz intro ${Date.now()}`, price: 0 })).id;
    async function quiz(title, settings, count) {
      const id = (await call('post', '/api/quizzes', teacher, { course_id: course, title, ...settings })).id;
      for (let i = 0; i < count; i++) await call('post', '/api/quizzes/questions', teacher, {
        quiz_id: id, content: `Câu ${i + 1}: 1 + 1 bằng bao nhiêu?`, option_a: '2', option_b: '3', correct_answer: 'A', order_index: i,
      });
      return id;
    }
    const timed = await quiz('Quiz có thời gian', { duration: 5, max_attempts: 2, passing_score: 70, description: 'Đọc kỹ thông tin trước khi bắt đầu làm bài.' }, 2);
    const unlimited = await quiz('Quiz ôn tập tự do', {}, 1);
    const empty = await quiz('Quiz đang soạn', {}, 0);
    const expired = await quiz('Quiz kiểm tra hết hạn', { duration: 1, max_attempts: 2 }, 1);
    const auto = await quiz('Quiz kiểm tra tự nộp', { duration: 1, max_attempts: 1 }, 1);
    await call('post', '/api/enrollments', student, { course_id: course });
    browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined });
    async function pageFor(auth) {
      const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
      await ctx.addInitScript(a => { localStorage.setItem('token', a.token); localStorage.setItem('user', JSON.stringify(a.user)); }, auth);
      return ctx.newPage();
    }
    const page = await pageFor(student);
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    let questionRequests = 0;
    page.on('request', r => { if (r.url().includes('/api/quizzes/questions?')) questionRequests++; });
    const intro = async id => { await page.goto(`${web}/quiz-show?id=${id}`); await page.locator('.q-intro').waitFor(); };
    const info = async id => (await call('get', `/api/quizzes?id=${id}`, student)).data;
    const begin = async () => { await page.getByRole('button', { name: 'Bắt đầu làm bài', exact: true }).click(); await page.locator('.question-card').first().waitFor(); };
    await intro(timed);
    await page.screenshot({ path: path.join(__dirname, 'quiz-start-intro.png'), fullPage: true });
    check('Mở giới thiệu không gọi câu hỏi hoặc tạo lượt', questionRequests === 0 && (await info(timed)).my_attempts === 0);
    const text = await page.locator('.q-intro').innerText();
    check('Có thời gian, điểm đạt và cách tính điểm', text.includes('5 phút') && text.includes('Từ 70%') && text.includes('Lượt cao nhất'));
    await page.reload(); await page.locator('.q-intro').waitFor();
    check('Tải lại giới thiệu không tốn lượt', questionRequests === 0 && (await info(timed)).my_attempts === 0);
    for (const width of [320, 390]) {
      await page.setViewportSize({ width, height: 844 });
      // Chờ hiệu ứng đổi margin của sidebar khi chuyển từ desktop sang mobile.
      await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth);
      check(`Không tràn ngang ở ${width}px`, await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    await page.screenshot({ path: path.join(__dirname, 'quiz-start-mobile.png'), fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.route('**/api/quizzes/questions?*', route => route.abort(), { times: 1 });
    await page.getByRole('button', { name: 'Bắt đầu làm bài', exact: true }).click();
    await page.getByRole('alert').waitFor();
    await page.waitForFunction(() => !document.querySelector('.q-intro-actions button').disabled);
    check('Lỗi mạng cho phép thử lại, chưa mất lượt', (await info(timed)).my_attempts === 0);
    await page.getByRole('button', { name: 'Bắt đầu làm bài', exact: true }).evaluate(b => { b.click(); b.click(); });
    await page.locator('.question-card').first().waitFor();
    const before = await info(timed);
    check('Bấm liên tiếp chỉ tạo một lượt', before.my_attempts === 1 && before.my_status.in_progress);
    const radioId = await page.locator('input[type=radio]').first().getAttribute('id');
    await page.locator(`label[for="${radioId}"]`).click();
    await page.reload(); await page.getByRole('button', { name: 'Tiếp tục làm bài', exact: true }).waitFor();
    check('Tải lại bài dở không tạo lượt mới', (await info(timed)).my_attempts === 1);
    await page.getByRole('button', { name: 'Tiếp tục làm bài', exact: true }).click(); await page.locator('.question-card').first().waitFor();
    check('Tiếp tục giữ đáp án và thời gian cũ', await page.locator(`#${radioId}`).isChecked() && (await info(timed)).my_status.remaining_sec <= before.my_status.remaining_sec);
    async function submitAll() {
      for (const card of await page.locator('.question-card').all()) await card.locator('label').first().click();
      await page.getByRole('button', { name: '🚀 Nộp bài', exact: true }).click();
      await page.waitForURL('**/student/quiz-result?result_id=*');
    }
    await submitAll(); await intro(timed);
    check('Xem giới thiệu sau nộp không tự tạo lượt hai', (await info(timed)).my_attempts === 1 && (await info(timed)).my_status.attempts_left === 1);
    await begin(); await submitAll(); await intro(timed);
    check('Hết lượt khóa nút bắt đầu', await page.getByRole('button', { name: 'Đã hết lượt làm', exact: true }).isDisabled());
    await intro(unlimited); await begin(); await page.reload();
    await page.getByRole('button', { name: 'Tiếp tục làm bài', exact: true }).waitFor();
    check('Quiz tự do nhận diện bài đang dở', (await info(unlimited)).my_status.in_progress);
    await intro(empty);
    check('Quiz rỗng khóa bắt đầu, không tốn lượt', await page.getByRole('button', { name: 'Bắt đầu làm bài', exact: true }).isDisabled() && (await info(empty)).my_attempts === 0);
    function ageAttempt(id, seconds) {
      // Chỉ đổi thời điểm của lượt thuộc quiz tạm do chính bài test vừa tạo.
      const backend = path.resolve(__dirname, '../backend');
      const python = path.join(backend, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
      execFileSync(python, ['-c', `import time; from app.core.database import SessionLocal,execute; db=SessionLocal(); execute(db, 'UPDATE quiz_attempts SET started_ts=:t WHERE quiz_id=:q AND finished_ts IS NULL', t=int(time.time())-${Number(seconds)},q=${Number(id)}); db.close()`], { cwd: backend, stdio: 'pipe' });
    }
    await intro(expired); await begin(); await page.reload();
    await page.getByRole('button', { name: 'Tiếp tục làm bài', exact: true }).waitFor(); ageAttempt(expired, 122);
    await page.getByRole('button', { name: 'Tiếp tục làm bài', exact: true }).click(); await page.getByRole('alert').waitFor();
    await page.getByRole('button', { name: 'Bắt đầu làm bài', exact: true }).waitFor();
    check('Bài vừa hết hạn báo lỗi, không ngầm tạo lượt mới', (await info(expired)).my_attempts === 1);
    await begin(); check('Xác nhận bắt đầu lại mới mở lượt mới', (await info(expired)).my_attempts === 2);
    await intro(auto); await begin(); ageAttempt(auto, 61); await page.reload();
    await page.getByRole('button', { name: 'Tiếp tục làm bài', exact: true }).click();
    await page.waitForURL('**/student/quiz-result?result_id=*');
    check('Hết giờ trong ân hạn tự nộp cả bài chưa trả lời', (await info(auto)).my_status.submitted === 1);
    const teacherPage = await pageFor(teacher);
    teacherPage.on('pageerror', e => errors.push(e.message));
    await teacherPage.goto(`${web}/quiz-show?id=${timed}`);
    await teacherPage.getByRole('button', { name: 'Làm thử quiz', exact: true }).click(); await teacherPage.locator('.question-card').first().waitFor();
    check('Giảng viên làm thử không tạo lượt', (await call('get', `/api/quizzes?id=${timed}`, teacher)).data.my_attempts === 0);
    check('Không có lỗi JavaScript', errors.length === 0);
    const report = { passed: checks.length, checks, jsErrors: errors };
    fs.writeFileSync(path.join(__dirname, 'quiz-start-check.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report, null, 2));
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
