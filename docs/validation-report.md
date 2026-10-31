# Validation report

**Date:** 2026-10-31 · **Skill version:** 0.1.0 · **Progress schema:** 1.0
**Environment:** macOS, Python 3.9.6 (code targets 3.8+), Playwright 1.60.0 with headless Chromium.

## Summary

| Area | Result |
|---|---|
| Automated tests | 105 / 105 pass (unit, packaging and browser tests) |
| Practice page in a real browser | All spec §13 checks pass: load, answer, explanations, confidence, self-check, export, import-merge; the coach-grading round trip works end to end; every subject-specific form (numbers, ordering, cloze, code tracing, terminal, graphs, parameter lab) is played through and its export validates |
| Packaging | Both ZIPs build reproducibly with no development files or macOS junk |
| Behaviour evals (22 evals, 102 expectations) | First run 89 / 102 (87%), full rerun after fixes 99 / 102 (97%); later targeted reruns all pass |
| Trigger check (proxy) | 18 / 18 queries routed as expected |
| Real platform installs | Codex CLI: triggered on a natural request, taught, saved valid progress, built the page from the template, and graded exported answers with a block the page accepted (section 7). Claude, ChatGPT, Gemini: **not tested** (section 8). |

## 1. Automated tests

```bash
python3 -m unittest discover -s tests
```

| File | Tests | Covers |
|---|---|---|
| `test_progress_tool.py` | 57 | Schema validation, Leitner scheduling (first attempt per day, fuzzy/fail, diagnostics never count, exam-date cap), replay from history, priority flags, due order, statistics and calibration, merge and import of session exports (idempotent), applying the coach's grading (replaces self-checks, fixes error entries, idempotent, unknown ids reported), compact export, CLI exit codes |
| `test_build_lesson.py` | 28 | Lesson-data rules (one correct MCQ option, table and diagram blanks, analogy limits, Plain Talk length), rules for the subject forms (tolerances, distinct order items, cloze blanks, trace lines inside the code, graph targets inside the slider range, one task per graph, a prediction before every parameter lab), the expression grammar (accepts arithmetic and listed functions, rejects everything else), fit warnings, `--strict`, `</script>` escaping, the example page matches a fresh build, and the template has no external requests or `innerHTML` |
| `test_skill_structure.py` | 7 | Frontmatter keys, `name` = folder, description, `SKILL.md` stays lean, every referenced file exists, all 12 methods and 4 modes present, no junk files in the skill folder |
| `test_package_skill.py` | 5 | ZIP root is `closebook/`, runtime files present, no evals or junk, the Gemini ZIP differs only by `agents/openai.yaml`, byte-identical rebuilds |
| `test_lesson_page_e2e.py` | 8 | Browser tests of the practice page, detailed in section 2 below |

## 2. Practice page (HTML)

The browser tests open [`examples/http-cache-lesson.html`](../examples/http-cache-lesson.html), [`examples/subject-widgets-lesson.html`](../examples/subject-widgets-lesson.html) and a fixture page in headless Chromium and use them like a learner would:

- **Full Chinese session.** Fill in a flow diagram (partly right) and pick a mistake cause. Answer a multiple-choice question wrong with confidence 3 and get per-option explanations. Answer a typed question wrong, then mark it "I was actually right". Answer "don't know". Complete a comparison table. Pass the teach-then-hide gate. Self-check a free-text answer against key points (partial). Do free recall and Plain Talk recall, then group and select mistakes.
- **Export and import.**
  - The export passes `progress_tool.py validate`. `import-session` merges it into an existing progress file, and a second import changes nothing.
  - The page refuses bad imports.
  - A fresh page import restores 7 / 7 answered.
  - State survives a reload.
- **Coach grading round trip.** The exported answers carry an ID per answer (filled blanks included) and ask the coach for a `closebook-grading` block. Pasting the block, even inside a Markdown code fence, applies it: each graded answer shows the coach's verdict and feedback instead of "self-checked", "I was actually right" disappears, and the mistakes list, the progress export and a reload all keep the coach's results. The export still validates and merges. Re-pasting changes nothing; unknown ids and other lessons are reported.
- **Subject forms.**
  - Numbers: `50/2 m` reads as 25 m and is right; `1,100` against 1102.5 is wrong with confidence 3, flagged, and the worked solution appears.
  - Parsons problem: lines are tapped into place, an arrow fixes the order and keyboard focus follows the moved line; distractors stay in the pool. Word tiles with a distractor score partial and show the right order.
  - Cloze: a word-bank tap fills the next blank and keeps focus; `H₂O` is accepted for 水; 3 of 4 is partial.
  - Code tracing: the trace stays hidden until the predictions are checked; stepping highlights the current line, marks the changed variable and builds the output.
  - Terminal: the scripted output appears, focus stays in the prompt, a wrong command is rejected with an honest message, a hint and "show the command" work, and the result is partial with hint level 3.
  - Graphs: the learner's curve is hidden until the first check; a near miss then a match scores partial. In predict mode the sliders unlock only after the prediction, and moving one redraws the curve.
  - Parameter lab: no graph before the prediction (it would give the answer away); readouts follow the sliders (2.01 s → 4.01 s for L = 1 → 4 m).
  - The export validates and carries the new interaction ids; "my answers" lists the typed number, the tile order, the commands (revealed ones marked), the trace predictions, the blanks and the slider values.
- **Edge cases.**
  - A retry produces two attempts.
  - Keyboard-only answering works.
  - The page opens in the light theme even when the OS is dark; "auto" follows the OS, and switching works.
  - The 375 px layout has no horizontal overflow.
  - An unknown interaction type falls back to typed answers.
  - Blocked `localStorage` still works, with a copy/paste export.
  - Broken lesson data shows a readable error.

**Manual checks:** screenshots in light mode, dark mode, at 390 px mobile width, and of every tab and interaction type (diagram, table, timeline, flashcard, multiple choice answered wrong, the mini-lesson gate, Plain Talk, Save & load, and each subject form before and after answering), all reviewed by eye ([example](images/lesson-page.jpg), [subject forms](images/subject-widgets.jpg)).

**Not possible:** the Cursor IDE browser cancels scripted clicks, so all interaction testing used Playwright.

## 3. Packaging

`python3 tools/package_skill.py` builds:

| ZIP | Files | Size |
|---|---|---|
| `dist/closebook.zip` | 42 | 141.0 KB |
| `dist/closebook-gemini.zip` | 41 (no `agents/`) | 140.7 KB |

Two consecutive builds had identical SHA-256 hashes. No `._*`, `.DS_Store` or `__pycache__` files are present in the repository or the ZIPs.

## 4. Behaviour evals

**Suite:** [`skills/closebook/evals/evals.json`](../skills/closebook/evals/evals.json), 22 evals covering every scenario in spec §13. The table that maps evals to scenarios is in the [evals README](../skills/closebook/evals/README.md).

**Method:** skill-creator wasn't available here, so its protocol was followed by hand:

- Each eval ran in a fresh agent that saw only the skill folder, the prompt and the attached files, never the expectations.
- A separate grader marked every expectation with quoted evidence and a strict burden of proof.
- For eval 22, the exported JSON was checked with the real tool: `validate` reported 0 errors, and `recompute` gave the same schedule (all three points due 2026-11-01, point 3 weak and flagged).
- Replies and grading are in [`docs/eval-results/2026-10-31/`](eval-results/2026-10-31/).

| Run | Scope | Result |
|---|---|---|
| Iteration 1 | All 22 | 89 / 102 (87%) |
| Iteration 2 | All 22, after the fixes below | 99 / 102 (97%) |
| Iteration 3 | Evals 4, 8, 17, 18, 21 | 20 / 22 |
| Iteration 4 | Evals 4, 13, 18 | 15 / 15 |

### Skill changes driven by the evals

**After iteration 1:**

| Failure | Fix |
|---|---|
| No confidence asked on a diagnostic question (eval 2) | Diagnostics with a right answer now ask for confidence 1–3. A confident wrong answer is taught with a contrast example but still never counts as an error. |
| Five glossary cards asked at once (eval 9) | A list of items to recall counts as several questions; ask one card per reply. |
| Re-argued after the user insisted on an unfit method (eval 12) | Comply without repeating the warning, then log it. |
| No visible per-point method plan for mixed material (eval 13) | The opening shows the planned approach for each point. |
| Architecture point got prose, not a diagram (eval 14) | `SKILL.md` now says structures and flows get a predict-first diagram even in plain text. |
| Extra questions after a Plain Talk recall question (eval 19) | The recall question ends the reply. |
| Plain Talk before learning came with an outline full of unexplained terms (eval 21) | Previews stay scoped to what was asked. The recall is skipped if the user said "don't quiz me yet". |

**After iteration 2:**

- Concept mode opens core points with a why or what-if question (eval 4).
- Feedback on a confident correct answer names what was right (eval 8).
- Plain Talk allows one sentence per part, two only for the analogy.
- Markdown is dropped when the environment says it isn't rendered.

**After iteration 3:**

- The anti-spoiler rule now covers outline notes and answer-format examples. In iteration 3, eval 4 leaked the answer through an outline note and eval 18 through an example answer.

### Eval-design fixes (not skill fixes)

- Evals 4 and 16 originally gave no time budget, so the correct behaviour was to ask for one, which contradicted their expectations. Both prompts now state the time ("有 30 分钟，直接开始" / "15 minutes, just start"). Their iteration-1 failures are partly due to this.
- The graders sometimes read "plain text" in the environment as "markdown doesn't render". In these evals it means interaction Level 0 (no clickable UI). Only eval 16 says nothing is rendered. Later grader prompts state this.

### Known weaknesses still observed

None of these fail an expectation in the latest runs, but they recur:

- Replies after "just start" can still carry a fairly long outline before the first question (evals 3 and 16).
- Plain Talk points tend to sit at the top of the 4–6 sentence cap.
- Outline wording can hint at the *direction* of an answer without giving it (eval 13, iteration 4).
- Short-reply limits are met inconsistently (eval 17 passed in iterations 1 and 3, failed in 2 at about 173 characters).
- Chat exports are valid but not always minimal: default values are sometimes kept.

Each eval was run once per iteration, so single passes and failures carry noise.

## 5. Trigger check (proxy)

The behaviour evals assume the skill is loaded. To test the description itself, an agent saw only the names and descriptions of four skills and routed the 18 queries in [`trigger-queries.json`](../skills/closebook/evals/trigger-queries.json): 18 / 18 matched. That includes "summarize this chapter for my exam" (should load and offer once) and near misses such as meeting summaries, factual questions and writing a quiz for students (should not load). Details: [`trigger-proxy.md`](eval-results/2026-10-31/trigger-proxy.md). This approximates routing; it is not any platform's router.

## 6. Spec §13 coverage

| Spec §13 item | Where it's checked |
|---|---|
| Exam, coding, language and concept scenarios | Evals 1–4 |
| Summary-only request | Evals 5–6, trigger query 9 |
| Return with a progress file; retest due items; correct schedule update | Evals 7–8; `test_progress_tool.py` |
| Pure glossary: no Feynman or analogies; retrieval, mnemonics, flashcards | Eval 9; `build_lesson.py` warns on factual analogies |
| Contested material: no predict-verify, no right/wrong, open responses | Eval 10; `build_lesson.py` fit warnings |
| User forces an unfit method: explain once, then comply and log | Evals 11–12 |
| Mixed types: method chosen per point | Eval 13 |
| Architecture: predict-first diagram, Feynman actually used | Evals 14–15 |
| Level 0 only: correct downgrade, no pretend UI | Evals 16, 1–15 (all chat-only) |
| One-sentence point: no component overuse | Eval 17 |
| Plain Talk: no unexplained jargon, analogy limits, recall afterwards, no forced analogies for definitions | Evals 18–19, 21 |
| Path B and "说人话" before learning | Evals 20–21 |
| Chat export: compact JSON that the script validates and can import back | Eval 22; `test_progress_tool.py` (merge, compact) |
| Python unit tests | Section 1 |
| HTML render test: load, answer, explanations, confidence, self-check, export, import-merge | Section 2 |

## 7. Hands-on run: Codex CLI

Run on 2026-10-31 with Codex CLI 0.153.4 (macOS, the maintainer's own config), using `codex exec` and `codex exec resume` for three turns in one session. The skill folder was copied to `.agents/skills/closebook/` inside a scratch git repository; `~/.codex` was not changed.

| Turn | What was sent | What happened |
|---|---|---|
| 1 | A beginner asks to really remember strong vs. revalidated HTTP caching, without naming closebook | The skill triggered on its own: Codex read `SKILL.md`, then `teaching-flow.md`, the coding mode, `method-fit.md`, `interaction-fit.md` and the method files. The reply showed a three-point route with an approach per point, a short mini-lesson, then one predict-first question with a `?` step, an answer format with placeholders and a 1–3 confidence ask. No answer was given away. |
| 2 | A wrong answer with confidence 3 | Treated as a misconception: the correct answer, why the reasoning failed, a source (RFC 9111 §4.2), then a different point first so the missed one is retested later. The progress file validated with `progress_tool.py validate` (0 errors), with the missed point due the next day. |
| 3 | "Make a page I can click through in the browser" | Codex wrote `lesson.json` and ran `build_lesson.py --strict`; the page is byte-identical to a clean build from the template. Its reply said written answers are self-checked, not auto-graded, and asked for the export to be pasted back. Codex then clicked through the page in Safari on its own (9 questions, confident-wrong flag, mistakes list, retry, reload keeps 9/9, export, re-import with no duplicates, bad JSON rejected, 390 px preview). |

A second session, with the coach-grading version of the skill, tested the other half of the round trip:

| Turn | What was sent | What happened |
|---|---|---|
| 1 | "I finished the practice page; here are my exported answers, please grade them", followed by a real export from the example page (7 answers, free recall, Plain Talk) | Codex read `html-lesson.md` and `grading.schema.json`, gave feedback worst-first, and ended with a `closebook-grading` block of 7 grades. Every id was copied exactly; the block validates. It also overturned an answer the learner had marked "I was actually right" (`--HEAD`), after checking with `curl --HEAD --version` that curl rejects it. Pasted into the page, all 7 grades applied, and the page's export still validated and merged into a progress file. |

Observations:

- Codex warned that skill descriptions were shortened to fit its context budget (many skills were installed). The skill still triggered; this is why the description front-loads its trigger words.
- Files went to the location set by the user's global `AGENTS.md`, not the scratch repository. That's expected: user instructions outrank the skill.
- Turn 3 took about 7.5 minutes, mostly Codex's own Safari check, prompted by the user's other installed skills rather than closebook.

## 8. Not verified

- **Real installs on the other platforms:**
  - uploading `dist/closebook.zip` to claude.ai or ChatGPT
  - uploading `dist/closebook-gemini.zip` to Gemini Apps
  - installing in Claude Code or Gemini CLI

  These install paths come from official documentation checked on 2026-10-31 ([log](platform-verification.md)), not from trying them. Codex CLI was run for real (section 7).
- **Trigger behaviour on the other platforms.** Codex CLI triggered on a natural request (section 7); elsewhere only the proxy above was run.
- **Level 1 native UI:** clickable options or quiz cards on Claude, ChatGPT or Gemini. The skill never assumes them.
- **Level 2 in hosted apps:**
  - whether a Claude artifact can be built from the template file, and whether `localStorage` and downloads work inside one
  - whether skill scripts can build files in ChatGPT
  - whether Canvas can be used from a skill in Gemini

  The page has copy/paste fallbacks.
- **Gemini Apps:** whether it executes the bundled Python scripts, and whether a `.yaml` file in the ZIP would be rejected.
- **The official skill-creator tooling:** not available here. The evals use its file format, but its runner and viewer were not used.
- **Other models.** Eval runners and graders were agents in this environment, and other models may behave differently. Running the suite on each target platform's own model is the most valuable next check.
- **Python versions:** the code avoids post-3.8 features, but only 3.9.6 was run.
- **Subject forms with real learners and models.** The forms were tested with hand-written lesson data. No model has yet been asked to author a lesson that uses them (for example a correct `trace` for a learner's code, or every valid spelling of a command), and their learning effect wasn't measured here; the research cited in `interaction-fit.md` is about the general technique, not about this page.
- **Not built:** image hotspots (anatomy, maps, circuit diagrams) and audio (pronunciation), because the page loads no external images and has no audio input.
