// All payment responses are simulated. No orders, bank calls or payments are created.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'F:/DATN/.cache/npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const checks = [];
function check(name, condition) { assert.ok(condition, name); checks.push(name); }

(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const login = await api.post('/api/auth/login', { data: { email: 'em.hoang@gmail.com', password: '123456' } });
  assert.ok(login.ok());
  const auth = await login.json();
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || 'C:/Users/DMIN/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe' });
  const errors = [];
  let paymentWrites = 0;
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript(({ token, user }) => {
      localStorage.setItem('token', token); localStorage.setItem('user', JSON.stringify(user));
    }, auth);
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    let scenario = 'pending';
    let enrolled = true;
    let requestCount = 0;
    let delayed;
    await page.route('**/api/payments/**', async route => {
      if (route.request().method() !== 'GET') { paymentWrites++; return route.abort(); }
      const url = new URL(route.request().url());
      if (url.pathname !== '/api/payments/status') return route.abort();
      requestCount++;
      const ref = url.searchParams.get('ref');
      if (scenario === 'network') return route.abort('internetdisconnected');
      if (scenario === 'timeout') { await new Promise(resolve => setTimeout(resolve, 17000)); return route.abort().catch(() => {}); }
      if (ref === 'OLD') {
        await new Promise(resolve => { delayed = resolve; });
        return route.fulfill({ json: { success: true, data: { status: 'completed', transaction_ref: 'OLD', enrolled: true, course_id: 100 } } }).catch(() => {});
      }
      if (scenario === '404') return route.fulfill({ status: 404, json: { success: false, message: 'Không tìm thấy đơn hàng.' } });
      if (scenario === '500') return route.fulfill({ status: 500, json: { success: false } });
      if (scenario === 'malformed') return route.fulfill({ json: { success: true, data: null } });
      if (scenario === 'wrong-ref') return route.fulfill({ json: { success: true, data: { status: 'completed', transaction_ref: 'OTHER', enrolled: true } } });
      return route.fulfill({ json: { success: true, data: {
        status: scenario, transaction_ref: ref, course_title: 'Khóa học kiểm thử trạng thái', course_id: 100,
        amount: '250000', enrolled, gateway_txn_no: '0', bank_code: 'NCB', created_at: '2026-10-30 12:00:00',
        message: 'Thông báo từ cổng thanh toán không quyết định trạng thái đơn',
      } } });
    });
    const main = page.locator('main.s-main');
    async function visit(ref = 'TEST-RESULT', suffix = '') {
      await page.goto(`http://localhost:5173/student/payment-result${ref ? '?ref=' + encodeURIComponent(ref) + suffix : ''}`);
      await main.getByRole('heading', { level: 1 }).waitFor();
    }
    async function heading(text) { check(scenario + ': ' + text, await main.getByRole('heading', { name: text, exact: true }).isVisible()); }
    async function noFalseClaims(name) {
      const content = await main.innerText();
      check(name + ': no unsupported failure/bank claim', !content.includes('Thanh toán thất bại') && !content.includes('Bạn chưa bị trừ tiền'));
    }

    await visit('TEST-RESULT', '&status=success&reason=invalid_signature');
    await heading('Thanh toán đang chờ xác nhận');
    await noFalseClaims('pending');
    check('Pending offers status refresh', await main.getByRole('button', { name: 'Kiểm tra lại trạng thái' }).isVisible());
    check('Pending has no payment retry action', await main.getByRole('link', { name: /Thử thanh toán lại|Vào học ngay/ }).count() === 0);
    check('Receipt shows formatted amount', (await main.innerText()).includes('250.000đ'));
    await page.screenshot({ path: path.join(__dirname, 'payment-result-pending.png'), fullPage: true });
    scenario = 'completed';
    await main.getByRole('button', { name: 'Kiểm tra lại trạng thái' }).click();
    await main.getByRole('heading', { name: 'Thanh toán thành công' }).waitFor();
    check('Pending refresh can reach successful outcome', await main.getByRole('link', { name: /Vào học ngay/ }).getAttribute('href') === '/chapters?course_id=100');
    await visit('TEST-RESULT', '&status=failed&reason=invalid_amount');
    await heading('Thanh toán thành công');
    check('Verified success ignores forged URL failure reason', !(await main.innerText()).includes('không khớp'));
    enrolled = false;
    await visit();
    check('Paid but not enrolled does not promise course access', await main.getByRole('link', { name: /Vào học ngay/ }).count() === 0 && (await main.innerText()).includes('chưa được xác nhận'));
    enrolled = true;

    for (const mode of ['network', '404', '500', 'malformed', 'wrong-ref', 'unexpected', 'constructor', 'timeout']) {
      scenario = mode;
      await visit();
      await heading('Chưa xác minh được thanh toán');
      await noFalseClaims(mode);
      check(mode + ': retry available', await main.getByRole('button', { name: 'Kiểm tra lại trạng thái' }).isVisible());
      if (mode === 'network') {
        await page.setViewportSize({ width: 390, height: 844 });
        await page.waitForFunction(() => parseFloat(getComputedStyle(document.querySelector('.s-wrapper')).marginLeft) < 0.5);
        await page.screenshot({ path: path.join(__dirname, 'payment-result-network-mobile.png'), fullPage: true });
        check('Mobile network error has no horizontal overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
        scenario = 'completed';
        await main.getByRole('button', { name: 'Kiểm tra lại trạng thái' }).click();
        await main.getByRole('heading', { name: 'Thanh toán thành công' }).waitFor();
        check('Network retry recovers to verified success', true);
        await page.setViewportSize({ width: 1440, height: 1000 });
      }
    }
    scenario = 'failed';
    await visit();
    await heading('Thanh toán không thành công');
    check('Failed outcome asks to check bank transaction history', (await main.innerText()).includes('kiểm tra lịch sử giao dịch ngân hàng'));
    await noFalseClaims('failed');
    scenario = 'refunded';
    await visit();
    await heading('Đã hoàn tiền');
    check('Refunded outcome has no payment retry or course access claim', await main.getByRole('link', { name: /Thử thanh toán lại|Vào học ngay/ }).count() === 0);
    const before = requestCount;
    await visit('');
    await heading('Chưa xác minh được thanh toán');
    check('Missing ref has clear explanation and does not request status', (await main.innerText()).includes('thiếu mã đơn hàng') && requestCount === before);
    check('Missing ref does not offer useless status retry', await main.getByRole('button', { name: 'Kiểm tra lại trạng thái' }).count() === 0);

    scenario = 'pending';
    await page.goto('http://localhost:5173/student/payment-result?ref=OLD', { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => document.querySelector('main.s-main')?.innerText.includes('Đang kiểm tra'));
    // Change the query in the same mounted route while an earlier request is pending.
    await page.evaluate(() => { history.pushState({}, '', '/student/payment-result?ref=NEW'); dispatchEvent(new PopStateEvent('popstate')); });
    await main.getByRole('heading', { name: 'Thanh toán đang chờ xác nhận' }).waitFor();
    if (delayed) delayed();
    await page.waitForTimeout(200);
    check('Late result for old ref cannot overwrite current order', (await main.innerText()).includes('NEW') && !(await main.innerText()).includes('Thanh toán thành công'));
    check('No payment creation or mutation requests', paymentWrites === 0);
    check('No JavaScript exceptions', errors.length === 0);
    fs.writeFileSync(path.join(__dirname, 'payment-result-browser-results.json'), JSON.stringify({ passed: checks.length, checks, errors, paymentWrites, scope: 'Simulated status responses; read-only login; no bank operations.' }, null, 2));
    console.log(JSON.stringify({ passed: checks.length, errors: errors.length, paymentWrites }));
  } finally { await browser.close(); await api.dispose(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
