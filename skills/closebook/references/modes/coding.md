# Mode: coding / technical (编程/技术)

**When to load:** the material is code, an API, a framework, a CLI, a system design, or the learner wants to be able to *do* something technical.

**Bias (never overrides `method-fit.md`):** predict-verify + self-explanation + mini project. The learner writes or predicts first, then runs or compares.

## What changes
1. **Learner first, always.** Before showing working code: "write it" or "predict what this prints". Showing the solution first turns a skill into reading.
2. **Ground truth over your memory.** Verify predictions by running code (learner's machine or your tool environment). If neither can run it, cite the documentation or the material as the source of the expected result. Never invent output.
3. **Self-explanation on real snippets** (≤ 12 lines, numbered). Intervene only at the first wrong step.
4. **Mini project** at the end of 60-minute sessions or as homework, when the learner has an environment. Review it like a code review: done-criterion, which points are applied correctly, one concrete improvement.
5. **Interaction:** code blocks in plain text are usually best. `diagram_fill` for architecture or data flow (predict or fill first). `simulation` only when tweaking a parameter teaches a pattern and Level 2 is available; otherwise text predict-verify with 2–3 values.
6. **Errors:** `transfer_failure` is common (knows the API, misuses it in a new case); answer it with a new-context variant.

## What doesn't change
- Conceptual points inside technical material (e.g. "why eventual consistency") still get Feynman or elaborative questioning. Don't turn them into code puzzles.
- Factual points (flag names, status codes) get retrieval + mnemonics, not projects.

## Safety
Only ask the learner to run code that is safe on their machine (no destructive commands, no network calls to unknown hosts). Say what a command does before asking them to run it.

## Progress fields
Session `mode: "coding"`; attempts with `phase: "project"` for project reviews.
