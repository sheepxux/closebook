import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';
import { exerciseSchema, lessonSchema, quizSchema, exerciseResult, lessonResult, quizResult } from '../cards.mjs';
import { responseMessage, submitResponse } from '../ui/submission.mjs';
import { createCardUI } from '../ui/render.mjs';
import { resolveLocale } from '../locale.mjs';

const html = await readFile(new URL('../ui/card.html', import.meta.url), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));
const base = { id: 'language-check', title: 'Practice', question: 'Write your answer.', collectConfidence: false };
const types = [
  { type: 'mcq', options: [{ id: 'A', text: 'one' }, { id: 'B', text: 'two' }] },
  { type: 'free_text' },
  { type: 'numeric', requireUnit: true },
  { type: 'cloze_passage', passage: 'I {{known}} her. She {{seen}} him.', blanks: [{ id: 'known', label: 'know' }, { id: 'seen', label: 'see' }] },
  { type: 'order_steps', items: [{ id: 'B', text: '  print(n)' }, { id: 'A', text: 'for n in nums:' }], monospace: true },
  { type: 'flashcard', reference: 'Private reference' },
];
function result(type, extra = {}) { return exerciseResult(exerciseSchema.parse({ ...base, ...types.find(value => value.type === type), ...extra })); }
function setup(hostLocale, send = async () => ({})) {
  const dom = new JSDOM(html), doc = dom.window.document, received = [];
  const ui = createCardUI(doc, {
    getHostContext: () => ({ locale: hostLocale }),
    sendMessage: async message => { received.push(message); return send(message); },
  });
  ui.setReady(true);
  function set(selector, value) {
    const field = doc.querySelector(selector); assert.ok(field, selector);
    if (field.type === 'checkbox' || field.type === 'radio') field.checked = value;
    else field.value = value;
    field.dispatchEvent(new dom.window.Event('input', { bubbles: true }));
  }
  return { dom, doc, ui, received, set,
    submit: async () => { doc.querySelector('#submit').click(); await tick(); },
    close: () => dom.window.close(),
  };
}

test('locale is optional on all tool schemas; explicit learner language wins over host and subject', () => {
  for (const locale of ['en', 'zh-CN', undefined]) {
    for (const shape of types) assert.equal(exerciseSchema.parse({ ...base, ...shape, locale }).locale, locale);
    assert.equal(quizSchema.parse({ ...base, options: types[0].options, locale }).locale, locale);
    assert.equal(lessonSchema.parse({ id: 'lesson', title: 'A lesson', explanation: 'An example.', locale }).locale, locale);
  }
  assert.equal(exerciseSchema.safeParse({ ...base, type: 'free_text', locale: 'invalid' }).success, false);
  assert.equal(resolveLocale({ locale: 'zh-CN', question: 'Complete the English sentence.' }, 'en-GB'), 'zh-CN');
  assert.equal(resolveLocale({ locale: 'en', question: '解释汉字。' }, 'zh-CN'), 'en');
  assert.equal(resolveLocale({ question: 'What is acceleration?' }, 'zh-CN'), 'zh-CN');
  assert.equal(resolveLocale({ question: '什么是加速度？' }), 'zh-CN');
  assert.equal(resolveLocale({ question: 'What is acceleration?' }), 'en');
});

test('English fallback text and original show_quiz shape use English controls without changing content', () => {
  for (const shape of types) {
    const value = result(shape.type, { locale: 'en', collectConfidence: true });
    assert.match(value.content[0].text, /Also select confidence/);
    assert.match(value.content[0].text, /Answer and submit in the card/);
    assert.doesNotMatch(value.content[0].text, /[\u3400-\u9fff]/u);
    assert.equal(value.structuredContent.card.locale, 'en');
  }
  const quiz = quizSchema.parse({ ...base, options: types[0].options, locale: 'en', collectConfidence: true });
  const value = quizResult(quiz);
  assert.deepEqual(value.structuredContent, { quiz });
  assert.match(value.content[0].text, /If the card is visible/);
  assert.doesNotMatch(value.content[0].text, /[\u3400-\u9fff]/u);
  assert.match(quizResult({ ...quiz, locale: 'zh-CN' }).content[0].text, /请同时选择把握程度/);
});

test('all six English exercise UIs submit English messages and retain literal learner input', async () => {
  for (const shape of types) {
    const t = setup('zh-CN');
    try {
      t.ui.render(result(shape.type, { locale: 'en', collectConfidence: true }));
      assert.equal(t.doc.documentElement.lang, 'en');
      assert.match(t.doc.title, /learning cards/);
      assert.doesNotMatch(t.doc.body.textContent, /[\u3400-\u9fff]/u);
      assert.equal(t.doc.querySelector('#submit').disabled, true);
      if (shape.type === 'mcq') t.set('input[name="answer"][value="B"]', true);
      if (shape.type === 'free_text' || shape.type === 'flashcard') t.set('textarea[name="response"]', '  First line\n‘ve known <answer>  ');
      if (shape.type === 'numeric') {
        t.set('input[name="value"]', '−1/2'); t.set('input[name="unit"]', 'm/s'); t.set('textarea[name="working"]', ' (2 − 3) / 2 ');
        assert.equal(t.doc.querySelector('input[name="value"]').placeholder, 'Fractions or expressions are welcome');
      }
      if (shape.type === 'cloze_passage') { t.set('input[name="known"]', '‘ve known'); t.set('input[name="seen"]', '‘s not seen'); }
      if (shape.type === 'order_steps') {
        t.doc.querySelector('.pool [data-item-id="B"]').click();
        t.doc.querySelector('.pool [data-item-id="A"]').click();
        t.doc.querySelector('[aria-label="Your order"] [data-item-id="A"] [data-action="up"]').click();
      }
      assert.equal(t.doc.querySelector('#submit').disabled, true);
      t.set('input[name="confidence"][value="2"]', true);
      await t.submit();
      assert.equal(t.received.length, 1, shape.type);
      const message = t.received[0].content[0].text;
      assert.match(message, /give feedback in English/);
      assert.match(message, /Confidence: 2/);
      assert.doesNotMatch(message, /[\u3400-\u9fff]/u);
      assert.match(t.doc.querySelector('#status').textContent, /Return to chat for feedback/);
      if (shape.type === 'free_text' || shape.type === 'flashcard') assert.ok(message.includes('  First line\n‘ve known <answer>  '));
      if (shape.type === 'numeric') assert.ok(message.includes('−1/2') && message.includes(' (2 − 3) / 2 '));
      if (shape.type === 'cloze_passage') assert.ok(message.includes('‘ve known') && message.includes('‘s not seen'));
      if (shape.type === 'order_steps') assert.ok(message.includes('A → B') && message.includes('[B]   print(n)'));
    } finally { t.close(); }
  }
});

test('Chinese learner studying English keeps Chinese UI and feedback with unchanged English answer', async () => {
  const t = setup('en-US');
  try {
    t.ui.render(result('free_text', { locale: 'zh-CN', title: 'Present perfect', question: 'Explain this English sentence.' }));
    assert.equal(t.doc.documentElement.lang, 'zh-CN');
    assert.equal(t.doc.querySelector('#submit').textContent, '提交答案');
    assert.equal(t.doc.querySelector('textarea[name="response"]').getAttribute('aria-label'), '用自己的话回答');
    t.set('textarea[name="response"]', "I've known her for years."); await t.submit();
    assert.match(t.received[0].content[0].text, /并用中文反馈/);
    assert.ok(t.received[0].content[0].text.includes("I've known her for years."));
  } finally { t.close(); }
});

test('legacy cards use host language; locale changes and duplicate notifications preserve an in-progress answer', async () => {
  const t = setup('zh-CN');
  try {
    const value = result('free_text'); t.ui.render(value);
    assert.equal(t.doc.documentElement.lang, 'zh-CN');
    t.set('textarea[name="response"]', 'Keep this exact answer.');
    t.ui.setHostLocale('en-GB');
    t.ui.render(value);
    assert.equal(t.doc.documentElement.lang, 'zh-CN');
    assert.equal(t.doc.querySelector('textarea').value, 'Keep this exact answer.');
    t.ui.render(result('numeric', { id: 'new-english-card' }));
    assert.equal(t.doc.documentElement.lang, 'en');
    assert.equal(t.doc.querySelector('#continue').textContent, 'Continue to practice');
    assert.equal(t.doc.querySelector('#fallback').getAttribute('aria-label'), 'Response text to copy');
    t.ui.render(result('order_steps', { id: 'new-chinese-card', locale: 'zh-CN' }));
    assert.equal(t.doc.documentElement.lang, 'zh-CN');
    assert.ok(t.doc.querySelector('[aria-label="待选项目"]'));
    assert.equal(t.doc.querySelector('[data-i18n="confidence"]').textContent, '你有多大把握？');
  } finally { t.close(); }
});

test('English lesson actions request teaching or a check without claiming mastery', async () => {
  for (const action of ['continue', 'explain-again']) {
    const t = setup('zh-CN');
    try {
      const value = lessonResult(lessonSchema.parse({ id: `lesson-${action}`, locale: 'en', title: 'A lesson', explanation: 'Acceleration describes how velocity changes.', example: { title: 'Example', text: 'After one second...' } }));
      assert.match(value.content[0].text, /does not demonstrate mastery/);
      t.ui.render(value);
      assert.doesNotMatch(t.doc.body.textContent, /[\u3400-\u9fff]/u);
      t.doc.querySelector(`#${action}`).click(); await tick();
      const text = t.received[0].content[0].text;
      assert.match(text, /Please continue in English/);
      if (action === 'continue') assert.match(text, /does not mean I have mastered it/);
      else assert.match(text, /different concrete example/);
      assert.doesNotMatch(text, /My answer|Confidence:/);
    } finally { t.close(); }
  }
});

test('English flashcard failures retain original input, localized fallback and hidden reference', async () => {
  const t = setup('en-US', async () => { throw new Error('offline'); });
  try {
    t.ui.render(result('flashcard', { locale: 'en' }));
    assert.ok(!t.doc.body.textContent.includes('Private reference'));
    t.set('textarea[name="response"]', '  Keep my answer\nunchanged. '); await t.submit();
    assert.equal(t.doc.querySelector('#reference').hidden, true);
    assert.ok(!t.doc.body.textContent.includes('Private reference'));
    assert.match(t.doc.querySelector('#status').textContent, /Submission was not confirmed/);
    assert.ok(t.doc.querySelector('#fallback').value.includes('  Keep my answer\nunchanged. '));
    assert.match(t.doc.querySelector('#fallback').value, /give feedback in English/);
    assert.equal(t.doc.querySelector('textarea[name="response"]').value, '  Keep my answer\nunchanged. ');
    t.ui.showConnectionError('connectionError');
    assert.match(t.doc.querySelector('#status').textContent, /card connection problem/);
  } finally { t.close(); }
});

test('English validation and missing-ack errors do not force Chinese', async () => {
  const card = result('numeric', { locale: 'en' }).structuredContent.card;
  assert.throws(() => responseMessage(card, { value: '1/2' }), /Please fill in Unit/);
  await assert.rejects(submitResponse({ sendMessage: async () => undefined }, card, { value: '1/2', unit: 'm/s' }), /did not accept/);
});
