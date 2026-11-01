# 11 Difficulty tuning (难度调节)

**Principle.** Learning is fastest when questions need real effort but stay within reach; too easy wastes time, too hard just produces guesses.

## Fits / doesn't fit
- ✓ all types; always on (doesn't count against the optional-method cap).
- ○ `contested`: tune the depth of reasoning asked for (one reason → two reasons → address a counter-argument), never "correctness".

## Difficulty ladder (use the levers in this order)
1. **Hints:** remove hints first (level 2 → 1 → 0).
2. **Format:** recognition (MCQ) → cued recall (cloze) → free recall → apply to a new case → explain/teach.
3. **Context:** same example as taught → new example → mixed with other points (interleaving).
4. **Constraints:** add a time limit only if the learner asked for exam simulation.

## Rules
- **2 correct in a row, no hints, confidence ≥ 2** → move one step up the ladder.
- **2 incorrect in a row** → move one step down and return to a short teaching chunk with a new example (`../new-learning.md`). Don't repeat the same explanation.
- **3 incorrect in a row, or answers getting shorter / "whatever"** → this is fatigue or overload: suggest a short break or narrowing to the core point (`../efficiency.md`).
- Never lower difficulty by giving away the answer; that's hint level 3 and is recorded as such.
- Announce changes briefly: "You've got this level; no hints from here."

## Example (en)
> *(two correct cloze answers on directives)*
> **Coach:** Both right without hints, so let's make it harder: no blanks this time. A CDN should cache an API response for 60 s, but browsers shouldn't cache it at all. Write the header.

## Scoring
Not scored itself. The ladder position appears in each attempt's `question_format` and `hint_level`.

## Progress fields
Attempt `question_format`, `hint_level`; `efficiency.rounds_to_mastery`.
