// Opens empty forms only; blocks all in-page writes.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  const findings = [];
  try {
    for (const [role, email, url, button] of [
      ['admin', 'admin@gmail.com', '/admin/users', '+ Thêm Thành viên'],
      ['admin', 'admin@gmail.com', '/admin/courses', '+ Thêm Khóa học'],
      ['teacher', 'an.nguyen@studyonline.vn', '/teacher/courses', '+ Thêm Khóa học'],
    ]) {
      const auth = await (await api.post('/api/auth/login', { data: { email, password: '123456' } })).json();
      assert.ok(auth.success);
      for (const [view, viewport] of [['desktop', { width: 1440, height: 1000 }], ['mobile', { width: 390, height: 844 }]]) {
        const context = await browser.newContext({ viewport });
        await context.addInitScript(({ token, user }) => { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }, auth);
        const page = await context.newPage();
        await page.route('**/api/**', route => route.request().method() === 'GET' ? route.continue() : route.fulfill({ status: 403, json: { success: false, message: 'Audit blocks writes.' } }));
        await page.goto('http://localhost:5173' + url);
        await page.getByRole('button', { name: button, exact: true }).click();
        const modal = page.locator('.modal-panel');
        await modal.waitFor(); await page.waitForTimeout(250);
        const close = modal.locator('.card-header button');
        let closeBlocked = false;
        try { await close.click({ trial: true, timeout: 1600 }); } catch { closeBlocked = true; }
        const hit = await close.evaluate(node => {
          const rect = node.getBoundingClientRect();
          const target = document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2);
          return { blockedByHeader: !!target?.closest('header'), targetClass: target?.className || '', x: rect.x, y: rect.y };
        });
        await page.keyboard.press('Escape');
        const escapeCloses = await modal.count() === 0;
        const result = { role, view, url, closeBlocked, escapeCloses, hit };
        findings.push(result);
        if (view === 'mobile') await page.screenshot({ path: path.join(__dirname, `web-health-current-modal-${role}-${url.split('/').pop()}.png`), fullPage: false });
        await context.close();
      }
    }
    fs.writeFileSync(path.join(__dirname, 'web-health-current-modals.json'), JSON.stringify({ cases: findings, blockedCloseCases: findings.filter(f => f.closeBlocked).length, realWrites: 0 }, null, 2));
    console.log(JSON.stringify({ cases: findings.length, blockedCloseCases: findings.filter(f => f.closeBlocked).length }));
  } finally { await browser.close(); await api.dispose(); }
})().catch(e => { console.error(e.message); process.exitCode = 1; });
