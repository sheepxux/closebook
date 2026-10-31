# HTML lesson page (Level 2)

A single self-contained page the learner opens in a browser: questions, confidence, explanations after answering, error list, free recall, Plain Talk, export and import. You only write the lesson **data** (JSON); the page logic in `assets/lesson-template.html` is fixed.

## When to build one

Only when it clearly pays off (see `interaction-fit.md`): the learner wants an offline or reusable practice page, a review deck of 8+ MCQ/flashcard items, or a `diagram_fill` / `simulation` that text can't express. The chat stays the main channel, because the page can't grade free text. If unsure, don't build it.

## How to produce the page

Pick the first route that works in this environment:

1. **You can run Python:** write `lesson.json`, then
   `python3 scripts/build_lesson.py lesson.json --out <topic-slug>.html`
   It validates the data (schema + per-type rules + fit warnings) and injects it. Fix every error; read every warning.
2. **You can create files but not run code:** copy `assets/lesson-template.html` unchanged and replace only the contents of `<script type="application/json" id="lesson-data">…</script>`. Escape every `</` inside the JSON as `<\/`.
3. **You can only type text into the chat:** don't build the page. The template is ~75 KB; retyping it costs a lot and one slip breaks it. Stay at Level 0/1.

Never edit, shorten or "improve" the page logic. Never add external scripts, fonts or images.

## Writing the lesson data

Schema: `schemas/lesson-data.schema.json`. Complete examples: the template's built-in demo (English) and `schemas/examples/lesson.http-cache.json` (Chinese, uses every core form plus free recall and Plain Talk).

- `lesson_id`: letters, digits, `-`, `_` (e.g. `http-cache-2026-10-31`). The page keys saved answers by it, and its exports refuse to merge into a different lesson.
- `topic` must equal the progress file's `topic` so the export merges cleanly. Reuse the progress file's knowledge-point ids.
- `language`: the learner's language (`zh-CN`, `en`, …). UI labels follow it (Chinese for `zh*`, English otherwise).
- `mode`: `learn` (attempts recorded as `retest`) or `review` (recorded as `review`).
- Per knowledge point, the chain still applies: `knowledge_type` → `method` → `interaction_type` (one of `mcq`, `flashcard`, `free_text`, `plain_qa`, `compare_table_fill`, `timeline_fill`, `diagram_fill`, `simulation`). `interaction_reason` is one sentence **to the learner** saying why this form helps here.
- `teach` only for points on entry path B (new to the learner). The page shows it step by step, then hides it before the questions.
- 1–3 `items` per point. Item rules:
  - `mcq`: exactly one correct option; every option has an `explanation` (why it's wrong, naming the misconception). No "all of the above".
  - `flashcard`: atomic `front`/`back`. Only for factual points.
  - `plain_qa`: `question` + `answer`. Add `accept` (exact variants) only when the answer is short and checkable; otherwise the learner self-grades against `answer`.
  - `free_text`: `prompt` + `reference_points`, marking the required ones (`required: true`). This is the checklist from `question-design.md`.
  - `compare_table_fill` / `timeline_fill` / `diagram_fill`: blanks with `accept` variants; the learner can override a mismatch with "count as right".
  - `simulation`: the page has no simulator; always give a `fallback` plain question.
- `free_recall` (optional): a prompt plus reference points tagged with `kp_id`. Results are recorded per point with phase `synthesis`.
- `plain_talk` (optional): only when Plain Talk was requested or accepted. Follow `plain-talk.md`: every `analogy` needs `analogy_limit`; factual points use `no_analogy_reason` instead. `recall` is required and is the only part that counts toward mastery.

## Telling the learner

Two or three sentences, no more: what's in the page, that written answers are **self-checked** (not graded), and to press **Export** at the end and paste the result back here (or send "export my answers" if they want you to grade their writing). Mention that the page also tries to keep answers in the browser, but export is the reliable copy.

## When the export comes back

The export has `"format": "closebook-session-export"`.
- **Files available:** `python3 scripts/progress_tool.py import-session <progress.json> <export.json>`; it validates, adds missing points from the export, skips attempts already imported, and replays the schedule.
- **Chat only:** append the attempts to the matching knowledge points in the pasted progress JSON (skip ids already present), then recompute boxes and review dates by the rules in `spaced-repetition.md`.
- Self-checked results keep `self_assessed: true`. If the learner also pasted their written answers, grade them; where your judgment differs from their self-check, say so in one sentence and record your result instead (drop `self_assessed`).
- High-confidence errors from the page go to the top of the next review, as usual.
