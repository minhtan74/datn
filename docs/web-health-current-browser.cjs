// Kiểm tra tải trang/quyền truy cập, không gửi bài quiz, thanh toán hay chỉnh tài khoản thật.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  const out = { pages: [], controls: [], findings: [], startedAt: new Date().toISOString() };
  const dir = __dirname;
  const save = () => fs.writeFileSync(path.join(dir, 'web-health-current-browser.json'), JSON.stringify(out, null, 2));
  const safe = url => url.replace(/([?&](?:token|signature|sig|key)=)[^&]+/gi, '$1[redacted]');
  const accounts = [
    ['student_em', 'em.hoang@gmail.com', '/student/dashboard'], ['student_phuong', 'phuong.vu@gmail.com', '/student/dashboard'],
    ['teacher_an', 'an.nguyen@studyonline.vn', '/teacher'], ['teacher_binh', 'binh.tran@studyonline.vn', '/teacher'],
    ['admin', 'admin@gmail.com', '/admin'],
  ];
  const sessions = {};
  try {
    for (const [name, email] of accounts) {
      const res = await api.post('/api/auth/login', { data: { email, password: '123456' } });
      assert.ok(res.ok()); sessions[name] = await res.json();
    }
    async function get(url, auth) {
      const res = await api.get(url, { headers: auth ? { Authorization: `Bearer ${auth.token}` } : {} });
      return { status: res.status(), body: await res.json() };
    }
    for (const [who, url, expected] of [['guest', '/api/users', 401], ['student_em', '/api/users', 403],
      ['student_em', '/api/payments/manage', 403], ['teacher_an', '/api/users', 403],
      ['teacher_an', '/api/payments/manage', 403], ['admin', '/api/users', 200], ['admin', '/api/payments/manage', 200]]) {
      const res = await get(url, sessions[who]);
      out.controls.push({ who, url, expected, actual: res.status, passed: res.status === expected });
    }
    const contexts = [];
    for (const [name, email, landing] of [['public', null, '/'], ...accounts]) {
      const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } }); contexts.push(context);
      const page = await context.newPage(); let events = [], pending = new Set();
      await page.route('**/api/**', route => { const p = new URL(route.request().url()).pathname; if (route.request().method() === 'GET' || p.startsWith('/api/auth/') || p === '/api/ai/chat') return route.continue(); return route.fulfill({ json: { success: true } }); });
      page.on('dialog', async d => { events.push({ type: 'dialog', message: d.message() }); await d.accept(); });
      page.on('pageerror', e => events.push({ type: 'javascript', message: e.message }));
      page.on('request', r => { if (r.url().includes('/api/')) pending.add(r); });
      page.on('requestfinished', r => pending.delete(r));
      page.on('requestfailed', r => { pending.delete(r); if (r.failure()?.errorText !== 'net::ERR_ABORTED') events.push({ type: 'network', url: safe(r.url()), message: r.failure()?.errorText }); });
      page.on('response', r => { if (r.status() >= 400) events.push({ type: 'http', status: r.status(), url: safe(r.url()), resource: r.request().resourceType() }); });
      async function settle() {
        await page.waitForTimeout(350);
        const end = Date.now() + 6500;
        while (pending.size && Date.now() < end) await page.waitForTimeout(100);
        await page.waitForTimeout(200);
      }
      if (email) {
        await page.goto('http://127.0.0.1:5173/login');
        await page.locator('#email').fill(email); await page.locator('#password').fill('123456');
        await page.locator('button[type=submit]').click(); await page.waitForURL('**' + landing);
        out.controls.push({ who: name, action: 'login_ui', passed: new URL(page.url()).pathname === landing });
      }
      let course, lesson, quiz, result;
      if (email) {
        const auth = sessions[name];
        const quizzes = (await get('/api/quizzes', auth)).body.data || [];
        quiz = quizzes[0]?.id; course = quizzes[0]?.course_id;
        if (course) {
          const chapters = (await get(`/api/chapters?course_id=${course}`, auth)).body.data || [];
          if (chapters[0]) lesson = (await get(`/api/lessons?chapter_id=${chapters[0].id}`, auth)).body.data?.[0]?.id;
        }
        if (auth.user.role === 'student') result = (await get('/api/quizzes/results', auth)).body.data?.[0]?.id;
      }
      let routes = !email ? ['/', '/login', '/register', '/courses', '/student/dashboard', '/admin', '/forgot-password', '/reset-password']
        : name.startsWith('student') ? ['/student/dashboard', '/student/courses', '/student/my-courses', '/student/profile', '/student/progress', '/quiz', '/student/ai-tutor', '/student/quiz-history', '/admin', '/teacher', '/courses']
          : name.startsWith('teacher') ? ['/teacher', '/teacher/courses', '/teacher/chapters', '/teacher/lessons', '/teacher/quizzes', '/teacher/quizzes?tab=ai', '/teacher/reports', '/teacher/documents', '/teacher/profile', '/teacher/ai-quiz', '/admin']
            : ['/admin', '/admin/users', '/admin/users/teachers', '/admin/users/students', '/admin/courses', '/admin/payments', '/admin/reports', '/teacher'];
      if (email && course) routes.push(`/chapters?course_id=${course}`);
      if (email && lesson) routes.push(`/lesson?id=${lesson}`);
      if (email && quiz) routes.push(`/quiz-show?id=${quiz}`);
      if (result) routes.push(`/student/quiz-result?result_id=${result}`);
      if (name.startsWith('teacher') && quiz) routes.push(`/teacher/quizzes/${quiz}/questions`);
      const mobile = !email ? ['/', '/login', '/register'] : name.startsWith('student') ? ['/student/dashboard', '/student/courses', '/student/progress', '/quiz', '/student/ai-tutor']
        : name.startsWith('teacher') ? ['/teacher/courses', '/teacher/quizzes', '/teacher/reports'] : ['/admin/users', '/admin/courses', '/admin/payments'];
      for (const [viewport, paths] of [['desktop', routes], ['mobile', mobile]]) {
        await page.setViewportSize(viewport === 'desktop' ? { width: 1440, height: 1000 } : { width: 390, height: 844 });
        for (const url of paths) {
          events = []; pending = new Set(); const start = Date.now();
          try {
            await page.goto('http://127.0.0.1:5173' + url); await settle();
            const state = await page.evaluate(() => ({ text: document.querySelector('main')?.innerText || document.body.innerText,
              title: document.title, width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
              overflow: document.documentElement.scrollWidth > innerWidth + 1,
              visibleSpinners: [...document.querySelectorAll('.spinner')].filter(e => e.getBoundingClientRect().width > 0).length,
              brokenImages: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src')) }));
            const row = { who: name, viewport, requested: url, actual: new URL(page.url()).pathname + new URL(page.url()).search,
              ms: Date.now() - start, ...state, events: [...events] };
            out.pages.push(row);
            if (state.overflow || state.brokenImages.length || events.some(e => e.type === 'javascript')) {
              row.screenshot = `web-health-current-${name}-${viewport}-${out.pages.length}.png`;
              await page.screenshot({ path: path.join(dir, row.screenshot), fullPage: true });
            }
          } catch (e) { out.pages.push({ who: name, viewport, requested: url, error: e.message, events: [...events] }); }
          save();
        }
      }
      if (name === 'public') {
        await page.goto('http://127.0.0.1:5173/login');
        const link = page.getByRole('link', { name: 'Quên mật khẩu?', exact: true });
        out.findings.push({ id: 'forgot-password', confirmed: await link.getAttribute('href') === '#', href: await link.getAttribute('href'), evidence: 'Inspected current login link; confirmed=true only when href remains #.' });
      }
      if (name === 'student_em') {
        await page.setViewportSize({ width: 1440, height: 1000 });
        for (const kind of ['pending', 'network']) {
          await page.route('**/api/payments/status?ref=AUDIT_PENDING', r => kind === 'network' ? r.abort() : r.fulfill({ json: {
            success: true, data: { status: 'pending', course_id: course, course_title: 'Đơn kiểm thử giả lập', amount: 100000, transaction_ref: 'AUDIT_PENDING' },
          } }), { times: 1 });
          await page.goto('http://127.0.0.1:5173/student/payment-result?ref=AUDIT_PENDING'); await settle();
          const text = await page.locator('main').innerText();
          out.findings.push({ id: `payment-${kind}`, simulated: true, confirmed: text.includes('Thanh toán thất bại') && text.includes('Bạn chưa bị trừ tiền'), text });
          await page.screenshot({ path: path.join(dir, `web-health-current-payment-${kind}.png`), fullPage: true });
        }
        await page.goto('http://127.0.0.1:5173/student/ai-tutor'); await settle();
        await page.route('**/api/ai/chat', r => r.fulfill({ json: { success: true, data: { answer: 'Ví dụ:\n```python\nprint(1 + 1)\n```',
          sources: [{ document_id: 1, document: 'Nguồn giả lập', page: 1 }], response_status: 'ok' } } }), { times: 1 });
        await page.getByLabel('Câu hỏi cho AI Tutor', { exact: true }).fill('Cho ví dụ Python');
        await page.getByLabel('Câu hỏi cho AI Tutor', { exact: true }).press('Enter');
        await page.getByText('Ví dụ:', { exact: false }).waitFor();
        const chat = page.locator('.ai-tutor-chat'); const content = await chat.innerText();
        out.findings.push({ id: 'ai-format-and-sources', simulated: true, confirmed: content.includes('```python') && await chat.locator('pre code').count() === 0,
          sourceIsClickable: await chat.getByRole('link', { name: /Nguồn giả lập/ }).count() > 0, content });
        await page.screenshot({ path: path.join(dir, 'web-health-current-ai-format.png'), fullPage: true });
      }
      await context.close(); console.log(name, 'pages checked', out.pages.filter(p => p.who === name).length); save();
    }
    out.finishedAt = new Date().toISOString();
    out.summary = { pageChecks: out.pages.length, controls: out.controls.length, failedControls: out.controls.filter(c => !c.passed).length,
      javascriptErrors: out.pages.flatMap(p => p.events || []).filter(e => e.type === 'javascript').length,
      overflows: out.pages.filter(p => p.overflow).length, brokenImagePages: out.pages.filter(p => p.brokenImages?.length).length,
      pageExceptions: out.pages.filter(p => p.error).length, httpErrorPages: out.pages.filter(p => p.events?.some(e => e.type === 'http')).length };
    save(); console.log(JSON.stringify(out.summary, null, 2));
  } finally { await browser.close(); await api.dispose(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
