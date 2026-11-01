# closebook evals

`evals.json` follows the skill-creator format (`skill_name`, `evals[]` with `id`, `prompt`, `expected_output`, `files`, `expectations`). `files` paths are relative to the skill root. This folder is left out of the packaged ZIP.

Each prompt starts with a bracketed `[Environment: …]` preamble: the platform's capabilities, today's date and, for mid-session scenarios, a summary of earlier turns. The runner treats it as context, not as text the user typed. Each eval checks one assistant turn, including its tool calls and any follow-up after a tool result.

The suite checks both directions: that a method or form is **used where it fits** (Feynman on conceptual material, predict-first diagrams on architecture, production on language) and **not used where it doesn't** (no analogies for a glossary, no right/wrong grading on contested material, no components for a one-line fact).

| id | Scenario (spec §13) | What it checks |
|---|---|---|
| 1 | 1 · exam prep | Opening, exam date caps reviews, procedural label for calculations |
| 2 | 1 · coding | Skips the outline on request; situational predict/choose question |
| 3 | 1 · language | Production task, not recognition only; no lecture first |
| 4 | 1 · concept | Why / what-if before explaining; Feynman planned |
| 5 | 2 · summary only | One-sentence offer, no forced quiz |
| 6 | 2 · summary declined | Summarizes, doesn't push again |
| 7 | 3 · review with progress file | Due order (high-confidence error first), retest before explaining |
| 8 | 3 · review, after an answer | Correct schedule update (box 2, 2026-11-03), error resolved |
| 9 | 4 · pure glossary | Retrieval + chunking/mnemonics, flashcard/cloze, no Feynman or analogies |
| 10 | 5 · contested material | Open responses, no right/wrong, no predict-verify |
| 11 | 6 · unfit form requested | Risk in one sentence + alternative, no lecture |
| 12 | 6 · user insists | Complies, records the override |
| 13 | 7 · mixed types | Different types and methods per point |
| 14 | 8 · architecture, predict first | Text diagram with blanks, predict before showing |
| 15 | 8 · architecture, synthesis | Feynman actually used (anti-over-suppression) |
| 16 | 9 · Level 0 only | Typed answers, no pretend UI |
| 17 | 10 · one-line fact | No outline or components |
| 18 | 11 · Plain Talk, conceptual | Analogy + its limit, jargon explained, recall question |
| 19 | 11 · Plain Talk, precise definitions | Exact definitions, no forced analogy |
| 20 | 12 · zero background (teach route) | First teaching chunk only, then one check on an unseen case |
| 21 | 12 · "说人话" before learning | Plain Talk first, no quiz (at most one light recall) |
| 22 | 13 · chat export | Compact core JSON that `progress_tool.py validate` accepts |
| 23 | teach route · "教我", no material | Teach-first plan, general-knowledge note, no quiz on the topic itself |
| 24 | teach route · whole subject | Learning path in prerequisite order; today's share marked; no mega-lecture |
| 25 | teach route · missed check | Specific correction, a different angle, one new check; not scored |
| 26 | routing · "quiz me" on unseen material | Explains first, says why in one line |
| 27 | teach route · point taught | Goes on to the next point; no retest yet |
| 28 | teach route · all points taught | Explanations closed; first retest on the point taught longest ago |
| 29 | native-first · suitable built-in tool | Uses native once; no duplicate MCP display |
| 30 | explicit MCP preview | Uses requested MCP with actual content, waits without scoring |
| 31 | restricted native tool | Does not use clarification/approval input as a quiz; Chinese UI for English subject text |
| 32 | open explanation | Preserves written production when native supports only choices |
| 33 | lesson acknowledgement | Gives a fresh guided check; no scored attempt, mastery or schedule change |
| 34 | failed native display | Attempts native once, then preserves the question in the MCP fallback |
| 35 | teach route · pace asked once | Opening asks step-by-step vs by-section in the same message; no repeated setup questions |
| 36 | teach route · section pace | One reply explains the whole section (2–4 points), no check in between, one check after |
| 37 | teach route · second miss on section pace | Says it slows down; one small chunk and one check for that point only; still unscored |
| 38 | teach route · stored pace | Progress file holds `teach_pace`; no pace question; retest first, then the next planned points |
| 39 | host widget · Codex Visualize | Writes an HTML fragment that checks the four-option answer itself (key + per-option explanation inside), confidence first, `sendFollowUpMessage` result line only on Next; `visualize{...}` line in the reply |
| 40 | host widget · `show_widget` + `sendPrompt` | One `show_widget` call with a numeric widget that checks the value within a tolerance and then shows the worked steps; `sendPrompt` result line on Next; no MCP duplicate |
| 41 | host question tool · `request_user_input` | One call: three options plus a confidence question; no text duplicate; no hint at the key |
| 42 | section review widget | One `show_widget` with three keyed questions stepped inside the widget, graded there, one summary `sendPrompt` at the end |
| 43 | daily assessment page | Builds an exam-mode HTML page from the progress file's points with `build_lesson.py`; closed-book; no questions in chat |
| 44 | no renderer at all | Says so in one line, asks the section's checks in text one per reply (`B 2`) |
| 45 | assessment page without the template | Host renders HTML output but the skill has no `assets/` and no network: writes a compact exam page by hand with the export contract |

## Running

**With skill-creator** (if your environment has it): point it at this folder; it reads `evals/evals.json`.

**With the repository runner:** an authenticated Codex CLI can execute `python3 tools/run_behavior_evals.py --out /absolute/path/to/new-eval-run` from the repository root. Use a fresh output directory outside the repository. It runs all 45 cases by default; `--ids 29,30,31,32,33,34,39,40,41,42,43,44,45` selects the renderer and assessment cases. It saves raw responses and tool logs but does not replace independent grading. This uses model calls and is separate from deterministic CI.

**Without it** (how the 2026-10-31 run was done): for each eval, a fresh agent gets the skill folder, reads `SKILL.md` and only the references it routes to, and writes the next assistant reply. It never sees `evals/`. A separate grader marks every expectation pass/fail with quoted evidence. For eval 22, the grader extracts the JSON block and runs `scripts/progress_tool.py validate` on it. Results and responses: `docs/eval-results/<date>/iteration-<n>/`.

## Tool-call cases (29–34, 39–44)

These cases require executable tool doubles and recorded calls, not just a reply saying which renderer the agent would choose. Expose the names and capabilities described in each environment. Keep the test runner and expectations outside the runner's readable skill snapshot.

- `host_native.show_exercise` represents a host-provided teaching component; constrain its supported forms per case. `host_native.ask_clarification` is restricted to clarification, planning and approval.
- `closebook_card.show_exercise` uses the current card schema. A successful double reports that presentation was requested but supplies no learner answer.
- In case 33, `learning_progress.record` records an actual scored attempt and updates mastery/scheduling. Log calls so a reading acknowledgement cannot silently count as an answer.
- In case 34, the first native call must return an explicit rendering error stating that no card appeared and no answer was collected. The MCP double then succeeds. Do not tell the runner about the planned failure before it occurs.
- Case 39 has no tool double: the environment describes a Visualize-style skill, and the grader checks the created fragment file (workspace changes) and the `visualize{...}` line in the reply.
- `host_widget.show_widget` (case 40) renders HTML/SVG inline with a global `sendPrompt(text)`; grade the recorded `widget_code` for the controls, the `sendPrompt` submit and the absence of a key. `host_question.request_user_input` (case 41) follows Codex's schema: 1–3 questions, 2–3 options each.
- Case 42 grades the recorded `widget_code` of the section-review widget (three questions stepped inside, one summary send). Case 43 has no double: grade the created lesson JSON and HTML in the workspace. Case 44 has no tools at all.

Grade actual call names, order, arguments and progress writes, together with the final reply. A separate grader must see the recorded evidence and cite it. These doubles test an agent's decisions with real tool calls; they do not establish that a client's built-in UI, MCP display or desktop click path works. Real-client submission checks remain separate.

The suite now contains 45 cases. Case 45 runs on a snapshot without `assets/` and `agents/`, like the upload package. New cases need results before a behaviour change is declared validated; defining an expectation does not prove it passed. See the [2026-11-01 MCP validation report](../../../docs/mcp-hardening-validation.md) for actual tool-call evidence, original failures, targeted repairs and validation limits.

## Trigger queries

`trigger-queries.json` lists 18 requests with `should_trigger` true/false: study requests in English and Chinese, a summary of study material (should trigger the one-sentence offer), and near misses such as meeting summaries, factual questions and a teacher writing a quiz for students. The behaviour evals above assume the skill is already loaded; these queries test the description. Use them with a description optimizer if you have one, or as a routing check on each platform after installing.
