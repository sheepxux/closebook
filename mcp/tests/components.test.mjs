import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';
import { exerciseSchema, lessonSchema, exerciseResult, lessonResult } from '../cards.mjs';
import { responseMessage, submitResponse } from '../ui/submission.mjs';
import { createCardUI } from '../ui/render.mjs';
import { sampleLesson, sampleExercises } from './fixtures.mjs';

const html = await readFile(new URL('../ui/card.html', import.meta.url), 'utf8');
const fixture = type => sampleExercises.find(exercise => exercise.type === type);
const payload = (type, extra = {}) => exerciseResult(exerciseSchema.parse({ ...fixture(type), collectConfidence: false, ...extra }));
const tick = () => new Promise(resolve => setImmediate(resolve));
function setup(sendMessage = async () => ({})) {
  const dom = new JSDOM(html); // DOM behavior only; no scripts, browser, or desktop host.
  const doc = dom.window.document;
  const received = [];
  const ui = createCardUI(doc, { sendMessage: async (...args) => { received.push(args[0]); return sendMessage(...args); } });
  ui.setReady(true);
  const set = (selector, value) => {
    const field = doc.querySelector(selector); assert.ok(field, selector);
    if (field.type === 'radio' || field.type === 'checkbox') field.checked = value;
    else field.value = value;
    field.dispatchEvent(new dom.window.Event('input', { bubbles: true }));
    field.dispatchEvent(new dom.window.Event('change', { bubbles: true }));
  };
  const submit = async () => { doc.querySelector('form').dispatchEvent(new dom.window.Event('submit', { bubbles: true, cancelable: true })); await tick(); };
  return { dom, doc, ui, received, set, submit, close: () => dom.window.close() };
}

test('所有组件输入严格校验：占位符、选项、排序数量、未知答案字段', () => {
  lessonSchema.parse(sampleLesson);
  sampleExercises.forEach(exercise => exerciseSchema.parse(exercise));
  const codeOrder = exerciseSchema.parse({
    id: 'code-order', title: '保留缩进', question: '排列这两行，保持原有缩进。', type: 'order_steps', monospace: true,
    items: [{ id: 'body', text: '    print(n)' }, { id: 'loop', text: 'for n in nums:' }],
  });
  assert.equal(codeOrder.items[0].text, '    print(n)');
  const invalid = [
    { ...fixture('cloze_passage'), passage: 'I {{known}} and {{known}}' },
    { ...fixture('cloze_passage'), passage: 'I {{known}} and {{other}}' },
    { ...fixture('cloze_passage'), passage: 'I {{known}} and {{seen}} {{' },
    { ...fixture('cloze_passage'), blanks: [{ id: 'known', label: 'A' }, { id: 'known', label: 'B' }] },
    { ...fixture('order_steps'), pickCount: 6 },
    { ...fixture('order_steps'), items: [{ id: 'a', text: 'A' }, { id: 'a', text: 'B' }] },
    { ...fixture('free_text'), answer: '不应该传递答案' },
    { ...fixture('numeric'), value: -0.5 },
    { ...fixture('flashcard'), reference: '' },
    { ...fixture('mcq'), type: 'graph' },
  ];
  for (const exercise of invalid) assert.equal(exerciseSchema.safeParse(exercise).success, false);
});

test('讲解卡显示知识和示范；继续练习不记成答对或掌握', async () => {
  const t = setup();
  try {
    t.ui.render(lessonResult(sampleLesson));
    assert.ok(t.doc.querySelector('#body').textContent.includes(sampleLesson.example.text));
    assert.equal(t.doc.querySelector('form').hidden, true);
    t.doc.querySelector('#continue').click(); await tick();
    assert.equal(t.received.length, 1);
    assert.match(t.received[0].content[0].text, /请出一道引导练习/);
    assert.match(t.received[0].content[0].text, /不表示我已经掌握/);
    t.doc.querySelector('#continue').click(); await tick();
    assert.equal(t.received.length, 1);
  } finally { t.close(); }
});

test('讲解卡的再解释按钮发送再教学请求，而不是作答', async () => {
  const t = setup();
  try {
    t.ui.render(lessonResult(sampleLesson));
    t.doc.querySelector('#explain-again').click(); await tick();
    assert.match(t.received[0].content[0].text, /换个具体例子再解释/);
    assert.doesNotMatch(t.received[0].content[0].text, /我的作答|把握程度/);
  } finally { t.close(); }
});

test('选择题必须作答和选择信心，错答原样提交；重复工具结果不清空状态', async () => {
  const t = setup();
  try {
    const result = payload('mcq', { collectConfidence: true }); t.ui.render(result);
    t.set('input[name="answer"][value="B"]', true);
    assert.equal(t.doc.querySelector('#submit').disabled, true);
    t.ui.render(result);
    assert.equal(t.doc.querySelector('input[value="B"]').checked, true);
    t.set('input[name="confidence"][value="3"]', true); await t.submit();
    assert.match(t.received[0].content[0].text, /我的选择：B（细胞核）/);
    assert.match(t.received[0].content[0].text, /把握程度：3/);
    t.ui.render(result); await t.submit(); assert.equal(t.received.length, 1);
  } finally { t.close(); }
});

test('简答保留多行原文，题目和学生文字不会作为 HTML 执行', async () => {
  const t = setup();
  try {
    t.ui.render(payload('free_text', { question: '<img src=x onerror=alert(1)> 请解释这个字符串。' }));
    assert.equal(t.doc.querySelector('img'), null);
    t.set('textarea[name="response"]', '第一行\n<script>answer()</script>\n第二行'); await t.submit();
    assert.match(t.received[0].content[0].text, /第一行\n<script>answer\(\)<\/script>\n第二行/);
  } finally { t.close(); }
});

test('数值题保留分数、负号、单位及过程，不在页面替学生改答案', async () => {
  const t = setup();
  try {
    t.ui.render(payload('numeric', { requireUnit: true }));
    t.set('input[name="value"]', '−1/2');
    assert.equal(t.doc.querySelector('#submit').disabled, true);
    t.set('input[name="unit"]', 'm/s'); t.set('textarea[name="working"]', '(2 - 3) / (4 - 2)');
    await t.submit(); const text = t.received[0].content[0].text;
    assert.match(text, /−1\/2/); assert.match(text, /m\/s/); assert.match(text, /\(2 - 3\) \/ \(4 - 2\)/);
    assert.doesNotMatch(t.doc.querySelector('#status').textContent, /正确|错误/);
  } finally { t.close(); }
});

test('填空需要所有空都有内容，并原样保留弯引号等价写法', async () => {
  const t = setup();
  try {
    t.ui.render(payload('cloze_passage'));
    t.set('input[name="known"]', '‘ve known');
    assert.equal(t.doc.querySelector('#submit').disabled, true);
    t.set('input[name="seen"]', '‘s not seen'); await t.submit();
    const text = t.received[0].content[0].text;
    assert.match(text, /known\]：‘ve known/); assert.match(text, /seen\]：‘s not seen/);
  } finally { t.close(); }
});

test('排序支持选取、上下移动和移回；未选干扰项不会混进答案', async () => {
  const t = setup();
  try {
    t.ui.render(payload('order_steps'));
    for (const id of ['commit', 'edit', 'stage']) t.doc.querySelector(`.pool [data-item-id="${id}"]`).click();
    t.doc.querySelector('[aria-label="你的排列"] [data-item-id="commit"] [data-action="down"]').click();
    t.doc.querySelector('[aria-label="你的排列"] [data-item-id="commit"] [data-action="down"]').click();
    t.doc.querySelector('[aria-label="你的排列"] [data-item-id="stage"] [data-action="remove"]').click();
    assert.equal(t.doc.querySelector('#submit').disabled, true);
    t.doc.querySelector('.pool [data-item-id="stage"]').click();
    t.doc.querySelector('[aria-label="你的排列"] [data-item-id="stage"] [data-action="up"]').click();
    await t.submit();
    assert.match(t.received[0].content[0].text, /edit → stage → commit/);
    assert.doesNotMatch(t.received[0].content[0].text, /删除整个仓库/);
  } finally { t.close(); }
});

test('回忆卡只在真实作答获确认后翻面；提交前 DOM 没有参考答案', async () => {
  let confirm;
  const t = setup(() => new Promise(resolve => { confirm = resolve; }));
  try {
    t.ui.render(payload('flashcard'));
    assert.ok(!t.doc.body.textContent.includes('线粒体'));
    assert.equal(t.doc.querySelector('#submit').disabled, true);
    t.set('textarea[name="response"]', '细胞核'); await t.submit();
    assert.equal(t.doc.querySelector('#reference').hidden, true);
    assert.ok(!t.doc.body.textContent.includes('线粒体'));
    assert.match(t.received[0].content[0].text, /我的作答：\n细胞核/);
    assert.doesNotMatch(t.received[0].content[0].text, /线粒体/);
    confirm({}); await tick();
    assert.equal(t.doc.querySelector('#reference').hidden, false);
    assert.ok(t.doc.querySelector('#reference').textContent.includes('线粒体'));
  } finally { t.close(); }
});

test('回忆卡发送失败不翻面，保留原答案供复制和重试', async () => {
  const t = setup(async () => { throw new Error('disconnected'); });
  try {
    t.ui.render(payload('flashcard'));
    t.set('textarea[name="response"]', '不知道具体名称'); await t.submit();
    assert.equal(t.doc.querySelector('#reference').hidden, true);
    assert.equal(t.doc.querySelector('#fallback').hidden, false);
    assert.match(t.doc.querySelector('#fallback').value, /不知道具体名称/);
    assert.equal(t.doc.querySelector('textarea[name="response"]').value, '不知道具体名称');
    assert.equal(t.doc.querySelector('#submit').disabled, false);
  } finally { t.close(); }
});

test('所有练习都允许诚实回答不会，不把默认值当作学习者答案', async () => {
  for (const exercise of sampleExercises) {
    const t = setup();
    try {
      t.ui.render(payload(exercise.type)); t.set('#dont-know', true); await t.submit();
      assert.match(t.received[0].content[0].text, /这题我还不会/);
      assert.doesNotMatch(t.received[0].content[0].text, /我的选择：|我的顺序：|我的数值/);
    } finally { t.close(); }
  }
});

test('旧题迟到的提交确认不能锁住新题或泄露旧卡背', async () => {
  let confirm;
  const t = setup(() => new Promise(resolve => { confirm = resolve; }));
  try {
    t.ui.render(payload('flashcard')); t.set('textarea[name="response"]', '我的旧答案'); await t.submit();
    t.ui.render(payload('free_text')); t.set('textarea[name="response"]', '这是新题的回答');
    confirm({}); await tick();
    assert.equal(t.doc.querySelector('#submit').disabled, false);
    assert.equal(t.doc.querySelector('#reference').hidden, true);
    assert.equal(t.doc.querySelector('textarea[name="response"]').value, '这是新题的回答');
  } finally { t.close(); }
});

test('回应验证拒绝漏空、重复排序项和无确认的消息返回', async () => {
  const order = payload('order_steps').structuredContent.card;
  assert.throws(() => responseMessage(order, { order: ['edit', 'edit', 'commit'] }), /按顺序/);
  const cloze = payload('cloze_passage').structuredContent.card;
  assert.throws(() => responseMessage(cloze, { blanks: { known: 'known' } }), /每一空/);
  const card = payload('free_text').structuredContent.card;
  await assert.rejects(submitResponse({ sendMessage: async () => undefined }, card, { text: '答案' }), /没有接受/);
});
