import { build } from 'esbuild';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { BUILD_STATE_VERSION, buildFingerprint, sha256 } from './build-state.mjs';

const root = new URL('./', import.meta.url);

// Zod exposes every translation as a namespace, which retains them all when
// bundled through the SDK. Only its optional error translations are narrowed;
// schemas, validation and protocol code are unchanged. Never patch node_modules.
export function supportedValidationLocales() {
  return {
    name: 'closebook-validation-locales',
    setup(builder) {
      builder.onLoad({ filter: /[/\\]zod[/\\]v4[/\\]locales[/\\]index\.js$/ }, args => ({
        contents: 'export { default as en } from "./en.js"; export { default as zhCN } from "./zh-CN.js";',
        loader: 'js', resolveDir: fileURLToPath(new URL('./', pathToFileURL(args.path))),
      }));
    },
  };
}

export function browserBuildOptions({ fullLocales = false } = {}) {
  return {
    bundle: true, write: false, format: 'iife', platform: 'browser', target: 'es2022',
    minify: true, legalComments: 'inline', metafile: true,
    plugins: fullLocales ? [] : [supportedValidationLocales()],
  };
}

export async function buildCard({ directory = root } = {}) {
  const fingerprint = await buildFingerprint(directory);
  const bundle = await build({
    ...browserBuildOptions(),
    absWorkingDir: fileURLToPath(directory),
    entryPoints: [fileURLToPath(new URL('ui/app.mjs', directory))],
  });
  const template = await readFile(new URL('ui/card.html', directory), 'utf8');
  const script = bundle.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');
  const html = template.replace('/* APP_BUNDLE */', () => script);
  if (fingerprint !== await buildFingerprint(directory)) {
    throw new Error('UI sources changed during the build. Run the build again.');
  }
  await mkdir(new URL('dist/', directory), { recursive: true });
  await writeFile(new URL('dist/card.html', directory), html);
  const report = {
    buildStateVersion: BUILD_STATE_VERSION, buildFingerprint: fingerprint, htmlSha256: sha256(html),
    htmlBytes: Buffer.byteLength(html), javascriptBytes: Buffer.byteLength(script),
    validationLocales: ['en', 'zh-CN'],
    inputs: Object.entries(Object.values(bundle.metafile.outputs)[0].inputs)
      .map(([path, value]) => ({ path, bytes: value.bytesInOutput })).sort((a, b) => b.bytes - a.bytes),
  };
  await writeFile(new URL('dist/bundle-report.json', directory), JSON.stringify(report, null, 2) + '\n');
  console.error(`Built closebook MCP UI (${report.htmlBytes} bytes; report: dist/bundle-report.json).`);
  return html;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) await buildCard();
