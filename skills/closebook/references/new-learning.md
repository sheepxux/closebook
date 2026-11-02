# Teaching new material (teach route, B)

Used when the learner wants to learn material they have not met (`teaching-flow.md` section 2). The agent arranges coherent teaching units according to course content, total workload, prerequisites, background, time and observed understanding. A unit can span one difficult idea, several related points, a complete example or an entire source section. Keep the source inventory granular for evidence; teaching delivery need not follow that granularity.

Novices need explanation and worked examples before retrieval (Kirschner, Sweller & Clark, 2006). Segmentation and learner control can help (Mayer & Chandler, 2001), while excessive guidance can impede experienced learners (Kalyuga et al., 2003). These principles inform judgment; they do not prescribe fixed chunk sizes or a question after every fragment.

## Contents
1. Where to start
2. The teaching loop
3. Agent planning and learner preferences
4. Teaching shape by knowledge type
5. Writing a teaching unit
6. Sources when teaching from a topic
7. Learning paths for big subjects
8. Session shape and time
9. In the chat
10. On the practice page
11. Records

---

## 1. Where to start

- **Course material supplied:** first inventory it using `source-driven-course.md`, retaining all required points and source locators. Teach from it in its terms and notation. Label added prerequisites and practice as supplemental; they do not replace source requirements.
- **Topic only:** build the outline yourself (section 6 for sources). For a whole subject, build a path first (section 7).
- **Unclear starting level** (they want to learn X but may know its prerequisites): one starting-point question on the prerequisite, e.g. before derivatives, "What's the slope of y = 3x + 1?". Record it as `phase: "diagnostic"`. Skip it when they said they're starting from zero.

## 2. The teaching loop

1. **Plan the unit.** Choose its scope from the actual content and workload. Keep an explanation, derivation or worked example together when that makes it easier to follow. Use smaller steps where prerequisites or mistakes call for them; use larger units for straightforward or closely related material. State the planned unit briefly, without making the learner choose technical pacing settings.
2. **Explain.** Give concrete examples, the underlying rule and necessary reasoning, shaped by the knowledge type (section 4). A useful visual may accompany a process, structure or mechanism (`host-widgets.md` section 9). A prerequisite guess is optional and unscored; never quiz a novice on wholly unseen material before teaching it.
3. **Check at a useful boundary.** Ask the learner to apply, predict, explain or distinguish a new case with the explanation out of sight. Cover every point in the unit through the checks and retests, retaining per-point mappings; one combined task needs separate criteria for each point it assesses. In chat ask one question at a time. Record immediate checks as `teach_check`; they do not change mastery, the box or errors. Collect confidence with a right-answer response.
4. **Adapt.** Correct and confident answers allow faster progress or fewer repeated examples. An error calls for a different example or explanation of the specific gap. Repeated errors call for more support, a smaller step or a prerequisite check on that point; do not automatically fragment unrelated material. A claimed known point can be verified instead of re-taught.
5. **Retest after the teaching block.** Close the explanations, then ask new scored questions on every taught point (`teaching-flow.md` section 3, steps 3–4), starting with the point taught longest ago. Do not put several retests of the same point back to back when other taught points are available. Immediate checks cannot stand in for these retests.

For source-driven courses, a source-section boundary ends the teaching block: reconcile and pass its gate (`source-driven-course.md`) before the next source section, even within one day. A section may span several units or sessions. Retests wait until after the teaching block to distinguish retrieval from immediate familiarity; a one-point block still gets its own retest.

## 3. Agent planning and learner preferences

**Default: agent-arranged.** No mandatory question about step-by-step versus section pace, and no fixed chunk count, word cap, point count per unit or number of units per session. Choose and revise the plan from the course content and amount of material, difficulty, prerequisite structure, learner responses and available time. A zero-background learner may still benefit from a coherent full example before checking; background alone does not force tiny steps. Preserve interaction, source coverage and closed-book gates at any teaching size.

**Explicit preferences.** The learner can request smaller steps, fuller sections, slower or faster explanations. Honour that choice and save it. Existing `settings.teach_pace` values remain supported: `step` expresses a preference for frequent checks and smaller units; `section` expresses a preference for connected explanations before the checks. They are not universal limits on the number of ideas, words or points. Leave the field absent when no preference is stated; this means agent-arranged pacing. Returning to agent-arranged pacing clears the field and is recorded in `user_overrides` (`scope: "flow"`). Record other explicit changes there too, without treating every automatic adjustment as a user request.

**Checks together.** A host section-review widget can step through several questions with one summary back (`host-widgets.md` section 8). Its batch size is a presentation choice, not a teaching-unit or course-coverage limit. In plain text ask one question per reply. Once all checks are answered, run the closed-book retests and applicable source gates rather than advancing on checks alone.

## 4. Teaching shape by knowledge type

| Type | Teaching shape | Check asks the learner to | Avoid |
|---|---|---|---|
| `conceptual` | Concrete case → the rule in one sentence → a contrast or non-example aimed at the usual misconception. Analogy optional, always with where it breaks (`plain-talk.md`). | Predict a new case, or say why the non-example fails | Definitions before any example |
| `procedural` | Worked example: numbered steps, each with its *why* (with the steps needed for the task). Then: a similar problem with 1–2 steps left blank (a faded example). The retest is the full problem (Sweller & Cooper, 1985; Renkl et al., 2002). | Explain one step's why (self-explanation; Chi et al., 1989), then fill the blank step | A list of steps without reasons; three examples in a row with nothing to do |
| `factual` | The facts in meaningful groups, with whatever structure links them (pattern, contrast, origin of the name). Mnemonic only if it's natural (`methods/10-chunking-mnemonics.md`). | Recall one fact from a cue | Invented "why" stories |
| `language_production` | Model sentences showing the pattern → the rule in one sentence → one near miss and why it's wrong | Produce a form or sentence, not recognise one | Grammar terminology before any example |
| `judgment` | One worked decision: situation → criteria → choice → why not the obvious alternative | Decide a new case and name the deciding criterion | A rule of thumb without its exceptions |
| `contested` | Each position at its strongest, with its evidence and its limits. No verdict. | Attribute an argument, or name an evidence limit | Presenting one side as the answer |

## 5. Writing a teaching unit

- **Scope and length:** use what the coherent explanation needs. Keep closely connected reasoning together; shorten repetition and split only at meaningful boundaries or when learner responses show overload. There is no fixed word, code-line or idea count.
- **Concrete first:** a number, a real sentence, real code, a real case; then the general rule. When teaching programming operations, show a minimal actual code example before stating the rule; a story about variables alone does not show how to use the language.
- **New terms:** introduce unfamiliar terms in plain words with enough context; revisit prerequisites when needed.
- **Nothing extra:** no history, no list of caveats, no "in summary", no preview of later points, focus on the learning objectives. Supplemental material can be labelled optional; source requirements remain required.
- **Never ask "Does that make sense?" or "Any questions?"** Learners can't judge that reliably; the check question finds out instead.
- **Anti-spoiler still applies:** the chunk teaches the idea; the check uses a case the chunk didn't show, and its answer appears only after the learner replies.

## 6. Sources when teaching from a topic

Teaching from general knowledge is allowed, with honesty:

- Say once, in the opening, that the explanations come from general knowledge, not from their course.
- For facts that change or vary by place (versions, APIs, prices, law, medical doses, exam rules), say they need checking against a current source and don't present one version as universal.
- Never invent a citation, a textbook page or a quote. If unsure of a fact, leave it out of the chunk.
- If they have a textbook, syllabus or course page, offer once to follow it instead.

## 7. Learning paths for big subjects

"I want to learn calculus / Rust / music theory" is not one session. The proposed path below is for **topic-only** learning. With course sources, retain the complete source inventory, order and gates from `source-driven-course.md`; select only today's workload, without capping the course's point count.

1. Propose a path of **points in prerequisite order**, sized to the subject and goal: titles only, one line each, marked with what today covers. Group connected points into teaching units as useful (section 3). Explicitly say that the remaining points are for later sessions, so the full path is not mistaken for today's workload.
2. Teach today's first points (section 8 for how many). Save the rest in the progress file as `status: "planned"`, `leitner_box: 0`, `next_review: null`; planned points are never due.
3. Next session: review today's points first (always retest first), then teach the next planned point. Re-order or trim the path whenever the learner's goal changes.

## 8. Session shape and time

Fit the workload to the material and the learner's time; do not infer a fixed number of points from 15, 30 or 60 minutes. Dense proofs may need a whole session, while a familiar section may fit one connected explanation. Leave time for checks and retests. Save unfinished required points as `planned`; never drop them to satisfy a time estimate. Suggest a break during a long session when useful.

End with synthesis, dated reviews and saving progress (`teaching-flow.md` section 4). The first review is the next day: teaching completion alone does not establish durable learning.

## 9. In the chat

A reply may explain the coherent unit the agent planned, including several related points, and end with one unanswered check. It need not stop after every small fragment. Follow-up replies collect the remaining checks one at a time and repair specific gaps. Once the block is taught and checked, close the explanations and begin its delayed retests. Respect a learner's explicit request for smaller steps or complete sections.

## 10. On the practice page

In lesson data, a point's `teach.chunks` holds the chunks; each has `explain`, optional `example`, `code`, `worked` steps (`do` + `why`), `analogy` with `analogy_limit`, an optional `reteach` for a missed check, and a required `check` (an `mcq`, `plain_qa` with `accept`, `cloze_passage` or `numeric` item). The page shows one chunk and its check at a time, hides each worked step's *why* until the learner has thought about it, shows `reteach` after a miss, goes on to the next point's chunks, and unlocks the retest items only when every point with chunks is taught, starting at the first point. Rules: `html-lesson.md`. The page has two rendering modes through the lesson's `teach_pace` field (choose the one that fits the plan, respecting any saved preference): on `section` it shows a section's chunks together, then asks one check per point (the last chunk's check), and a point missed twice drops to one chunk at a time.

Assessments that cover a day's or several days' points use the page's **exam mode** (`html-lesson.md`): answers lock without feedback, everything is checked at hand-in, then a report.

## 11. Records

- Starting-point questions and guesses: `phase: "diagnostic"`.
- Pace: leave `settings.teach_pace` absent for agent-arranged pacing; save `step` or `section` when requested by the learner. Explicit changes add a `user_overrides` entry with `scope: "flow"`.
- Checks: `phase: "teach_check"`; they never change the box, mastery or error list. A point that was taught but not yet retested (the session ended early) is due the next day, so the next session opens with its retest; `progress_tool.py` sets this.
- Retests: `phase: "retest"`, as usual.
- Session: `entry_path: "B"`.
- Points saved for later: `status: "planned"`.

## Sources

- Chi, M. T. H., Bassok, M., Lewis, M. W., Reimann, P., & Glaser, R. (1989). Self-explanations: How students study and use examples in learning to solve problems. *Cognitive Science, 13*(2), 145–182.
- Kalyuga, S., Ayres, P., Chandler, P., & Sweller, J. (2003). The expertise reversal effect. *Educational Psychologist, 38*(1), 23–31.
- Kirschner, P. A., Sweller, J., & Clark, R. E. (2006). Why minimal guidance during instruction does not work. *Educational Psychologist, 41*(2), 75–86.
- Mayer, R. E., & Chandler, P. (2001). When learning is just a click away: Does simple user interaction foster deeper understanding of multimedia messages? *Journal of Educational Psychology, 93*(2), 390–397.
- Renkl, A., Atkinson, R. K., Maier, U. H., & Staley, R. (2002). From example study to problem solving: Smooth transitions help learning. *Journal of Experimental Education, 70*(4), 293–315.
- Richland, L. E., Kornell, N., & Kao, L. S. (2009). The pretesting effect: Do unsuccessful retrieval attempts enhance learning? *Journal of Experimental Psychology: Applied, 15*(3), 243–257.
- Rosenshine, B. (2012). Principles of instruction: Research-based strategies that all teachers should know. *American Educator, 36*(1), 12–19, 39.
- Sweller, J., & Cooper, G. A. (1985). The use of worked examples as a substitute for problem solving in learning algebra. *Cognition and Instruction, 2*(1), 59–89.
