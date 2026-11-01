import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { App } from '@modelcontextprotocol/ext-apps';
import { AppBridge } from '@modelcontextprotocol/ext-apps/app-bridge';
import { submitResponse } from '../ui/submission.mjs';

const lesson = {
  id: 'locale-protocol-lesson', title: 'Present perfect',
  explanation: 'Use the present perfect to connect a past situation with the present.',
  example: { title: 'Example', text: 'I have lived here since 2021.' },
};
const exercise = {
  id: 'locale-protocol-written', title: 'Explain the tense', type: 'free_text',
  question: 'Explain why the present perfect is used in this sentence.', collectConfidence: true,
};
const quiz = {
  id: 'locale-protocol-choice', title: 'Choose a tense', question: 'Which form connects this situation to the present?',
  options: [{ id: 'A', text: 'have lived' }, { id: 'B', text: 'lived' }], collectConfidence: true,
};
const tools = [
  { name: 'show_lesson', key: 'lesson', value: lesson },
  { name: 'show_exercise', key: 'exercise', value: exercise },
  { name: 'show_quiz', key: 'quiz', value: quiz },
];

async function withClient(run) {
  const client = new Client({ name: 'closebook-locale-protocol-test', version: '1.0.0' });
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [fileURLToPath(new URL('../server.mjs', import.meta.url)), '--stdio'],
    stderr: 'pipe',
  });
  try { await client.connect(transport); await run(client); }
  finally { await client.close(); }
}

const invoke = (client, tool, locale) => client.callTool({
  name: tool.name, arguments: { [tool.key]: { ...tool.value, locale } },
});

test('STDIO tools carry explicit English locale through validated inputs and text results', { timeout: 15000 }, async () => {
  await withClient(async client => {
    for (const tool of tools) {
      const result = await invoke(client, tool, 'en');
      assert.notEqual(result.isError, true, tool.name);
      const payload = result.structuredContent.card ?? result.structuredContent.quiz;
      assert.equal(payload.locale, 'en', tool.name);
      assert.equal(payload.id, tool.value.id);
      const text = result.content.filter(block => block.type === 'text').map(block => block.text).join('\n');
      assert.doesNotMatch(text, /[\u3400-\u9fff]/u, tool.name);
      assert.ok(text.includes(tool.value.question ?? tool.value.explanation));
      if (tool.name === 'show_lesson') assert.match(text, /does not demonstrate mastery/);
      else assert.match(text, /confidence 1–3/);
    }
  });
});

test('STDIO Chinese learner locale keeps Chinese fallback instructions for English lesson content', { timeout: 15000 }, async () => {
  await withClient(async client => {
    for (const tool of tools) {
      const result = await invoke(client, tool, 'zh-CN');
      assert.notEqual(result.isError, true, tool.name);
      const payload = result.structuredContent.card ?? result.structuredContent.quiz;
      assert.equal(payload.locale, 'zh-CN', tool.name);
      const text = result.content[0].text;
      assert.ok(text.includes(tool.value.question ?? tool.value.explanation));
      if (tool.name === 'show_lesson') assert.match(text, /阅读完成不代表已经掌握/);
      else assert.match(text, /请同时选择把握程度/);
      assert.doesNotMatch(text, /Also select confidence|If the card is visible|Continue to practice/);
    }
  });
});

test('STDIO rejects unsupported locale for all three tools instead of silently changing language', { timeout: 15000 }, async () => {
  await withClient(async client => {
    for (const tool of tools) {
      const result = await invoke(client, tool, 'fr-FR');
      assert.equal(result.isError, true, tool.name);
      assert.equal(result.structuredContent, undefined, tool.name);
      assert.match(result.content[0].text, /locale/);
    }
  });
});

test('English locale survives server-to-app-to-host submission without translating the learner answer', { timeout: 15000 }, async () => {
  await withClient(async client => {
    const result = await invoke(client, tools[1], 'en');
    const received = [];
    const bridge = new AppBridge(null, { name: 'locale-test-host', version: '1' }, { message: { text: {} } });
    bridge.onmessage = async message => { received.push(message); return {}; };
    const app = new App({ name: 'locale-test-card', version: '1' }, {}, { autoResize: false });
    const [hostTransport, appTransport] = InMemoryTransport.createLinkedPair();
    const original = '  ‘ve known her\n我是在练习英文，不要替我改写。  ';
    try {
      await bridge.connect(hostTransport); await app.connect(appTransport);
      await submitResponse(app, result.structuredContent.card, { text: original, confidence: 2 });
    } finally { await app.close(); await bridge.close(); }
    assert.equal(received.length, 1);
    assert.equal(received[0].role, 'user');
    const message = received[0].content[0].text;
    assert.ok(message.includes(`My answer:\n${original}\nConfidence: 2`));
    assert.match(message, /give feedback in English/);
    assert.doesNotMatch(message, /请用中文继续|并用中文反馈/);
    assert.ok(message.includes(exercise.id));
  });
});
