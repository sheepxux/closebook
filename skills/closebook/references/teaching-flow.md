# Teaching flow (detailed)

This file expands the flow in `SKILL.md`. Everything here runs in plain text; interaction forms only change how a question is presented, never the order of steps.

## Contents
1. Opening
2. Routes: practice (A) and teach (B)
3. The per-point loop
4. Synthesis and wrap-up
5. Review flow
6. Anti-spoiler rule
7. Edge cases

---

## 1. Opening

Goal: one message from you, one reply from the learner, and the session is set up.

**Splitting material into knowledge points**
- 3–5 points. A point is something you can test with one or two questions. If the material is bigger, take the 3–5 most important points and list the rest under "optional extension" (tell the learner what you trimmed).
- Importance: `core` (the material makes no sense without it), `important` (commonly tested or used), `minor` (detail, edge case).
- Knowledge type: primary type plus optional secondary type (see `knowledge-types.md`). Record it now; reviews reuse it instead of re-judging.
- Mixed material is classified **per point**, never as a whole, and each point shows its planned approach in a few words (from `method-fit.md`).

**Template (adapt to the user's language)**

```
Here's how I'd split this into points:

1. [core · conceptual] Strong cache vs. negotiated cache: predict the request flow, then why-questions
2. [important · factual] Cache-Control directives and the 304 status: quick recall cards
3. [important · procedural] Checking cache behaviour with curl: predict the output of commands
4. [core · judgment] Choosing a caching strategy per resource type: pick and justify
(optional extension: CDN cache keys, Vary header)

One reply is enough:
a) Time today: 15 / 30 / 60 min?
b) How familiar: new to it / seen it but shaky / fairly familiar?
c) Any change to the list? ("drop 3", "merge 1 and 2")
```

If you have no reliable date: add "d) What's today's date? (I use it to schedule reviews.)"

Add one line on how questions will appear here (`host-widgets.md` section 3): "I'll show the questions as clickable cards in this chat" or "This chat has no cards, so reply like `B 2`." Decide it from the tools actually listed, never from the platform's name.

Drop b) when the request already settled the route (section 2). On the teach route, replace it with: "b) Already know any of these? Tell me which and I'll test those instead of teaching them." Approach notes on the teach route say "explain → check → …" so the learner can see teaching comes first.

On the teach route, when no `settings.teach_pace` is stored yet, add one more line (`new-learning.md` section 3): "d) Pace: step by step (a short explanation, then a question; good from zero) or by section (2–4 points at once, then the questions; good with some background)?" Once answered, the pace is saved and never asked again. If the learner skips it: `step` for "zero / never seen it", otherwise `section`; say which in one line.

**Applying the answer**
- 15 min → core points only; one retest each; no synthesis beyond 2–3 sentences.
- 30 min → 3–4 points; synthesis.
- 60 min → up to 5 points; synthesis; optional mini project or Plain Talk.
- See `efficiency.md` for the full time budget.

If the learner ignores the questions and just says "start", default to 30 minutes, the route from section 2, and the outline as proposed, and say so in one line.

## 2. Routes: practice (A) and teach (B)

The learner's intent picks the route; what they say about prior knowledge overrides the wording.

| Signal | Route |
|---|---|
| "teach me", "I want to learn X", "get me started", "from scratch", 教我、我想学、入门、从零学、零基础 | **B — teach, then test** |
| "quiz me", "test me", "practice", "review", "drill", "help me memorize", 考考我、练习、刷题、复习、背、测验、备考 | **A — practice** |
| "learn X" + "I've studied it / it's shaky / I know the basics" | A |
| "quiz me" + "never seen it" | B; say in one line that you'll explain first because there's nothing to retrieve yet |
| Material supplied, "help me study this", no signal either way | Ask familiarity in the opening; if they just say "start", B for material they haven't read, A for their own notes |

**A — practice (has met the material).** Go straight to the diagnostic question for point 1, then the loop in section 3.

**B — teach, then test (new to the learner).** Each of today's points in turn: chunks with checks (`new-learning.md`), one chunk and one check per reply on the `step` pace, or a section of 2–4 points and then one check per point on the `section` pace (`new-learning.md` section 3; `settings.teach_pace`). Once all are taught: the closed-book retests and judging of section 3, steps 3–4, starting with the point taught longest ago. The diagnostic is replaced by the chunk checks; a starting-point question is used only when it's unclear what the learner already knows.

Mixed familiarity ("I know 1 and 2, never saw 3"): A for 1–2, B for 3. A point taught on route B in one session is reviewed like any other point afterwards: reviews always test first.

## 3. The per-point loop

### Step 1 — Diagnose
- One question, low stakes. Say explicitly that "I don't know" is a good answer here.
- Right-answer questions: ask for confidence 1–3 in the same reply, as in the retest. A confident wrong diagnostic answer means a misconception: teach it with a contrast example in step 2. It still isn't an error and sets no `priority_flag`.
- Diagnostic results are recorded with `phase: "diagnostic"` and never update the box, mastery, or error list.
- "I already know this": ask one verification question (`phase: "verify_known"`). Correct with no hint → mark `status: "skipped_known"`, schedule per `spaced-repetition.md`, move on. Wrong → continue the loop normally, no fuss.

### Step 2 — Feedback + minimal teaching
Exactly three parts (see `feedback-style.md`):
1. What's right (only if something is; one clause).
2. What's missing or wrong (specific).
3. What fills the gap: one example + one sentence of principle.

Don't restate what they already said correctly. Don't add extra facts "while we're here".

### Step 3 — Retest
- Closed-book: ask them not to look at the material. You can't enforce it; say why it matters ("looking turns this into reading practice").
- Question format and interaction form come from `method-fit.md` and `interaction-fit.md`.
- Questions with a right answer: collect confidence in the same reply as the answer. Plain text format: "Answer + confidence 1–3, e.g. `B 3`". 1 = guessing, 2 = fairly sure, 3 = certain.
- Hints escalate only on request or after a stall: level 1 keyword → level 2 structure (e.g. "three parts: who, when, what") → level 3 show the answer. Record the highest level used.
- Contested material: no confidence rating, no right answer. Judge whether the reasoning is coherent (`coherent` / `partly_coherent` / `incoherent`).

### Step 4 — Judge and record
- Result: `correct` / `partial` / `incorrect` / `dont_know` (or the coherence values).
- Wrong or partial → classify the error and name the remedy:

| Error type | Signal | Remedy |
|---|---|---|
| `misconception` | Coherent but wrong model | Contrast example that breaks the wrong model; elaborative "why not" question |
| `memory_lapse` | Knows it when shown, couldn't produce it | Re-retrieve later in the session; mnemonic if factual |
| `careless` | Slip in an otherwise right answer | Point it out once; no re-teaching |
| `misread` | Answered a different question | Re-ask with the key word highlighted; teach the cue to look for |
| `transfer_failure` | Knows the rule, failed in a new context | New-context variant; self-explanation of why the rule applies |

- High-confidence error (confidence 3 + incorrect) → set `priority_flag`, say plainly that this is the most valuable kind of mistake to catch.
- A `memory_lapse` or `misconception` in the retest earns one more retrieval attempt later in the same session (after another point), not immediately.

One reply may contain feedback on the previous answer plus the next question. Then stop.

## 4. Synthesis and wrap-up

1. **Synthesis.**
   - Any point is `conceptual` or `judgment` → Feynman synthesis: "Explain the whole topic as if to a smart friend who never studied it" (procedure in `methods/04-feynman.md`). Score it, list concrete gaps.
   - Otherwise → free recall: "Without looking, list everything you remember about X." Compare against the points; missing items become review items.
2. **Review list.** Every point with its next review date as an absolute date (e.g. "2026-11-01 (tomorrow): points 2, 4"). High-confidence errors first.
3. **Plain Talk offer** (one sentence, only if time remains). See `plain-talk.md`.
4. **Save progress.** File environments: write the file and confirm the path. Chat environments: output compact core JSON (see `progress-state.md`).
5. Efficiency note (one line, optional): first-retest accuracy and where time went. Skip it if the session was short.

## 5. Review flow

1. **Load.** Read the file, or ask the user to paste the JSON. Validate it (tool or by eye); if broken, repair what's obvious and say what you changed.
2. **Get today's date** (environment, or ask).
3. **Select due items** (`next_review <= today`), ordered:
   1. `priority_flag` (high-confidence errors)
   2. due `weak`
   3. due `fuzzy`
   4. due `solid`
   Ties: more overdue first, then core > important > minor.
4. **Cap the batch** at `settings.review_batch_size` (default 8 questions) or fewer for a known 15-minute budget. Use the stored/default cap when time is unspecified; do not add a time-budget questionnaire to the first review question. The learner can shorten the session at any point. Leftover due items stay due; say so.
5. **Retest first.** No re-teaching before the question; that would turn review into re-reading.
6. **Interleave** if conditions hold (≥ 2 learned points of the same level with basic mastery; default on in review). Mix question order across points instead of finishing one point first. Announce once: "I'll mix the points; that's harder on purpose."
7. **Feedback + error classification** as in the loop.
8. **Update the schedule** per `spaced-repetition.md`, then show the new review list with dates.
9. Optional calibration feedback when ≥ 5 confidence-rated answers exist (`methods/09-calibration.md`).

## 6. Anti-spoiler rule

- Never show the answer to an open question: not in the question text, not in a hint the learner didn't ask for, not in a "fun fact" after it, not by marking the right option.
- Not in the outline either: point titles and approach notes name the topic and the method ("why the third step exists: why-questions"), never the conclusion. Answer-format examples use placeholders (`X, because …, 2`), never a plausible answer.
- One open question per reply. Feedback on the previous question may accompany it. A numbered list of items to recall is several questions, not one; for glossaries ask one card per reply.
- Flashcards: show the front only; show the back after the learner's attempt.
- Multiple choice: never order options so the answer is always first/longest; don't make the correct option the only detailed one.
- Level 2 HTML pages reveal answers only after the learner submits; that is built into the template.

## 7. Edge cases

| Situation | What to do |
|---|---|
| "Just tell me the answer" | Give it. Record `hint_level: 3`. One sentence: shown answers come back tomorrow. |
| Learner wants to skip retest | Explain the cost in one sentence (no retest = no evidence it stuck). If they insist, skip and log in `user_overrides`. |
| Three wrong in a row, or replies getting shorter | Lower difficulty, return to a short teaching chunk with a new example (`new-learning.md`), or suggest a break / smaller scope (`efficiency.md`). |
| "Slow down" / "bigger chunks" / 慢一点 / 一次多讲点 on the teach route | Change `settings.teach_pace` (`step` ↔ `section`), log it in `user_overrides` (`scope: "flow"`), apply from the next chunk or section. A point missed twice on `section` drops to `step` by itself (`new-learning.md` section 3). |
| Practice route, but the diagnostic shows the point is new to them | Switch that point to the teach route and say so in one line. |
| Learner pastes the material back to answer | Gently note it's now open-book; record `hint_level: 3` for that answer. |
| Material is wrong or outdated | Say so with the correction; don't test them on the wrong version. |
| No material, only a topic | Build the outline from general knowledge; say the points are your proposal and may not match their course. On the teach route follow the source rules in `new-learning.md`. |
| Very long material or a whole subject | Pick what fits today; save the rest as `planned` points (`new-learning.md`, learning paths). |
| Learner disputes your grading | Re-check. If they're right, correct the record and say so plainly. If not, explain once with evidence. |
| Session interrupted | Save progress immediately with what exists; unfinished points keep `mastery: "not_assessed"`. |
