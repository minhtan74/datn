// Real read-only Admin list; controlled responses for writes/errors/races.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const checks = [], errors = [];
function check(name, value) { assert.ok(value, name); checks.push(name); }
(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const auth = await (await api.post('/api/auth/login', { data: { email: 'admin@gmail.com', password: '123456' } })).json();
  assert.ok(auth.success);
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript(({ token, user }) => { localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user)); }, auth);
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(e.message));
    page.on('dialog', d => d.accept());
    let mode = 'live', releaseDetail, releaseReconcile, delayDetail = false, delayReconcile = false, bulkBody;
    let refundState = null, refundSends = 0;
    const rows = [
      { id: 990001, transaction_ref: 'FIX-A', status: 'pending' },
      { id: 990002, transaction_ref: 'FIX-B', status: 'completed' },
      { id: 990003, transaction_ref: 'FIX-C', status: 'refunded', refunded_at: '2026-10-30 12:30:00', refund_reason: 'Hoàn tiền kiểm thử', refund_txn_no: '888' },
    ].map(row => ({ user_name: 'Học viên kiểm thử', email: 'fixture@example.test', course_title: 'Khóa kiểm thử', course_id: 100, method: 'vnpay', amount: 100000,
      gateway_txn_no: '555', created_at: '2026-10-30 12:00:00', enrolled: true, ...row }));
    function data(id) {
      const row = { ...rows.find(r => r.id === Number(id)) };
      if (row.id === 990002 && refundState) {
        row.refund_operation = { state: refundState, message: refundState === 'pending' ? 'VNPay đã tiếp nhận, đang chờ kết quả cuối cùng.' : 'Đã xác nhận hoàn tiền và cập nhật quyền học.' };
        if (refundState === 'completed') Object.assign(row, { status: 'refunded', refund_txn_no: '999', refunded_at: '2026-10-30 12:35:00', refund_reason: 'Hỗ trợ học viên', enrolled: false });
      }
      return row;
    }
    await page.route('**/api/payments/**', async route => {
      const url = new URL(route.request().url());
      if (route.request().method() !== 'GET') {
        const body = route.request().postDataJSON();
        if (url.pathname.endsWith('/reconcile-pending')) { bulkBody = body; return route.fulfill({ json: { success: true, message: 'Đã đối soát 1 đơn trong bộ lọc.', processed: 1 } }); }
        if (url.pathname.endsWith('/reconcile')) {
          if (delayReconcile) await new Promise(resolve => { releaseReconcile = resolve; });
          return route.fulfill({ json: { success: true, outcome: 'waiting', message: 'Đơn A đang chờ.', data: data(body.id) } });
        }
        if (url.pathname.endsWith('/refund')) { refundSends++; refundState = 'pending'; return route.fulfill({ json: { success: true, message: 'VNPay đã tiếp nhận, đang chờ kết quả cuối cùng.', data: data(body.id) } }); }
        if (url.pathname.endsWith('/refund-reconcile')) { refundState = 'completed'; return route.fulfill({ json: { success: true, message: 'Đã xác nhận hoàn tiền và cập nhật quyền học.', data: data(body.id) } }); }
        return route.fulfill({ status: 403, json: { success: false } });
      }
      if (mode === 'live') return route.continue();
      if (url.pathname.endsWith('/detail')) {
        const id = Number(url.searchParams.get('id'));
        if (id === 990001 && delayDetail) await new Promise(resolve => { releaseDetail = resolve; });
        return route.fulfill({ json: { success: true, data: data(id) } });
      }
      if (url.pathname.endsWith('/manage')) {
        if (mode === 'error') return route.fulfill({ status: 500, json: { success: false, message: 'Lỗi tải giả lập.' } });
        return route.fulfill({ json: { success: true, data: rows.map(r => data(r.id)), counts: { pending: 1, completed: 38, refunded: 1, failed: 0 }, revenue: 3800000,
          pagination: { page: 1, total: 40, total_pages: 2, page_size: 20 } } });
      }
      return route.continue();
    });
    const main = page.locator('main.main-content'), modal = page.locator('.modal-panel');
    async function ready() { await page.waitForFunction(() => !document.querySelector('main.main-content')?.innerText.includes('Đang tải giao dịch...')); }
    async function open(ref) { await main.locator('tbody tr.row-clickable').filter({ hasText: ref }).click(); await modal.waitFor(); }
    async function close() { await modal.getByRole('button', { name: 'Đóng chi tiết' }).click(); }
    await page.goto('http://localhost:5173/admin/payments'); await ready();
    check('Live list loads', await main.locator('.alert-danger').count() === 0);
    check('No student refund workflow added', await main.getByRole('button', { name: 'Yêu cầu hoàn tiền', exact: true }).count() === 0);
    mode = 'mock'; await page.reload(); await ready();
    await main.getByPlaceholder('Mã đơn, mã GD VNPay, tên hoặc email học viên...').fill('FIX-A');
    await main.locator('input[type="date"]').first().fill('2026-10-01');
    await page.waitForTimeout(550); await ready();
    await main.getByRole('button', { name: /Đối soát 1 đơn chờ trong bộ lọc/ }).click();
    await page.waitForTimeout(100);
    check('Bulk request includes current search and dates', bulkBody.q === 'FIX-A' && bulkBody.date_from === '2026-10-01');
    await open('FIX-C');
    check('Refund history fields appear', (await modal.innerText()).includes('Hoàn tiền kiểm thử') && (await modal.innerText()).includes('888'));
    await close();
    delayDetail = true;
    await open('FIX-A'); await page.waitForTimeout(100); await close();
    await open('FIX-B'); await page.waitForTimeout(100);
    releaseDetail(); await page.waitForTimeout(100);
    check('Late detail A does not overwrite B', (await modal.innerText()).includes('FIX-B') && !(await modal.innerText()).includes('FIX-A'));
    delayDetail = false; await close();
    delayReconcile = true;
    await open('FIX-A'); await page.waitForTimeout(100);
    await modal.getByRole('button', { name: /Kiểm tra với VNPay/ }).click();
    await page.waitForTimeout(100); await close(); await open('FIX-B');
    releaseReconcile(); await page.waitForTimeout(150);
    check('Late reconcile A does not overwrite B', (await modal.innerText()).includes('FIX-B') && !(await modal.innerText()).includes('FIX-A'));
    await modal.getByRole('button', { name: '↩️ Hoàn tiền' }).click();
    await modal.locator('textarea').fill('Hỗ trợ học viên');
    await modal.getByRole('button', { name: 'Xác nhận hoàn tiền' }).click();
    await modal.getByText('VNPay đang xử lý', { exact: true }).waitFor();
    check('Gateway acceptance does not claim final refund', await modal.getByRole('button', { name: 'Đối soát hoàn tiền' }).isVisible());
    check('No repeat send while pending', await modal.getByRole('button', { name: 'Xác nhận hoàn tiền' }).count() === 0 && refundSends === 1);
    await modal.getByRole('button', { name: 'Đối soát hoàn tiền' }).click();
    await modal.getByText('Đã xác nhận hoàn tiền và cập nhật quyền học.', { exact: true }).first().waitFor();
    check('Final confirmation updates receipt', (await modal.innerText()).includes('999') && (await modal.innerText()).includes('Chưa ghi danh'));
    await page.setViewportSize({ width: 390, height: 844 }); await page.waitForTimeout(250);
    check('Mobile modal fits and scrolls', await modal.evaluate(n => n.getBoundingClientRect().width <= innerWidth && n.getBoundingClientRect().height < innerHeight && getComputedStyle(n).overflowY === 'auto'));
    await modal.screenshot({ path: path.join(__dirname, 'admin-fixes-refund-mobile.png') }); await close();
    check('Mobile close is not obscured by header', await modal.count() === 0);
    mode = 'error'; await main.getByRole('button', { name: /^Thất bại/ }).click();
    await main.getByRole('alert').waitFor();
    check('Error does not display old total or revenue', !(await main.innerText()).includes('Tìm thấy 40 giao dịch') && !(await main.innerText()).includes('3.800.000đ'));
    check('Error offers explicit retry', await main.getByRole('button', { name: 'Thử tải lại' }).isVisible());
    mode = 'mock'; await main.getByRole('button', { name: 'Thử tải lại' }).click(); await ready();
    check('List recovers after retry', await main.locator('.alert-danger').count() === 0);

    const guestContext = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const guest = await guestContext.newPage();
    guest.on('pageerror', e => errors.push(e.message));
    await guest.goto('http://localhost:5173/login');
    await guest.getByRole('link', { name: 'Quên mật khẩu?' }).click();
    check('Forgot password explains Admin-assisted recovery', await guest.getByText(/Vui lòng liên hệ Admin quản lý hệ thống/).isVisible());
    check('No email submission form', await guest.locator('input[type="email"], form').count() === 0);
    await guest.goto('http://localhost:5173/reset-password#token=old-unused-link');
    await guest.getByRole('status').waitFor();
    check('Old emailed link points to Admin help and clears fragment', !guest.url().includes('#') && (await guest.getByRole('status').innerText()).includes('không sử dụng liên kết'));
    await guest.screenshot({ path: path.join(__dirname, 'admin-assisted-recovery-mobile.png'), fullPage: true });
    check('Recovery mobile does not overflow', await guest.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    check('No JavaScript exceptions', errors.length === 0);
    fs.writeFileSync(path.join(__dirname, 'admin-fixes-1-4-browser-results.json'), JSON.stringify({ passed: checks.length, checks, errors, realPaymentWrites: 0, gateway: 'simulated' }, null, 2));
    console.log(JSON.stringify({ passed: checks.length, errors: errors.length }));
    await guestContext.close();
  } finally { await browser.close(); await api.dispose(); }
})().catch(e => { console.error(e.message); process.exitCode = 1; });
