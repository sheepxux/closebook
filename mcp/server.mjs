import { createServer as createHttpServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { currentBuiltCard } from './build-state.mjs';
import { McpServer } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';
import { NodeStreamableHTTPServerTransport } from '@modelcontextprotocol/node';
import { registerAppResource, registerAppTool, RESOURCE_MIME_TYPE } from '@modelcontextprotocol/ext-apps/server';
import { z } from 'zod';
import { quizSchema, exerciseSchema, lessonSchema, exerciseResult, lessonResult, quizResult } from './cards.mjs';

export { quizSchema } from './cards.mjs';
export const MCP_VERSION = JSON.parse(await readFile(new URL('package.json', import.meta.url), 'utf8')).version;
export const RESOURCE_URI = 'ui://closebook/learning-card-v5.html';
// Empty calls retain the explicit connection-test demo. Lessons pass quiz data.
export const quiz = Object.freeze({
  id: 'python-list-length-v1',
  title: '先学一点，再试一题',
  lesson: 'Python 列表按顺序保存元素，例如 [10, 20] 有两个元素。len(列表) 返回元素的个数，不是元素的总和。',
  question: 'len([2, 4, 6]) 的结果是什么？',
  options: [
    { id: 'A', text: '2' }, { id: 'B', text: '3' },
    { id: 'C', text: '6' }, { id: 'D', text: '12' },
  ],
});

let cardHtml;
async function loadCard() {
  if (!cardHtml) cardHtml = (async () => {
    const html = await currentBuiltCard();
    if (html !== null) return html;
    console.error('closebook MCP UI is missing or outdated; building it before startup.');
    try { return await (await import('./build.mjs')).buildCard(); }
    catch (cause) {
      throw new Error('Cannot build closebook MCP UI. In the mcp directory, run npm ci (including dev dependencies), then npm run build, and restart.', { cause });
    }
  })().catch(error => { cardHtml = undefined; throw error; });
  return cardHtml;
}

export async function createServer() {
  const html = await loadCard();
  const server = new McpServer(
    { name: 'closebook-mcp', version: MCP_VERSION },
    { instructions: 'On every agent platform, discover and prefer suitable built-in teaching components/tools/plugins. These MCP cards are fallback only; being installed does not give them priority. Explicit MCP requests override this default. Teach new material with show_lesson before checks. show_exercise supports mcq, free_text, numeric, cloze_passage, order_steps and flashcard. Wait for actual user messages before grading; reading acknowledgement is not mastery. Tool success does not prove visible UI or delivered answers. Set locale to the learner\'s communication language (en or zh-CN), independent of the language being studied.' },
  );
  const annotations = { readOnlyHint: true, destructiveHint: false, openWorldHint: false, idempotentHint: true };
  const uiMeta = {
    ui: { resourceUri: RESOURCE_URI },
    'openai/outputTemplate': RESOURCE_URI,
    'openai/toolInvocation/invoking': 'Preparing learning card',
    'openai/toolInvocation/invoked': 'Learning card ready',
  };
  registerAppTool(server, 'show_lesson', {
    title: 'Teach one idea',
    description: 'Use this for a coherent teaching unit when no suitable native teaching card is available, or the learner explicitly requests closebook MCP. Arrange the explanation from course content, workload and learner responses; it may connect several points or present a complete worked example, within the field limits. Use chat if a card would fragment the explanation. The learner can continue or request another explanation. Neither action is a scored answer or evidence of mastery. Do not include an unanswered test and its solution together.',
    inputSchema: z.strictObject({ lesson: lessonSchema }), annotations, _meta: uiMeta,
  }, async ({ lesson }) => lessonResult(lesson));
  registerAppTool(server, 'show_exercise', {
    title: 'Show a closebook exercise',
    description: 'Use this as a fallback when suitable native teaching tools are unavailable, or closebook MCP is explicitly requested. Choose the form that fits learning: mcq, free_text, numeric, cloze_passage, order_steps or flashcard. Supply the actual exercise, never an unrelated demo. Teach unfamiliar material first. Do not include answer keys except flashcard reference (hidden until submission); independently verify that reference. For ordering, supply shuffled items, never the solution order. For cloze, use each {{blank_id}} once. Numeric input preserves expressions and units for chat grading. Wait for the actual submission; these cards do not auto-grade.',
    inputSchema: z.strictObject({ exercise: exerciseSchema }), annotations, _meta: uiMeta,
  }, async ({ exercise }) => exerciseResult(exercise));
  registerAppTool(server, 'show_quiz', {
    title: 'Show a closebook quiz',
    description: 'Use this when no suitable native teaching/quiz tool is available, or the user explicitly requests closebook MCP. Renders one single-choice quiz with optional confidence. For real lessons supply quiz with id, title, question and 2–6 unique options; omit lesson during closed-book retests. Do not include answers or grading keys. Empty input shows a fixed Python connectivity demo only. Wait for the learner to submit; do not infer their choice. Text-only hosts receive the same question.',
    inputSchema: z.strictObject({ quiz: quizSchema.optional() }),
    annotations, _meta: uiMeta,
  }, async ({ quiz: suppliedQuiz }) => quizResult(suppliedQuiz ?? quiz));
  registerAppResource(server, 'closebook-quiz-card', RESOURCE_URI,
    { mimeType: RESOURCE_MIME_TYPE },
    async () => ({ contents: [{
      uri: RESOURCE_URI, mimeType: RESOURCE_MIME_TYPE, text: html,
      _meta: {
        ui: { prefersBorder: true, csp: { connectDomains: [], resourceDomains: [] } },
        'openai/widgetDescription': 'Learning cards in English or Simplified Chinese: lessons, choice, writing, numbers, blanks, ordering and recall. Original responses return to chat for feedback. Reading does not count as mastery; cards do not grade answers.',
      },
    }] }),
  );
  return server;
}

export async function startHttp(port = 43129) {
  // Do not announce readiness until the UI can actually be served.
  await loadCard();
  const http = createHttpServer(async (req, res) => {
    const address = http.address();
    const hosts = new Set([`127.0.0.1:${address.port}`, `localhost:${address.port}`]);
    if (!hosts.has(req.headers.host)) { res.writeHead(403).end('Invalid host'); return; }
    if (req.headers.origin && ![...hosts].some(host => req.headers.origin === `http://${host}`)) {
      res.writeHead(403).end('Invalid origin'); return;
    }
    if (req.url === '/health' && req.method === 'GET') {
      res.writeHead(200, { 'Content-Type': 'application/json' }).end(JSON.stringify({ status: 'ok', name: 'closebook-mcp', version: MCP_VERSION }));
      return;
    }
    if (req.url !== '/mcp') { res.writeHead(404).end('Not found'); return; }
    let server, transport;
    try {
      let body;
      if (req.method === 'POST') {
        const chunks = []; let bytes = 0;
        for await (const chunk of req) {
          bytes += chunk.length;
          if (bytes > 1024 * 1024) { res.writeHead(413).end('Request too large'); return; }
          chunks.push(chunk);
        }
        try { body = JSON.parse(Buffer.concat(chunks).toString('utf8')); }
        catch { res.writeHead(400).end('Invalid JSON'); return; }
      }
      server = await createServer();
      transport = new NodeStreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
      res.on('close', () => { void transport.close().catch(() => {}); void server.close().catch(() => {}); });
      await server.connect(transport);
      await transport.handleRequest(req, res, body);
    } catch (error) {
      console.error('MCP request failed:', error.message);
      if (!res.headersSent) res.writeHead(500).end('MCP request failed');
      await transport?.close().catch(() => {});
      await server?.close().catch(() => {});
    }
  });
  await new Promise((resolve, reject) => { http.once('error', reject); http.listen(port, '127.0.0.1', resolve); });
  return http;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
  if (process.argv.includes('--http')) {
    const port = Number(process.env.PORT ?? 43129);
    if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('Invalid PORT');
    const http = await startHttp(port);
    console.error(`closebook MCP: http://127.0.0.1:${http.address().port}/mcp`);
    for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => http.close(() => process.exit(0)));
  } else {
    await (await createServer()).connect(new StdioServerTransport());
  }
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
