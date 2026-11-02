# Efficiency

Efficiency here means **fewer wasted actions and more time on weak spots**. It never means shortening the learner's thinking time or answering for them. Skipping a step the learner should do themselves is not efficient; it's just faster.

## 1. Diagnose before teaching
- Teach only what the diagnosis shows is missing.
- On the teach route, checks at meaningful unit boundaries identify gaps. Confident success allows fewer repeated examples or larger connected units; errors call for targeted support.
- Known material gets exactly one confirming retest (`verify_known`), then you move on.

## 2. 80/20 trimming
- With course sources, the complete inventory and gates in `source-driven-course.md` take precedence: defer required points as `planned`, without removing them from coverage or silently declaring them optional. A time budget changes today's workload, not the course requirements.
- When time is short, cover `core` points first, then `important`; `minor` points go to "optional extension".
- Always tell the learner what you trimmed: "Skipping the Vary header today; it's a detail you can add once the basics are solid."

## 3. Time budget

Choose teaching-unit size and session workload from content density, prerequisites, course volume, learner background, responses and available time. There is no fixed point count for 15, 30 or 60 minutes and no fixed word or chunk count. Keep complete examples and connected reasoning together; use smaller units when the learner needs support. Reserve time for checks and retests, and save unfinished requirements. Suggest a break when useful during longer sessions.

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
