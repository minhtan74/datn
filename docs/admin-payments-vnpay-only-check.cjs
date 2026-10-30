// Read-only smoke check of the live Admin transaction list.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const response = await api.post('/api/auth/login', { data: { email: 'admin@gmail.com', password: '123456' } });
  assert.ok(response.ok());
  const auth = await response.json();
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript(({ token, user }) => { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }, auth);
    const page = await context.newPage();
    const errors = [];
    const apiResponses = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('response', r => { if (new URL(r.url()).pathname.startsWith('/api/')) apiResponses.push({ path: new URL(r.url()).pathname, status: r.status() }); });
    const loaded = page.waitForResponse(r => new URL(r.url()).pathname === '/api/payments/manage');
    await page.goto('http://localhost:5173/admin/payments');
    const listing = await loaded.catch(error => { console.error(JSON.stringify({ page: page.url(), errors, apiResponses })); throw error; });
    assert.ok(listing.ok());
    const data = await listing.json();
    assert.equal(new URL(listing.url()).searchParams.get('method'), 'vnpay');
    assert.ok(data.data.every(row => row.method === 'vnpay'));
    await page.waitForFunction(() => document.querySelectorAll('tbody tr.row-clickable').length > 0);
    const methods = await page.locator('tbody tr.row-clickable td:nth-child(5)').allTextContents();
    assert.ok(methods.length > 0 && methods.every(method => method.trim() === '🔴 VNPay'));
    assert.equal(errors.length, 0);
    const defaultResult = await api.get('/api/payments/manage?page_size=100', { headers: { Authorization: 'Bearer ' + auth.token } });
    assert.ok(defaultResult.ok());
    assert.ok((await defaultResult.json()).data.every(row => row.method === 'vnpay'));
    const report = { passed: true, displayedRows: methods.length, onlyVnpay: true, explicitFilter: true, defaultApiOnlyVnpay: true, javascriptErrors: 0, scope: 'Read-only live list; no payment mutations.' };
    fs.writeFileSync(path.join(__dirname, 'admin-payments-vnpay-only-check.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report));
  } finally { await browser.close(); await api.dispose(); }
})().catch(e => { console.error(e.message); process.exitCode = 1; });
