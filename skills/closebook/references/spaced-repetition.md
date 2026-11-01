# Spaced repetition: scheduling rules

closebook uses a simplified **Leitner system with five boxes**. It's simple enough to compute by hand in a chat, deterministic enough for `scripts/progress_tool.py` to reproduce exactly, and good enough for personal study. It isn't an optimal scheduler (algorithms like SM-2 or FSRS adapt intervals per item); the trade-off is transparency over precision.

## Parameters (configurable in `settings`)

| Setting | Default | Meaning |
|---|---|---|
| `leitner_intervals_days` | `[1, 3, 7, 14, 30]` | Days until next review for boxes 1–5 |
| `review_batch_size` | `8` | Max questions per review session |
| `interleaving` | `"auto"` | `auto` = on in review when conditions hold; `on`; `off` |

Why these intervals: roughly doubling gaps match the usual forgetting-curve advice, and 1 → 30 days covers a typical course or exam cycle. Learners preparing for a far-off exam can append longer intervals by editing the list (it must stay 5 increasing values in schema 1.0).

Box `0` means "not scheduled yet" (new or only diagnosed); `next_review` is then `null`.

## Which attempts count
| `phase` | Updates the schedule? |
|---|---|
| `diagnostic` | **No.** Diagnosis is low-stakes by design. |
| `teach_check` | **No.** Answered seconds after reading the explanation, so it overstates learning. A point with only checks (taught, not yet retested) stays in box 0 but is due the next day, so its retest isn't lost. |
| `verify_known` | Yes, special rule below |
| `retest`, `review`, `synthesis`, `plain_talk_recall`, `project` | Yes |

## Outcome from result and hint level
| Result | hint 0–1 | hint 2 | hint 3 |
|---|---|---|---|
| `correct` / `coherent` | **pass** | fuzzy | fail |
| `partial` / `partly_coherent` | fuzzy | fuzzy | fail |
| `incorrect` / `incoherent` / `dont_know` | fail | fail | fail |

Hint 3 means the answer was shown, so nothing was retrieved.

## Box update

| Outcome | Box change | Mastery |
|---|---|---|
| pass | +1 (max 5) — **only if it's the first scored attempt for this point today**; otherwise unchanged | `solid` (or `fuzzy` if an earlier attempt today failed or was fuzzy) |
| fuzzy | −1 (min 1) | `fuzzy` |
| fail | back to 1 | `weak` |

Then `next_review = date of attempt + interval[box]`, and `last_reviewed = date of attempt`.

**Why "first attempt of the day":** a learning session often retests the same point several times (retest, re-try after an error, synthesis, plain-talk recall). Same-day successes after a failure show short-term memory, not durable learning, so only the day's first answer can promote. Failures always demote.

**New points:** box 0 → a pass moves to box 1 (review tomorrow). So everything learned today is reviewed tomorrow, which is intended: the first review is the most valuable one.

**`verify_known`** ("I already know this", confirmed by one question): pass → box becomes at least 2 (review in 3 days), point gets `status: "skipped_known"`. Fuzzy/fail → normal rules, and the point is taught.

**Exam date** (exam-prep mode, `exam.date` set): if the computed `next_review` falls after the day before the exam, it's moved to that day, so every point gets one last review before the exam.

## Priority flag (high-confidence errors)
- Set `priority_flag: true` when an attempt is `incorrect` with `confidence: 3`.
- Cleared by a later **promoting** pass (first attempt of a later day, no hint ≥ 2).
- Flagged items are reviewed first regardless of box.

## Due selection and order
Due: `next_review <= today` and `status` is not `optional_extension` or `planned`.
Order: `priority_flag` → `weak` → `fuzzy` → `solid`; ties by days overdue (more first), then importance (core → important → minor). Take up to `review_batch_size`.

## Worked example
| Date | Attempt | Outcome | Box | Next review |
|---|---|---|---|---|
| 2026-10-27 | diagnostic: dont_know | — | 0 | — |
| 2026-10-27 | retest: correct, hint 0, conf 2 | pass (first today) | 1 | 2026-10-28 |
| 2026-10-27 | synthesis: correct | pass (not first today) | 1 | 2026-10-28 |
| 2026-10-28 | review: incorrect, conf 3 | fail, flag set | 1 | 2026-10-29 |
| 2026-10-29 | review: correct, hint 0 | pass, flag cleared | 2 | 2026-11-01 |
| 2026-11-01 | review: partial | fuzzy | 1 | 2026-11-02 |

## Computing dates by hand (chat environments)
Add the interval to the attempt date as a calendar date (month lengths matter: 2026-10-30 + 3 = 2026-11-02). Always write absolute dates in the review list; add a relative hint in brackets if helpful ("2026-11-01 (tomorrow)"). If you aren't sure of today's date, ask; never guess it.

## Tool support
`progress_tool.py record` applies these rules to one attempt; `progress_tool.py recompute` replays a whole history; `merge` and `import-session` replay after combining histories, so the file and the rules can't drift apart.
