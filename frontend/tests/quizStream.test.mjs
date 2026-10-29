import test from 'node:test';
import assert from 'node:assert/strict';
import { readQuizStream } from '../src/services/quizStream.js';

function response(parts) {
  return new Response(new ReadableStream({ start(controller) {
    for (const part of parts) controller.enqueue(part);
    controller.close();
  } }));
}

test('partial Unicode packets arrive before the final verified draft', async () => {
  const encoder = new TextEncoder();
  const events = [
    { type: 'status', message: 'Đang sinh' },
    { type: 'batch', questions: [{ question: 'Hệ điều hành là gì?' }] },
    { type: 'complete', data: { questions: [{ question: 'Hệ điều hành là gì?', verified: 'B' }] } },
  ];
  const bytes = encoder.encode(events.map(e => JSON.stringify(e)).join('\n'));
  const progress = [];
  const result = await readQuizStream(response([...bytes].map(b => new Uint8Array([b]))), event => progress.push(event));
  assert.deepEqual(progress.map(e => e.type), ['status', 'batch']);
  assert.equal(progress[1].questions[0].question, 'Hệ điều hành là gì?');
  assert.equal(result.data.data.questions[0].verified, 'B');
});

test('reports an error after partial questions without erasing them', async () => {
  const progress = [];
  const body = [
    { type: 'batch', questions: [{ question: 'Bản nháp' }] },
    { type: 'error', status: 422, message: 'Gemini tạm gián đoạn' },
  ].map(e => JSON.stringify(e)).join('\n');
  const result = await readQuizStream(response([new TextEncoder().encode(body)]), e => progress.push(e));
  assert.equal(result.ok, false);
  assert.equal(result.status, 422);
  assert.equal(progress[0].questions[0].question, 'Bản nháp');
});

test('an interrupted response cannot be mistaken for completion', async () => {
  const bytes = new TextEncoder().encode(JSON.stringify({ type: 'batch', questions: [] }) + '\n');
  const result = await readQuizStream(response([bytes]), () => {});
  assert.equal(result.ok, false);
  assert.match(result.data.message, /gián đoạn/);
});
