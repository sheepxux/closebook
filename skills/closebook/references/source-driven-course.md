# Source-driven courses and coverage evidence

Use this workflow when the learner supplies course slides, a PDF, official documents or a syllabus. It wraps the v0.4.1 teaching and retrieval loop; it does not replace that loop. A course inventory describes the supplied source, not the coach's impression of the subject.

## 1. Establish the source inventory before teaching

- Identify each supplied file, its version/date (or hash when available), actual page/slide count, and its Module/section structure. Preserve the source's order and terminology. For non-paginated documents or outlines, use numbered headings/items with stable locators. If the source has no hierarchy, label any grouping as a coach proposal.
- Inspect **every page/slide**, including diagrams, tables, formulae, examples, exercises, footnotes and available speaker notes. Use suitable document tools already available on the host. Text extraction alone cannot establish coverage of visual content; inspect the rendering where needed. Do not claim access to missing notes, animations, attachments or unreadable content.
- Record every unit as `pending`, `extracted`, `blocked` or `non_instructional`. Give `blocked` units a specific reason; exclude a cover, blank page or bibliography only with a recorded reason. A page with an exercise or a worked example is not non-instructional merely because it lacks prose.
- Extract all testable requirements into stable point IDs, with source locators and an observable learning objective. Split broad headings into testable subpoints without losing the parent heading. Multiple pages may map to one point, and one page may map to many; list every mapping. Deduplicate only equivalent requirements, retaining all locators. A point's objective must include the source's relevant conditions, exceptions and skills, not just its topic title.
- A **syllabus alone** fixes scope and order, not missing teaching detail. Keep its original items as the baseline; label any coach-added subpoints, prerequisites, explanations or practice as supplemental. Do not imply an unprovided slide deck has been parsed or that the syllabus proves full slide-level coverage.
- Build the complete inventory before ordinary teaching starts. For large inputs, extract in batches and save the extraction cursor; do not silently sample. If extraction is blocked, state the unverified range. The learner may explicitly choose to start the available subset; retain the block and restrict every coverage claim to the inspected scope.
- Supplied sources define scope; never substitute a generic AI outline. If official sources conflict or appear wrong/outdated, preserve their original requirements, identify the discrepancy with evidence, and teach the correction explicitly. Do not grade a known falsehood as correct just because it is printed.

## 2. Keep a coverage ledger alongside learning progress

With file access, save `closebook-progress/<topic-slug>.course.md` beside `<topic-slug>.json`, respecting the host's storage rules. The Markdown ledger needs no new progress-schema fields or runtime. Load both when resuming. The progress JSON remains the authority for attempts and spaced repetition; the ledger retains source scope, teaching evidence and assessment mappings. Update them after each relevant event, not from memory at the end.

Use these tables (add rows as needed):

```markdown
# Course: <title>
Updated: <YYYY-MM-DD>
Scope: <supplied files/items; any missing material>
Progress: <topic-slug>.json

## Sources
| Source ID | File/title and version | Total units | Module/section structure |
| --- | --- | --- | --- |
| src1 | <file, revision/date/hash> | <count or unknown> | <source structure> |

## Extraction register — one row per page/slide/outline item
| Source/unit locator | Status | Point IDs | Notes or exclusion/block reason |
| --- | --- | --- | --- |
| src1, slide 1 | pending | — | <not inspected yet> |

## Required points — one row per testable requirement
| Point ID | Module / source section | Source locators | Objective | Teaching evidence | Assessment evidence | Current gap |
| --- | --- | --- | --- | --- | --- | --- |
| kp1 | <module / section> | <source, slide/item> | <observable objective> | planned | not assessed | not taught |

## Assessment evidence — append, do not replace earlier failures
| Assessment ID/date | Kind and scope | Question / criterion | Point IDs actually assessed | Attempt refs | Result / hint level / grading basis |
| --- | --- | --- | --- | --- | --- |
| <id/date> | <section retest or Module exam; source scope> | <question and criterion after hand-in, or saved artifact locator> | <IDs> | <kp_id / attempt.id> | <per-point result, hints, coach/key/self grading> |

## Gates and unresolved work
| Source section / Module | Required | Taught or verified known | Assessed closed-book | Passed | Missing IDs / pending grading / next action |
| --- | --- | --- | --- | --- | --- |
| <scope> | <N> | <n/N> | <n/N> | <n/N> | <specific gaps> |
```

`Teaching evidence` records the date and a locatable lesson/chunk or explanation artifact showing the whole objective was taught. Alternatively, record `verified_known` with a successful closed-book `verify_known` attempt covering that objective. Merely generating a lesson or recording a diagnostic answer does not establish teaching completion.

Give assessment attempts stable IDs in progress. Record the question, criterion, learner response (or a saved response locator) and per-point judgment in the assessment record/artifact, so a later reviewer can check what was actually assessed. Titles, aggregate scores and lists of point tags alone are insufficient evidence. Do not expose an unanswered question's key in the learner's opening inventory or the exam view; retain grading details after hand-in. Static local files are not a secure exam system.

Keep supplemental points outside the required denominator, labelled as additions. Required points deferred by time limits remain `planned`; opening-outline size, topic-only learning paths, teaching-unit sizes and 80/20 trimming never cap or delete this inventory. Do not mark source details `optional_extension` solely because they are minor. If the learner explicitly narrows scope, record the original scope and exclusions; report completion only of the chosen subset.

## 3. Teach point by point

Follow `new-learning.md`: explanation → interactive check → adaptive correction → delayed closed-book retest. The agent chooses teaching-unit size and arrangement from the course content, workload, prerequisites and learner responses, respecting explicit preferences. Several required points may be taught together; each still needs its own coverage and assessment evidence. A **source section** is a curriculum boundary, while a teaching unit is a delivery choice. A long source section may need several units or sessions; a connected section may be explained as a whole. Do not force one small chunk per point or fixed word/point counts.

Map each explanation and question to the inventory IDs. Immediate checks remain `phase: "teach_check"` and do not advance mastery. Record closed-book retests as `retest`, known-point verification as `verify_known`, and Module-exam answers as `review`; no new attempt phases are needed. Do not set mastery or change Leitner rules merely to make a gate look complete.

## 4. Reconcile a source section before the next section

Compare the ledger with the **original source section**, not just today's selected points. Check both directions: every instructional unit has mapped requirements, and every required point has its teaching and assessment evidence. An uninspected unit blocks a full-source completion claim even if every currently listed point passed.

Report four separate facts: extraction status, taught/verified count, assessed count, passed count. `Assessed` means an actual closed-book answer has been graded against the relevant objective; a wrong answer counts as assessed but not passed. A `teach_check`, diagnostic, reading acknowledgement, hinted answer, self-rating or pending written-answer grade cannot establish a pass. A pass needs a correct/coherent, hint-free, keyed or coach-graded retrieval covering the point's objective; accept valid equivalent reasoning. If the learner used the material, record it as open-book/hinted, not a pass.

Default gate: all required points taught or verified known, all assessed and passed, no unresolved extraction or grading gaps in that section. Re-teach weak points with different examples, then use new closed-book questions. Do not let a high average compensate for an unassessed or failed point. A later failed assessment reopens the relevant gap; old passes cannot hide it. Resume at the first unresolved point before advancing. Respect an explicit request to proceed anyway, record the override and open gaps, and never label that section fully complete.

## 5. Run a Module exam and repair weak points

After the Module's sections pass, build an assessment blueprint from **all its required IDs**, not only due items or recent attempts. Cover each objective and include cross-point application/synthesis where the content permits. A combined question may assess multiple points only if its rubric separately judges each one. Several questions or sittings are fine; mark the Module pending until all are submitted and graded. A capped review batch is not a comprehensive exam.

Tell the learner to close the material. With file access, use the existing HTML exam mode (`html-lesson.md`), check that its item-to-point mapping covers the blueprint, and retain the blueprint and grading evidence in the ledger. Grade written answers before deciding the gate. With chat only, ask one question per reply, acknowledge submission without revealing correctness, hints or explanations, and grade after the whole sitting is handed in. Record missing answers as gaps. Record closed-book conditions as reported, never as independently verified physical supervision.

Use the source's pass rule if supplied; otherwise state before starting that every required point must pass a hint-free criterion and weak points will be repaired. A source's aggregate pass threshold may establish its exam result while coverage or point-level gaps remain open; report these separately. Keep Module results separate from section results. Re-teach weak objectives, then retest with new questions (including transfer across points when the gap calls for it). Append repair evidence; do not erase the original exam result. Continue spaced review after passing: completion is not a guarantee of durable mastery.

## 6. Resume, export and honest claims

- On resume, reconcile source identity/version, ledger IDs and progress attempts before teaching. Missing ledger or answer evidence means coverage is unverified; do not rebuild a fictitious history from mastery flags. If a source changes, re-inspect changed units, revise the inventory and reopen affected gates. Retain earlier attempts labelled with their original source version; do not automatically credit them against changed objectives.
- Chat only: maintain the same tables in conversation and export the coverage ledger **alongside** compact progress JSON at session end. Do not squeeze coverage into progress `notes` or claim it survives a compact export: extension fields are dropped. If space is limited, export in labelled parts; do not silently truncate. Ask for both records on a later chat.
- Report, for example: “提供的 Module 1 共 24 页，已核对 24 页；18 个必学点，已讲/验证 18，已闭卷考核 18，通过 16；kp7、kp12 待补教重测。尚未进入下一节。” Adjust the named scope to the actual gate being reported.
- “No omissions” can only mean the inspected, versioned source inventory has been reconciled with teaching and answer evidence. It cannot promise coverage of unseen course material, hidden notes or the whole discipline. Unknown page counts, unreadable visuals and missing attachments must remain visible limitations.
