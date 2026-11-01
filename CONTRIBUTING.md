# Contributing to closebook

Thanks for helping. closebook is a teaching skill, so most changes are changes to how an AI behaves. A small wording change in `SKILL.md` can change many conversations, so please read this before opening a pull request.

## Ground rules

1. **Honesty first.** The skill's priority order is honesty > explicit user instructions > knowledge-type fit > scenario mode > efficiency > default flow. A change that makes the coach friendlier but less honest (softening "wrong", hiding uncertainty, claiming abilities it lacks) won't be merged.
2. **No invented platform facts.** Any claim about what Claude, ChatGPT, Codex, Gemini or another platform can do needs a source and a date. Add it to [`docs/platform-verification.md`](docs/platform-verification.md) and mark it verified or unverified in the matching adapter. If you can't find a source, write "unverified".
3. **Plain text must keep working.** Every feature needs a Level 0 (plain text) path. Richer interaction is an optional layer and may only downgrade, never be required.
4. **Keep `SKILL.md` lean.** It holds priorities, the flow and routing. Details belong in `references/`, loaded only when needed. Frontmatter may only use `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and `name` must stay `closebook`.
5. **Scripts are optional helpers.** Python 3.8+, standard library only, no network. The teaching flow must never depend on them.

## Running the checks

Install Node.js 20+, the MCP dependencies and the browser test dependencies once:

```sh
npm ci --prefix mcp
python3 -m pip install playwright
python3 -m playwright install chromium-headless-shell
```

Then run all deterministic checks from the repository root:

```sh
python3 tools/check.py
```

This runs the Python suite, packaging checks and MCP tests. The full command fails if tests are skipped, so a missing browser cannot silently look like a complete pass. GitHub Actions runs the same command on pushes and pull requests.

When browser access is unavailable or prohibited in the current environment, run `python3 tools/check.py --skip-browser` and label the result as partial. Do not bypass a host's browser restrictions. For focused work, `npm --prefix mcp test` runs only MCP checks.

Model behaviour evaluations and real-client clicks are separate from deterministic CI. Protocol/DOM tests do not prove correct renderer selection, learning-state updates or successful interaction in a desktop app.

If you change `skills/closebook/assets/lesson-template.html`, rebuild the example page (a test compares them):

```bash
python3 skills/closebook/scripts/build_lesson.py skills/closebook/schemas/examples/lesson.http-cache.json --out examples/http-cache-lesson.html
```

If you change a schema, update the examples in `skills/closebook/schemas/examples/` and keep `schema_version` handling backward compatible, or add a migration note in `references/progress-state.md`.

## Changing the skill's behaviour

Behaviour is tested with the evals in [`skills/closebook/evals`](skills/closebook/evals) (skill-creator format: prompt, attached files, expectations).

1. Find or add the eval for the behaviour you're changing. Each expectation should be checkable from a single reply.
2. Run the eval **blind**: the runner gets only the skill folder, the prompt and the attached files, never the expectations. The grader gets the expectations and the reply, and must quote evidence for each pass.
3. Save replies and grading under `docs/eval-results/<date>/iteration-<n>/` and report before/after numbers in the pull request.
4. For renderer cases 29–34, record actual calls and arguments using the tool doubles described in [`evals/README.md`](skills/closebook/evals/README.md). Check progress-writing calls too. A textual promise to use a tool is not a passing tool-selection test.
5. Prefer fixing the skill text over loosening an expectation. If the eval itself was wrong (e.g. the prompt didn't contain what the expectation assumed), fix the eval and say so explicitly.

The repository provides an opt-in runner for an authenticated Codex CLI:

```sh
python3 tools/run_behavior_evals.py --out /absolute/path/to/new-eval-run
```

Use a new output directory outside the repository for private raw logs. The runner snapshots the skill without `evals/`, records tool calls and saves responses; a separate grader still needs to assess the expectations. It is not part of ordinary CI and consumes model calls.

One run per eval is noisy. A pull request that changes `SKILL.md` should rerun all evals. A change limited to one reference file can rerun the evals that route to it. Report behavioural results separately from CI and desktop submission checks.

## Repository hygiene

- On macOS, external drives create `._*` and `.DS_Store` files. They're ignored by git and excluded from the ZIPs, but don't commit them.
- `evals/` stays in the repo but is never shipped in the ZIPs.
- The Gemini ZIP leaves out `agents/openai.yaml` on purpose (see [`adapters/gemini.md`](adapters/gemini.md)).

## Pull requests

Describe what changed in behaviour, not only in text, and include the eval results. For platform changes, link the source you checked and the date. By contributing you agree that your work is released under the [MIT License](LICENSE).
