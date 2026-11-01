import { z } from 'zod';
import { resolveLocale, messages } from './locale.mjs';

const locale = z.enum(['en', 'zh-CN']).optional().describe('Learner UI language, independent of the language being studied. Set explicitly when known.');

const text = max => z.string().trim().min(1).max(max);
const content = max => z.string().max(max).refine(value => value.trim().length > 0, 'Content cannot be blank');
const item = z.strictObject({ id: text(32), text: content(2000) });
const base = { locale, id: text(160), title: text(160), question: content(6000), collectConfidence: z.boolean().default(true) };
function unique(items, ctx, path) {
  for (const key of ['id', 'text']) {
    if (new Set(items.map(value => value[key])).size !== items.length) {
      ctx.addIssue({ code: 'custom', path: [path], message: `Each ${key} must be unique` });
    }
  }
}
export const quizSchema = z.strictObject({
  ...base, lesson: z.string().trim().max(6000).optional(), options: z.array(item).min(2).max(6),
}).superRefine((value, ctx) => unique(value.options, ctx, 'options'));

export const exerciseSchema = z.discriminatedUnion('type', [
  z.strictObject({ ...base, type: z.literal('mcq'), options: z.array(item).min(2).max(6) }),
  z.strictObject({ ...base, type: z.literal('free_text') }),
  z.strictObject({ ...base, type: z.literal('numeric'), requireUnit: z.boolean().default(false) }),
  z.strictObject({ ...base, type: z.literal('cloze_passage'), passage: content(6000),
    blanks: z.array(z.strictObject({ id: z.string().regex(/^[a-zA-Z0-9_-]{1,32}$/), label: text(120) })).min(2).max(8) }),
  z.strictObject({ ...base, type: z.literal('order_steps'), items: z.array(item).min(2).max(10),
    pickCount: z.number().int().min(2).max(10).optional(), monospace: z.boolean().default(false) }),
  z.strictObject({ ...base, type: z.literal('flashcard'), reference: content(6000) }),
]).superRefine((value, ctx) => {
  if (value.type === 'mcq') unique(value.options, ctx, 'options');
  if (value.type === 'order_steps') {
    unique(value.items, ctx, 'items');
    if (value.pickCount > value.items.length) ctx.addIssue({ code: 'custom', path: ['pickCount'], message: 'pickCount exceeds available items' });
  }
  if (value.type === 'cloze_passage') {
    const slots = [...value.passage.matchAll(/\{\{([^{}]+)\}\}/g)].map(match => match[1]);
    const ids = value.blanks.map(blank => blank.id);
    const malformed = /\{\{|\}\}/.test(value.passage.replace(/\{\{([^{}]+)\}\}/g, ''));
    if (malformed || new Set(ids).size !== ids.length || slots.length !== ids.length || ids.some(id => slots.filter(slot => slot === id).length !== 1)) {
      ctx.addIssue({ code: 'custom', path: ['passage'], message: 'Use each declared {{blank_id}} exactly once, with no other slots' });
    }
  }
});

export const lessonSchema = z.strictObject({
  locale, id: text(160), title: text(160), explanation: content(5000),
  example: z.strictObject({ title: text(160), text: content(5000) }).optional(),
  takeaway: content(1000).optional(),
});

export function exerciseResult(exercise) {
  const { reference, ...visible } = exercise;
  const card = { kind: 'exercise', ...visible };
  const t = messages(resolveLocale(card));
  const lines = [card.title, card.question];
  if (card.type === 'mcq') lines.push(...card.options.map(option => `${option.id}. ${option.text}`));
  if (card.type === 'cloze_passage') {
    lines.push(card.passage, ...card.blanks.map(blank => `${blank.id}: ${blank.label}`));
  }
  if (card.type === 'order_steps') lines.push(t.orderPrompt(card.pickCount ?? card.items.length), ...card.items.map(value => `${value.id}. ${value.text}`));
  if (card.type === 'numeric' && card.requireUnit) lines.push(t.unitRequired);
  if (card.collectConfidence) lines.push(t.confidenceRequired);
  lines.push(t.answerInCard);
  return {
    content: [{ type: 'text', text: lines.join('\n\n') }],
    structuredContent: { card },
    ...(reference ? { _meta: { 'closebook/reference': reference } } : {}),
  };
}

export function lessonResult(lesson) {
  const t = messages(resolveLocale(lesson));
  return {
    content: [{ type: 'text', text: [lesson.title, lesson.explanation, lesson.example && `${lesson.example.title}\n${lesson.example.text}`, lesson.takeaway, t.lessonFooter].filter(Boolean).join('\n\n') }],
    structuredContent: { card: { kind: 'lesson', ...lesson } },
  };
}

// Keep the original tool-result shape for clients using show_quiz.
export function quizResult(quiz) {
  const t = messages(resolveLocale(quiz));
  return {
    content: [{ type: 'text', text: `${quiz.lesson ? quiz.lesson + '\n\n' : ''}${quiz.question}\n${quiz.options.map(option => `${option.id}. ${option.text}`).join('\n')}\n\n${quiz.collectConfidence ? t.confidenceRequired + '\n' : ''}${t.quizFooter}` }],
    structuredContent: { quiz },
  };
}
