// Kiểm tra lỗi/chờ có kiểm soát bằng route mạng Playwright; không cố gây lỗi dịch vụ LLM thật.
// Một câu làm rõ gọi API thật; các ca lỗi/chậm được giả lập và ghi rõ trong kết quả.
const { chromium, request } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const api = await request.newContext({ baseURL: 'http://127.0.0.1:8080' });
  const checks = [], conversations = [];
  const check = (name, value) => { assert.ok(value, name); checks.push(name); };
  async function call(method, url, auth, data) {
    const r = await api[method](url, { headers: auth ? { Authorization: `Bearer ${auth.token}` } : {}, data });
    const b = await r.json(); assert.ok(r.ok(), `${url}: ${JSON.stringify(b)}`); return b;
  }
  const teacher = await call('post', '/api/auth/login', null, { email: 'an.nguyen@studyonline.vn', password: '123456' });
  const student = await call('post', '/api/auth/login', null, { email: 'em.hoang@gmail.com', password: '123456' });
  let course, browser, enrolled = false;
  try {
    const document = (await call('get', '/api/lessons?id=1', teacher)).data.document_url;
    course = (await call('post', '/api/courses', teacher, { title: `PYTEST AI waiting ${Date.now()}`, price: 0 })).id;
    const chapter = (await call('post', '/api/chapters', teacher, { course_id: course, chapter_name: 'Kiểm thử chờ AI' })).id;
    const lesson = (await call('post', '/api/lessons', teacher, { chapter_id: chapter, title: 'Bài kiểm thử thứ nhất', document_url: document })).id;
    const lesson2 = (await call('post', '/api/lessons', teacher, { chapter_id: chapter, title: 'Bài kiểm thử thứ hai', document_url: document })).id;
    await call('post', '/api/enrollments', student, { course_id: course }); enrolled = true;
    browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined });
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await ctx.addInitScript(a => { localStorage.setItem('token', a.token); localStorage.setItem('user', JSON.stringify(a.user)); }, student);
    const page = await ctx.newPage(); const jsErrors = [];
    page.on('pageerror', e => jsErrors.push(e.message));
    const tutor = 'http://127.0.0.1:5173/student/ai-tutor';
    const input = (inLesson = false) => page.getByLabel(inLesson ? 'Câu hỏi cho AI về bài học' : 'Câu hỏi cho AI Tutor', { exact: true });
    const submit = async (text, inLesson = false) => { await input(inLesson).fill(text); await input(inLesson).press('Enter'); };
    const fresh = () => page.getByRole('button', { name: '+ Cuộc trò chuyện mới', exact: true }).click();
    const endpoint = '**/api/ai/chat';
    const success = (answer, extra = {}) => ({ success: true, data: { answer, sources: [], response_status: 'ok', ...extra } });
    const respondOnce = (body, status = 200, inspect) => page.route(endpoint, r => {
      inspect?.(r.request().postDataJSON()); return r.fulfill({ status, json: body });
    }, { times: 1 });
    const holdOnce = async () => {
      let held;
      await page.route(endpoint, r => { held = r; }, { times: 1 });
      return () => held;
    };
    const late = async (route, text) => { if (route) await route.fulfill({ json: success(text) }).catch(() => {}); };
    await page.goto(tutor);
    await page.locator(`#ai-tutor-course option[value="${course}"]`).waitFor({ state: 'attached' });
    await page.getByLabel('KHÓA HỌC', { exact: true }).selectOption(String(course));
    await fresh();
    const reply = page.waitForResponse(r => r.url().endsWith('/api/ai/chat'));
    await submit('giai thich giup em'); const real = await (await reply).json();
    const cid = real.data.conversation_id; conversations.push(cid);
    await page.locator('.ai-clarification-label').waitFor();
    check('API thật vẫn trả lời làm rõ và giữ hội thoại', real.data.needs_clarification && !!cid);
    await fresh(); await page.clock.install();
    let held = await holdOnce();
    await submit('Câu hỏi đang chờ'); await page.getByRole('button', { name: 'Dừng chờ', exact: true }).waitFor();
    check('Có trạng thái đang xử lý và khóa gửi trong lúc chờ', await input().isDisabled() && (await page.locator('.ai-chat-waiting').innerText()).includes('Tối đa 2 phút'));
    await page.clock.fastForward(16000);
    await page.getByText('AI vẫn đang xử lý. Một số câu hỏi cần thêm thời gian.', { exact: true }).waitFor();
    check('Sau 15 giây có giải thích tiếp tục chờ', (await page.locator('.ai-chat-waiting').innerText()).includes('0:16'));
    await page.clock.fastForward(30000);
    await page.getByText('AI đang mất nhiều thời gian hơn thường lệ. Bạn có thể dừng chờ; câu hỏi vẫn được giữ.', { exact: true }).waitFor();
    check('Sau 45 giây có thông báo chờ lâu', (await page.locator('.ai-chat-waiting').innerText()).includes('0:46'));
    await page.screenshot({ path: path.join(__dirname, 'ai-waiting.png'), fullPage: true });
    await page.getByRole('button', { name: 'Dừng chờ', exact: true }).click();
    check('Dừng chờ mở lại ô nhập và giữ nguyên câu hỏi', await input().isEnabled() && (await page.locator('.ai-chat-feedback').innerText()).includes('Câu hỏi đang chờ'));
    check('Giải thích đúng việc AI có thể tiếp tục lưu kết quả', (await page.locator('.ai-chat-feedback').innerText()).includes('AI có thể vẫn hoàn tất'));
    await late(held(), 'PHẢN HỒI CŨ KHÔNG ĐƯỢC HIỆN');
    check('Không hiện phản hồi cũ sau khi dừng', !((await page.locator('.ai-tutor-chat').innerText()).includes('PHẢN HỒI CŨ KHÔNG ĐƯỢC HIỆN')));
    await page.getByRole('button', { name: 'Sửa câu hỏi', exact: true }).click();
    check('Sửa câu hỏi đưa nguyên văn về ô nhập', await input().inputValue() === 'Câu hỏi đang chờ');
    await fresh();
    const question = 'HTTP là gì?';
    await respondOnce({ success: false, message: 'Dịch vụ AI tạm gián đoạn', data: { conversation_id: cid,
      answer: 'Dịch vụ AI tạm gián đoạn', response_status: 'error', retryable: true, sources: [] } }, 503);
    await submit(question); await page.getByRole('button', { name: 'Thử lại', exact: true }).waitFor();
    check('HTTP503 hiện ở vùng lỗi riêng, có thể thử lại', await page.locator('.ai-chat-failed[role="alert"]').isVisible() && await input().isEnabled());
    check('Lỗi không bị hiển thị như nội dung trả lời AI', !((await page.locator('.ai-tutor-chat').innerText()).includes('HTTP 503')));
    await page.screenshot({ path: path.join(__dirname, 'ai-retry.png'), fullPage: true });
    let retried;
    await respondOnce(success('CÂU TRẢ LỜI SAU KHI THỬ LẠI', { conversation_id: cid }), 200, p => { retried = p; });
    await page.getByRole('button', { name: 'Thử lại', exact: true }).click(); await page.getByText('CÂU TRẢ LỜI SAU KHI THỬ LẠI', { exact: true }).waitFor();
    check('Thử lại giữ câu hỏi và đúng conversation_id', retried.message === question && retried.conversation_id === cid && String(retried.course_id) === String(course));
    check('Thử lại không nhân đôi bong bóng câu hỏi trong khung chat', await page.locator('.ai-tutor-chat').getByText(question, { exact: true }).count() === 1);
    await fresh(); await page.route(endpoint, r => r.abort('failed'), { times: 1 });
    await submit('Câu hỏi khi mất mạng'); await page.locator('.ai-chat-failed').waitFor();
    check('Mất mạng có hướng dẫn kiểm tra kết nối và thử lại', (await page.locator('.ai-chat-failed').innerText()).includes('kiểm tra kết nối mạng'));
    await fresh();
    await page.evaluate(() => {
      const open = XMLHttpRequest.prototype.open, send = XMLHttpRequest.prototype.send;
      XMLHttpRequest.prototype.open = function (method, url, ...args) { this.__chat = String(url).endsWith('/api/ai/chat'); return open.call(this, method, url, ...args); };
      XMLHttpRequest.prototype.send = function (...args) {
        if (this.__chat) { window.configuredChatTimeout = this.timeout; this.timeout = 80; XMLHttpRequest.prototype.open = open; XMLHttpRequest.prototype.send = send; }
        return send.apply(this, args);
      };
    });
    held = await holdOnce(); await submit('Câu hỏi kiểm tra timeout'); await page.getByText('AI phản hồi quá lâu', { exact: true }).waitFor();
    check('Request chat được đặt timeout hai phút', await page.evaluate(() => window.configuredChatTimeout) === 120000);
    check('Hết thời gian giữ câu hỏi và không dùng thông báo sinh quiz', (await page.locator('.ai-chat-failed').innerText()).includes('Câu hỏi kiểm tra timeout') && !(await page.locator('.ai-chat-failed').innerText()).includes('sinh'));
    await late(held(), 'KẾT QUẢ SAU TIMEOUT');
    await fresh(); await respondOnce({ success: false, message: 'Câu hỏi không hợp lệ.' }, 400);
    await submit('Câu hỏi không hợp lệ'); await page.locator('.ai-chat-failed').waitFor();
    check('Lỗi nhập liệu cho sửa, không lặp lại request bị từ chối', await page.getByRole('button', { name: 'Thử lại', exact: true }).count() === 0 && await page.getByRole('button', { name: 'Sửa câu hỏi', exact: true }).isVisible());
    await fresh(); await respondOnce(success('[Lỗi gọi LLM: HTTP 429]'));
    await submit('Câu hỏi nhận lỗi dạng cũ'); await page.locator('.ai-chat-failed').waitFor();
    check('Tương thích lỗi HTTP200 cũ, không lộ chuỗi lỗi kỹ thuật', !((await page.locator('.ai-tutor-chat').innerText()).includes('[Lỗi gọi LLM')));
    await fresh(); await respondOnce(success('NỘI DUNG TRÍCH TỪ TÀI LIỆU', { response_status: 'fallback', sources: [{ document: 'Tài liệu kiểm thử', page: 1 }] }));
    await submit('Câu hỏi dùng dự phòng'); await page.getByText('NỘI DUNG TRÍCH TỪ TÀI LIỆU', { exact: false }).waitFor();
    check('Nội dung dự phòng có nhãn riêng và vẫn có nguồn', (await page.locator('.ai-tutor-chat').innerText()).includes('Trích đoạn tài liệu dự phòng') && (await page.locator('.ai-tutor-chat').innerText()).includes('Tài liệu kiểm thử'));
    await page.route(`**/api/ai/conversations/${cid}`, r => r.fulfill({ json: { success: true, data: {
      conversation: { id: cid, course_id: course, lesson_id: null }, messages: [
        { role: 'user', content: 'CÂU HỎI LƯU BỊ LỖI' }, { role: 'assistant', content: 'AI tạm gián đoạn', response_status: 'error', retryable: true, sources: [] },
      ] } } }), { times: 1 });
    await page.locator('.ai-tutor-grid > .s-card').first().getByText('giai thich giup em', { exact: false }).click();
    await page.getByRole('button', { name: 'Thử lại', exact: true }).waitFor();
    check('Mở lịch sử lỗi khôi phục câu hỏi để thử lại', (await page.locator('.ai-chat-failed').innerText()).includes('CÂU HỎI LƯU BỊ LỖI'));
    await respondOnce(success('ĐÃ THỬ LẠI TỪ LỊCH SỬ', { conversation_id: cid }), 200, p => { retried = p; });
    await page.getByRole('button', { name: 'Thử lại', exact: true }).click(); await page.getByText('ĐÃ THỬ LẠI TỪ LỊCH SỬ', { exact: true }).waitFor();
    check('Thử lại từ lịch sử gửi đúng nội dung, không trùng bong bóng', retried.message === 'CÂU HỎI LƯU BỊ LỖI' && await page.locator('.ai-tutor-chat').getByText('CÂU HỎI LƯU BỊ LỖI', { exact: true }).count() === 1);
    await page.goto(`http://127.0.0.1:5173/lesson?id=${lesson}`); await page.getByTitle('Hỏi AI về bài học', { exact: true }).click();
    held = await holdOnce(); await submit('CÂU HỎI ĐANG CHỜ Ở BÀI CŨ', true);
    await page.getByRole('button', { name: 'Dừng chờ', exact: true }).click();
    check('Khung AI bài học cũng dừng và giữ câu hỏi', await input(true).isEnabled() && (await page.locator('.ai-chat-feedback').innerText()).includes('CÂU HỎI ĐANG CHỜ Ở BÀI CŨ'));
    await late(held(), 'TRẢ LỜI BÀI CŨ');
    await respondOnce(success('CÂU TRẢ LỜI CHO BÀI HỌC'), 200, p => { retried = p; });
    await page.getByRole('button', { name: 'Thử lại', exact: true }).click(); await page.getByText('CÂU TRẢ LỜI CHO BÀI HỌC', { exact: true }).waitFor();
    check('Thử lại ở bài học giữ đúng lesson_id', Number(retried.lesson_id) === Number(lesson) && Number(retried.course_id) === Number(course));
    held = await holdOnce(); await submit('YÊU CẦU ĐỔI BÀI', true); await page.getByRole('button', { name: 'Dừng chờ', exact: true }).waitFor();
    await page.goto(`http://127.0.0.1:5173/lesson?id=${lesson2}`); await page.getByTitle('Hỏi AI về bài học', { exact: true }).click();
    await late(held(), 'KHÔNG ĐƯỢC CHÈN SANG BÀI MỚI');
    check('Đổi bài hủy chờ, không chèn phản hồi hoặc lỗi của bài cũ', await page.locator('.ai-chat-feedback').count() === 0 && !(await page.locator('main').innerText()).includes('KHÔNG ĐƯỢC CHÈN SANG BÀI MỚI'));
    await respondOnce({ success: false, message: 'AI unavailable' }, 503); await submit('Kiểm tra bố cục lỗi điện thoại', true); await page.locator('.ai-chat-failed').waitFor();
    await page.setViewportSize({ width: 390, height: 844 }); await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth);
    check('Thông báo lỗi trong bài học không tràn trên điện thoại', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    check('Không có lỗi JavaScript', jsErrors.length === 0);
    const report = { passed: checks.length, checks, jsErrors, simulation: 'Các ca chậm/lỗi/timeout/dự phòng dùng route mạng giả lập; ca đầu gọi API thật. Timeout trình duyệt được rút ngắn có kiểm soát, đồng thời xác minh cấu hình thực là120000ms.' };
    fs.writeFileSync(path.join(__dirname, 'ai-wait-feedback-check.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report, null, 2));
  } finally {
    if (browser) await browser.close();
    for (const id of conversations) await call('delete', `/api/ai/conversations/${id}`, student);
    if (enrolled) await call('delete', `/api/enrollments?course_id=${course}`, student);
    if (course) await call('delete', `/api/courses?id=${course}`, teacher);
    await api.dispose(); console.log('Đã dọn dữ liệu kiểm thử tạm.');
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
