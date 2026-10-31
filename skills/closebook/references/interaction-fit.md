# Interaction fit: forms, platform levels, downgrades

Step 3 and 4 of the decision chain: knowledge type → method → **interaction form** → **platform capability**. Decide the form only after the method; the platform can only downgrade it.

**The one test:** compared with plain text Q&A, does this form make learning more effective or save time? If you can't name the gain, use plain text. Plain text is always legal and often best for simple points.

## Contents
1. Interaction ids
2. Fit matrix
3. Decision rules
4. Platform levels and capability detection
5. Downgrade map
6. Recording

---

## 1. Interaction ids

Shared with the HTML lesson template and the progress schema.

| id | Form | Notes |
|---|---|---|
| `plain_qa` | Plain text question and answer (incl. cloze, short answer) | Level 0 baseline |
| `mcq` | Multiple choice card | Confidence is collected in the same step |
| `flashcard` | Front → recall → flip | Learner must attempt before flipping |
| `free_text` | Answer box for longer text | Feynman, free recall, essays |
| `diagram_fill` | Diagram / flowchart with blanks or a prediction step | Predict or fill first, then full version |
| `simulation` | Runnable sandbox, parameter sliders | Expensive to build |
| `timeline_fill` | Timeline with blanks | Fill first, then check |
| `compare_table_fill` | Comparison table with blanks | Fill first, then check |
| `checklist` | Progress board / review list | Never for teaching content |
| `voice` | Spoken answer | Only for language production, only if supported |

## 2. Fit matrix

| Form | Fits (type + method) | Don't use when | Why not | Cost | Fallback |
|---|---|---|---|---|---|
| `mcq` | `factual` with confusable items; `conceptual` when you can write distractors from **real misconceptions** | `judgment`, `contested`; pure recall with no confusables; Feynman / free recall | Options flatten trade-offs into one "right" pick and turn recall into recognition | Low (but good distractors take effort) | `free_text` / `plain_qa` |
| `flashcard` | `factual`; vocabulary in `language_production`; retrieval + spaced repetition | `conceptual` and up | A one-line back can't hold an explanation; invites rote recall | Low | `plain_qa` cloze |
| `free_text` | Feynman, free recall, self-explanation; `judgment`, `contested` | High-frequency `factual` drills | Typing long answers for one-word facts wastes time | Learner's typing time | `plain_qa` |
| `diagram_fill` | `conceptual` / `procedural` with structure, flow or state change; predict-verify | Single facts; points without structure | A diagram for one fact is decoration | Medium–high | Text outline with blanks; ordered list "put these steps in order" |
| `simulation` | `procedural` or mechanisms where tweaking a parameter reveals the pattern; predict-verify | Benefit unclear; static facts; `contested` | High build cost; easy to make something pretty that teaches nothing | High | Predict-verify in plain text with 2–3 concrete parameter values |
| `timeline_fill` | Evolution, sequences in history or versions | No temporal order | — | Medium | Ordered list with blanks |
| `compare_table_fill` | Option comparison, selection, `judgment`; positions in `contested` | Only one item | A table of one is a list | Medium | Markdown table with blanks; or bullet pairs |
| `checklist` | Overall progress; review list with dates | Teaching content | Checklists hide reasoning | Low | Plain list |
| `voice` | `language_production` (pronunciation, fluency) | Platform lacks audio; other types | — | Varies | `free_text`; note the gap |
| `plain_qa` | Everything; best for simple points answerable in one line | — | — | Lowest | — |

**Must-follow details**
- Flashcards: the learner answers (types it, or says it to themselves and commits) **before** flipping.
- Pure recall → flashcard or cloze. MCQ only when there are genuinely confusable options.
- Diagrams, timelines and tables: **fill or predict first**, then show the complete version. A finished diagram shown up front is re-reading.
- Method beats interaction: if the method needs free text (Feynman, free recall, contested reasoning), don't replace it with options.

## 3. Decision rules

1. **Cap:** at most 1–2 forms per knowledge point. If one plain text turn covers it, use no component.
2. **Mobile / short sessions:** prefer tap-to-answer forms (`mcq`, `flashcard`) where they fit; avoid long typing and drag-and-drop.
3. **Consistency:** in one session, the same kind of question uses the same form. Don't vary forms for variety.
4. **No interaction inflation.** Before using any component, finish this sentence: "This saves the learner ___ or helps them remember ___ better than plain text." If you can't, use plain text.
5. **Not supported by the platform** → nearest available form (section 5) + one sentence: "I can't show clickable cards here, so I'll use lettered options; reply like `B 2`."
6. **Not covered by the matrix** → `plain_qa`.
7. **User asks for an unfit form** (e.g. MCQ for a contested question): one sentence of risk and an alternative ("Options would make one view look 'correct'; a short written answer keeps the trade-off. Still want options?"). If they insist, do it and record `interaction_override_by_user`.

## 4. Platform levels and capability detection

| Level | What it means | Examples of forms |
|---|---|---|
| 0 | Plain text only. Must always work. | `plain_qa`, lettered `mcq`, text flashcards, markdown tables if they render |
| 1 | Native clickable options, quiz/flashcard cards, checklists rendered by the platform | Native `mcq`, `flashcard`, `checklist` |
| 2 | You can produce a single self-contained HTML page or artifact the learner can open | `assets/lesson-template.html` with all forms |

**Detection (once per session):**
1. Look at what you can actually do in this environment: available tools, the ability to create files or artifacts, rendered UI elements you've been told about. Only concrete evidence counts.
2. When unsure, assume **Level 0**. Don't ask the learner to debug your UI; at most ask once "Do you see clickable options above?" if you tried a Level 1 element and got no confirmation.
3. Pick the richest form **within the fit result** that the level supports. A higher level never adds forms the matrix didn't choose.
4. Never describe a form you can't render ("click the card below") on a Level 0 platform.

**When to use Level 2 (HTML page):** only when it clearly pays off. Typical cases: the learner wants an offline or reusable practice page; a review deck of ≥ 8 MCQ/flashcard items; a `diagram_fill` or `simulation` that text can't express. The page can't grade free text (see below), so the chat remains the main channel. How to build the page: `html-lesson.md`.

**Static page honesty:** a static HTML page can check MCQ and flashcard answers against stored keys, but it can't grade free-text answers. For `free_text` and free recall it shows a reference checklist and asks the learner to self-assess, plus an "export my answers" button for pasting back into chat. Never present self-assessment as automatic grading.

## 5. Downgrade map

| Wanted | Level 1 | Level 0 |
|---|---|---|
| `mcq` | Native option chips/cards | Lettered options in text; answer `B 2` (option + confidence) |
| `flashcard` | Native card if it requires an attempt before flipping; otherwise text | Front in one reply; back after the learner answers |
| `diagram_fill` | — | Numbered text outline or ordered list with blanks; ASCII arrows if helpful |
| `simulation` | — | Plain-text predict-verify with 2–3 concrete parameter values |
| `timeline_fill`, `compare_table_fill` | Native table if available | Markdown table with `___`; plain bullet pairs if tables don't render |
| `checklist` | Native checklist | Plain list with dates |
| `voice` | — | `free_text`; mention that pronunciation can't be checked here |

Some platforms limit the number of quick-reply options (e.g. only a few suggestion bubbles). If an MCQ has more options than the platform shows, use the Level 0 lettered format instead of dropping options.

## 6. Recording

Per knowledge point (extension fields):
- `interaction_selected`: the form actually used.
- `interaction_downgraded_from`: `{from, reason}` when the platform forced a downgrade.
- `interaction_override_by_user`: `{requested, recommended, risk_note, at}`.
- Attempts may carry `interaction` and `duration_sec`, so `progress_tool.py interaction-stats` can compare forms by accuracy and time.
