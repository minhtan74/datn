// Reads live lists only. Every payment POST is intercepted; no real gateway operations.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const report = { checks: [], findings: {}, realPaymentWrites: 0, mockedPaymentWrites: 0, errors: [] };
function check(name, value) { assert.ok(value, name); report.checks.push(name); }

(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const login = await api.post('/api/auth/login', { data: { email: 'admin@gmail.com', password: '123456' } });
  assert.ok(login.ok());
  const auth = await login.json();
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript(({ token, user }) => { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }, auth);
    const page = await context.newPage();
    page.on('pageerror', e => report.errors.push(e.message));
    let mode = 'live';
    let releaseSync;
    let syncStarted = false;
    let bulkBody;
    let lastManage;
    const samples = Array.from({ length: 20 }, (_, index) => ({
      id: 910000 + index, transaction_ref: 'AUDIT-' + String.fromCharCode(65 + index),
      status: index === 0 ? 'pending' : index === 2 ? 'refunded' : 'completed',
      amount: 100000, method: 'vnpay', gateway_txn_no: String(999000 + index),
      user_name: 'Học viên kiểm thử', email: 'audit@example.test', course_title: 'Khóa học kiểm thử giao dịch',
      course_id: 100, user_id: 999000, created_at: '2026-10-30 12:00:00', enrolled: index !== 0,
    }));
    await page.route('**/api/payments/**', async route => {
      const url = new URL(route.request().url());
      if (route.request().method() !== 'GET') {
        report.mockedPaymentWrites++;
        if (url.pathname.endsWith('/reconcile-pending')) {
          bulkBody = route.request().postData();
          return route.fulfill({ json: { success: true, message: 'Đối soát giả lập hoàn tất.' } });
        }
        if (url.pathname.endsWith('/reconcile')) {
          syncStarted = true;
          await new Promise(resolve => { releaseSync = resolve; });
          return route.fulfill({ json: { success: true, outcome: 'waiting', message: 'Đơn A vẫn đang chờ.', data: samples[0] } });
        }
        return route.fulfill({ status: 409, json: { success: false, message: 'Audit blocks real payment writes.' } });
      }
      if (url.pathname === '/api/payments/manage') {
        lastManage = Object.fromEntries(url.searchParams);
        if (mode === 'error') return route.fulfill({ status: 500, json: { success: false, message: 'Audit: lỗi tải giao dịch.' } });
        if (mode === 'mock') return route.fulfill({ json: { success: true, data: samples,
          pagination: { page: Number(url.searchParams.get('page') || 1), total: 40, total_pages: 2, page_size: 20 },
          counts: { pending: 1, completed: 37, refunded: 2, failed: 0 }, revenue: 3700000 } });
      }
      return route.continue();
    });
    const main = page.locator('main.main-content');
    async function settled() { await page.waitForFunction(() => !document.querySelector('main.main-content')?.innerText.includes('Đang tải giao dịch...')); }
    async function open(index) { await main.locator('tbody tr.row-clickable').nth(index).click(); await page.locator('.modal-panel h3').waitFor(); }
    async function close() { await page.locator('.modal-panel .card-header button').click(); }
    await page.goto('http://localhost:5173/admin/payments');
    await main.getByRole('heading', { name: /Quản lý Giao dịch/ }).waitFor();
    await settled();
    check('Live admin list loads without API error', await main.locator('.alert-danger').count() === 0);
    check('Live table has six columns', await main.locator('thead th').count() === 6);
    report.liveRowsOnPage = await main.locator('tbody tr.row-clickable').count();
    if (report.liveRowsOnPage) {
      await open(0);
      check('Live order detail opens', await page.locator('.modal-panel').innerText().then(t => t.includes('Mã đơn hàng') && t.includes('Quyền học')));
      await close();
    }
    await main.getByRole('button', { name: /^Thành công/ }).click(); await settled();
    check('Status tab sends completed filter', lastManage.status === 'completed');
    const search = main.getByPlaceholder('Mã đơn, mã GD VNPay, tên hoặc email học viên...');
    await search.fill('AUDIT-NOT-A-REAL-ORDER');
    await page.waitForTimeout(550); await settled();
    check('Live no-match search shows empty state', (await main.innerText()).includes('Không có giao dịch phù hợp.'));
    await main.getByRole('button', { name: /Xóa lọc/ }).click();
    await page.waitForTimeout(550); await settled();
    check('Reset filters clears search and status', !lastManage.q && !lastManage.status);
    await main.locator('input[type="date"]').first().fill('2026-01-01'); await settled();
    check('Date filter sent to API', lastManage.date_from === '2026-01-01');

    mode = 'mock';
    await page.reload(); await settled();
    await main.getByRole('button', { name: 'Sau ›' }).click(); await settled();
    check('Pagination requests second page', lastManage.page === '2');
    await main.getByRole('button', { name: '‹ Trước' }).click(); await settled();
    check('Pagination returns to first page', lastManage.page === '1');
    await main.getByPlaceholder('Mã đơn, mã GD VNPay, tên hoặc email học viên...').fill('AUDIT-A');
    await page.waitForTimeout(550); await settled();
    await main.getByRole('button', { name: /Đối soát 1 đơn đang chờ/ }).click();
    await page.waitForTimeout(100);
    check('Confirmed filtered bulk action sends no filter', !bulkBody);
    report.findings.bulkScope = { displayedPending: 1, requestBody: bulkBody || null, queryUsedForList: 'AUDIT-A' };
    await open(0);
    await page.locator('.modal-panel').getByRole('button', { name: /Kiểm tra với VNPay/ }).click();
    await page.waitForTimeout(100);
    check('Controlled single reconciliation started', syncStarted);
    await close();
    await open(1);
    check('Second order selected before old response', (await page.locator('.modal-panel').innerText()).includes('AUDIT-B'));
    releaseSync();
    await page.waitForTimeout(200);
    const wrongDetail = (await page.locator('.modal-panel').innerText()).includes('AUDIT-A');
    check('Confirmed stale reconciliation replaces another open order', wrongDetail);
    report.findings.staleDetail = { selectedOrder: 'AUDIT-B', displayedAfterOldResponse: 'AUDIT-A' };
    await page.screenshot({ path: path.join(__dirname, 'web-health-current-admin-payments-stale-detail.png'), fullPage: true });
    await close();
    mode = 'error';
    await main.getByRole('button', { name: /^Thất bại/ }).click();
    await main.locator('.alert-danger').waitFor();
    const staleCount = (await main.innerText()).includes('Tìm thấy 40 giao dịch');
    check('Confirmed load error retains stale totals', staleCount);
    report.findings.staleTotalsOnError = { visibleTotal: 40, listRequestFailed: true };
    await page.screenshot({ path: path.join(__dirname, 'web-health-current-admin-payments-stale-totals.png'), fullPage: true });
    mode = 'mock';
    await page.setViewportSize({ width: 390, height: 844 });
    await page.reload(); await settled();
    check('Mobile page does not overflow horizontally', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await open(2);
    check('Mobile refund detail opens', (await page.locator('.modal-panel').innerText()).includes('Ngày hoàn tiền'));
    check('Mobile refund detail fits viewport', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await page.screenshot({ path: path.join(__dirname, 'web-health-current-admin-payments-mobile.png'), fullPage: true });
    check('No JavaScript exceptions', report.errors.length === 0);
    fs.writeFileSync(path.join(__dirname, 'web-health-current-admin-payments-browser-audit.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify({ checks: report.checks.length, findings: Object.keys(report.findings).length, errors: report.errors.length, realPaymentWrites: 0 }));
  } finally { await browser.close(); await api.dispose(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
