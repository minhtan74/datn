// Mỗi dòng là một sự kiện JSON; một dòng có thể bị chia qua nhiều gói mạng.
export async function readQuizStream(response, onProgress) {
  if (!response.body) throw new Error('Không đọc được phản hồi AI dạng luồng.');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let result = null;

  function consume(line) {
    if (!line.trim()) return;
    const event = JSON.parse(line);
    if (event.type === 'complete') {
      if (!Array.isArray(event.data?.questions)) throw new Error('Phản hồi câu hỏi không hợp lệ.');
      result = { ok: true, status: 200, data: { success: true, data: event.data } };
    } else if (event.type === 'error') {
      result = { ok: false, status: event.status || 422,
        data: { success: false, message: event.message || 'Không sinh được câu hỏi.' } };
    } else if (event.type === 'status' || event.type === 'batch') {
      onProgress?.(event);
    }
  }

  try {
    while (!result) {
      const { value, done } = await reader.read();
      buffer += done ? decoder.decode() : decoder.decode(value, { stream: true });
      let end;
      while (!result && (end = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, end);
        buffer = buffer.slice(end + 1);
        consume(line);
      }
      if (done) {
        if (!result && buffer.trim()) consume(buffer);
        break;
      }
    }
    return result || { ok: false, status: 0,
      data: { success: false, message: 'Kết nối AI bị gián đoạn trước khi hoàn tất. Các câu đã nhận được vẫn giữ trong bản nháp.' } };
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
