# Optional closebook MCP learning cards

Use this fallback when the host has no inline widget facility or usable question tool of its own (`host-widgets.md`), following the renderer order in `interaction-fit.md`. Plain-text teaching requires no Node.js, MCP installation or API key.

## Availability and tools

Discover the actual tools in this session and read their live schemas; namespaces vary by host. The companion server is separate from the skill ZIP. An installed skill, a configured server, a visible card and a delivered response are different facts.

| Tool | Use |
|---|---|
| `show_lesson({lesson})` | Teach one idea, with a concrete example and optional takeaway. The learner chooses to continue to a guided check or asks for another explanation. Neither action is a scored attempt or evidence of mastery. |
| `show_exercise({exercise})` | One exercise in the chosen form; the actual response returns to chat for feedback. |
| `show_quiz({quiz})` | Compatibility with the original single-choice card; prefer `show_exercise` for new lessons. An empty call is a fixed Python connection-test demo only. |

If a configured companion needs starting/reloading, use the host's supported mechanism when available. Do not reinstall or change global settings on every lesson. If unavailable, keep teaching with HTML/text; configure it when setup is requested. The host may start a registered STDIO process eagerly; renderer priority does not control process startup.

## Interface language

Pass `locale` on lessons, exercises and legacy quizzes: `zh-CN` for Simplified Chinese or `en` for English. Choose the learner's communication language, not the language being studied: an English cloze exercise for a Chinese-speaking learner still uses `locale: "zh-CN"`. Prompts, options and submitted answers keep their original text. Clients may provide a locale when it is omitted; content-language detection is only a compatibility fallback, so do not rely on it for bilingual lessons.

## Teach before testing new material

`show_lesson` takes `id`, `title`, `explanation`, optional `example: {title, text}`, and optional `takeaway`. Keep one short chunk per card, shaped by knowledge type. Use the example to demonstrate reasoning, not just list facts. On the `step` pace, `continue` leads to a fresh guided check; on `explain_again`, use a different example or smaller step. On the `section` pace (`new-learning.md` section 3), `continue` opens the next chunk's card instead, and the checks follow the whole section, one per point and one per reply. Do not record either click as mastery. Ordinary chat explanation is equally valid when a card offers no benefit.

## Exercise types

All exercises take `id`, `title`, `type`, `question`, and optional `collectConfidence` (default true). Use new IDs for new questions; retries of unchanged cards may reuse an ID. Set confidence false for contested reasoning or unscored checks when a confidence rating is not needed.

| `type` | Fields and behavior | Best fit |
|---|---|---|
| `mcq` | `options`: 2–6 distinct `{id, text}` choices; no preselection | Confusable facts, conceptual misconceptions |
| `free_text` | Multiline answer; preserves the learner's wording | Short answers, Feynman explanations, reasoning, language production |
| `numeric` | Optional `requireUnit` (default false); accepts typed value/expression, unit and optional working | Maths/physics calculations; keep fractions, minus signs and units intact |
| `cloze_passage` | `passage` with each `{{blank_id}}` exactly once; 2–8 `blanks: [{id, label}]`; labels identify slots without giving answers | Grammar, terminology in context |
| `order_steps` | 2–10 distinct `items: [{id, text}]` in scrambled display order; optional `pickCount` for distractors, optional `monospace` for code | Procedures, word order, Parsons problems; learner can select, move and remove items |
| `flashcard` | `reference` is placed in widget-only metadata and revealed only after a submitted recall attempt receives confirmation | Vocabulary and factual recall; not a substitute for conceptual teaching |

All exercises allow “I don't know.” There is no local automatic grading: the assistant judges the actual response in chat. This avoids rejecting equivalent language, expressions or sequences through an incomplete exact-match key. It also means a successful submission is not proof of a correct answer.

Keep the independently checked key and grading criteria in the coaching context. Do not send `answer`, `correct`, `value`, solution orders or other keys in exercise data. Flashcard `reference` is the sole exception: verify it before delivery, keep it out of narration and the front, and reveal only after recall. A hidden card back is a learning aid, not a secure exam boundary. For numeric questions independently calculate from the prompt; for ordering and language accept defensible alternatives. Input/schema checks do not verify educational correctness.

Closed-book exercises have no teaching-text field. Teach first in a separate chat turn or lesson card, then ask a fresh question. Do not turn open reasoning into MCQ just to use a renderer. Code tracing with an executable trace, simulated terminals, graphs, parameter labs, and voice remain in suitable native tools or the existing HTML/text routes; these MCP tools do not implement them yet.

## Submission and progress

Wait for the actual learner message. It includes a stable response ID, the question ID/type, original answer, and requested confidence. Numeric expressions and units, smart apostrophes, multiline writing, and chosen order are preserved for grading. The card does not infer the learner's answer, mark it correct, or update mastery.

Follow the same feedback and progress rules as native/text interactions. Do not record a display or lesson acknowledgement as an attempt. If a submission timed out but later arrived, deduplicate by the response ID and do not count the pasted fallback twice. If sending fails, the card keeps the answer and supplies copyable text. If UI is unavailable, use the tool's text fallback for the same question; do not silently switch to an unrelated demo.
