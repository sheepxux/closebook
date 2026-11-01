# Host widgets: the agent's own interactive components

closebook ships no UI of its own that an agent must install. Many agent hosts already have one: a way to render an interactive widget inside the conversation and send a message back to the chat. Those come **first** in the renderer order (`interaction-fit.md` section 4), before the optional closebook MCP, the HTML page and plain text. This file says how to recognise them, how to build a closebook question with them, and what never to do.

## Contents
1. What counts as a host widget
2. Known hosts and their signals
3. Detection and the one-line notice
4. Building a question widget (contract shared by every form)
5. Recipes per interaction form
6. Question tools with options
7. Fallbacks and recording
8. Section review widget: 3–5 questions in one widget
9. Teaching with visuals

---

## 1. What counts as a host widget

**The test** (all three must hold; a product name, a plugin listing or "it can draw buttons" proves none of them):

1. It shows the **real question**: the full stem, every option, every blank, in the learner's language.
2. The learner **answers inside it**: a click, a typed value, an order, a filled blank.
3. **Something comes back to you**: a message the widget sends to the chat, a tool result, or a stored state you can read. Rendering alone tells you nothing, and a confirmation that the widget was displayed is not an answer either.

Two families pass this test:

| Family | How it works | Examples |
|---|---|---|
| **Inline widget facility** | You write HTML or SVG, the host renders it inline, and when the learner clicks the widget's button the host's own API posts their answer into the chat | Codex app and ChatGPT: Visualize (`visualize{"path": …}` + `window.openai.sendFollowUpMessage`); Claude Code app: `show_widget` + `sendPrompt(text)` |
| **Question tool with options** | A built-in tool shows 2–4 options (plus a free "Other") and returns the choice | Codex `request_user_input` (Plan mode by default); Claude Code `AskUserQuestion` (see section 6 for its limits) |

A tool that only collects **approvals or permissions** is never a quiz. A tool whose own rules forbid quizzes stays off limits even if it could draw the options.

## 2. Known hosts and their signals

Facts checked on 2026-11-01; see `docs/platform-verification.md` for sources. Hosts change: trust what is actually listed in the session over this table.

| Host | Signal that it exists | How a question goes out | How the result comes back | Limits |
|---|---|---|---|---|
| **Codex desktop app** | A `visualize` skill or plugin is listed (`$visualize`) | Read that skill first and follow it: write an HTML **fragment** (no `<html>`/`<body>`) to a writable task directory, put `visualize{"path":"<absolute path>"}` on its own line in the reply | When the learner clicks the button, `window.openai.sendFollowUpMessage({ prompt, title })` posts `prompt` into the chat after the host's confirmation dialog | Codex CLI and the IDE extension do not render it. Fragment ≤ 1 MB, no `fetch`; CDN allowlist only. State: `window.openai.setWidgetState` |
| **Codex (any mode)** | `request_user_input` is in this turn's tool list | One call: 1–3 questions, each 2–3 options; the client adds "Other" | The tool result holds the choices | Plan mode by default; in Default mode only when the host enables it (`features.default_mode_request_user_input`, marked under development on 2026-11-01). Its host rules: optional questions that improve the work, never permissions. Three options at most, so a four-option item stays in another renderer |
| **ChatGPT** | `@Visualize` is available in the composer or listed as a plugin | Same fragment model as the Codex app | Same `sendFollowUpMessage` | Verified in docs for ChatGPT; no closebook test yet |
| **Claude Code desktop app** | A `show_widget` tool (often with a `read_me` companion) is listed | Call `read_me` once (module `interactive`), then `show_widget` with the HTML or SVG | When the learner clicks the button, the global `sendPrompt(text)` posts `text` into the chat | Seen in the Claude Code desktop app on 2026-11-01; availability in other Claude clients unverified. `AskUserQuestion` is reserved by its own rules for decisions the user must make, so it is **not** a quiz tool there |
| **Gemini** | — | — | — | No inline widget or question tool verified; Canvas renders pages, not chat widgets. Next renderer in order |
| **Any other host** | A listed tool or skill whose description says it renders HTML/SVG or widgets inline **and** names a way to send a message or return a value | Follow that tool's own instructions | As described by the tool | If only one of "renders" and "returns" is present, it fails the test |

## 3. Detection and the one-line notice

At the start of the session (`SKILL.md`, "Detect the environment once"):

1. Scan the available tools, skills and plugins for the signals above. Read the matching skill or tool description before the first use; its rules bind you (Visualize's own guidance on style and files, `show_widget`'s `read_me`).
2. Decide the renderer for this session: host widget → question tool → closebook MCP → HTML page → text. Keep it for the whole session unless it fails.
3. Tell the learner in **one line** what the questions will look like here, in the opening message: "I'll show the questions as cards here; they check your answer on the spot" / "这里我会用题卡出题，点“检查答案”当场看对错" / "This chat has no interactive cards, so I'll ask in text; reply like `B 2`." Never ask the learner to debug the setup.
4. After the **first** widget, if nothing comes back in the expected form when the learner moves on, ask once ("Do you see a question card above?") and then downgrade for the rest of the session (`interaction-fit.md` section 5). Do not retry the same renderer in a loop.

## 4. Building a question widget (contract shared by every form)

- **One question per widget**, and never two open questions in the chat at once. The widget *is* the question; do not repeat it as lettered options in text (the host may ask you not to narrate the widget at all: Visualize does). The one exception is the section review widget (section 8): it holds 3–5 questions but shows one at a time and sends one summary.
- **The widget checks keyed answers itself.** For forms with a stored key (`mcq`, `flashcard`, `numeric`, `cloze_passage`, `order_steps`, `diagram_fill`, `timeline_fill`, `compare_table_fill`, `code_trace`, `terminal`, `graph` targets) the fragment carries the key and the feedback, exactly as the HTML practice page does: a **Check answer** (检查答案) button marks the answer right or wrong on the spot, shows the explanation for the chosen option or the worked steps, and reveals what was hidden (the flashcard back, the full diagram, the trace, the sliders). Until that click nothing is revealed and the options stay editable; after it they lock.
- **Written answers are not graded in the widget.** `free_text`, Feynman explanations, free recall and contested reasoning have no key: the widget collects the text and sends it to the chat, and you judge it there (recipes below).
- **Honesty about the key.** A key in the widget can be read in the page source. Closed-book means the learner does not look, as with the practice page; say so once if they ask, and never present the check as proof of retrieval. Grading is exact-match or tolerance-based: for numbers set a tolerance and accept listed equivalent forms; for orders list `alternatives`; for blanks accept listed variants. When equivalents cannot be listed, send the answer to the chat instead.
- **Controls:** native `button`, `input`, `select`, `textarea`, `range`; one check button; keyboard reachable; labels in the learner's communication language (zh-CN or en), independent of the subject text.
- **Validate before checking:** an empty required field shows an inline error and does not check. Keep "I don't know" (不知道) as a legitimate choice on every question; it counts as `dont_know`, never as an error.
- **Confidence before the check** for questions with a right answer: three pills `1 / 2 / 3`, required before the check button enables. Omit it for contested reasoning and unscored teach checks when it adds nothing.
- **One line back when the learner moves on.** The feedback panel ends with a **Next** (下一题) button. It sends one line:

  ```text
  closebook result · <kp_id>/<item_id> · <answer> · correct|partial|incorrect|dont_know · confidence <n>
  ```

  For written answers the submit button sends the text instead:

  ```text
  closebook answer · <kp_id>/<item_id> · <text>
  ```

  Codex/ChatGPT: `window.openai.sendFollowUpMessage({ prompt: line, title: "Next question" })` (the host shows a confirmation dialog; tell the learner once that a confirm click follows). Claude Code: `sendPrompt(line)`. `<answer>` is the option id, the typed value with unit, the order as ids, or the blanks as `1=…; 2=…`. This line is what lets you record the attempt, classify the error with the confidence, and choose the next question; without it the result exists only on the learner's screen.
- **The send button never locks for good.** Disable it only while the send is in flight (`await`); when the call settles, re-enable it with the label "Send again" (再发一次), because a cancelled host dialog may resolve just like a sent one and the learner must be able to retry. Keep a copy line (the same text, in a read-only field) under the button as the fallback for a host that blocks the send. Duplicates are harmless: you treat a second result line for the same `<kp_id>/<item_id>` as a repeat, not a new attempt.
- **Style:** follow the host's own widget guidance; closebook adds no theme. Keep it compact and transparent; the question text is content, not decoration.
- **Teaching chunks:** on hosts with a widget facility a chunk may be shown as a card (explanation, example, one button "I've read it, ask me" that sends `closebook ready · <kp_id>`). The click is not mastery. On the `section` pace show the section's chunks together, then one check per point (`new-learning.md` section 3).
- **Nothing is recorded on display.** An attempt exists only when the result line or the written answer has arrived in the chat. A repeated line for the same `<kp_id>/<item_id>` (a retry after a cancelled dialog) is the same attempt: record it once, answer it once. Record it, give any feedback the widget could not (the cause of the error, what to practise), and send the next question (another widget).

## 5. Recipes per interaction form

| Form | Widget | Check inside the widget | Comes back on Next | Then, in chat |
|---|---|---|---|---|
| `mcq` | Stem, 2–6 option buttons (single select, `aria-pressed`), confidence pills, **Check answer** | Marks the chosen option, highlights the key, shows the explanation written for that option (why the distractor tempts) | `B · incorrect · confidence 3` | Classify the error, decide the next question |
| `flashcard` | Front + a text field "Your answer" + **Check**; the back is hidden until then | Reveals the back next to the typed recall; the learner marks right / fuzzy / wrong | `… · partial · confidence 2` | Schedule by the self-mark |
| `free_text` | Stem + `textarea` + **Submit**; optional "I don't know"; no key | — | `closebook answer · … · <text>` | Judge against the hidden checklist, name the gap |
| `numeric` | Number or expression field, unit field when required, optional "working" textarea, confidence, **Check** | Compares with the key within the set tolerance (and listed equivalents), then shows the worked steps | `12.5 m/s · correct · confidence 2` | Note a right number with a wrong method if the working shows one |
| `cloze_passage` | Passage with inline `input`s at each blank; optional word bank as buttons | Marks each blank against its listed variants; shows the filled passage | `1=accept; 2=reject · partial · confidence 2` | Explain the missed blanks |
| `order_steps` | Items as buttons: tap to append to "your order", ↑ ↓ ✕ to fix; distractors stay unselected; `monospace` for code | Compares with the key and `alternatives`; shows the first wrong position | `C, A, D, B · incorrect · confidence 1` | Why that step belongs where it does |
| `diagram_fill` | SVG of the flow or structure with `?` boxes bound to inputs | Marks each box and draws the **complete** diagram | `1=DNS; 2=TCP; 3=TLS · partial · confidence 2` | Name each miss |
| `timeline_fill`, `compare_table_fill` | A table or line with input cells | Marks the cells, shows the filled version | the cells · result | Same |
| `code_trace` | Code block + inputs for the predicted values or output | Marks the predictions and shows the step-through trace | the predictions · result | Explain the first wrong step |
| `graph`, `simulation` | **Predict first**: the prediction question with confidence; the plot and sliders are locked | Marks the prediction and unlocks the sliders to explore | the prediction · result | Pose the "what changes if" follow-up |
| `terminal` | A single command input ("which command does X?") | Matches against the listed accepted commands; shows the prepared output | the command · result | Accept valid variants the key missed; say so |
| teach check on the `step` pace | Same as the form above, `phase: "teach_check"`, no scoring | Same | Same line | Reteach on a miss (a different example), next chunk on a hit |

What a widget cannot do here: grade free text, run code, accept an equivalent it was not told about, or prove the learner did not look. Say so when it matters; never present the check as more than a key comparison.

## 6. Question tools with options

Use a host question tool only when **all** of these hold: it is listed in this turn's tools; its host rules allow optional questions that improve the work (not "approvals only", not "clarification only", not "decisions the user must make"); the item fits its limits (Codex: 2–3 options, at most 3 questions per call) without dropping an option. Then:

- One call per item: question 1 = the stem with the options (`id` = option letter, `label` = text, no `(Recommended)` suffix, no description that hints), question 2 = confidence `1 / 2 / 3` when the item has a right answer. The host's "Other" field is the learner's free answer or "I don't know".
- A question tool cannot check the answer itself: the result is the raw choice, and you grade it in the next reply. Never pre-select, never place the key first, never reveal it in the headers.
- Never use the tool for free production tasks (Feynman, free recall, writing a command) and never shrink a four-option item to three to fit it: use the next renderer instead.
- If the tool refuses (wrong mode, not enabled) once, say nothing about setup beyond one sentence and continue with the next renderer.

## 7. Fallbacks and recording

Renderer order (same as `interaction-fit.md`): explicit learner request → host widget facility → host question tool → closebook MCP card → HTML page when it clearly pays off → plain text. A missing or failed renderer moves to the next one with the **same question**; options are never dropped, open questions never become choices. The closebook MCP cards keep their own contract (`mcp-cards.md`): they return the raw answer and you grade it in chat.

Record per knowledge point (`interaction-fit.md` section 6): `interaction_selected` (the form) and, on a forced change, `interaction_downgraded_from: {from, reason}` with a reason such as `"no host widget; MCP absent; text"`. Attempts may carry `interaction`, so `progress_tool.py interaction-stats` keeps working.

## 8. Section review widget: 3–5 questions in one widget

**When.** The learner has just finished a section of 2–4 related points on the `section` pace (`new-learning.md` section 3), or asks for a quick check on 3–5 points learned in one sitting, and the host has an inline widget facility. The task decides this, not the question count (`interaction-fit.md` section 3): a single point's check stays a single widget; a day's or several days' points go to the HTML assessment page (`html-lesson.md`, exam mode).

**One widget, stepped inside.** Build one fragment that holds all the items (3–5, one per point, each on a case the explanation did not show) with their keys and explanations, and shows **one at a time**:

1. Question *n* of *N*: stem, options or input, confidence pills, **Check answer**. Nothing of the key or explanation is in view before the click.
2. After Check: right or wrong, the explanation for the chosen answer, the item locks (no second scoring).
3. **Next** switches to the next item **inside the widget**: no message, no new widget, no second confirmation. Keep the answered items' answer, result and confidence in the widget's state.
4. After the last item: a **summary** in the same widget: score (right / N), the wrong items with their point names, weak points (any point missed, and any confident miss first), and one **Finish** button.
5. Finish sends **one** line (same button rule as section 4: disabled only while sending, "Send again" afterwards, copy line as fallback):

   ```text
   closebook section · <section_id> · <right>/<N> · <item_id> <answer> <result> c<n>; <item_id> <answer> <result> c<n>; …
   ```

   On Codex this is the only confirmation dialog of the whole section; on Claude Code there is none.

**Stop early.** Mark each item with its point's importance. When a `core` item is answered wrong with confidence 3, show, next to Next, a button **Stop and explain this** (先讲这个); it sends the same summary line with ` · stopped_at <item_id>` for the items done so far. Otherwise the review runs to the end and the misconception is taught right after it.

**Never:** a message per question; a new widget to simulate switching; a new chat message to simulate updating the widget; a visible key before Check; re-scoring an answered item; dropping a question to keep a fixed count when the learner is clearly lost.

**What the agent does with the summary.** Record one attempt per item (`phase: "teach_check"` for a section's checks, `review` for a review batch; `source: "widget"`; confidence and result as sent; `interaction` as the form). Then teach the weakest point first with a *different* example, starting with any confident miss, before going on; the section's scored retests still come only after all of today's points are taught. Say in one line what the summary showed; do not repeat the questions.

**Without a widget facility:** one check per reply as before (`new-learning.md` section 3), or the closebook MCP cards one at a time; never pretend a stepped widget exists.

## 9. Teaching with visuals

When the learner asked to **learn**, teaching comes before any question, and the host's widgets are for teaching as much as for checking. The words stay in the chat (concrete case first, then the rule: `new-learning.md` sections 4–5); a widget shows the **structure the words describe**:

| The chunk explains | Visual in the chunk | Interaction inside it |
|---|---|---|
| A flow, pipeline, lifecycle, architecture (3+ parts) | SVG diagram with labelled boxes and arrows, drawn **after** the predict-first version with `?` boxes has been answered | none, or hover labels |
| A procedure or a run of code | Step-through: one step or one line at a time, the state after it, a Next button inside the widget | Next, Back |
| A mechanism where a quantity drives another (physics law, interest, supply and demand) | Explainer: one or two sliders, a readout, a small plot; the prediction question comes **first**, the sliders unlock after it | slider, readout |
| Two or three things often confused | Comparison table, filled in; or the fill-first version as the check | none |
| A taught example worth keeping | Lesson card: the explanation's example and one takeaway line, with a button "I've read it, ask me" that sends `closebook ready · <kp_id>` | one button |

Rules: one visual per chunk at most, and only when the picture shows something a sentence cannot (order, flow, scale, change over a parameter). No walls of text inside a widget; no decoration; the visual never contains the answer of the check that follows. Reading or clicking through a visual is not mastery: the check still comes, on a case the visual did not show. Without a widget facility, the same chunk uses the text forms: numbered steps, ASCII arrows, a markdown table, 2–3 concrete parameter values.
