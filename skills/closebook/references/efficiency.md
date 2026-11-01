# Efficiency

Efficiency here means **fewer wasted actions and more time on weak spots**. It never means shortening the learner's thinking time or answering for them. Skipping a step the learner should do themselves is not efficient; it's just faster.

## 1. Diagnose before teaching
- Teach only what the diagnosis shows is missing.
- On the teach route the chunk checks do this job: two easy, confident checks in a row → skip the remaining worked examples for that point.
- Known material gets exactly one confirming retest (`verify_known`), then you move on.

## 2. 80/20 trimming
- When time is short, cover `core` points first, then `important`; `minor` points go to "optional extension".
- Always tell the learner what you trimmed: "Skipping the Vary header today; it's a detail you can add once the basics are solid."

## 3. Time budget

Target 25–45 minutes of work per session. Rough plans:

| Time | Points | Per point | Synthesis | Extras |
|---|---|---|---|---|
| 15 min | 2–3 core | diagnose + 1 retest | 2–3 sentence free recall | none |
| 30 min | 3–4 | diagnose + feedback + 1–2 retests | Feynman or free recall | Plain Talk offer if ≥ 5 min left |
| 60 min | up to 5 | full loop, optional methods | Feynman | mini project or Plain Talk; suggest a 5-min break at ~30 min |
| Review | due items | retest first | none | calibration feedback if ≥ 5 rated answers |

Teach route (new material) covers fewer points: 1 in 15 minutes, 2–3 in 30, 3–4 in 60 (`new-learning.md`).

Review batch: default 8 questions (`settings.review_batch_size`), 4–5 for a 15-minute review.

## 4. Fatigue and overload signals
- 3 incorrect in a row.
- Answers getting noticeably shorter, "whatever", "idk" on things they knew earlier.
- Long pauses the learner mentions, or "I'm tired".

Response (pick one, say it in one sentence): suggest a short break; narrow to the remaining core point; end with the review list now and save progress. Don't push through: errors made while exhausted pollute the schedule.

## 5. Short, precise feedback
Right / missing / next step. Don't repeat what the learner already said correctly. See `feedback-style.md`.

## 6. No empty actions
- No generic summaries at the end of each point.
- No praise without content ("Great job!" alone).
- No repeated follow-ups on minor details.
- No component that doesn't pass the test in `interaction-fit.md`.

## 7. Review where it matters
Due items only, priority order, capped batch. Solid points that aren't due are not reviewed "just in case".

## 8. Confidence costs nothing extra
Confidence is collected in the same reply as the answer (`B 3`, `304, 2`). Never as a separate question. Only for questions with a right answer.

## 9. Efficiency metrics (recorded)
Per knowledge point, extension field `efficiency`:
- `minutes_spent`: rough wall-clock estimate (from timestamps if available, otherwise the learner's time budget divided across points; say it's an estimate).
- `rounds_to_mastery`: scored attempts until the first correct, hint-free answer.
- `first_retest_correct`: was the first scored retest correct without hints?

Attempts may carry `duration_sec` when the environment provides timing (HTML page, timestamps). Don't invent durations; leave the field out instead.
