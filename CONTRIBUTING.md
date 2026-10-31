# Contributing to closebook

Thanks for helping. closebook is a teaching skill, so most changes are changes to how an AI behaves. A small wording change in `SKILL.md` can change many conversations, so please read this before opening a pull request.

## Ground rules

1. **Honesty first.** The skill's priority order is honesty > explicit user instructions > knowledge-type fit > scenario mode > efficiency > default flow. A change that makes the coach friendlier but less honest (softening "wrong", hiding uncertainty, claiming abilities it lacks) won't be merged.
2. **No invented platform facts.** Any claim about what Claude, ChatGPT, Codex, Gemini or another platform can do needs a source and a date. Add it to [`docs/platform-verification.md`](docs/platform-verification.md) and mark it verified or unverified in the matching adapter. If you can't find a source, write "unverified".
3. **Plain text must keep working.** Every feature needs a Level 0 (plain text) path. Richer interaction is an optional layer and may only downgrade, never be required.
4. **Keep `SKILL.md` lean.** It holds priorities, the flow and routing. Details belong in `references/`, loaded only when needed. Frontmatter may only use `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and `name` must stay `closebook`.
5. **Scripts are optional helpers.** Python 3.8+, standard library only, no network. The teaching flow must never depend on them.

## Running the checks

```bash
python3 -m unittest discover -s tests          # unit, packaging and (if Playwright is installed) browser tests
python3 tools/package_skill.py --check         # what would ship in the ZIPs
```

Browser tests need `pip install playwright && python3 -m playwright install chromium-headless-shell`. Without it they're skipped, not failed.

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
4. Prefer fixing the skill text over loosening an expectation. If the eval itself was wrong (e.g. the prompt didn't contain what the expectation assumed), fix the eval and say so explicitly.

One run per eval is noisy. A pull request that changes `SKILL.md` should rerun all evals. A change limited to one reference file can rerun the evals that route to it.

## Repository hygiene

- On macOS, external drives create `._*` and `.DS_Store` files. They're ignored by git and excluded from the ZIPs, but don't commit them.
- `evals/` stays in the repo but is never shipped in the ZIPs.
- The Gemini ZIP leaves out `agents/openai.yaml` on purpose (see [`adapters/gemini.md`](adapters/gemini.md)).

## Pull requests

Describe what changed in behaviour, not only in text, and include the eval results. For platform changes, link the source you checked and the date. By contributing you agree that your work is released under the [MIT License](LICENSE).
