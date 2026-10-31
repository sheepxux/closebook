# 07 Self-explanation (自我解释)

**Principle.** Explaining each step of a worked example or a piece of code to yourself reveals the step you only thought you understood.

## Fits / doesn't fit
- ✓ `procedural`, `conceptual`, `judgment`.
- ○ `language_production` (explain why this tense/case), `contested` (explain each step of one argument).
- ✗ `factual`.
- Preferred over Feynman for beginners and for procedures: the example gives structure, so the learner isn't explaining into a void.

## Procedure
1. Give a short worked example, code snippet or solved case (≤ ~12 lines). Number the steps or lines.
2. "Explain what each step does and *why* it's needed. Go line by line; skip nothing."
3. **Stay quiet while it's right.** Intervene only at the first wrong or empty explanation: one question pointing at that step ("Line 4: why `-I` and not plain `curl`?").
4. After the learner fixes it, let them continue from there.
5. Close with one transfer question: same principle, slightly different example.

## Example (en, procedural)
> **Coach:** Explain each line: what it does and why.
> ```
> 1  curl -I https://example.com/app.js
> 2  # → Cache-Control: max-age=31536000, immutable
> 3  curl -I -H 'If-None-Match: "abc123"' https://example.com/index.html
> 4  # → HTTP/2 304
> ```
> **Learner:** 1 fetches only headers. 2 says cache for a year. 3 sends the ETag. 4 means it changed.
> **Coach:** Lines 1–3 are right. Line 4: does 304 mean the file changed?
> **Learner:** No, not modified, so the cached copy is fine.
> **Coach:** Right. Transfer: if line 3 used an old ETag after a deploy, what status would you expect?

## Scoring
| Result | Criterion |
|---|---|
| `correct` | Every step explained with purpose, no intervention needed |
| `partial` | One intervention, fixed by the learner |
| `incorrect` | Two or more interventions, or a fix that needed the answer |
The transfer question is scored separately as a retrieval attempt.

## Progress fields
Attempts with `method: "self_explanation"`, `question_format: "explain_steps"`; intervention count can go in the attempt `note`.
