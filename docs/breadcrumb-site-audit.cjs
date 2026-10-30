// Breadcrumb/layout audit only. Prevents all in-page API mutations.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const origin = 'http://localhost:5173';
const selector = '.breadcrumb, nav.q-breadcrumb, nav.chapters-breadcrumb, nav.tq-breadcrumb';
const report = { pages: [], preventedWrites: [], errors: [], scope: 'Breadcrumb duplication and layout across canonical pages/redirects; not a full functional retest.' };
(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const sessions = {};
  for (const [role, email] of [['admin', 'admin@gmail.com'], ['teacher', 'an.nguyen@studyonline.vn'], ['student', 'em.hoang@gmail.com']]) {
    const res = await api.post('/api/auth/login', { data: { email, password: '123456' } });
    assert.ok(res.ok()); sessions[role] = await res.json();
  }
  async function get(url, role) {
    const response = await api.get(url, { headers: { Authorization: 'Bearer ' + sessions[role].token } });
    return response.ok() ? (await response.json()).data : [];
  }
  const studentQuizzes = await get('/api/quizzes', 'student');
  const teacherQuizzes = await get('/api/quizzes', 'teacher');
  const enrolled = await get('/api/enrollments?ids_only=1', 'student');
  const course = enrolled?.[0] || studentQuizzes?.[0]?.course_id;
  const chapters = course ? await get('/api/chapters?course_id=' + course, 'student') : [];
  const lessons = chapters?.[0] ? await get('/api/lessons?chapter_id=' + chapters[0].id, 'student') : [];
  const results = await get('/api/quizzes/results', 'student');
  const quiz = studentQuizzes?.find(q => !q.my_status?.attempts_used) || studentQuizzes?.[0];
  const routes = {
    public: ['/', '/login', '/register', '/forgot-password', '/reset-password'],
    admin: ['/admin', '/admin/users', '/admin/users/teachers', '/admin/users/students', '/admin/courses', '/admin/payments', '/admin/reports', '/admin/teachers', '/admin/students'],
    teacher: ['/teacher', '/teacher/courses', '/teacher/chapters', '/teacher/lessons', '/teacher/quizzes', '/teacher/quizzes?tab=ai', '/teacher/reports', '/teacher/documents', '/teacher/profile', '/teacher/students', '/teacher/stats', '/teacher/topics', '/teacher/ai-quiz'],
    student: ['/student/dashboard', '/student/courses', '/student/my-courses', '/student/profile', '/student/progress', '/quiz', '/student/ai-tutor', '/student/payment-result', '/student/quiz-history', '/courses'],
  };
  if (course) routes.student.push('/chapters?course_id=' + course);
  if (lessons?.[0]) routes.student.push('/lesson?id=' + lessons[0].id);
  if (quiz) routes.student.push('/quiz-show?id=' + quiz.id);
  if (results?.[0]) routes.student.push('/student/quiz-result?result_id=' + results[0].id);
  if (teacherQuizzes?.[0]) routes.teacher.push('/teacher/quizzes/' + teacherQuizzes[0].id + '/questions');
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  try {
    for (const [role, paths] of Object.entries(routes)) {
      const context = await browser.newContext();
      if (sessions[role]) await context.addInitScript(({ token, user }) => { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }, sessions[role]);
      const page = await context.newPage();
      let pageErrors = [];
      page.on('pageerror', error => pageErrors.push(error.message));
      await page.route('**/api/**', route => {
        if (route.request().method() === 'GET') return route.continue();
        report.preventedWrites.push({ role, method: route.request().method(), path: new URL(route.request().url()).pathname });
        return route.fulfill({ json: { success: true } });
      });
      for (const [viewport, size] of [['desktop', { width: 1440, height: 1000 }], ['mobile', { width: 390, height: 844 }]]) {
        await page.setViewportSize(size);
        for (const url of paths) {
          pageErrors = [];
          await page.goto(origin + url);
          await page.waitForLoadState('networkidle');
          const observed = await page.evaluate(selector => {
            const visible = [...document.querySelectorAll(selector)].filter(node => node.getBoundingClientRect().height && getComputedStyle(node).visibility !== 'hidden');
            return {
              breadcrumbs: visible.map(node => ({ text: node.innerText.replace(/\s+/g, ' ').trim(), insideMain: !!node.closest('main'), insideHeader: !!node.closest('header') })),
              hasContent: !!(document.querySelector('main')?.innerText.trim() || document.querySelector('h1')?.innerText.trim()),
              overflow: document.documentElement.scrollWidth > innerWidth + 1,
            };
          }, selector);
          const item = { role, viewport, requested: url, actual: new URL(page.url()).pathname + new URL(page.url()).search, ...observed, errors: [...pageErrors] };
          report.pages.push(item);
          assert.ok(observed.hasContent, role + ': missing content ' + url);
          assert.ok(observed.breadcrumbs.length <= 1, role + ': duplicate breadcrumb ' + url);
          if (role === 'admin') {
            assert.equal(observed.breadcrumbs.length, 1, url + ': admin breadcrumb must remain');
            assert.ok(observed.breadcrumbs[0].insideMain && !observed.breadcrumbs[0].insideHeader, url + ': keep lower breadcrumb');
          }
          assert.equal(pageErrors.length, 0, url + ': JavaScript error');
          if (role === 'admin' && url === '/admin/payments') await page.screenshot({ path: path.join(__dirname, 'breadcrumb-admin-' + viewport + '.png'), fullPage: true });
        }
      }
      await context.close();
    }
    report.summary = { pageViews: report.pages.length, duplicateBreadcrumbs: report.pages.filter(p => p.breadcrumbs.length > 1).length, javascriptErrorPages: report.pages.filter(p => p.errors.length).length, overflowPages: report.pages.filter(p => p.overflow).map(p => ({ role: p.role, viewport: p.viewport, url: p.requested })) };
    fs.writeFileSync(path.join(__dirname, 'breadcrumb-site-audit.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report.summary));
  } finally { await browser.close(); await api.dispose(); }
})().catch(error => {
  fs.writeFileSync(path.join(__dirname, 'breadcrumb-site-audit.json'), JSON.stringify({ ...report, failure: error.message }, null, 2));
  console.error(error.message); process.exitCode = 1;
});
