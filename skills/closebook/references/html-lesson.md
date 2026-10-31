# HTML lesson page (Level 2)

A single self-contained page the learner opens in a browser: questions, confidence, explanations after answering, error list, free recall, Plain Talk, export and import. You only write the lesson **data** (JSON); the page logic in `assets/lesson-template.html` is fixed.

## When to build one

Only when it clearly pays off (see `interaction-fit.md`): the learner wants an offline or reusable practice page, a review deck of 8+ MCQ/flashcard items, or a form text can't express well (`diagram_fill`, `simulation`, `graph`, `code_trace`, `terminal`, `order_steps`). The chat stays the main channel: the page can't grade free text by itself, so written answers come back to you for grading (see below). If unsure, don't build it.

## How to produce the page

Pick the first route that works in this environment:

1. **You can run Python:** write `lesson.json`, then
   `python3 scripts/build_lesson.py lesson.json --out <topic-slug>.html`
   It validates the data (schema + per-type rules + fit warnings) and injects it. Fix every error; read every warning.
2. **You can create files but not run code:** copy `assets/lesson-template.html` unchanged and replace only the contents of `<script type="application/json" id="lesson-data">…</script>`. Escape every `</` inside the JSON as `<\/`.
3. **You can only type text into the chat:** don't build the page. The template is ~135 KB; retyping it costs a lot and one slip breaks it. Stay at Level 0/1.

Never edit, shorten or "improve" the page logic. Never add external scripts, fonts or images.

## Writing the lesson data

Schema: `schemas/lesson-data.schema.json`. Complete examples: the template's built-in demo (English), `schemas/examples/lesson.http-cache.json` (Chinese, uses every core form plus free recall and Plain Talk) and `schemas/examples/lesson.subjects.json` (Chinese, one subject-specific form per point: numbers, ordering, cloze, code tracing, terminal, graphs, parameter lab).

- `lesson_id`: letters, digits, `-`, `_` (e.g. `http-cache-2026-10-31`). The page keys saved answers by it, and its exports refuse to merge into a different lesson.
- `topic` must equal the progress file's `topic` so the export merges cleanly. Reuse the progress file's knowledge-point ids.
- `language`: the learner's language (`zh-CN`, `en`, …). UI labels follow it (Chinese for `zh*`, English otherwise).
- `mode`: `learn` (attempts recorded as `retest`) or `review` (recorded as `review`).
- Per knowledge point, the chain still applies: `knowledge_type` → `method` → `interaction_type` (one of `mcq`, `flashcard`, `free_text`, `plain_qa`, `compare_table_fill`, `timeline_fill`, `diagram_fill`, `simulation`, `numeric`, `order_steps`, `cloze_passage`, `code_trace`, `terminal`, `graph`; subject defaults in `interaction-fit.md`). `interaction_reason` is one sentence **to the learner** saying why this form helps here.
- `teach` only for points on entry path B (new to the learner). The page shows it step by step, then hides it before the questions.
- 1–3 `items` per point. Item rules:
  - `mcq`: exactly one correct option; every option has an `explanation` (why it's wrong, naming the misconception). No "all of the above".
  - `flashcard`: atomic `front`/`back`. Only for factual points.
  - `plain_qa`: `question` + `answer`. Add `accept` (exact variants) only when the answer is short and checkable; otherwise the learner self-grades against `answer`.
  - `free_text`: `prompt` + `reference_points`, marking the required ones (`required: true`). This is the checklist from `question-design.md`.
  - `compare_table_fill` / `timeline_fill` / `diagram_fill`: blanks with `accept` variants; the learner can override a mismatch with "count as right".
  - `numeric`: `question`, `value`, `unit`, and `tolerance` (absolute) or `tolerance_pct` when rounding is expected; without them the number must match exactly. Always add `solution` (worked steps). The learner may type `3/4`, `2*pi`, `1,100` or `25%`.
  - `order_steps`: `prompt` + `steps` in the right order (3+). `distractors` for Parsons problems (one per real misconception, e.g. a wrongly indented `return`); `monospace: true` for code; `layout: "tiles"` for word order. If several orders are right, list them in `alternatives`. All items must differ.
  - `cloze_passage`: `prompt` + `text` with blanks written `[[answer|variant|variant]]`. `bank: true` shows the answers as a word bank (add 1–2 `bank_extra` wrong words); without a bank it's pure recall.
  - `code_trace`: `prompt`, `language`, `code`, 1–3 prediction `questions` (short exact answers, with `accept` variants), and a `trace`: one entry per executed line with `line`, the `vars` changed by that line and any `out`. Keep it short (≤ 15 steps); check every step by hand.
  - `terminal`: `prompt`, optional `setup` (earlier session text) and `shell_prompt`, and `commands`: one `task` per step with every valid spelling in `accept` (whitespace is normalised, case matters) and the scripted `output`. List the common variants (`git add .` / `git add -A`); a missing variant marks a right answer wrong. The page says it's a simulation.
  - `graph`: `prompt`, `expr` (y in terms of x and the params), `params` (sliders: `name`, `min`, `max`, `step`, `value`), `x_range`, `y_range`, and exactly one task: `target` (param values for a dashed curve the learner must reproduce; their own curve stays hidden until the first check) or `predict` (a multiple-choice prediction; sliders unlock after it).
  - `simulation`: a parameter lab: `prompt`, `params`, `outputs` (readouts: `label`, `expr`, `unit`, `digits`) and/or `plot`, and a required `predict` question; sliders and plot unlock after the prediction. Add a `fallback` plain question for chats and older pages. Without `params`, the page shows only the `fallback`.
  - Expressions (`expr`, `outputs[].expr`): numbers, the param names, `x`, `+ - * / ^`, parentheses, `pi`, `e`, and `sin cos tan asin acos atan sqrt abs exp ln log floor ceil round min max pow`. Nothing else is evaluated; `build_lesson.py` rejects anything outside this grammar.
- `free_recall` (optional): a prompt plus reference points tagged with `kp_id`. Results are recorded per point with phase `synthesis`.
- `plain_talk` (optional): only when Plain Talk was requested or accepted. Follow `plain-talk.md`: every `analogy` needs `analogy_limit`; factual points use `no_analogy_reason` instead. `recall` is required and is the only part that counts toward mastery.

## Telling the learner

Two or three sentences, no more: what's in the page, that written answers are **self-checked** in the page, and that for your grading they export "my answers" and paste them here; you reply with a grading block they paste back into the page. Also: press **Export** at the end and paste the progress back here. The page tries to keep answers in the browser, but export is the reliable copy.

## When the export comes back

The export has `"format": "closebook-session-export"`.
- **Files available:** `python3 scripts/progress_tool.py import-session <progress.json> <export.json>`; it validates, adds missing points from the export, skips attempts already imported, and replays the schedule.
- **Chat only:** append the attempts to the matching knowledge points in the pasted progress JSON (skip ids already present), then recompute boxes and review dates by the rules in `spaced-repetition.md`.
- Self-checked results keep `self_assessed: true` until you grade them.
- High-confidence errors from the page go to the top of the next review, as usual.

## When "my answers" come back: grade them

The learner pastes a Markdown list that starts with `# closebook ·`; every answer has an **ID** (the attempt id) and the learner's self-check.

1. Grade each written answer against the item's reference answer or points, using `feedback-style.md`: judge the substance, not the wording. Contested points use `coherent` / `partly_coherent` / `incoherent`.
2. In the chat, give the feedback one answer at a time, worst first; where your result differs from the self-check, say so in one sentence.
3. End the reply with one fenced `json` block the learner can paste into the page's import box (Save & load), with one line saying so. Format (`schemas/grading.schema.json`, example `schemas/examples/grading.example.json`):

   ```json
   {"format": "closebook-grading", "schema_version": "1.0", "lesson_id": "<from the answers header>", "graded_at": "<now, ISO 8601 with offset>",
    "grades": [{"attempt_id": "<ID>", "result": "partial", "feedback": "<1–2 sentences: what was right, what was missing>", "error_type": "memory_lapse"}]}
   ```

   - Only answers you actually graded; copy each ID exactly. `error_type` only for wrong or partial answers, and only if you can tell the cause.
   - Don't include answers the page checked against a key (multiple choice, matched blanks, numbers, orders, commands) unless you're correcting the page, e.g. a terminal command that was valid but missing from `accept`.
   - `feedback` must not reveal answers to questions the learner hasn't attempted yet.
4. The page marks those answers "graded by your coach", shows the feedback, and the mistakes list and export follow your results.
5. Update the progress file with the same block. **Files available:** save it and run `python3 scripts/progress_tool.py apply-grading <progress.json> <grading.json>` (import the session export first if those attempts aren't in the file yet). **Chat only:** in the progress JSON, set each attempt's `result`, add `coach_graded: true` and `note` (the feedback), drop `self_assessed`, then recompute by `spaced-repetition.md`.
