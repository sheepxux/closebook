import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';

const root = new URL('./', import.meta.url);
export const BUILD_STATE_VERSION = 1;

export function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

// This module deliberately has no build-tool dependency. Prebuilt deployments
// can verify their assets after npm ci --omit=dev without importing esbuild.
export async function buildFingerprint(directory = root) {
  const paths = ['build-state.mjs', 'build.mjs', 'locale.mjs', 'package.json', 'package-lock.json'];
  async function collect(relative) {
    for (const entry of await readdir(new URL(relative, directory), { withFileTypes: true })) {
      if (entry.name.startsWith('.') || entry.name.endsWith('~')) continue;
      const path = relative + entry.name;
      if (entry.isDirectory()) await collect(path + '/');
      else if (entry.isFile()) paths.push(path);
    }
  }
  await collect('ui/');
  const hash = createHash('sha256').update(`closebook-build-state:${BUILD_STATE_VERSION}\0`);
  for (const path of paths.sort()) {
    const content = await readFile(new URL(path, directory));
    hash.update(path).update('\0').update(String(content.length)).update('\0').update(content);
  }
  return hash.digest('hex');
}

export async function currentBuiltCard(directory = root) {
  try {
    const [html, rawReport] = await Promise.all([
      readFile(new URL('dist/card.html', directory), 'utf8'),
      readFile(new URL('dist/bundle-report.json', directory), 'utf8'),
    ]);
    let report;
    try { report = JSON.parse(rawReport); }
    catch { return null; }
    if (!report || report.buildStateVersion !== BUILD_STATE_VERSION || report.htmlSha256 !== sha256(html)) return null;
    return report.buildFingerprint === await buildFingerprint(directory) ? html : null;
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}
