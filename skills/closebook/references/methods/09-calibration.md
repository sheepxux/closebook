# 09 Metacognitive calibration (元认知校准)

**Principle.** Learners decide what to study based on how sure they feel; comparing that feeling with actual results fixes the decisions, and confident errors are the ones that never get corrected by themselves.

## Fits / doesn't fit
- ✓ all types with right/wrong answers.
- ○ `contested`: no correctness comparison. Instead ask "how well can you defend this?" and compare with the coherence judgment, or skip.

## Two parts
1. **Always-on data collection** (doesn't count as an optional method): every right/wrong retest collects confidence 1–3 in the same reply as the answer. Never as an extra round trip.
2. **Feedback** (optional, short): at session end or in review, once there are ≥ 5 confidence-rated answers.

## Procedure (feedback)
1. Compute, per confidence level, how often answers were right (`progress_tool.py calibration` does this; in chat, count by hand).
2. Report in ≤ 3 sentences:
   - "When you said 3 (certain) you were right 6 of 8 times; the two misses were both about `no-cache`."
   - Name the bias: **overconfident** (3s often wrong), **underconfident** (1s mostly right), or **calibrated**.
   - One action: overconfident → "before answering 3, try to name one way you could be wrong"; underconfident → "your 1s are usually right, so trust your first recall more and spend review time elsewhere".
3. High-confidence errors are always the first items in the next review (`priority_flag`).

## Example (en)
> **Coach:** Calibration check: your 3s were right 4/6 times, your 1s were right 3/3. You're a bit overconfident on directive names and underconfident on mechanisms. Before you mark a 3 on a header name, picture the header in a real response first.

## Scoring
Not scored. Bias label can be stored in the session `notes`.

## Progress fields
Attempt `confidence`; `priority_flag`; `errors[].high_confidence`; `progress_tool.py calibration` and `high-confidence-errors`.
