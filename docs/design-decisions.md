# Design decisions

Defaults chosen where the brief left room. Each can be revisited; the reason is stated so a change can be argued against it.

| # | Decision | Reason |
|---|---|---|
| 1 | Name `closebook`; installable package lives in `skills/closebook/` | Folder name must equal `name` (spec + Claude upload). The `skills/<name>/` layout also matches Claude Code plugins and leaves room for more skills. |
| 2 | Unit tests in repo-level `tests/`, not `scripts/tests/` | Keeps the uploadable package small and free of test files; Gemini uploads reject stray binary files such as `.pyc`. |
| 3 | Instruction files written in English; examples in both Chinese and English; replies follow the learner's language | Widest reach for an open-source repo; models follow English instructions reliably on all three platforms; bilingual examples show the language-following behaviour. |
| 4 | Calibration (confidence collection) and difficulty tuning are **always-on mechanics** that don't count against the "≤ 2 optional methods" cap | They cost no extra round trips and run inside the core loop; counting them would push out methods that need dedicated turns (Feynman, self-explanation). |
| 5 | Elaborative interrogation excluded for pure factual points, with the research caveat stated | Brief says so; Dunlosky et al. (2013) found some benefit for facts, so the reference says so honestly and routes "facts with a real why" through a secondary conceptual type. |
| 6 | Self-explanation allowed for procedural points; Feynman not | The brief defines self-explanation as "explain worked examples or code"; Feynman on procedures skips step-level reasoning. |
| 7 | New points start in box 0; the first pass moves them to box 1 (review tomorrow) | The first review is the most valuable; a same-session retest only shows short-term memory. |
| 8 | Only the **first scored attempt per point per day** can promote; failures always demote | A session retests the same point several times; letting each success promote would push freshly failed items out to weeks. |
| 9 | Hint policy: correct with hint 2 = fuzzy; anything after hint 3 = fail | Hint 3 shows the answer, so nothing was retrieved; hint 2 gives the structure, so recall was partial. |
| 10 | `verify_known` pass → box 2 (3 days), status `skipped_known` | Skipped content still gets a cheap check soon, without wasting tomorrow's review. |
| 11 | High-confidence error = `incorrect` with confidence 3; cleared only by a promoting pass on a later day | Matches "高信心答错" literally; partial answers at confidence 3 are fuzzy, not confident errors. |
| 12 | Exam date caps `next_review` at the day before the exam | Every point gets a last review before the exam without changing the box rules. |
| 13 | Schedule state is always **replayed from attempt history** on merge/import/record | Makes the tool deterministic and idempotent; chat-computed state that drifts from the rules is detected (`validate` warning) and fixed (`recompute`). |
| 14 | Compact export keeps **all** attempts (core fields only) rather than truncating history | Replay needs history; a 5-point topic after several sessions stays a few KB. |
| 15 | Contested points use `coherent / partly_coherent / incoherent` results, no confidence | No right answer exists; coherence still maps onto the scheduler (pass / fuzzy / fail). |
| 16 | `user_override` from the brief is stored as per-point `method_override_by_user` / `interaction_override_by_user` plus a top-level `user_overrides` log | Per-point fields answer "why was this point taught this way"; the log also covers flow-level overrides such as skipping a retest. |
| 17 | Session export format (`schemas/session-export.schema.json`) defined in phase 1 | The script must merge HTML-page exports now; the phase-2 page implements this format. |
| 18 | Validator is a small built-in JSON Schema subset; unknown fields are errors (`--lenient` makes them warnings) | Standard library only; strictness catches typos in model-written JSON, lenient mode avoids blocking a learner over an extra field. |
| 19 | Default platform level is 0 unless there is concrete evidence of more | Honesty is the top priority; claiming a UI that doesn't render is worse than plain text. |
| 20 | Interaction ids in the progress schema add `checklist` and `voice` to the 8 HTML ids | They appear in the interaction matrix but aren't HTML lesson components. |
| 21 | Subject-specific forms are new interaction types (`numeric`, `order_steps`, `cloze_passage`, `code_trace`, `terminal`, `graph`) plus a parameter-lab `simulation`; subject is a starting point, never a replacement for the knowledge-type fit | Keeps the decision chain intact: a history point that is contested still gets open argument. One form per subject would have hidden that. |
| 22 | Every subject form makes the learner commit first: a typed value, a prediction, or slider values with their own curve hidden until checked | Sliding until two curves overlap, or reading the answer off a visible graph, is guessing, not recall. |
| 23 | Formulas use a small built-in expression grammar, mirrored in `build_lesson.py`, instead of `eval` | Lesson data is model-written; nothing in it may run as code in the learner's browser. |
| 24 | The terminal accepts only listed commands, says so on the page, and lets the coach regrade a valid variant | A fake shell that pretends to run commands would mislead; an honest exact-match check is still useful retrieval practice. |
| 25 | Image hotspots and audio are left out | They need external images or microphone access; the page is offline and self-contained. |
