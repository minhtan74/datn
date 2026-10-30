// API/Vite local, Playwright/Chromium. Hai tài khoản mẫu, khóa học/hội thoại tạm tự dọn.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const checks = [], cases = [], conversations = [], enrolled = [];
  const check = (label, value) => { assert.ok(value, label); checks.push(label); };
  async function call(method, url, auth, data) {
    const res = await api[method](url, { headers: auth ? { Authorization: `Bearer ${auth.token}` } : {}, data });
    const body = await res.json(); assert.ok(res.ok(), `${method} ${url}: ${JSON.stringify(body)}`); return body;
  }
  const teacher = await call('post', '/api/auth/login', null, { email: 'an.nguyen@studyonline.vn', password: '123456' });
  const students = [];
  for (const email of ['em.hoang@gmail.com', 'phuong.vu@gmail.com']) students.push(await call('post', '/api/auth/login', null, { email, password: '123456' }));
  const baselines = await Promise.all(students.map(a => call('get', '/api/ai/conversations', a)));
  let browser, course;
  try {
    // Dùng lại đường dẫn PDF có sẵn để trang bài học hiển thị thật; không sửa/xóa file đó.
    const sourceLesson = (await call('get', '/api/lessons?id=1', teacher)).data;
    assert.ok(sourceLesson.document_url);
    course = (await call('post', '/api/courses', teacher, { title: `PYTEST AI clarification ${Date.now()}`, price: 0 })).id;
    const chapter = (await call('post', '/api/chapters', teacher, { course_id: course, chapter_name: 'Chương kiểm thử' })).id;
    const lesson = (await call('post', '/api/lessons', teacher, { chapter_id: chapter, title: 'Bài kiểm thử hỏi lại', document_url: sourceLesson.document_url })).id;
    browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined });
    const errors = [];
    for (const [index, auth] of students.entries()) {
      await call('post', '/api/enrollments', auth, { course_id: course }); enrolled.push(auth);
      const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
      await ctx.addInitScript(a => { localStorage.setItem('token', a.token); localStorage.setItem('user', JSON.stringify(a.user)); }, auth);
      const page = await ctx.newPage(); page.on('pageerror', e => errors.push(e.message));
      const selectCourse = async () => {
        await page.goto('http://127.0.0.1:5173/student/ai-tutor');
        await page.locator(`#ai-tutor-course option[value="${course}"]`).waitFor({ state: 'attached' });
        await page.getByLabel('KHÓA HỌC', { exact: true }).selectOption(String(course));
        await page.getByRole('button', { name: '+ Cuộc trò chuyện mới', exact: true }).click();
      };
      async function send(question, inLesson = false) {
        const input = page.getByLabel(inLesson ? 'Câu hỏi cho AI về bài học' : 'Câu hỏi cho AI Tutor', { exact: true });
        await input.fill(question);
        const response = page.waitForResponse(r => r.url().endsWith('/api/ai/chat') && r.request().method() === 'POST');
        await input.press('Enter');
        const res = await response; const body = await res.json(); assert.ok(res.ok(), JSON.stringify(body));
        const data = body.data;
        if (!conversations.some(c => c.id === data.conversation_id)) conversations.push({ id: data.conversation_id, auth });
        cases.push({ account: index + 1, question, answer: data.answer, kind: data.clarification_kind, sources: data.sources });
        return data;
      }
      await selectCourse();
      for (const [question, kind] of [['giai thich giup em', 'topic'], ['code em bị lỗi', 'debug'], ['Giải câu 2', 'exercise'], ['Nên chọn cái nào?', 'comparison']]) {
        await page.getByRole('button', { name: '+ Cuộc trò chuyện mới', exact: true }).click();
        const data = await send(question);
        await page.locator('.ai-clarification-label').waitFor();
        check(`Tài khoản ${index + 1}: hỏi lại đúng nhóm ${kind}`, data.needs_clarification && data.clarification_kind === kind && data.sources.length === 0 && !data.used_context);
        check(`Tài khoản ${index + 1}: có gợi ý bổ sung cho ${kind}`, await page.getByLabel('Câu hỏi cho AI Tutor', { exact: true }).getAttribute('placeholder') === 'Bổ sung thông tin AI đang hỏi…');
        if (kind === 'debug') {
          const more = await send('Python');
          check(`Tài khoản ${index + 1}: chỉ tên ngôn ngữ vẫn hỏi code/lỗi`, more.needs_clarification && more.clarification_kind === 'debug' && more.conversation_id === data.conversation_id);
        }
      }
      const saved = cases.at(-1);
      await selectCourse();
      await page.locator('.ai-tutor-grid > .s-card').first().getByText(saved.question, { exact: false }).first().click();
      await page.locator('.ai-clarification-label').waitFor();
      check(`Tài khoản ${index + 1}: tải lại giữ lời hỏi lại`, (await page.locator('.ai-tutor-chat').innerText()).includes(saved.answer));
      if (index === 0) await page.screenshot({ path: path.join(__dirname, 'ai-clarification.png'), fullPage: true });
      await page.setViewportSize({ width: 390, height: 844 });
      await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth);
      check(`Tài khoản ${index + 1}: điện thoại không tràn ngang`, await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.setViewportSize({ width: 1440, height: 1000 });
      await page.goto(`http://127.0.0.1:5173/lesson?id=${lesson}`);
      await page.getByTitle('Hỏi AI về bài học', { exact: true }).click();
      const fromLesson = await send('Giải bài này', true); await page.locator('.ai-clarification-label').waitFor();
      check(`Tài khoản ${index + 1}: khung AI bài học cũng hỏi lại`, fromLesson.needs_clarification && fromLesson.clarification_kind === 'exercise');
      await selectCourse();
      await page.locator('.ai-tutor-grid > .s-card').first().getByText('Giải bài này', { exact: false }).first().click();
      await page.locator('.ai-scope-note').waitFor();
      const continued = await send('Giải câu 2');
      check(`Tài khoản ${index + 1}: mở hội thoại bài học giữ đúng phạm vi`, continued.conversation_id === fromLesson.conversation_id && continued.needs_clarification);
      await ctx.close();
    }
    const other = await api.get(`/api/ai/conversations/${conversations[0].id}`, { headers: { Authorization: `Bearer ${students[1].token}` } });
    check('Tài khoản khác không đọc được hội thoại', other.status() === 404);
    check('Không có lỗi JavaScript', errors.length === 0);
    const report = { passed: checks.length, checks, cases, jsErrors: errors };
    fs.writeFileSync(path.join(__dirname, 'ai-clarification-check.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify({ passed: checks.length, checks }, null, 2));
  } finally {
    if (browser) await browser.close();
    for (const c of conversations) await call('delete', `/api/ai/conversations/${c.id}`, c.auth);
    for (const auth of enrolled) await call('delete', `/api/enrollments?course_id=${course}`, auth);
    if (course) await call('delete', `/api/courses?id=${course}`, teacher);
    for (const [i, auth] of students.entries()) {
      const after = (await call('get', '/api/ai/conversations', auth)).data;
      assert.ok(baselines[i].data.every(c => after.some(a => a.id === c.id)), 'Giữ nguyên hội thoại có sẵn');
    }
    await api.dispose(); console.log('Đã dọn dữ liệu kiểm thử; giữ nguyên hội thoại có sẵn.');
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
