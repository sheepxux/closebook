# 05 Interleaving (交错练习)

**Principle.** Mixing problems from related points forces the learner to first decide *which* idea applies, the skill that blocked practice never trains.

## Fits / doesn't fit
- ○ all types, under one condition: **≥ 2 learned points at the same level** (same topic depth, similar difficulty) **and each has basic mastery** (at least one correct scored attempt).
- Default **on** in review mode, **off** in first-time learning. The learner can toggle it ("don't mix", "mix them").
- Not useful when points are unrelated (mixing HTTP caching with Spanish verbs adds nothing but context switching).

## Procedure
1. Check the condition from the progress file.
2. Announce once: "I'll mix the questions across points; it's harder on purpose because you have to recognise which idea applies."
3. Order questions so no two consecutive questions test the same point when avoidable. Prefer pairs that are easily confused (`no-cache` vs `no-store`, preterite vs imperfect).
4. Questions shouldn't name the point they test; recognising which point applies is the skill.
5. After the batch, note which confusions appeared and log them as `misconception` or `transfer_failure` errors.

## Example (en)
> **Coach:** Mixed review, three questions, one at a time.
> Q1: A hashed JS bundle (`app.3f9a.js`) should be cached for how long, and with which directive? Answer + confidence.
> *(after feedback)* Q2: The server answers 304. What did the browser send to make that possible?
> *(after feedback)* Q3: Your HTML changed but users still see the old page. Which header is the likely culprit?

## Scoring
Same as retrieval. Track separately: did the learner pick the right *point/idea*? A wrong pick is `transfer_failure` or `misconception`.

## Progress fields
`settings.interleaving` (`auto` / `on` / `off`); attempts with `method: "interleaving"`; `methods_skipped` with reason when the condition isn't met.
