import { App, applyDocumentTheme, applyHostStyleVariables } from '@modelcontextprotocol/ext-apps';
import { createCardUI } from './render.mjs';

const app = new App({ name: 'closebook learning cards', version: '0.3.0' });
const ui = createCardUI(document, app);
function theme(ctx) {
  ui.setHostLocale(ctx?.locale);
  if (ctx?.theme) applyDocumentTheme(ctx.theme);
  if (ctx?.styles?.variables) applyHostStyleVariables(ctx.styles.variables);
}
app.onhostcontextchanged = theme;
app.ontoolresult = ui.render;
app.onerror = () => ui.showConnectionError('connectionError');
async function connect() {
  try {
    await app.connect();
    theme(app.getHostContext()); ui.setReady(true);
  } catch {
    ui.showConnectionError('connectionFailed');
  }
}
void connect();
