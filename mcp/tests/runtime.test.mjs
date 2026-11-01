import test from 'node:test';
import assert from 'node:assert/strict';
import { build } from 'esbuild';
import { cp, mkdir, mkdtemp, readFile, rm, stat, symlink, utimes, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { runInNewContext } from 'node:vm';
import { webcrypto } from 'node:crypto';
import { browserBuildOptions, buildCard } from '../build.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const initialize = { jsonrpc: '2.0', id: 1, method: 'initialize', params: {
  protocolVersion: '2025-11-25', capabilities: {}, clientInfo: { name: 'startup-test', version: '1' },
} };

async function isolatedRuntime(t, { brokenBuild = false } = {}) {
  const directory = await mkdtemp(join(dirname(root), '.runtime-test-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  // Share installed dependencies, but never move or remove the working build.
  await symlink(join(root, 'node_modules'), join(directory, 'node_modules'), 'dir');
  for (const name of ['server.mjs', 'cards.mjs', 'package.json', 'package-lock.json', '.npmrc', 'locale.mjs', 'build-state.mjs']) {
    try { await cp(join(root, name), join(directory, name)); }
    catch (error) { if (name !== 'locale.mjs' || error.code !== 'ENOENT') throw error; }
  }
  if (!brokenBuild) {
    await cp(join(root, 'build.mjs'), join(directory, 'build.mjs'));
    await cp(join(root, 'ui'), join(directory, 'ui'), { recursive: true });
  }
  return directory;
}

async function handshake(command, args, directory) {
  const child = spawn(command, args, { cwd: directory, stdio: ['pipe', 'pipe', 'pipe'] });
  const closed = once(child, 'close');
  let stdout = '', stderr = '', pending = '';
  const timeout = setTimeout(() => child.kill('SIGKILL'), 12000);
  try {
    const result = await new Promise((resolve, reject) => {
      child.on('error', reject);
      child.once('close', code => reject(new Error(`Exited before handshake (${code}): ${stderr}\n${stdout}`)));
      child.stderr.on('data', data => { stderr += data; });
      child.stdout.on('data', data => {
        stdout += data; pending += data;
        while (pending.includes('\n')) {
          const index = pending.indexOf('\n'), line = pending.slice(0, index);
          pending = pending.slice(index + 1);
          if (!line.trim()) continue;
          let message;
          try { message = JSON.parse(line); }
          catch { reject(new Error(`Non-protocol stdout: ${line}`)); return; }
          if (message.id === 1) resolve(message);
        }
      });
      child.stdin.write(JSON.stringify(initialize) + '\n');
    });
    return { result, stdout, stderr };
  } finally {
    clearTimeout(timeout);
    child.stdin.end();
    // Closing stdin ends the Node transport and npm's foreground child.
    const killer = setTimeout(() => child.kill('SIGKILL'), 3000);
    await closed;
    clearTimeout(killer);
  }
}

test('fresh checkout: direct STDIO startup builds missing UI without protocol noise', { timeout: 20000 }, async t => {
  const directory = await isolatedRuntime(t);
  const { result, stdout, stderr } = await handshake(process.execPath, ['server.mjs', '--stdio'], directory);
  assert.equal(result.result.serverInfo.name, 'closebook-mcp');
  assert.match(stderr, /building it before startup/);
  assert.ok(stdout.split('\n').filter(Boolean).every(line => JSON.parse(line).jsonrpc === '2.0'));
  assert.match(await readFile(join(directory, 'dist/card.html'), 'utf8'), /ui\/message/);
});

test('fresh checkout: npm start also builds and keeps stdout exclusively JSON-RPC', { timeout: 20000 }, async t => {
  const directory = await isolatedRuntime(t);
  const { result } = await handshake(process.platform === 'win32' ? 'npm.cmd' : 'npm', ['start'], directory);
  assert.equal(result.result.serverInfo.name, 'closebook-mcp');
  assert.ok((await readFile(join(directory, 'dist/card.html'), 'utf8')).length > 0);
});

test('existing UI is rebuilt after source content changes even when its timestamp is unchanged', { timeout: 20000 }, async t => {
  const directory = await isolatedRuntime(t);
  await buildCard({ directory: pathToFileURL(directory + '/') });
  const previous = JSON.parse(await readFile(join(directory, 'dist/bundle-report.json'), 'utf8'));
  const source = join(directory, 'ui/card.html'), before = await stat(source);
  await writeFile(source, (await readFile(source, 'utf8')) + '\n<!-- source freshness probe -->\n');
  await utimes(source, before.atime, before.mtime);
  const { stderr } = await handshake(process.execPath, ['server.mjs', '--stdio'], directory);
  assert.match(stderr, /outdated; building/);
  assert.match(await readFile(join(directory, 'dist/card.html'), 'utf8'), /source freshness probe/);
  const current = JSON.parse(await readFile(join(directory, 'dist/bundle-report.json'), 'utf8'));
  assert.notEqual(current.buildFingerprint, previous.buildFingerprint);
});

test('dependency lock changes invalidate an existing build', { timeout: 20000 }, async t => {
  const directory = await isolatedRuntime(t);
  await buildCard({ directory: pathToFileURL(directory + '/') });
  const previous = JSON.parse(await readFile(join(directory, 'dist/bundle-report.json'), 'utf8'));
  const lock = join(directory, 'package-lock.json');
  await writeFile(lock, (await readFile(lock, 'utf8')) + '\n');
  const { stderr } = await handshake(process.execPath, ['server.mjs', '--stdio'], directory);
  assert.match(stderr, /outdated; building/);
  const current = JSON.parse(await readFile(join(directory, 'dist/bundle-report.json'), 'utf8'));
  assert.notEqual(current.buildFingerprint, previous.buildFingerprint);
});

test('matching prebuilt UI starts with only production dependencies and never imports esbuild', { timeout: 20000 }, async t => {
  const directory = await isolatedRuntime(t);
  await buildCard({ directory: pathToFileURL(directory + '/') });
  const report = await readFile(join(directory, 'dist/bundle-report.json'), 'utf8');
  await rm(join(directory, 'node_modules'));
  await mkdir(join(directory, 'node_modules'));
  const { dependencies } = JSON.parse(await readFile(join(directory, 'package.json'), 'utf8'));
  for (const name of Object.keys(dependencies)) {
    const target = join(directory, 'node_modules', name);
    await mkdir(dirname(target), { recursive: true });
    await symlink(join(root, 'node_modules', name), target, 'dir');
  }
  const probe = spawn(process.execPath, ['--input-type=module', '-e',
    "try { await import('esbuild'); process.exit(2); } catch (error) { if (error.code !== 'ERR_MODULE_NOT_FOUND') throw error; }"],
  { cwd: directory, stdio: 'pipe' });
  const [code] = await once(probe, 'close');
  assert.equal(code, 0, 'esbuild must genuinely be unavailable to this runtime');
  const { result, stderr } = await handshake(process.execPath, ['server.mjs', '--stdio'], directory);
  assert.equal(result.result.serverInfo.name, 'closebook-mcp');
  assert.doesNotMatch(stderr, /building/);
  assert.equal(await readFile(join(directory, 'dist/bundle-report.json'), 'utf8'), report);
});

test('HTTP startup fails clearly before announcing health when UI cannot be built', { timeout: 15000 }, async t => {
  const directory = await isolatedRuntime(t, { brokenBuild: true });
  const child = spawn(process.execPath, ['server.mjs', '--http'], {
    cwd: directory, env: { ...process.env, PORT: '0' }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let stdout = '', stderr = '';
  child.stdout.on('data', data => { stdout += data; });
  child.stderr.on('data', data => { stderr += data; });
  const [code] = await once(child, 'close');
  assert.equal(code, 1);
  assert.equal(stdout, '');
  assert.match(stderr, /npm ci.*npm run build/);
  assert.doesNotMatch(stderr, /closebook MCP: http/);
});

test('trimmed browser SDK preserves validation and an official App/AppBridge message round trip', { timeout: 15000 }, async () => {
  const source = `
    import { z } from 'zod';
    import { App, McpUiMessageRequestSchema } from '@modelcontextprotocol/ext-apps';
    import { AppBridge } from '@modelcontextprotocol/ext-apps/app-bridge';
    import { InMemoryTransport } from '@modelcontextprotocol/client';
    globalThis.probe = async () => {
      z.config(z.locales.en());
      const englishError = z.string().min(2).safeParse('').error.issues[0].message;
      z.config(z.locales.zhCN());
      const chineseError = z.string().min(2).safeParse('').error.issues[0].message;
      const malformed = McpUiMessageRequestSchema.safeParse({ method: 'ui/message', params: { role: 42, content: [] } });
      const valid = McpUiMessageRequestSchema.safeParse({ method: 'ui/message', params: { role: 'user', content: [{ type: 'text', text: '原始 answer' }] } });
      const received = [];
      const bridge = new AppBridge(null, { name: 'bundle-test-host', version: '1' }, { message: { text: {} } });
      bridge.onmessage = async message => { received.push(message); return {}; };
      const app = new App({ name: 'bundle-test-app', version: '1' }, {}, { autoResize: false });
      const [host, client] = InMemoryTransport.createLinkedPair();
      try {
        await bridge.connect(host); await app.connect(client);
        await app.sendMessage({ role: 'user', content: [{ type: 'text', text: '  −1/2 ‘ve known  ' }] });
        return { englishError, chineseError, malformed: malformed.success, valid: valid.success, received };
      } finally { await app.close(); await bridge.close(); }
    };
  `;
  const output = await build({ ...browserBuildOptions(), stdin: { contents: source, resolveDir: root, sourcefile: 'sdk-validation-probe.mjs' } });
  const context = { console, setTimeout, clearTimeout, setInterval, clearInterval, TextEncoder, TextDecoder,
    URL, URLSearchParams, AbortController, AbortSignal, crypto: webcrypto, performance };
  runInNewContext(output.outputFiles[0].text, context);
  const result = await context.probe();
  assert.equal(result.malformed, false);
  assert.equal(result.valid, true);
  assert.match(result.englishError, /Too small/);
  assert.match(result.chineseError, /[\u3400-\u9fff]/);
  assert.equal(result.received.length, 1);
  assert.equal(result.received[0].content[0].text, '  −1/2 ‘ve known  ');
});
