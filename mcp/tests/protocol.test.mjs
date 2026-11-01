import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { request } from 'node:http';
import { Client, InMemoryTransport, StreamableHTTPClientTransport } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { App } from '@modelcontextprotocol/ext-apps';
import { AppBridge } from '@modelcontextprotocol/ext-apps/app-bridge';
import { RESOURCE_MIME_TYPE } from '@modelcontextprotocol/ext-apps/server';
import { startHttp, RESOURCE_URI, quiz } from '../server.mjs';
import { answerMessage, submitChoice, submitResponse } from '../ui/submission.mjs';
import { exerciseSchema, exerciseResult, lessonResult } from '../cards.mjs';
import { sampleLesson, sampleExercises } from './fixtures.mjs';

const lessonQuiz = {
  id: 'biology-cell-membrane-01',
  title: '细胞结构复习',
  question: '哪种结构主要控制物质进出细胞？',
  options: [{ id: 'A', text: '细胞膜' }, { id: 'B', text: '细胞核' }, { id: 'C', text: '细胞壁' }],
};

async function checkProtocol(client) {
  const { tools } = await client.listTools();
  assert.deepEqual(tools.map(tool => tool.name).sort(), ['show_exercise', 'show_lesson', 'show_quiz']);
  assert.equal(tools[0]._meta.ui.resourceUri, RESOURCE_URI);
  assert.equal(tools[0].annotations.readOnlyHint, true);
  const result = await client.callTool({ name: 'show_quiz', arguments: {} });
  assert.equal(result.isError, undefined);
  assert.deepEqual(result.structuredContent.quiz, quiz);
  assert.match(result.content[0].text, /len\(\[2, 4, 6\]\)/);
  const resource = await client.readResource({ uri: RESOURCE_URI });
  const content = resource.contents[0];
  assert.equal(content.mimeType, RESOURCE_MIME_TYPE);
  assert.match(content.text, /id="submit"/);
  assert.match(content.text, /ui\/message/);
  assert.doesNotMatch(content.text, /APP_BUNDLE|<script[^>]+src=/);
  assert.deepEqual(content._meta.ui.csp.connectDomains, []);

  // A real lesson must keep its own subject, options and closed-book state.
  const custom = await client.callTool({ name: 'show_quiz', arguments: { quiz: lessonQuiz } });
  assert.equal(custom.isError, undefined);
  assert.deepEqual(custom.structuredContent.quiz, { ...lessonQuiz, collectConfidence: true });
  assert.doesNotMatch(custom.content[0].text, /Python|len\(/);
  assert.equal(custom.structuredContent.quiz.lesson, undefined);
  assert.match(custom.content[0].text, /1–3/);
  const nextQuiz = { ...lessonQuiz, id: 'biology-cell-membrane-02', collectConfidence: false };
  const next = await client.callTool({ name: 'show_quiz', arguments: { quiz: nextQuiz } });
  assert.deepEqual(next.structuredContent.quiz, nextQuiz);
  assert.equal(custom.structuredContent.quiz.id, lessonQuiz.id);

  const lesson = await client.callTool({ name: 'show_lesson', arguments: { lesson: sampleLesson } });
  assert.equal(lesson.isError, undefined);
  assert.deepEqual(lesson.structuredContent.card, { ...sampleLesson, kind: 'lesson' });
  for (const exercise of sampleExercises) {
    const result = await client.callTool({ name: 'show_exercise', arguments: { exercise } });
    assert.equal(result.isError, undefined);
    assert.equal(result.structuredContent.card.type, exercise.type);
    assert.equal(result.structuredContent.card.id, exercise.id);
    assert.equal(result.structuredContent.card.collectConfidence, true);
    assert.equal(result.structuredContent.card.reference, undefined);
    if (exercise.type === 'flashcard') {
      assert.equal(result._meta['closebook/reference'], exercise.reference);
      assert.ok(!JSON.stringify(result.content).includes(exercise.reference));
      assert.ok(!JSON.stringify(result.structuredContent).includes(exercise.reference));
    }
  }
}

test('真实 STDIO：握手、教学和练习工具、题目结果和自包含 UI 资源', { timeout: 15000 }, async () => {
  const client = new Client({ name: 'closebook-stdio-test', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../server.mjs', import.meta.url)), '--stdio'],
    stderr: 'pipe',
  });
  try { await client.connect(transport); await checkProtocol(client); }
  finally { await client.close(); }
});

test('真实 HTTP：握手与资源读取，拒绝不符的 Host 和 Origin', { timeout: 15000 }, async () => {
  const server = await startHttp(0);
  const base = `http://127.0.0.1:${server.address().port}`;
  const client = new Client({ name: 'closebook-http-test', version: '1.0.0' });
  try {
    assert.equal((await fetch(base + '/health')).status, 200);
    const invalidHostStatus = await new Promise((resolve, reject) => {
      const req = request(base + '/health', { headers: { Host: 'attacker.example' } }, res => {
        res.resume(); resolve(res.statusCode);
      });
      req.on('error', reject); req.end();
    });
    assert.equal(invalidHostStatus, 403);
    assert.equal((await fetch(base + '/health', { headers: { Origin: 'https://attacker.example' } })).status, 403);
    await client.connect(new StreamableHTTPClientTransport(new URL(base + '/mcp')));
    await checkProtocol(client);
  } finally { await client.close(); await new Promise(resolve => server.close(resolve)); }
});

test('工具拒绝畸形题目、重复选项和泄露答案的字段，不退回无关演示题', { timeout: 15000 }, async () => {
  const client = new Client({ name: 'closebook-input-test', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../server.mjs', import.meta.url)), '--stdio'],
    stderr: 'pipe',
  });
  try {
    await client.connect(transport);
    const cases = [
      { ...lessonQuiz, question: '   ' },
      { ...lessonQuiz, options: lessonQuiz.options.slice(0, 1) },
      { ...lessonQuiz, options: [{ id: 'A', text: '甲' }, { id: 'A', text: '乙' }] },
      { ...lessonQuiz, options: [{ id: 'A', text: '甲' }, { id: 'B', text: '甲' }] },
      { ...lessonQuiz, answer: 'A' },
      { ...lessonQuiz, options: [{ id: 'A', text: '甲', correct: true }, { id: 'B', text: '乙' }] },
      { ...lessonQuiz, collectConfidence: 'yes' },
    ];
    for (const invalid of cases) {
      const result = await client.callTool({ name: 'show_quiz', arguments: { quiz: invalid } });
      assert.equal(result.isError, true);
      assert.equal(result.structuredContent, undefined);
    }
  } finally { await client.close(); }
});

// This is an SDK protocol round trip with an in-memory test host, not a
// browser or a real Codex/Claude conversation. Host rendering remains separate.
async function withBridge(onmessage, run) {
  const bridge = new AppBridge(null, { name: 'test-host', version: '1' }, { message: { text: {} } });
  bridge.onmessage = onmessage;
  const app = new App({ name: 'test-card', version: '1' }, {}, { autoResize: false });
  const [hostTransport, appTransport] = InMemoryTransport.createLinkedPair();
  try {
    await bridge.connect(hostTransport);
    await app.connect(appTransport);
    await run(app);
  } finally { await app.close(); await bridge.close(); }
}

test('真实 SDK 消息协议：提交包含用户选项、题目编号和题目正文', async () => {
  const received = [];
  await withBridge(async message => { received.push(message); return {}; }, async app => {
    await submitChoice(app, quiz, 'B');
  });
  assert.equal(received.length, 1);
  assert.equal(received[0].role, 'user');
  assert.match(received[0].content[0].text, /我的选择：B（3）/);
  assert.match(received[0].content[0].text, /python-list-length-v1/);
});

test('课程题同时提交真实选项和信心，未选信心时不发送', async () => {
  const current = { ...lessonQuiz, collectConfidence: true };
  const received = [];
  await withBridge(async message => { received.push(message); return {}; }, async app => {
    for (const confidence of [undefined, 0, 4, '2']) {
      await assert.rejects(submitChoice(app, current, 'B', { confidence }), /把握程度/);
    }
    assert.equal(received.length, 0);
    await submitChoice(app, current, 'B', { confidence: 2 });
  });
  assert.equal(received.length, 1);
  assert.match(received[0].content[0].text, /我的选择：B（细胞核）/);
  assert.match(received[0].content[0].text, /把握程度：2/);
  assert.match(received[0].content[0].text, /biology-cell-membrane-01/);
  assert.doesNotMatch(answerMessage({ ...current, collectConfidence: false }, 'B'), /把握程度/);
});

test('七种组件的回应均通过官方 SDK 消息通道，教学回应不作为测验答案', async () => {
  const received = [];
  const answers = {
    mcq: { optionId: 'B' }, free_text: { text: '分子分母乘以同一个非零数，比值不变。' },
    numeric: { value: '-1/2' }, cloze_passage: { blanks: { known: '‘ve known', seen: '‘s not seen' } },
    order_steps: { order: ['edit', 'stage', 'commit'] }, flashcard: { text: '线粒体' },
  };
  await withBridge(async message => { received.push(message); return {}; }, async app => {
    for (const exercise of sampleExercises) {
      const card = exerciseResult(exerciseSchema.parse(exercise)).structuredContent.card;
      await submitResponse(app, card, { ...answers[exercise.type], confidence: 2 });
    }
    await submitResponse(app, lessonResult(sampleLesson).structuredContent.card, { action: 'explain_again' });
  });
  assert.equal(received.length, 7);
  assert.ok(received.every(message => message.role === 'user'));
  for (let i = 0; i < sampleExercises.length; i++) {
    assert.ok(received[i].content[0].text.includes(sampleExercises[i].id));
    assert.match(received[i].content[0].text, /把握程度：2/);
  }
  assert.match(received[6].content[0].text, /换个具体例子再解释/);
  assert.doesNotMatch(received[6].content[0].text, /题目编号|把握程度/);
});

test('宿主拒绝 ui/message 时不能报告提交成功', async () => {
  await withBridge(async () => ({ isError: true }), async app => {
    await assert.rejects(submitChoice(app, quiz, 'B'), /没有接受/);
  });
});

test('未选择或不存在的选项不会发送消息', async () => {
  let calls = 0;
  const stub = { sendMessage: async () => { calls++; return {}; } };
  assert.throws(() => answerMessage(quiz, 'X'), /先选择/);
  await assert.rejects(submitChoice(stub, quiz, ''), /先选择/);
  assert.equal(calls, 0);
});

test('消息通道中断会保留失败状态；错答也如实发送而非改成正确选项', async () => {
  const received = [];
  const stub = { sendMessage: async message => { received.push(message); throw new Error('disconnected'); } };
  await assert.rejects(submitChoice(stub, quiz, 'D'), /disconnected/);
  assert.match(received[0].content[0].text, /我的选择：D（12）/);
});
