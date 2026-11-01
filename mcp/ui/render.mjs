import { responseMessage, submitResponse } from './submission.mjs';
import { resolveLocale, normalizeLocale, messages } from '../locale.mjs';

const supportedTypes = new Set(['mcq', 'free_text', 'numeric', 'cloze_passage', 'order_steps', 'flashcard']);

// DOM-only controller: the bridge is injected so actual interactions can be
// tested without pretending a test host is the user's desktop conversation.
export function createCardUI(document, app) {
  const $ = selector => document.querySelector(selector);
  const form = $('#exercise-form'), submit = $('#submit'), status = $('#status');
  const fallback = $('#fallback'), body = $('#body'), answer = $('#answer');
  const reference = $('#reference'), unknown = $('#dont-know');
  let ready = false, state, hostLocale = normalizeLocale(app.getHostContext?.()?.locale);
  let locale = resolveLocale({}, hostLocale), t = messages(locale);
  function applyLabels(nextLocale) {
    locale = nextLocale; t = messages(locale);
    document.documentElement.lang = locale; document.title = t.pageTitle;
    for (const node of document.querySelectorAll('[data-i18n]')) node.textContent = t[node.dataset.i18n];
    for (const [index, node] of [...document.querySelectorAll('[data-confidence-label]')].entries()) node.textContent = t.confidenceChoices[index];
    fallback.setAttribute('aria-label', t.copyLabel);
    if (!state) { $('#kind').textContent = `closebook · ${t.card}`; $('h1').textContent = t.preparing; }
  }
  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function input(name, label, multiline = false) {
    const field = el(multiline ? 'textarea' : 'input');
    if (!multiline) field.type = 'text';
    field.name = name; field.maxLength = 12000;
    field.setAttribute('aria-label', label);
    const wrapper = el('label', undefined, 'field');
    wrapper.append(el('span', label), field);
    return { field, wrapper };
  }
  function readResponse() {
    return { ...state.read(), dontKnow: unknown.checked, confidence: Number(form.querySelector('input[name="confidence"]:checked')?.value) };
  }
  function sync() {
    const locked = !ready || !state || state.busy || state.sent;
    $('#continue').disabled = locked;
    $('#explain-again').disabled = locked;
    $('#answer-fields').disabled = locked || unknown.checked;
    $('#confidence').disabled = locked;
    unknown.disabled = locked;
    let valid = false;
    if (state?.card.kind === 'exercise') {
      try { responseMessage(state.card, readResponse()); valid = true; } catch { /* unfinished answer */ }
    }
    submit.disabled = locked || !valid;
  }
  function orderInput(card) {
    const selected = [], count = card.pickCount ?? card.items.length;
    const note = el('p', '', 'note'), list = el('div', undefined, 'stack'), pool = el('div', undefined, 'pool stack');
    list.setAttribute('aria-label', t.order); pool.setAttribute('aria-label', t.pool);
    if (card.monospace) { list.classList.add('monospace'); pool.classList.add('monospace'); }
    const draw = () => {
      note.textContent = t.orderCount(selected.length, count);
      list.replaceChildren(); pool.replaceChildren();
      selected.forEach((id, index) => {
        const value = card.items.find(item => item.id === id);
        const row = el('div', undefined, 'item'); row.dataset.itemId = id;
        row.append(el('span', `${index + 1}. ${value.text}`, 'item-text'));
        const moves = el('div', undefined, 'moves');
        for (const [name, label, offset] of [['up', t.up, -1], ['down', t.down, 1], ['remove', t.remove, 0]]) {
          const button = el('button', label, 'secondary'); button.type = 'button'; button.dataset.action = name;
          button.setAttribute('aria-label', t.moveItem(label, index + 1));
          button.disabled = name !== 'remove' && (index + offset < 0 || index + offset >= selected.length);
          button.addEventListener('click', () => {
            if (name === 'remove') selected.splice(index, 1);
            else [selected[index], selected[index + offset]] = [selected[index + offset], selected[index]];
            draw(); sync();
            const focusTarget = [...list.children].find(row => row.dataset.itemId === id)?.querySelector('button:not(:disabled)') || pool.querySelector('button');
            focusTarget?.focus();
          });
          moves.append(button);
        }
        row.append(moves); list.append(row);
      });
      for (const item of card.items.filter(item => !selected.includes(item.id))) {
        const button = el('button', `${item.id}. ${item.text}`, 'secondary');
        button.type = 'button'; button.dataset.itemId = item.id; button.disabled = selected.length >= count;
        button.addEventListener('click', () => {
          selected.push(item.id); draw(); sync();
          (pool.querySelector('button:not(:disabled)') || list.querySelector('button:not(:disabled)'))?.focus();
        });
        pool.append(button);
      }
    };
    answer.append(note, list, el('p', t.pool, 'note'), pool); draw();
    return () => ({ order: [...selected] });
  }
  function exerciseInput(card) {
    if (card.type === 'mcq') {
      const choices = el('div', undefined, 'choices');
      for (const option of card.options) {
        const label = el('label', undefined, 'choice'), radio = el('input');
        radio.type = 'radio'; radio.name = 'answer'; radio.value = option.id;
        label.append(radio, el('span', `${option.id}. ${option.text}`, 'preserve')); choices.append(label);
      }
      answer.append(choices);
      return () => ({ optionId: answer.querySelector('input:checked')?.value });
    }
    if (card.type === 'free_text' || card.type === 'flashcard') {
      const { field, wrapper } = input('response', card.type === 'flashcard' ? t.recallPrompt : t.writtenPrompt, true);
      answer.append(wrapper);
      return () => ({ text: field.value });
    }
    if (card.type === 'numeric') {
      const value = input('value', t.valueLabel), unit = input('unit', card.requireUnit ? t.requiredUnit : t.optionalUnit);
      value.field.placeholder = t.expression;
      const row = el('div', undefined, 'numeric-row'); row.append(value.wrapper, unit.wrapper);
      const working = input('working', t.optionalWorking, true);
      answer.classList.add('stack'); answer.append(row, working.wrapper);
      return () => ({ value: value.field.value, unit: unit.field.value, working: working.field.value });
    }
    if (card.type === 'cloze_passage') {
      const passage = el('div', undefined, 'passage'), fields = new Map();
      let end = 0;
      for (const match of card.passage.matchAll(/\{\{([^{}]+)\}\}/g)) {
        passage.append(document.createTextNode(card.passage.slice(end, match.index)));
        const blank = card.blanks.find(blank => blank.id === match[1]);
        const field = el('input'); field.type = 'text'; field.name = blank.id; field.maxLength = 12000;
        field.className = 'inline-blank'; field.placeholder = blank.label; field.setAttribute('aria-label', blank.label);
        fields.set(blank.id, field); passage.append(field); end = match.index + match[0].length;
      }
      passage.append(document.createTextNode(card.passage.slice(end))); answer.append(passage);
      return () => ({ blanks: Object.fromEntries([...fields].map(([id, field]) => [id, field.value])) });
    }
    if (card.type === 'order_steps') return orderInput(card);
    throw new Error(t.unsupportedType);
  }
  function render(result) {
    const data = result.structuredContent;
    const source = data?.card ?? (data?.quiz && { ...data.quiz, kind: 'exercise', type: 'mcq' });
    const card = source && { ...source, locale: resolveLocale(source, hostLocale ?? app.getHostContext?.()?.locale) };
    if (!card || !['lesson', 'exercise'].includes(card.kind) || (card.kind === 'exercise' && !supportedTypes.has(card.type))) {
      showError(t.invalidContent); return;
    }
    const privateReference = result._meta?.['closebook/reference'];
    const signature = JSON.stringify([source, privateReference]);
    if (state?.signature === signature) return;
    state = { card, signature, privateReference, sent: false, busy: false, read: () => ({}) };
    applyLabels(card.locale);
    form.reset(); answer.replaceChildren(); answer.className = '';
    body.replaceChildren(); reference.replaceChildren(); reference.hidden = true;
    fallback.value = ''; fallback.hidden = true;
    $('h1').textContent = card.title;
    $('#kind').textContent = `closebook · ${card.kind === 'lesson' ? t.lesson : t.kinds[card.type]}`;
    form.hidden = card.kind !== 'exercise'; $('#lesson-actions').hidden = card.kind !== 'lesson';
    if (card.kind === 'lesson') {
      body.append(el('p', card.explanation, 'preserve'));
      if (card.example) {
        const example = el('section', undefined, 'example');
        example.append(el('h2', card.example.title), el('p', card.example.text, 'preserve')); body.append(example);
      }
      if (card.takeaway) body.append(el('p', card.takeaway, 'preserve'));
      body.append(el('p', t.nextCheck, 'note'));
    } else {
      if (card.lesson) body.append(el('p', card.lesson, 'preserve')); // legacy connectivity demo
      $('#question').textContent = card.question;
      $('#confidence').hidden = !card.collectConfidence;
      submit.textContent = card.type === 'flashcard' && privateReference ? t.submitFlip : t.submit;
      if (card.type === 'flashcard' && !privateReference) body.append(el('p', t.laterReference, 'note'));
      try { state.read = exerciseInput(card); }
      catch { showError(t.incomplete); return; }
    }
    status.textContent = ready ? '' : t.connecting;
    sync();
  }
  async function send(response) {
    const active = state;
    if (!ready || !active || active.busy || active.sent) return;
    let message;
    try { message = responseMessage(active.card, response); }
    catch (error) { status.textContent = error.message; return; }
    active.busy = true; sync(); status.textContent = t.sending;
    try {
      await submitResponse(app, active.card, response, { signal: AbortSignal.timeout(15000) });
      if (state !== active) return;
      active.sent = true; submit.textContent = t.submitted; fallback.hidden = true;
      status.textContent = t.sent;
      if (active.card.type === 'flashcard' && active.privateReference) {
        reference.append(el('h2', t.reference), el('p', active.privateReference, 'preserve'), el('p', t.referenceNote, 'note'));
        reference.hidden = false;
      }
    } catch {
      if (state !== active) return;
      status.textContent = t.unconfirmed;
      fallback.value = message; fallback.hidden = false;
    } finally {
      active.busy = false;
      if (state === active) sync();
    }
  }
  function showError(message) { ready = false; status.textContent = message; sync(); }
  form.addEventListener('input', sync); form.addEventListener('change', sync);
  form.addEventListener('submit', event => { event.preventDefault(); if (!submit.disabled) void send(readResponse()); });
  $('#continue').addEventListener('click', () => void send({ action: 'continue' }));
  $('#explain-again').addEventListener('click', () => void send({ action: 'explain_again' }));
  applyLabels(locale); status.textContent = t.connecting; sync();
  return {
    render, showError,
    showConnectionError(key) { showError(t[key]); },
    setHostLocale(value) {
      hostLocale = normalizeLocale(value) ?? hostLocale;
      // Keep a card's language stable while the learner is answering. The next
      // card uses the updated host preference unless its own locale is explicit.
      if (!state) { applyLabels(resolveLocale({}, hostLocale)); status.textContent = ready ? t.preparing : t.connecting; }
    },
    setReady(value) { ready = value; status.textContent = value ? (state ? '' : t.preparing) : t.connecting; sync(); },
  };
}
