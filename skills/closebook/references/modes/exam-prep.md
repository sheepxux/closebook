# Mode: exam prep (备考)

**When to load:** the learner mentions an exam, test, certification, interview, a date they must be ready by, or past papers.

**Bias (never overrides `method-fit.md`):** retrieval in exam-like formats + error review + interleaving + syllabus coverage tracking.

## What changes
1. **Ask once for the exam date** (absolute date) and format (MCQ, short answer, essay, practical). Store in the session `notes` and the progress file's `exam` object.
2. **Coverage first.** In the opening, map the syllabus or material to knowledge points and mark which are covered so far. Show coverage as a fraction ("6/14 syllabus points assessed") in the review list.
3. **Exam-format questions.** Match the exam's question types in retests. MCQ exams still get some free recall: recall trains the memory MCQs depend on.
4. **Error review is central.** At the end of each session, show error counts by type (`progress_tool.py error-stats`) and the top high-confidence errors.
5. **Interleaving on** as soon as its condition holds, including in first-time sessions after the first 2 points are learned, because exams mix topics.
6. **Schedule toward the date.** If the exam is closer than the next interval, schedule the review for (exam date − 1 day) instead and say so. Don't compress all boxes; just cap `next_review` at that date.
7. **Timed practice** only on request ("simulate the exam"): no hints, then feedback after the whole set, not after each question.

## What doesn't change
- Contested or judgment points still get open answers, even if the exam is MCQ-heavy. If the exam itself asks MCQs on them, practise both and say why.
- Feynman stays for core conceptual points: understanding makes exam variants answerable.

## Progress fields
Top-level `exam: {date, format, syllabus_points_total}`; session `mode: "exam"`.
