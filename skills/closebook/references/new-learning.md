# Teaching new material (teach route, B)

Used when the learner wants to learn something they haven't met (routing: `teaching-flow.md` section 2). The goal is a correct first model, built in small steps and checked at every step, then handed to the normal closed-book loop. It is still not a summary: teach only what today's points need, and the learner answers something after every chunk, or, on the section pace, after every section of 2–4 points (section 3).

Why not just ask questions from the start: novices have nothing to retrieve, and for them explicit explanation with worked examples beats unguided problem solving (Kirschner, Sweller & Clark, 2006). Why not one long explanation: new material is learned better in learner-paced segments (Mayer & Chandler, 2001) with practice and a check for understanding after each small step (Rosenshine, 2012). Why the support fades: what helps a novice gets in the way once they can do it (expertise reversal; Kalyuga et al., 2003).

## Contents
1. Where to start
2. The chunk loop
3. Pace: step or section
4. Chunk shape by knowledge type
5. Writing a chunk
6. Sources when teaching from a topic
7. Learning paths for big subjects
8. Session shape and time
9. In the chat
10. On the practice page
11. Records

---

## 1. Where to start

- **Material supplied:** teach from it, in its terms and notation. Add only a prerequisite the material assumes, and say that it's an addition.
- **Topic only:** build the outline yourself (section 6 for sources). For a whole subject, build a path first (section 7).
- **Unclear starting level** (they want to learn X but may know its prerequisites): one starting-point question on the prerequisite, e.g. before derivatives, "What's the slope of y = 3x + 1?". Record it as `phase: "diagnostic"`. Skip it when they said they're starting from zero.

## 2. The chunk loop

A knowledge point is taught in **1–3 chunks**; a chunk is **one idea**. The loop below is the `step` pace: a check after every chunk. Section 3 describes the `section` pace, which keeps the chunks and moves the checks to the end of a section of points.

1. **Optional guess first.** For a conceptual, procedural or judgment point, one quick "What do you think happens if …?" before the first chunk. A wrong guess is fine: an attempted answer before study improves what is learned from the study that follows (Richland, Kornell & Kao, 2009). Unscored (`phase: "diagnostic"`). Skip it when the learner has nothing to reason from, and for arbitrary facts.
2. **Explain the chunk** (section 4 for its shape, section 5 for the rules).
3. **Check.** One question on this chunk only, answered without scrolling back. It must make the learner *use* the idea (apply it to a slightly different case, predict, pick the non-example, do one step), not copy the sentence they just read. Right-answer checks take confidence 1–3 in the same reply. Record as `phase: "teach_check"`: answers given seconds after reading overstate learning, so checks never touch the box, mastery or error list.
4. **Adapt.**
   - Right → next chunk. Right and confident on two checks in a row → compress: drop the remaining worked examples for this point and go on to the next point.
   - Wrong or "don't know" → say what's missing in one sentence, re-explain with a **different** example or angle (never the same words again), then a new check.
   - Wrong twice → smaller step: split the idea, or go back to the prerequisite. Still stuck → note the gap as a weak point, move on, and come back to it after the next point.
   - The learner says "I already know this" → one check; right → go on to the next point (it still gets its retest in step 6).
5. **Next point.** After a point's last chunk, teach the next of today's points the same way. Don't retest yet.
6. **Retests, after all of today's points are taught.** Say that the explanations are now closed, then run the closed-book retests of `teaching-flow.md` section 3, steps 3–4: a new question on each whole point, scored, with confidence, error types and scheduling. Start with the point taught longest ago; when a point has more than one retest question, don't put them back to back. This is ordering for delay, not the interleaving method (`methods/05-interleaving.md` stays off in first-time learning). This is the first scored answer for each point.

Why retests wait: an answer given right after the explanation mostly shows what is still in working memory. Answering after other material has come in between takes more effort and shows better what was retained, the same reason reviews are spaced (`methods/02-spaced-repetition.md`). The checks inside each point catch misunderstandings early, so later points aren't built on a wrong model. With a single point today (15 minutes), its retest follows its last chunk.

## 3. Pace: step or section

A check after every chunk suits a learner with nothing to build on. For a learner with some background, or for easy material, the same cadence becomes a question every two hundred words and breaks the thread of the explanation (expertise reversal again: the support that helps a novice gets in the way once they can follow). So the teach route has two paces, and the learner chooses.

| Pace | One reply explains | Checks | Default for |
|---|---|---|---|
| `step` | one chunk (section 2 as written) | one after every chunk | "zero background / never seen it", or no signal |
| `section` | one **section**: 2–4 related points, all their chunks in order (at most ~8 chunks) | one per point, asked one at a time after the section | "seen a little / know the basics", or the learner asks for it |

**Sections.** On the `section` pace, group today's points into sections of 2–4 that share one idea or one prerequisite, name each section in the outline (a path of 8 points becomes 2–3 sections), and teach a section in one reply: its chunks in order, each still written by section 5's rules, with no check between them. There is no separate word limit for the section: the chunk rules already bound each point. The limit is structural: at most 4 points and about 8 chunks per section, so a section whose points each need 3 chunks holds 2–3 points. Over that → split the section. Then, in the same reply, say that the explanation is now closed and ask the first of the section's checks; the following replies ask the rest, one per point, one per reply: still unscored (`phase: "teach_check"`), still on cases the explanation didn't show, still requiring the learner to *use* the idea. All checks right → the next section.

**Missed section check.** First miss on a point → the usual repair (section 2, step 4): say what's missing in one sentence, re-explain that point from a different angle, one new check on it; the pace stays `section`. Second miss on the same point → drop that point to `step`: re-teach it one chunk at a time with a check after each, say so in one line ("I'll slow down on this one"), then return to `section` for the next section. A miss never changes the pace of other points.

**Asking once.** On the teach route, when the progress file or state has no `settings.teach_pace`, add one line to the opening (`teaching-flow.md` section 1): "Pace: step by step (a short explanation, then a question; good from zero) or by section (2–4 points at once, then the questions; good with some background)?" Store the answer as `settings.teach_pace` and never ask again; later sessions read it. If the learner skips the question or says "start": `step` for "zero / never seen it", otherwise `section`; say which in one line. The practice route never asks.

**Changing it.** The learner can switch at any time in one sentence ("slow down", "bigger chunks", 慢一点、一次多讲点、讲完一节再考). Update `settings.teach_pace`, log a `user_overrides` entry (`scope: "flow"`, `requested: "teach_pace: section"`), and apply it from the next chunk or section. On `step`, after "right, confident" on two checks in a row, you may offer `section` once per session, in one sentence inside the feedback; never again after a no.

**What the pace never changes.** Chunk shape and length (sections 4–5), the anti-spoiler rule, and the retests: every point's scored retest still comes only after all of today's points are taught, starting with the point taught longest ago (section 2, step 6). The pace decides how much is explained between checks, never whether a point is retested.

## 4. Chunk shape by knowledge type

| Type | Chunk shape | Check asks the learner to | Avoid |
|---|---|---|---|
| `conceptual` | Concrete case → the rule in one sentence → a contrast or non-example aimed at the usual misconception. Analogy optional, always with where it breaks (`plain-talk.md`). | Predict a new case, or say why the non-example fails | Definitions before any example |
| `procedural` | Worked example: numbered steps, each with its *why* (≤ ~6 steps). Next chunk: a similar problem with 1–2 steps left blank (a faded example). The retest is the full problem (Sweller & Cooper, 1985; Renkl et al., 2002). | Explain one step's why (self-explanation; Chi et al., 1989), then fill the blank step | A list of steps without reasons; three examples in a row with nothing to do |
| `factual` | The facts in groups of ≤ 4, with whatever structure links them (pattern, contrast, origin of the name). Mnemonic only if it's natural (`methods/10-chunking-mnemonics.md`). | Recall one fact from a cue | Invented "why" stories |
| `language_production` | 2–3 model sentences showing the pattern → the rule in one sentence → one near miss and why it's wrong | Produce a form or sentence, not recognise one | Grammar terminology before any example |
| `judgment` | One worked decision: situation → criteria → choice → why not the obvious alternative | Decide a new case and name the deciding criterion | A rule of thumb without its exceptions |
| `contested` | Each position at its strongest, with its evidence and its limits. No verdict. | Attribute an argument, or name an evidence limit | Presenting one side as the answer |

## 5. Writing a chunk

- **Length:** about 80–200 words (≤ ~400 Chinese characters), plus at most ~12 lines of code or one small table. If it's longer, it's two chunks.
- **Concrete first:** a number, a real sentence, real code, a real case; then the general rule. When teaching programming operations, show a minimal actual code example before stating the rule; a story about variables alone does not show how to use the language.
- **New terms:** at most two per chunk, each described in plain words before its name is used.
- **Nothing extra:** no history, no list of caveats, no "in summary", no preview of later points, no fact the check or retest won't need. Extras go to "optional extension".
- **Never ask "Does that make sense?" or "Any questions?"** Learners can't judge that reliably; the check question finds out instead.
- **Anti-spoiler still applies:** the chunk teaches the idea; the check uses a case the chunk didn't show, and its answer appears only after the learner replies.

## 6. Sources when teaching from a topic

Teaching from general knowledge is allowed, with honesty:

- Say once, in the opening, that the explanations come from general knowledge, not from their course.
- For facts that change or vary by place (versions, APIs, prices, law, medical doses, exam rules), say they need checking against a current source and don't present one version as universal.
- Never invent a citation, a textbook page or a quote. If unsure of a fact, leave it out of the chunk.
- If they have a textbook, syllabus or course page, offer once to follow it instead.

## 7. Learning paths for big subjects

"I want to learn calculus / Rust / music theory" is not one session.

1. Propose a path of **6–12 points in prerequisite order**: titles only, one line each, marked with what today covers. On the `section` pace, group them into named sections of 2–4 points (section 3). Explicitly say that the remaining points are for later sessions, so the full path is not mistaken for today's workload.
2. Teach today's first points (section 8 for how many). Save the rest in the progress file as `status: "planned"`, `leitner_box: 0`, `next_review: null`; planned points are never due.
3. Next session: review today's points first (always retest first), then teach the next planned point. Re-order or trim the path whenever the learner's goal changes.

## 8. Session shape and time

| Time | New points | Notes |
|---|---|---|
| 15 min | 1 | 1–2 chunks with checks, then its retest |
| 30 min | 2–3 | Teach all, then one retest each; short free recall at the end |
| 60 min | 3–4 | Teach all, then the retests; Feynman or free recall synthesis; suggest a break at ~30 min, ideally between teaching and the retests |

The number of points is the same on both paces; on `section`, a 30-minute session is one section and a 60-minute session is two, each followed by its checks before the next section.

Then synthesis, the review list with absolute dates, and saving progress, as in `teaching-flow.md` section 4. The first review comes the next day: teaching once is not learning it.

## 9. In the chat

On the `step` pace, one reply = feedback on the last answer (if any) + **one** chunk + its check question. Then stop. Never two chunks in one reply, never all points at once. On the `section` pace, one reply = feedback (if any) + the whole section's explanation + its first check; the following replies ask the remaining checks one at a time, each with feedback on the previous answer. Either way, after the last point's last check, the next reply gives feedback, says the explanations are closed now, and asks the first retest question.

Example (zh, zero background, eigenvectors, first chunk):

> **Coach:** 你说完全没学过，那我先讲一小块，讲完马上考你一题。
>
> **1 特征向量：被矩阵"只拉伸、不转向"的向量**
> 取矩阵 A = [[2, 0], [0, 3]]。它把向量 (1, 0) 变成 (2, 0)：方向没变，只是长度变成 2 倍。再看 (1, 1)：变成 (2, 3)，方向变了。
> 像 (1, 0) 这样，被 A 作用后方向不变、只被放大或缩小（也可能反向）的非零向量，叫 A 的**特征向量**；放大的倍数 2 叫对应的**特征值**。写成式子是 A·v = λ·v。
>
> 先别往上看：矩阵 B = [[3, 1], [0, 2]]，向量 (1, 0) 是不是 B 的特征向量？如果是，特征值是多少？请回答"是/不是 + 数字 + 信心 1–3"，例如 `X, Y, 2`。

The check uses a matrix the chunk didn't show, and the answer format uses placeholders.

## 10. On the practice page

In lesson data, a point's `teach.chunks` holds the chunks; each has `explain`, optional `example`, `code`, `worked` steps (`do` + `why`), `analogy` with `analogy_limit`, an optional `reteach` for a missed check, and a required `check` (an `mcq`, `plain_qa` with `accept`, `cloze_passage` or `numeric` item). The page shows one chunk and its check at a time, hides each worked step's *why* until the learner has thought about it, shows `reteach` after a miss, goes on to the next point's chunks, and unlocks the retest items only when every point with chunks is taught, starting at the first point. Rules: `html-lesson.md`. The page follows the `step` pace only: one chunk and its check at a time. When the learner prefers the `section` pace, teach in the chat or put the section's explanation before the page and keep the page for the checks and retests.

## 11. Records

- Starting-point questions and guesses: `phase: "diagnostic"`.
- Pace: `settings.teach_pace` (`step` or `section`), written when first asked or chosen; a later change also adds a `user_overrides` entry with `scope: "flow"`.
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
