import { resolveLocale, messages } from '../locale.mjs';

function filled(value, label, t) {
  if (typeof value !== 'string' || !value.trim() || value.length > 12000) throw new Error(t.fill(label));
  return value;
}

export function responseMessage(card, response) {
  const t = messages(resolveLocale(card));
  const prefix = t.responsePrefix(card);
  if (card.kind === 'lesson') {
    if (!['continue', 'explain_again'].includes(response.action)) throw new Error(t.chooseNext);
    return `${prefix}\n${response.action === 'continue' ? t.continueMessage : t.explainMessage}\n${t.continueLanguage}`;
  }
  if (card.kind !== 'exercise') throw new Error(t.unsupportedCard);
  if (card.collectConfidence && ![1, 2, 3].includes(response.confidence)) throw new Error(t.chooseConfidence);
  let answer;
  if (response.dontKnow === true) {
    answer = t.unknownAnswer;
  } else if (card.type === 'mcq') {
    const option = card.options.find(item => item.id === response.optionId);
    if (!option) throw new Error(t.chooseAnswer);
    answer = t.choiceAnswer(option);
  } else if (card.type === 'free_text' || card.type === 'flashcard') {
    answer = t.textAnswer(filled(response.text, t.answerLabel, t));
  } else if (card.type === 'numeric') {
    answer = t.numberAnswer(filled(response.value, t.valueLabel, t));
    if (card.requireUnit) filled(response.unit, t.unitLabel, t);
    if (response.unit) answer += `\n${t.unitAnswer(filled(response.unit, t.unitLabel, t))}`;
    if (response.working) answer += `\n${t.workingAnswer(filled(response.working, t.workingLabel, t))}`;
  } else if (card.type === 'cloze_passage') {
    const blanks = response.blanks;
    if (!blanks || Object.keys(blanks).length !== card.blanks.length || Object.keys(blanks).some(id => !card.blanks.some(blank => blank.id === id))) throw new Error(t.eachBlank);
    answer = t.passageAnswer(card.passage, card.blanks.map(blank => t.blankAnswer(blank, filled(blanks[blank.id], blank.label, t))).join('\n'));
  } else if (card.type === 'order_steps') {
    const ids = response.order;
    const count = card.pickCount ?? card.items.length;
    if (!Array.isArray(ids) || ids.length !== count || new Set(ids).size !== count || ids.some(id => !card.items.some(item => item.id === id))) throw new Error(t.selectOrder(count));
    answer = t.orderAnswer(ids, ids.map((id, index) => `${index + 1}. [${id}] ${card.items.find(item => item.id === id).text}`).join('\n'));
  } else throw new Error(t.unsupportedType);
  return `${prefix}\n${t.questionInfo(card)}\n${answer}${card.collectConfidence ? `\n${t.confidenceAnswer(response.confidence)}` : ''}\n${t.feedback}`;
}

export async function submitResponse(app, card, response, options = {}) {
  const text = responseMessage(card, response);
  const result = await app.sendMessage({ role: 'user', content: [{ type: 'text', text }] }, options);
  if (result == null || result.isError) throw new Error(messages(resolveLocale(card)).notAccepted);
  return text;
}

// Compatibility with the original show_quiz API and its protocol tests.
export function answerMessage(quiz, optionId, confidence) {
  return responseMessage({ ...quiz, kind: 'exercise', type: 'mcq' }, { optionId, confidence });
}
export function submitChoice(app, quiz, optionId, options = {}) {
  const { confidence, ...requestOptions } = options;
  return submitResponse(app, { ...quiz, kind: 'exercise', type: 'mcq' }, { optionId, confidence }, requestOptions);
}
