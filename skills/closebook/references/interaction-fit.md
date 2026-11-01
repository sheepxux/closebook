# Interaction fit: forms, platform levels, downgrades

Step 3 and 4 of the decision chain: knowledge type → method → **interaction form** → **platform capability**. Decide the form only after the method; the platform can only downgrade it.

**The one test:** compared with plain text Q&A, does this form make the learner produce more (a typed number, a filled blank, an order, a prediction) or save time? When the host can render the form (`host-widgets.md`), most forms in the matrix pass by construction and are the default. Plain text is always legal and remains best for one-line points and for answers that are a sentence anyway.

## Contents
1. Interaction ids
2. Fit matrix (plus subject starting points)
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
| `simulation` | Parameter lab: sliders, computed readouts, optional graph; a prediction comes first | The page unlocks the sliders only after the prediction |
| `timeline_fill` | Timeline with blanks | Fill first, then check |
| `compare_table_fill` | Comparison table with blanks | Fill first, then check |
| `numeric` | Type a number (or an expression like `3/4`, `2*pi`); tolerance and unit | Worked solution shown after answering |
| `order_steps` | Put items in order; optional distractors (Parsons problems) or word tiles | Tap to place, arrows to fix |
| `cloze_passage` | A passage with several blanks; optional word bank | Blanks in context, not isolated cards |
| `code_trace` | Read code, predict values/output, then step through the run | The trace stays hidden until the prediction is checked |
| `terminal` | Simulated command line with scripted steps | Only recognises the expected commands; runs nothing |
| `graph` | Plot of y = f(x) with parameter sliders: match a target curve, or predict then explore | The learner's own curve stays hidden until the first check |
| `checklist` | Progress board / review list | Never for teaching content |
| `voice` | Spoken answer | Only for language production, only if supported |

## 2. Fit matrix

| Form | Fits (type + method) | Don't use when | Why not | Cost | Fallback |
|---|---|---|---|---|---|
| `mcq` | `factual` with confusable items; `conceptual` when you can write distractors from **real misconceptions** | `judgment`, `contested`; pure recall with no confusables; Feynman / free recall | Options flatten trade-offs into one "right" pick and turn recall into recognition | Low (but good distractors take effort) | `free_text` / `plain_qa` |
| `flashcard` | `factual`; vocabulary in `language_production`; retrieval + spaced repetition | `conceptual` and up | A one-line back can't hold an explanation; invites rote recall | Low | `plain_qa` cloze |
| `free_text` | Feynman, free recall, self-explanation; `judgment`, `contested` | High-frequency `factual` drills | Typing long answers for one-word facts wastes time | Learner's typing time | `plain_qa` |
| `diagram_fill` | `conceptual` / `procedural` with structure, flow or state change; predict-verify | Single facts; points without structure | A diagram for one fact is decoration | Medium–high | Text outline with blanks; ordered list "put these steps in order" |
| `simulation` | `procedural` or mechanisms where tweaking a parameter reveals the pattern; predict-verify | Benefit unclear; static facts; `contested` | Easy to make something pretty that teaches nothing; the prediction question is what makes it a lesson | Medium (on the page: params, formulas, a predict question) | Predict-verify in plain text with 2–3 concrete parameter values |
| `timeline_fill` | Evolution, sequences in history or versions | No temporal order | — | Medium | Ordered list with blanks |
| `compare_table_fill` | Option comparison, selection, `judgment`; positions in `contested` | Only one item | A table of one is a list | Medium | Markdown table with blanks; or bullet pairs |
| `checklist` | Overall progress; review list with dates | Teaching content | Checklists hide reasoning | Low | Plain list |
| `voice` | `language_production` (pronunciation, fluency) | Platform lacks audio; other types | — | Varies | `free_text`; note the gap |
| `numeric` | Applying a formula or procedure that ends in a number (maths, physics, chemistry, finance, statistics) | The point is the method, not the value; answers that are words | A right number can hide a wrong method: prepare worked steps for feedback after answering (`solution` in HTML data) | Low | `plain_qa` with the number as answer |
| `order_steps` | `procedural` sequences, causal chains, history order, Parsons problems for code, sentence building in `language_production` | Items with no single order (unless you list `alternatives`); `contested` | Ordering is recognition-heavy: the learner sees every item | Low | Numbered list "put these in order: C, A, D, B" |
| `cloze_passage` | `factual` terms in context (definitions, laws, biology, chemistry); grammar and collocations | One-blank questions (use `plain_qa`); blanks whose wording varies a lot | Free wording can't be matched against a key | Low | Text with `___` blanks |
| `code_trace` | Reading and predicting code (`procedural`); predict-verify | Writing code from scratch (use `free_text` and review it in chat); `factual` | Tracing is a prerequisite for writing, not a replacement | Medium | Code block + "what does it print?" in text |
| `terminal` | Command-line skills where the learner must produce the exact command (git, shell, package managers) | Open-ended tasks with many valid commands you can't list | It only accepts the commands you list, so missing variants mark right answers wrong | Medium | Ask for the command in text; check it yourself |
| `graph` | `conceptual` links between a formula and its shape (functions, physics laws, supply and demand); predict-verify | Facts; anything without a formula | Sliding until it looks right is guessing; use `target` (curve hidden until checked) or `predict` | Medium | 2–3 concrete parameter values + "what changes?" in text |
| `plain_qa` | Everything; best for simple points answerable in one line | — | — | Lowest | — |

**Must-follow details**
- Flashcards: the learner answers (types it, or says it to themselves and commits) **before** flipping.
- Pure recall → flashcard or cloze. MCQ only when there are genuinely confusable options.
- Diagrams, timelines and tables: **fill or predict first**, then show the complete version. A finished diagram shown up front is re-reading.
- Method beats interaction: if the method needs free text (Feynman, free recall, contested reasoning), don't replace it with options.
- Produce rather than pick where you can: a typed number, a typed command or a filled blank is recall; options are recognition.

**Subject starting points.** The knowledge type still decides; the subject only suggests which form to try first. These are defaults, not rules.

| Subject | Try first | Why (evidence) |
|---|---|---|
| Programming | `code_trace` before `free_text` (writing); `order_steps` with `monospace` and distractors (Parsons problems) | Novices who can't trace code reliably struggle to write it (Lister et al., 2004; Lopez et al., 2008). Parsons problems took less time than writing or fixing the same code with similar learning gains (Ericson et al., 2017); distractor lines target specific misconceptions (Parsons & Haden, 2006; Denny et al., 2008). |
| Command line, git, devops | `terminal` | Typing the command is retrieval of the exact form you'll need later; recognising it among options is a different, easier task. |
| Maths, physics, chemistry, finance | `numeric` with `solution`; `graph` for formula ↔ shape | Studying worked solutions helps novices; fading them into own attempts helps further (Sweller & Cooper, 1985; Renkl et al., 2002). Linking an equation to its graph is a multiple-representations task (Ainsworth, 2006). |
| Science mechanisms, economics models | `simulation` (prediction first) or `graph` with `predict` | Interactive simulations can support conceptual learning when they're built around exploration with a goal (Wieman et al., 2008); committing to a prediction first follows predict-observe-explain (White & Gunstone, 1992). |
| Biology, law, definitions | `cloze_passage`; `order_steps` for processes | Recall in context; the passage keeps the relationships the isolated fact loses. |
| History | `timeline_fill`, `order_steps` | Order and dates are the content. |
| Languages | `cloze_passage` (grammar, collocations); `order_steps` with `layout: "tiles"` (word order); `flashcard` (vocabulary) | Production practice: building the sentence rather than choosing it. Pronunciation needs audio, which the page doesn't have. |

## 3. Decision rules

1. **Cap:** at most 1–2 forms per knowledge point. If one plain text turn covers it, use no component.
2. **Mobile / short sessions:** prefer tap-to-answer forms (`mcq`, `flashcard`) where they fit; avoid long typing and drag-and-drop.
3. **Consistency:** in one session, the same kind of question uses the same form. Don't vary forms for variety.
4. **Renderer available → form by default; no decoration.** With a host widget, question tool or MCP card available, every question that has a form in the matrix uses it. Plain text is for forms whose answer is a sentence typed in chat anyway (Feynman, free recall, contested reasoning) and for simple one-line points; without any renderer, use the Level 0 downgrade (section 5). A component must carry the question itself; never add one that only displays.
5. **Not supported by the platform** → nearest available form (section 5) + one sentence: "I can't show clickable cards here, so I'll use lettered options; reply like `B 2`."
6. **Not covered by the matrix** → `plain_qa`.
7. **User asks for an unfit form** (e.g. MCQ for a contested question): one sentence of risk and an alternative ("Options would make one view look 'correct'; a short written answer keeps the trade-off. Still want options?"). If they still choose it after that explanation, honor it and record `interaction_override_by_user`. A previous suggestion of a format does not establish that its trade-off was explained. In chat-only mode, include a short visible session note now (for example, "Recorded as your chosen format"), then proceed; carry it into the next progress export. Do not repeat a warning already given.

## 4. Platform levels and capability detection

| Level | What it means | Examples of forms |
|---|---|---|
| 0 | Plain text only. Must always work. | `plain_qa`, lettered `mcq`, text flashcards, markdown tables if they render |
| 1 | In-chat interaction: the host's own widget facility or question tool (`host-widgets.md`), or the optional closebook MCP App | A host widget renders any form you can draw in HTML/SVG and sends the answer back; a question tool shows 2–4 options; closebook MCP supports lesson cards plus `mcq`, `free_text`, `numeric`, `cloze_passage`, `order_steps`, `flashcard` |
| 2 | You can produce a single self-contained HTML page or artifact the learner can open | `assets/lesson-template.html` with all forms |

**Detection (once per session):**
1. Look at what you can actually do in this environment: available tools, skills and plugins, the ability to create files or artifacts, rendered UI elements you've been told about. Concrete signals: a `visualize` skill or plugin, a `show_widget` tool, a `request_user_input` or similar question tool, closebook MCP tools, file write access (`host-widgets.md` section 2). Only concrete evidence counts, and the matching tool's own rules are read before its first use.
2. When unsure, assume **Level 0**. Don't ask the learner to debug your UI; at most ask once "Do you see clickable options above?" if you tried a Level 1 element and got no confirmation.
3. Keep the chosen form and select its renderer in the order below. Levels are capabilities, not a ranking: the ability to build HTML does not override a suitable native quiz tool.
4. Never describe a form you can't render ("click the card below") on a Level 0 platform.

**Renderer order (within the chosen form):**

Apply the same order on every agent platform, including future or unfamiliar hosts. Discover capabilities from actual available tools and their usage rules; never branch on a brand name or prefer closebook merely because its MCP server is installed.

1. Honor an explicit renderer request, such as testing closebook MCP or producing an offline practice page.
2. Otherwise prefer the **agent's own components** (`host-widgets.md`): first an inline widget facility (Codex/ChatGPT Visualize, Claude Code `show_widget`) that renders the real question and sends the answer back to the chat; then a built-in question tool with options, when it is listed this turn and its own rules allow optional questions. Read the usage rules first: an approval/permission tool, or one whose rules forbid quizzes or reserve it for decisions, is not a quiz tool. A product name alone proves nothing; a listed tool whose description says it renders inline and can send a message back does.
3. If native interaction is absent, cannot express this question, or fails, use the **optional closebook MCP** when available and suitable. Use `show_lesson` for a teaching chunk and `show_exercise` for supported forms; neither display nor reading acknowledgement counts as mastery. Read `mcp-cards.md` for the supported forms and limits; do not call an empty demo during a real lesson. Do not invoke both renderers for the same unanswered question.
4. If the card is unavailable or unsuitable, use **HTML when it clearly pays off**, otherwise **plain text**. Preserve the question and its learning purpose. Never turn a production task or open explanation into MCQ just to use the fallback.

Choose interface language from the learner's communication language, independently of the subject text. A Chinese-speaking learner may answer an English passage without English buttons or forced English feedback. When the renderer accepts `locale`, pass it explicitly.

Detect once, reassess after a failure or tool change. A successful tool call is not proof of visible UI or delivered answers. If a renderer fails, explain briefly and continue with the same question in the next suitable form; do not repeatedly retry, pretend a click happened, or ask the learner to debug setup. Host-controlled MCP process startup can happen before any tool call; this priority governs which renderer the coach uses, not when the host spawns processes.

**When to use Level 2 (HTML page):** when requested, or when the in-chat choices cannot meet a useful interaction need. Typical cases: an offline or reusable practice page; a review deck of ≥ 8 MCQ/flashcard items; a form that text can't express well (`diagram_fill`, `simulation`, `graph`, `code_trace`'s step-through, `terminal`, `order_steps` by tapping). The page can't grade free text (see below), so the chat remains the main channel. How to build the page: `html-lesson.md`. On a host with a widget facility, `diagram_fill`, `graph`, `code_trace` and `order_steps` render inline (`host-widgets.md` section 5), so the page is mainly for offline or reusable practice there.

**Static page honesty:** a static HTML page can check answers that have a stored key (multiple choice, blanks, numbers, orders, commands, graph targets), but it can't grade free-text answers by itself, and its terminal only knows the commands you listed. For `free_text` and free recall it shows a reference checklist and asks the learner to self-assess, plus an "export my answers" button. Grading is a round trip through the chat: the learner pastes the answers, you grade them and reply with a grading block, and the page shows your results once they paste it back (`html-lesson.md`). Never present self-assessment, or this round trip, as automatic grading.

## 5. Downgrade map

| Wanted | Level 1 | Level 0 |
|---|---|---|
| `mcq` | Host widget or question tool first; closebook MCP card second | Lettered options in text; answer `B 2` (option + confidence) |
| `flashcard` | Host widget (front + answer field; the back is revealed in chat), then MCP recall-before-flip card | Front in one reply; back after the learner answers |
| `free_text`, `plain_qa` | Host widget answer box, then MCP `free_text` when a card helps | Answer in chat |
| `diagram_fill` | Host widget: SVG with `?` inputs; full diagram after the answer | Numbered text outline or ordered list with blanks; ASCII arrows if helpful |
| `simulation`, `graph` | Host widget: a prediction question first, sliders after the answer | Plain-text predict-verify with 2–3 concrete parameter values ("L = 1 m gives T ≈ 2.0 s; what does L = 4 m give?") |
| `numeric` | Host widget value/unit fields, then MCP value/unit/working fields; assistant grades | `plain_qa`; check the number yourself and show the worked steps |
| `order_steps` | Host widget tap-to-order, then MCP select/reorder with optional distractors | Letter the items and ask for the order ("C A D B") |
| `cloze_passage` | Host widget passage with inputs, then MCP passage with input fields | The passage with numbered `___(1)` blanks; answer as a numbered list |
| `code_trace` | Host widget: code + prediction inputs; the trace after the answer | Code block + prediction questions; after the answers, a short table of variable values per step |
| `terminal` | Host widget: one command input | Ask for each command in text and check it yourself; you can accept valid variants the page couldn't |
| `timeline_fill`, `compare_table_fill` | Host widget or native table with input cells | Markdown table with `___`; plain bullet pairs if tables don't render |
| `checklist` | Native checklist | Plain list with dates |
| `voice` | — | `free_text`; mention that pronunciation can't be checked here |

Some platforms limit the number of quick-reply options. If a native MCQ cannot show all options, try the suitable MCP fallback, then HTML/text. Never drop options to fit a renderer.

## 6. Recording

Per knowledge point (extension fields):
- `interaction_selected`: the form actually used.
- `interaction_downgraded_from`: `{from, reason}` when the platform forced a downgrade; the reason names the renderers tried (e.g. `no host widget; MCP absent`).
- `interaction_override_by_user`: `{requested, recommended, risk_note, at}`.
- Attempts may carry `interaction` and `duration_sec`, so `progress_tool.py interaction-stats` can compare forms by accuracy and time.
