// Read-only live reports plus simulated empty/single-status data. No payment writes.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const checks = [];
function check(name, value) { assert.ok(value, name); checks.push(name); }
(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const login = await api.post('/api/auth/login', { data: { email: 'admin@gmail.com', password: '123456' } });
  assert.ok(login.ok());
  const auth = await login.json();
  const headers = { Authorization: 'Bearer ' + auth.token };
  const summary = (await (await api.get('/api/reports/summary', { headers })).json()).data;
  const manage = await (await api.get('/api/payments/manage', { headers })).json();
  const ov = summary.overview;
  check('Report states match management counts', ov.total_orders === manage.counts.completed && ov.pending_orders === manage.counts.pending && ov.failed_orders === manage.counts.failed && ov.refunded_orders === manage.counts.refunded);
  check('Report revenue matches management revenue', ov.total_revenue === manage.revenue);
  check('Recent payments contain only VNPay', summary.recent_payments.every(row => row.method === 'vnpay'));
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1050 } });
    await context.addInitScript(({ token, user }) => { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }, auth);
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const card = page.locator('.card').filter({ has: page.getByRole('heading', { name: '💳 Tình trạng giao dịch VNPay', exact: true }) });
    async function open() { await page.goto('http://localhost:5173/admin/reports'); await card.waitFor(); }
    await open();
    check('Old method comparison removed', await page.getByRole('heading', { name: /Doanh thu theo phương thức/ }).count() === 0);
    check('Status chart drawn', await card.locator('canvas').count() === 1);
    for (const [label, value] of [['Thành công', ov.total_orders], ['Đang chờ', ov.pending_orders], ['Thất bại', ov.failed_orders], ['Đã hoàn tiền', ov.refunded_orders]]) {
      check('Accessible count: ' + label, await card.getByText(`${label}: ${value}`, { exact: true }).isVisible());
    }
    check('Status chart labels all-time scope', (await card.innerText()).includes('Toàn bộ thời gian'));
    check('No legacy method labels in page', !/\b(momo|zalopay|bank_transfer|card)\b/i.test(await page.locator('main').innerText()));
    await page.waitForTimeout(1100); // Let the chart's entrance animation finish for the evidence image.
    const desktopCards = await card.evaluate(node => [...node.parentElement.children].map(child => {
      const { x, y, width, height } = child.getBoundingClientRect(); return { x, y, width, height };
    }));
    check('Desktop chart cards have equal width and height', Math.abs(desktopCards[0].width - desktopCards[1].width) < 1 && Math.abs(desktopCards[0].height - desktopCards[1].height) < 1 && Math.abs(desktopCards[0].y - desktopCards[1].y) < 1);
    await card.locator('..').screenshot({ path: path.join(__dirname, 'reports-vnpay-layout.png') });
    await card.screenshot({ path: path.join(__dirname, 'reports-vnpay-status.png') });
    await page.getByRole('button', { name: '30 ngày', exact: true }).click();
    await page.getByRole('heading', { name: /Doanh thu 30 ngày gần nhất/ }).waitFor();
    check('Revenue range remains functional', true);
    const downloaded = page.waitForEvent('download');
    await page.getByRole('button', { name: /Xuất CSV/ }).first().click();
    const download = await downloaded;
    check('CSV download works', download.suggestedFilename().endsWith('.csv') && !(await download.failure()));
    await page.setViewportSize({ width: 390, height: 844 });
    await card.scrollIntoViewIfNeeded();
    const mobileCards = await card.evaluate(node => [...node.parentElement.children].map(child => {
      const { x, y, width, height } = child.getBoundingClientRect(); return { x, y, width, height };
    }));
    check('Mobile chart cards stack at the same width', Math.abs(mobileCards[0].width - mobileCards[1].width) < 1 && mobileCards[1].y >= mobileCards[0].y + mobileCards[0].height);
    check('Mobile report does not overflow horizontally', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await card.screenshot({ path: path.join(__dirname, 'reports-vnpay-status-mobile.png') });

    let single = false;
    await page.route('**/api/reports/summary?*', route => {
      const data = { ...summary, recent_payments: [], overview: { ...ov, total_revenue: single ? 100000 : 0, total_orders: single ? 1 : 0, pending_orders: 0, failed_orders: 0, refunded_orders: 0, refunded_amount: 0 } };
      return route.fulfill({ json: { success: true, data } });
    });
    await open();
    check('Empty data has clear placeholder', await card.getByText('Chưa có giao dịch VNPay.', { exact: true }).isVisible());
    check('Empty chart does not create misleading ring', await card.locator('canvas').count() === 0);
    single = true;
    await open();
    check('Single-state chart works', await card.locator('canvas').count() === 1 && await card.getByText('Thành công: 1', { exact: true }).isVisible());
    check('Zero status counts remain visible', await card.getByText('Đang chờ: 0', { exact: true }).isVisible());
    check('No JavaScript exceptions', errors.length === 0);
    const result = { passed: checks.length, checks, errors, liveCounts: { completed: ov.total_orders, pending: ov.pending_orders, failed: ov.failed_orders, refunded: ov.refunded_orders }, scope: 'Read-only; simulated empty and single-state UI cases.' };
    fs.writeFileSync(path.join(__dirname, 'reports-vnpay-browser-results.json'), JSON.stringify(result, null, 2));
    console.log(JSON.stringify({ passed: checks.length, errors: errors.length }));
  } finally { await browser.close(); await api.dispose(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
