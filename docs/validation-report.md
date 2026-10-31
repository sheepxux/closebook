# Validation report

**Date:** 2026-10-31 · **Skill version:** 0.1.0 · **Progress schema:** 1.0
**Environment:** macOS, Python 3.9.6 (code targets 3.8+), Playwright 1.60.0 with headless Chromium.

## Summary

| Area | Result |
|---|---|
| Automated tests | 86 / 86 pass (unit, packaging and browser tests) |
| Practice page in a real browser | All spec §13 checks pass: load, answer, explanations, confidence, self-check, export, import-merge |
| Packaging | Both ZIPs build reproducibly with no development files or macOS junk |
| Behaviour evals (22 evals, 102 expectations) | First run 89 / 102 (87%), full rerun after fixes 99 / 102 (97%); later targeted reruns all pass |
| Trigger check (proxy) | 18 / 18 queries routed as expected |
| Real platform installs | **Not tested** (see the last section) |

## 1. Automated tests

```bash
python3 -m unittest discover -s tests
```

| File | Tests | Covers |
|---|---|---|
| `test_progress_tool.py` | 51 | Schema validation, Leitner scheduling (first attempt per day, fuzzy/fail, diagnostics never count, exam-date cap), replay from history, priority flags, due order, statistics and calibration, merge and import of session exports (idempotent), compact export, CLI exit codes |
| `test_build_lesson.py` | 17 | Lesson-data rules (one correct MCQ option, table and diagram blanks, analogy limits, Plain Talk length), fit warnings, `--strict`, `</script>` escaping, the example page matches a fresh build, and the template has no external requests or `innerHTML` |
| `test_skill_structure.py` | 7 | Frontmatter keys, `name` = folder, description, `SKILL.md` stays lean, every referenced file exists, all 12 methods and 4 modes present, no junk files in the skill folder |
| `test_package_skill.py` | 5 | ZIP root is `closebook/`, runtime files present, no evals or junk, the Gemini ZIP differs only by `agents/openai.yaml`, byte-identical rebuilds |
| `test_lesson_page_e2e.py` | 6 | Browser tests of the practice page, detailed in section 2 below |

## 2. Practice page (HTML)

The browser tests open [`examples/http-cache-lesson.html`](../examples/http-cache-lesson.html) and a fixture page in headless Chromium and use them like a learner would:

- **Full Chinese session.** Fill in a flow diagram (partly right) and pick a mistake cause. Answer a multiple-choice question wrong with confidence 3 and get per-option explanations. Answer a typed question wrong, then mark it "I was actually right". Answer "don't know". Complete a comparison table. Pass the teach-then-hide gate. Self-check a free-text answer against key points (partial). Do free recall and Plain Talk recall, then group and select mistakes.
- **Export and import.**
  - The export passes `progress_tool.py validate`. `import-session` merges it into an existing progress file, and a second import changes nothing.
  - The page refuses bad imports.
  - A fresh page import restores 7 / 7 answered.
  - State survives a reload.
- **Edge cases.**
  - A retry produces two attempts.
  - Keyboard-only answering works.
  - Theme switching works.
  - The 375 px layout has no horizontal overflow.
  - An unknown interaction type falls back to typed answers.
  - Blocked `localStorage` still works, with a copy/paste export.
  - Broken lesson data shows a readable error.

**Manual checks:** screenshots in light mode, dark mode, at 390 px mobile width and of the Plain Talk tab, all reviewed by eye ([example](images/lesson-page.jpg)).

**Not possible:** the Cursor IDE browser cancels scripted clicks, so all interaction testing used Playwright.

## 3. Packaging

`python3 tools/package_skill.py` builds:

| ZIP | Files | Size |
|---|---|---|
| `dist/closebook.zip` | 39 | 110.9 KB |
| `dist/closebook-gemini.zip` | 38 (no `agents/`) | 110.7 KB |

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

## 7. Not verified

- **Real installs on any platform:**
  - uploading `dist/closebook.zip` to claude.ai or ChatGPT
  - uploading `dist/closebook-gemini.zip` to Gemini Apps
  - installing in Claude Code, Codex or Gemini CLI

  The install paths come from official documentation checked on 2026-10-31 ([log](platform-verification.md)), not from trying them.
- **Each platform's real trigger behaviour.** Only the proxy above was run.
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
