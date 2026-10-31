# Method fit: matrix and selection rules

This is step 2 of the decision chain (knowledge type → **method** → interaction → platform). Interaction forms are chosen only after this, in `interaction-fit.md`.

## Contents
1. Method ids and roles
2. Fit matrix (summary)
3. Fit matrix (reasons and alternatives)
4. Selection procedure
5. Switching, overrides and transparency
6. Recording

---

## 1. Method ids and roles

| # | id | Role | File |
|---|---|---|---|
| 1 | `retrieval` | **Baseline** | `methods/01-retrieval.md` |
| 2 | `spaced_repetition` | **Baseline** | `methods/02-spaced-repetition.md` |
| 3 | `error_review` | **Baseline when errors exist** | `methods/03-error-review.md` |
| 4 | `feynman` | Optional | `methods/04-feynman.md` |
| 5 | `interleaving` | Optional (conditional) | `methods/05-interleaving.md` |
| 6 | `elaborative_interrogation` | Optional | `methods/06-elaborative-interrogation.md` |
| 7 | `self_explanation` | Optional | `methods/07-self-explanation.md` |
| 8 | `predict_verify` | Optional | `methods/08-predict-verify.md` |
| 9 | `calibration` | Always-on mechanic + optional feedback | `methods/09-calibration.md` |
| 10 | `chunking_mnemonics` | Optional | `methods/10-chunking-mnemonics.md` |
| 11 | `difficulty_tuning` | Always-on mechanic | `methods/11-difficulty-tuning.md` |
| 12 | `mini_project` | Optional | `methods/12-mini-project.md` |

**Always-on mechanics** don't count against the "≤ 2 optional methods" cap: collecting confidence on right/wrong questions (raw data for calibration) and adjusting difficulty run inside the core loop at almost no cost. Explicit calibration feedback ("you tend to be overconfident on X") is a short add-on at the end of a session or review once there are ≥ 5 rated answers.

## 2. Fit matrix (summary)

✓ = fits · ○ = fits only under the stated condition · ✗ = don't use

| Method | factual | conceptual | procedural | judgment | language_production | contested |
|---|---|---|---|---|---|---|
| retrieval | ✓ | ✓ | ✓ | ✓ | ✓ | ○ recall positions and arguments, not "the answer" |
| spaced_repetition | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| error_review | ✓ | ✓ | ✓ | ✓ | ✓ | ○ only factual errors about the positions; reasoning gaps are not "errors" |
| feynman | ✗ | ✓ | ✗ (use self_explanation) | ✓ | ✗ | ○ explain each position plainly; scored on coherence and fairness |
| interleaving | ○ | ○ | ○ | ○ | ○ | ○ — all: ≥ 2 learned points of the same level with basic mastery |
| elaborative_interrogation | ✗ | ✓ | ○ "why this step" | ✓ | ✗ | ○ "why would someone hold this view" |
| self_explanation | ✗ | ✓ | ✓ | ✓ | ○ explain a grammar choice | ○ explain an argument's steps |
| predict_verify | ✗ | ○ only with a checkable outcome | ✓ | ✗ | ✗ | ✗ never |
| calibration | ✓ | ✓ | ✓ | ✓ | ✓ | ○ no right/wrong comparison; only "is your reasoning coherent" |
| chunking_mnemonics | ✓ | ✗ | ✗ | ✗ | ○ only the factual part (vocab lists, irregular forms) | ✗ |
| difficulty_tuning | ✓ | ✓ | ✓ | ✓ | ✓ | ○ tune depth of reasoning, not correctness |
| mini_project | ✗ | ✗ | ○ hands-on and the learner can practise | ✗ | ✗ | ✗ |

A method may also be used through a point's **secondary type**, but only for that part of the point.

## 3. Fit matrix (reasons and alternatives)

| Method | Not for | Why not | Use instead |
|---|---|---|---|
| feynman | factual | Arbitrary facts have no "why" to explain; explaining them invites invented reasons | retrieval + chunking_mnemonics |
| feynman | procedural | Explaining a procedure in general terms skips the step-level reasoning that matters | self_explanation on a worked example |
| feynman | language_production | Talking about a language isn't producing it | production-direction retrieval |
| elaborative_interrogation | factual | Research finds it can help with facts when learners have prior knowledge (Dunlosky et al., 2013), but for pure lists it slows drills and invites made-up reasons. closebook excludes it by design; if a fact has a real "why", tag the point with a secondary `conceptual` type | retrieval + chunking_mnemonics |
| predict_verify | contested | There is no ground truth to verify a prediction against | elaborative_interrogation, compare positions |
| predict_verify | judgment | Real outcomes of decisions are rarely observable in a session | case-based retrieval: "what would you choose and why", then compare with the reasoning in the material |
| predict_verify | conceptual without checkable outcome | A prediction no one can check teaches nothing | elaborative_interrogation |
| chunking_mnemonics | conceptual / procedural / judgment | Mnemonics memorise surface form; these types need understanding | feynman / self_explanation |
| mini_project | anything not hands-on, or learner can't practise now | Without doing, a project is just another essay | self_explanation on a worked example; schedule the project for later |
| calibration (right/wrong) | contested | No correct answer to compare confidence with | ask for reasons; judge coherence |
| interleaving | fewer than 2 learned points, or no basic mastery yet | Mixing before anything is learned is just confusion | blocked practice first |

## 4. Selection procedure

Run per knowledge point, not per material.

1. **Baseline:** `retrieval` + `spaced_repetition`; add `error_review` as soon as there is an error.
2. **Candidates:** optional methods with ✓ for the primary type, plus ○ methods whose condition is met (including via secondary type).
3. **Mode bias** (`modes/`): reorder candidates; never add a ✗ method.
4. **Learner signals:**
   - 15 minutes or tired → at most 1 optional method, often 0.
   - Beginner (path B) → prefer `self_explanation` and `elaborative_interrogation` on the provided example before a free `feynman` explanation.
   - Stated preference → honour it if it fits; otherwise see section 5.
   - Importance `minor` → usually 0 optional methods.
5. **Pick at most 2.** Fewer is better. Default picks when nothing else applies:

| Primary type | Default optional methods |
|---|---|
| factual | `chunking_mnemonics` if there are ≥ 3 items or arbitrary associations; else none |
| conceptual | `feynman` for core points, `elaborative_interrogation` otherwise; add `predict_verify` only with a checkable outcome |
| procedural | `self_explanation` + `predict_verify`; `mini_project` at session end if hands-on is possible |
| judgment | `elaborative_interrogation`; `feynman` for core points |
| language_production | none beyond production-direction retrieval; `chunking_mnemonics` for the factual part |
| contested | `elaborative_interrogation` (coherence-scored) |

6. **Not covered by the matrix** (unusual type mix, unclear material) → most conservative plan: retrieval + one short-answer question; set `method_fit_flag: "needs_review"`.
7. **Insensitivity rule:** if a method fails twice for the same learner (e.g. two Feynman attempts that only repeat jargon), switch to the listed alternative and record `methods_insensitive: [{method, note}]`. Read this field at the start of later sessions.

## 5. Switching, overrides and transparency

- **Announce** each method in one sentence with the reason *now*: "This one is a mechanism, so I'll ask you to explain it in plain words; gaps show up faster that way."
- **Skipping** a standard step: say what and why ("Skipping the mnemonic; there's only one fact here").
- **User switches** ("only Feynman today", "just quiz me"): comply; name the effect on records ("No retests today, so these points won't move up a review box").
- **User demands an unfit method** (e.g. Feynman on a glossary): one sentence of risk + alternative ("A glossary has no 'why' to explain, so Feynman tends to produce invented reasons; flashcards with your own memory hooks work better. Still want Feynman?"). If they insist, do it and record `method_override_by_user: {requested, recommended, risk_note, at}`.
- Never use an unfit method to look thorough. Never suppress a fitting one to look minimal: a conceptual core point with time available **should** get Feynman or elaborative questioning.

## 6. Recording

Per knowledge point (extension fields, see `progress-state.md`):
- `methods_selected`: ids used.
- `methods_skipped`: `[{method, reason}]` for standard steps skipped or fitting methods not used for a reason worth knowing (time, fatigue, user request).
- `method_override_by_user`, `method_fit_flag`, `methods_insensitive`.
- Every attempt can carry `method` so `progress_tool.py method-stats` can compare methods by knowledge type.
