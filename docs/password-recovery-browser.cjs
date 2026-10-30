// Requires the temporary backend/tests/password_recovery_browser_server.py fixture.
const { chromium } = require('F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const checks = [];
const errors = [];
const origin = 'http://localhost:5173';
const fixture = 'http://127.0.0.1:8082';
async function state() { return (await fetch(fixture + '/_test/state')).json(); }
function check(name, condition) { assert.ok(condition, name); checks.push(name); }

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 980 } });
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(e.message));
    await page.route('**/api/auth/**', async route => {
      const url = new URL(route.request().url());
      const response = await route.fetch({ url: fixture + url.pathname, maxRetries: 0 });
      await route.fulfill({ response });
    });
    const users = (await state()).users;
    await page.goto(origin + '/login');
    await page.getByRole('link', { name: 'Quên mật khẩu?' }).click();
    await page.getByRole('heading', { name: 'Quên mật khẩu', exact: true }).waitFor();
    check('Login links to recovery page', page.url().endsWith('/forgot-password'));
    await page.screenshot({ path: path.join(__dirname, 'password-recovery-desktop.png'), fullPage: true });
    let generic;
    for (const role of ['admin', 'student', 'teacher']) {
      await page.goto(origin + '/forgot-password');
      await page.getByLabel('Email đã đăng ký').fill(users[role].email);
      await page.getByRole('button', { name: 'Gửi liên kết đặt lại' }).click();
      const result = page.getByRole('status');
      await result.waitFor();
      const text = await result.innerText();
      if (!generic) generic = text;
      check(role + ': identical public confirmation', text === generic);
      await page.getByRole('button', { name: 'Gửi liên kết đặt lại' }).waitFor({ state: 'visible' });
    }
    // Background SMTP may still be finishing after the public response.
    let fixtureState;
    for (let i = 0; i < 30; i++) {
      fixtureState = await state();
      if (fixtureState.messages.length === 2) break;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    check('Local SMTP received exactly two messages', fixtureState.messages.length === 2);
    check('Admin received no email', !fixtureState.messages.some(m => m.email === users.admin.email));
    for (const role of ['student', 'teacher']) {
      const token = fixtureState.messages.find(m => m.email === users[role].email)?.token;
      check(role + ': SMTP message contains reset link', typeof token === 'string' && token.length === 43);
      await page.goto(origin + '/reset-password#token=' + token);
      await page.getByLabel('Mật khẩu mới', { exact: true }).waitFor();
      check(role + ': referrer policy', await page.locator('meta[name="referrer"]').getAttribute('content') === 'no-referrer');
      await page.getByLabel('Mật khẩu mới', { exact: true }).fill('NewPass456!');
      await page.getByLabel('Xác nhận mật khẩu mới').fill('Different456!');
      await page.getByRole('button', { name: 'Lưu mật khẩu mới' }).click();
      check(role + ': mismatch feedback', (await page.getByRole('alert').innerText()).includes('không khớp'));
      await page.getByLabel('Xác nhận mật khẩu mới').fill('NewPass456!');
      await page.getByRole('button', { name: 'Lưu mật khẩu mới' }).click();
      await page.getByRole('link', { name: 'Đăng nhập bằng mật khẩu mới' }).waitFor();
      check(role + ': reset succeeds', (await page.getByRole('status').innerText()).includes('thành công'));
      check(role + ': fragment removed on success', !page.url().includes('#'));
      await page.getByRole('link', { name: 'Đăng nhập bằng mật khẩu mới' }).click();
      await page.locator('#email').fill(users[role].email);
      await page.locator('#password').fill('NewPass456!');
      await page.getByRole('button', { name: /Đăng nhập/ }).click();
      await page.waitForURL(role === 'student' ? '**/student/dashboard' : '**/teacher');
      check(role + ': new password logs into correct dashboard', true);
      await page.goto(origin + '/reset-password#token=' + token);
      await page.getByRole('alert').waitFor();
      check(role + ': reused link rejected', (await page.getByRole('alert').innerText()).includes('đã được sử dụng'));
      await page.evaluate(() => localStorage.clear());
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(origin + '/forgot-password');
    await page.getByRole('heading', { name: 'Quên mật khẩu', exact: true }).waitFor();
    check('Mobile recovery has no horizontal overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: path.join(__dirname, 'password-recovery-mobile.png'), fullPage: true });
    await page.goto(origin + '/reset-password');
    await page.getByRole('alert').waitFor();
    check('Missing token has clear error and new-link action', await page.getByRole('link', { name: 'Yêu cầu liên kết mới' }).isVisible());
    check('No browser JavaScript errors', errors.length === 0);
    fs.writeFileSync(path.join(__dirname, 'password-recovery-browser-results.json'), JSON.stringify({ checks: checks.length, passed: checks, errors, smtp: 'local collector; no external mail' }, null, 2));
    console.log(JSON.stringify({ passed: checks.length, errors: errors.length }));
  } finally { await browser.close(); }
})().catch(e => { console.error(e.message.replace(/token=[\w-]+/g, 'token=[REDACTED]')); process.exitCode = 1; });
