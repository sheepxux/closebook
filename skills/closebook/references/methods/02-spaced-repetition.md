# 02 Spaced repetition (间隔重复) — baseline

**Principle.** Reviewing just as memory starts to fade, at growing intervals, keeps more for longer than the same reviews crammed together.

## Fits / doesn't fit
- Fits every type. For `contested` points the review retrieves positions and arguments.
- Not a substitute for understanding: a point that keeps failing at box 1 needs re-teaching or a different method, not more repetitions.

## Procedure
1. After each scored attempt, update the Leitner box and `next_review` with the rules in `../spaced-repetition.md` (default intervals 1 / 3 / 7 / 14 / 30 days).
2. At wrap-up, show the review list with absolute dates.
3. At review time, select due items by priority, cap the batch, retest first.
4. If a point has failed 3 reviews in a row, flag it as a weak point with a note, re-teach with a different example, and consider switching optional method.

## Example (en)
> **Coach:** Review list:
> - **2026-11-01 (tomorrow):** 2 Cache-Control directives (missed `no-cache` with confidence 3, so it goes first), 3 curl inspection, 4 caching strategy
> - **2026-11-03:** 1 strong vs negotiated cache (you already knew it and the check question confirmed it, so it starts with a longer gap)
>
> Short and often beats long and rare: tomorrow's review is about 5 minutes.

## Scoring
Doesn't score anything itself; it consumes results from retrieval.

## Progress fields
`leitner_box`, `next_review`, `last_reviewed`, `priority_flag`, `mastery`; settings in `settings.leitner_intervals_days` and `settings.review_batch_size`.
