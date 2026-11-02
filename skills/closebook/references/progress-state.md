# Progress state: storage, updates, export

The progress file lets learning continue across sessions and platforms. No platform's cross-chat memory is reliable enough to depend on, so the learner owns a JSON file.

- Schema: `schemas/progress.schema.json` (`schema_version` "1.0"). Fields are tagged `x-tier: core` or `x-tier: extension`.
- Examples: `schemas/examples/progress.agent-arranged.json` (explicit pacing reset), `schemas/examples/progress.full.json`, `schemas/examples/progress.core.json` (compact), `schemas/examples/session-export.example.json`.
- Tool: `scripts/progress_tool.py` (Python 3.8+, standard library only).
- Course sources also require the companion `closebook-progress/<topic-slug>.course.md` ledger from `source-driven-course.md`. Load, save and export it alongside progress (including in chat-only sessions). It retains source locators, complete scope and gate/assessment evidence without changing progress schema 1.0; compact progress JSON alone cannot preserve or prove course coverage.

## 1. Three storage tiers

### a. File system available (Claude Code, Codex, Gemini CLI, any agent with file tools)
- Path: `closebook-progress/<topic-slug>.json` in the working directory, unless the learner names another path. Tell them the path once.
- Record **core + extension** fields.
- Prefer the tool over hand-editing, so scheduling rules stay exact:
  ```bash
  python3 scripts/progress_tool.py new --topic "HTTP caching" --kp "kp1|Strong vs negotiated cache|core|conceptual" --kp "kp2|Cache-Control directives|important|factual" --date 2026-10-31 --out closebook-progress/http-caching.json
  python3 scripts/progress_tool.py record closebook-progress/http-caching.json --kp kp2 --phase retest --result incorrect --confidence 3 --error-type misconception --question "Does no-cache mean 'don't store'?" --method retrieval --interaction mcq --date 2026-10-31
  python3 scripts/progress_tool.py due closebook-progress/http-caching.json --date 2026-11-01
  python3 scripts/progress_tool.py validate closebook-progress/http-caching.json
  ```
- Extension fields with no CLI flag (`methods_selected`, `interaction_downgraded_from`, `feynman`, `sessions`…) are edited directly in the JSON; run `validate` afterwards.
- If Python isn't available, edit the JSON by hand following `spaced-repetition.md`.

### b. Chat only (no files)
- Keep the state in the conversation as you go (no need to show it).
- At the end of the session, output the **compact core version** in a single fenced `json` code block, minified, with one line before it: "Save this; paste it back next time to continue." Full version only if the learner asks.
- Next session: ask the learner to paste it. Check it (shape, dates, ids), then run the review flow.
- If the pasted JSON is broken (truncated, edited), repair what's obvious, list the repairs in one sentence, and continue.
- Never claim you'll remember without the file.

### c. Platform persistence (project files, memory features, storage APIs)
- Use it if it exists and you have concrete evidence it works in this environment.
- Still output the compact JSON at the end. Platform memory can be cleared, summarised or unavailable on another device, so it can't be the only copy.

## 2. Core vs extension fields

**Core** (needed to resume; kept in compact export):
`schema_version`, `profile`, `topic`, `language`, `created`, `updated`, `settings`, `exam`, `weak_points`, and per knowledge point: `id`, `title`, `importance`, `knowledge_type`, `secondary_types`, `status`, `mastery`, `leitner_box`, `next_review`, `last_reviewed`, `priority_flag`, `attempts` (core attempt fields: `id`, `at`, `phase`, `result`, `hint_level`, `confidence`, `error_type`), `errors`, `feynman`, `plain_talk_used`, `plain_talk_recall_result`.

**Extension** (analytics and decision records; full version only):
`sessions`, `user_overrides`, and per point: `mnemonics`, `methods_selected`, `methods_skipped`, `methods_insensitive`, `method_override_by_user`, `method_fit_flag`, `interaction_selected`, `interaction_downgraded_from`, `interaction_override_by_user`, `efficiency`, `notes`; per attempt: `question`, `question_format`, `method`, `interaction`, `duration_sec`, `self_assessed`, `coach_graded`, `source`, `note`.

Compact rules: drop extension fields; drop core fields that are empty or default (`false`, `[]`, `null`, `""`), except the required ones (`next_review`, `attempts`, `weak_points`). `progress_tool.py compact` does exactly this.

## 3. What to write when

| Event | Write |
|---|---|
| Opening confirmed | Create the file / state: topic, points with type and importance, `status` (`optional_extension` for trimmed points, `planned` for later points on a learning path), `created`, `settings` (`teach_pace` only for a learner preference of `step` or `section`; absent/null means the agent arranges units from content and workload) |
| Check after a teaching chunk | attempt with `phase: "teach_check"`; no box, mastery or error update; until the point's first retest, it is due the next day |
| Each answer | Append an attempt (`at`, `phase`, `result`, `hint_level`, `confidence` for right/wrong questions, `error_type` if wrong). Then update box, `next_review`, `mastery`, `priority_flag` |
| Error | Append to `errors[]` with remedy |
| Feynman scored | `feynman` object |
| Plain Talk recall | attempt with `phase: "plain_talk_recall"`, `plain_talk_used`, `plain_talk_recall_result` |
| Method / interaction decisions | extension fields (section 2) |
| User overrides | the point's `*_override_by_user` and an entry in `user_overrides` |
| Pace changed mid-session ("slow down", "bigger chunks") | `settings.teach_pace` and a `user_overrides` entry with `scope: "flow"`; set `teach_pace: null` to explicitly reset the setting when the learner delegates pacing to the agent again |
| A result line arrives twice for the same item (retry after a cancelled host dialog) | Nothing new: the attempt already exists; reply once |
| Section review widget summary comes back (`host-widgets.md` section 8) | One attempt per item from the summary line: `phase: "teach_check"` (section checks) or `"review"` (review batch), `source: "widget"`, `result`, `confidence`, `interaction`; teach checks change no schedule |
| Exam page export comes back (`html-lesson.md`, exam mode) | `import-session` (or merge by hand): attempts `phase: "review"`, `source: "html"`; confident misses set `priority_flag`; each point gets `section` from the export; then `weak_points` from the report |
| Session end | `weak_points` (with a specific note), `updated`, a `sessions` entry |

Attempt ids: `<kp_id>-<n>`, continuing the numbering already in the file. They let merges recognise the same attempt in two copies.

## 4. Dates
- Absolute dates only (`YYYY-MM-DD`; attempts may use full ISO timestamps).
- Get today's date from the environment. If you don't have one, ask. Never guess.

## 5. Merging and imports
- **Compact chat export → local full file:** `progress_tool.py merge local.json pasted.json` (deduplicates attempts, keeps extension fields from the local file, replays the schedule).
- **HTML page export → progress:** `progress_tool.py import-session progress.json export.json` (creates missing points from the export's definitions; self-assessed answers keep `self_assessed: true`).
- **Your grading of the page's written answers → progress:** `progress_tool.py apply-grading progress.json grading.json` (same `closebook-grading` block the learner pastes into the page; sets `result`, `coach_graded`, `note`, then replays the schedule).
- **In chat without tools:** append the new attempts to the pasted JSON by hand and update the schedule per `spaced-repetition.md`.
- Settings merge field by field: explicit fields in the input with the newer `updated` date win; on the same day, the imported input wins. Missing fields leave local settings unchanged. An explicit `teach_pace: null` resets pacing and is kept inside `settings` by compact export; omitting the field alone cannot clear an existing local preference. Older inputs cannot replace newer settings.
- After any merge the schedule is **replayed from the full attempt history**, so the file and the rules can't drift apart. `validate` warns when stored state differs from the replay.

## 6. Schema versions
`schema_version` "1.x" is readable by this skill. Minor versions only add optional fields. A file with another major version: tell the learner, don't silently convert.

Pacing compatibility: existing `step` and `section` progress values remain valid. A null value is an explicit reset for current readers; older installations that reject null need the updated skill/tool. Lesson data still accepts only `step` or `section`: choose its delivery mode from the plan instead of copying the reset value.
