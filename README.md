<p align="center"><img src="docs/images/logo.jpg" alt="closebook" width="160"></p>

<h1 align="center">closebook</h1>

<p align="center"><b>Learn it. Close the notes. Explain it yourself.</b><br>
An agent skill for guided lessons, recall practice and spaced review.</p>

<p align="center">English · <a href="README.zh-CN.md">简体中文</a> · <a href="LICENSE">MIT</a></p>

closebook gives your AI assistant a teaching flow. Bring a topic, your notes or a progress file, and tell it what you want to learn.

- **For new material**, the agent arranges teaching units from the content, course workload, prerequisites and your responses. It may explain a complete example, several connected points or a full section, and use smaller steps where needed. Checks at useful boundaries guide correction, followed by closed-book retests; coverage and assessment remain tracked per knowledge point. You can request smaller steps or fuller explanations at any time.
- **For practice and review**, it starts with a question, explains the gap in your answer and gives you a new question to check it.

**On every agent platform, suitable built-in components, tools and plugins come first.** Optional MCP cards, HTML and text follow the same [renderer rules](skills/closebook/references/interaction-fit.md).

## Install by pasting a prompt

Copy the entire block below into the agent you use. It asks the agent to download, install, configure and verify closebook. You do not need to download a prompt file or work out configuration paths. The prompt is in English; installation updates and any steps for you are in Simplified Chinese.

```text
Install and configure closebook for the agent I am using now:
https://github.com/sheepxux/closebook

Assume I have no technical background. Handle environment checks, downloads, installation paths, configuration, activation, and verification yourself. Do not ask me to choose technical settings, edit configuration files, or run terminal commands when your tools can do that work.

Fetch and follow the installation workflow:
https://raw.githubusercontent.com/sheepxux/closebook/main/INSTALL.md

Identify your actual host and active profile. Download the latest stable release yourself, install the complete skill in the correct persistent location, enable it using the host's supported mechanism, and verify that the host can discover it. If the host loads skills from a local directory, install the full `skills/closebook` folder from the release's source archive (the upload ZIP leaves out the practice-page template and `agents/openai.yaml`); use the release's `closebook.zip` only for a chat app's skill upload. Use your tools to complete the work; do not stop at instructions or ask me to download files that you can download yourself.

Preserve my existing settings, local skill modifications, and learning records. Involve me only for required permissions, unavoidable UI actions, or unresolved conflicts. If persistent installation is impossible, explain the specific limitation and the minimum remaining step; do not claim success or mistake a temporary sandbox for an installed skill.

When I must act, give one concrete step at a time in everyday Chinese: where to click or what to paste, and what I should see next. Use the actual interface or verified documentation; do not invent controls. If the platform has no supported installation path, offer a clearly labeled session-only learning option instead of leaving me with a technical setup tutorial.

Use Simplified Chinese for all progress updates, questions, and the final response. Lead with whether closebook is actually ready to use, any action I still need to take, and one ready-to-copy learning request. Keep version, path, and verification details brief and secondary. Complete installation first; do not begin a lesson yet.
```

The agent needs a supported installation mechanism and permission to use it. Some apps still require a click, an upload or a restart. If persistent installation is unavailable, it should say so and offer a clearly labelled session-only option. See the [installation workflow](INSTALL.md).

**Release scope:** the prompt installs the latest stable release, [v0.4.1](https://github.com/sheepxux/closebook/releases/tag/v0.4.1), which includes the three-level teaching and assessment flow (checks per point, section review cards, exam-mode pages), the agent's-own-components-first renderer order and the single upload ZIP described here. The optional Chinese/English MCP companion is available in this release's source under `mcp/`; it is configured separately and is not included in the skill ZIP.

## Start learning

After installation, fill in the brackets and send. You can use your own language.

| What you want | What to send |
|---|---|
| Start from zero | "Use closebook to teach me [topic]. I'm a complete beginner and have [minutes] minutes." |
| Learn something you half know | "Use closebook to help me learn [topic]. I've studied it but it's shaky; I have [minutes] minutes." |
| Review notes | "Use closebook to quiz me on these notes. Focus on anything I get wrong." (attach or paste the notes) |
| Get a simpler explanation | "Explain [concept] in everyday language, with an example, then let me try." |
| Continue later | "Here is my closebook progress file. Review what's due today." (attach the file) |
| Test a whole day | "Use closebook to test me on everything I learned today, closed-book, as an exam page." |
| Practise offline | "Make an offline practice page for [topic], with explanations before the exercises." |

Filled in, the first one reads: "Use closebook to teach me the present perfect. I'm a complete beginner and have 20 minutes."

Your stated background takes priority: saying "quiz me" while explaining that you have never studied the topic still calls for teaching first. For a large subject, closebook proposes a path in prerequisite order and saves the unfinished points for later.

The development version adds a [source-driven course workflow](skills/closebook/references/source-driven-course.md), not yet included in the published v0.4.1 package. With slides, PDFs, official documents or a syllabus, it inventories every page or item with source locators, then retains the v0.4.1 teaching and retrieval methods while arranging teaching units from content and workload and tracking each point’s coverage. Source sections require reconciliation against that inventory; each Module ends with a comprehensive closed-book assessment and targeted re-teaching/retests. Parsed, taught, assessed and passed are tracked separately. Time limits defer requirements rather than deleting them. A syllabus supports syllabus-level claims only; unreadable visuals and missing pages remain explicit gaps.

During practice, you answer before seeing the reference answer. "I don't know" is allowed, and questions with a correct answer can ask how confident you are. Feedback names the gap and gives another chance to retrieve the idea. Reading a card or clicking "continue" never counts as mastery.

Terms can use recall cards; concepts can use explanations in your own words; procedures can use prediction followed by verification. You can change the method, ask for plain language or request only a summary.

## Choose the interaction that fits

The same teaching flow can use different interfaces; the [interaction guide](skills/closebook/references/interaction-fit.md) defines their selection order and exceptions.

| Interface | When it is used | How answers are checked |
|---|---|---|
| The agent's own components: inline widgets (Codex and ChatGPT Visualize, Claude Code `show_widget`) or a question tool with options | First choice wherever the agent has them: the question is drawn in the chat and the answer comes back as a message | Keyed questions are checked inside the widget with instant feedback, and one result line returns to the chat when the learner moves on; written answers are graded by the assistant |
| Optional closebook MCP cards | Fallback in clients that support MCP Apps | Submission returns to chat; the assistant checks the answer |
| Offline HTML practice page | When requested, or when a reusable page suits the task | The page checks supported answer types; written answers can be exported for assistant feedback |
| Plain-text chat | Always available as a fallback | The assistant checks each reply in the conversation |

A tool reserved for approvals, or whose own rules forbid quizzes or reserve it for decisions, is never repurposed as a quiz. An explicit request for a particular interface, such as an MCP preview or an offline page, takes priority.

### Seven MCP components

The optional companion currently implements **seven components**:

| Component | What the learner does |
|---|---|
| Lesson card | Reads one explanation and example, then continues to practice or asks for another example |
| Multiple choice | Selects an answer and submits it |
| Written answer | Explains or reasons in their own words |
| Numeric answer | Enters a value or expression, a unit and an optional calculation |
| Cloze passage | Fills blanks in the original passage |
| Ordering | Arranges words, steps or code lines; can leave distractors unused |
| Recall card | Writes an answer or chooses "I don't know", then submits to reveal the reference |

Exercise cards can also collect confidence. They return the original response to chat and do not grade it or update learning progress themselves. If submission fails, the input remains available to retry or copy. The shared design uses pale cyan accents, system fonts, light and dark themes, and keyboard controls. Chinese and English interface text follows the learner's communication language through `locale`, independently of the language being studied.

Code tracing, simulated terminals, graphs and parameter labs are currently available through the HTML page, not these MCP cards. Voice interaction depends on the host. See the [MCP setup, tools and verification notes](mcp/README.md) for details.

### Offline practice pages

<p align="center"><img src="docs/images/lesson-page.jpg" alt="Offline HTML practice page with a request-flow prediction exercise" width="720"></p>

*The screenshot shows the HTML practice page. MCP cards use a separate interface.*

Ask the agent to make a practice page and it can generate a single HTML file that opens offline, with no API key or network requests. It supports teaching sections (one chunk at a time, or a whole section before its checks), questions, diagrams, recall cards and subject-specific exercises. In **exam mode** it becomes a closed-book assessment: answers lock without feedback, a countdown is optional, and handing in produces a report with per-point results, weak points and every explanation:

| Subject | Examples of exercises |
|---|---|
| Programming and Git | Predict code output, step through variables, arrange code lines or practise commands in a simulated terminal |
| Maths and physics | Enter numbers or fractions, match a target graph, predict a change before exploring parameters |
| Languages and biology | Complete a passage, arrange a sentence or recall terminology |

The simulated terminal checks expected commands and shows prepared output; it does not execute shell commands. When building a page, the Python trace checker runs supported teaching code and rejects inconsistent execution steps. Other languages and the answers to natural-language questions still need independent review.

The page checks answer-key exercises automatically. Written answers and recall cards can be self-checked, or exported to chat for feedback. Paste the assistant's grading block back into the page to update its results. This is a manual round trip, so the page can stay offline.

Download and open an example: [teach-first lesson](examples/new-learner-lesson.html), [HTTP caching practice](examples/http-cache-lesson.html), [subject exercises](examples/subject-widgets-lesson.html) or a [daily assessment in exam mode](examples/daily-assessment.html). The [interaction guide](skills/closebook/references/interaction-fit.md) explains how forms are chosen and how they fall back to text.

## Keep your progress

closebook records knowledge points, answers, mistakes and next review dates. Spaced review uses 1, 3, 7, 14 and 30-day intervals, adjusted from your answer history. A confident wrong answer gets attention first.

In environments with persistent files, the agent maintains a JSON progress file. In chat-only environments, it gives you a compact block to save and paste back next time. You own the record; cross-chat memory is never assumed. See the [progress format](skills/closebook/schemas/progress.schema.json).

## Platform guides and manual installation

The teaching flow works in text. Installation and richer interfaces depend on the host's actual capabilities; connecting an MCP server alone does not prove that the client can display its cards.

| Agent or app | Guide |
|---|---|
| Claude Code, Claude Desktop, claude.ai | [Claude](adapters/claude.md) |
| Codex and ChatGPT | [OpenAI clients](adapters/chatgpt-codex.md) |
| Hermes Agent | [Hermes](adapters/hermes.md) |
| Gemini CLI and Gemini Apps | [Gemini](adapters/gemini.md) |
| Other agents or session-only instructions | [Generic setup](adapters/generic.md) |

Prefer manual installation? Use the [skill ZIP](https://github.com/sheepxux/closebook/releases/latest/download/closebook.zip) for claude.ai, ChatGPT and Gemini Apps (one package; it leaves out the offline page template and `agents/openai.yaml`, which those uploads refuse), or copy the `skills/closebook` folder for Codex CLI, Claude Code and other directory installs (everything included) with the relevant guide. These packages contain the skill, not the MCP server. Platform claims and their sources are recorded in the [platform verification log](docs/platform-verification.md).

## What has been verified

The [validation report](docs/validation-report.md) records skill behaviour, progress handling and HTML browser tests. The [answer-key audit](docs/answer-key-validation.md) includes independently executed code, formula checks, real Git commands and equivalent-answer tests, including the failures found and their fixes. The [MCP improvement report](docs/mcp-hardening-validation.md) records this version's automated checks, six new tool-selection cases, targeted repairs, desktop submissions and remaining acceptance checks.

For the MCP companion, as of 2026-11-01:

- Automated checks cover protocol, message return, DOM interaction, interface language and startup. The suite is separate from the agent behaviour cases; neither proves that every desktop client works. The local audit excluded HTML browser tests. The subsequent [Ubuntu CI run](https://github.com/sheepxux/closebook/actions/runs/41266442700) for commit `445d330` passed the full `python3 tools/check.py`: 135 Python tests (including 11 browser tests), packaging checks and 41 MCP tests, with no skipped tests.
- After reloading the MCP service in Codex desktop, all seven card forms produced nine real submissions in the same chat, including three ordering attempts. Samples preserved the selected option and confidence, multiline Chinese/English text, a fraction and unit, and blank IDs with a curly apostrophe. The user also confirmed that the recall-card reference appeared only after submission; reading acknowledgement and preview answers did not count toward learning progress.
- The final two-item ordering check returned the requested order, 1 → 2, after instructions to move 1 above 2. The earlier inconclusive attempt and user-reported misclick remain in the record. The click sequence was not independently observed, and this check does not cover every control or failure path. A targeted DOM check passed separately.
- The current cyan theme and all interface labels have not been independently reviewed visually. Chinese and English return messages were observed; Claude, Hermes and other clients have not been tested hands-on with this companion.

These checks do not guarantee every generated answer key is complete. The assistant still needs to verify answers and accept valid alternatives. See the [MCP verification details](mcp/README.md#检查与验证范围).

## Development

<details>
<summary>Source layout and checks</summary>

```text
skills/closebook/        Installable skill: core instructions, references and optional helpers
  SKILL.md              Teaching flow and routing
  references/           Learning methods, interaction rules and platform fallbacks
  schemas/              Progress, lesson, export and grading formats
  scripts/              Progress management and HTML builder (Python 3.8+, standard library)
  assets/               Offline HTML template
  evals/                53 behaviour cases, excluded from release ZIPs
mcp/                    Optional MCP Apps companion (Node.js 20+)
adapters/               Platform installation guides
docs/                   Validation reports and design decisions
examples/               Generated HTML practice pages
tests/                  Skill, packaging, grading and browser tests
tools/package_skill.py  Release ZIP builder
```

From the repository root:

```sh
npm ci --prefix mcp --loglevel=error
python3 tools/check.py
```

The full check includes Python, packaging, browser and MCP tests, and fails on skipped tests. Install the browser dependencies as described in [CONTRIBUTING.md](CONTRIBUTING.md). In environments that cannot run browser tests, use `--skip-browser` and report a partial check. GitHub Actions runs the full deterministic command; the 53 [agent behaviour cases](skills/closebook/evals) are run separately.

For the optional MCP companion:

```sh
cd mcp
npm ci --loglevel=error
npm run build
npm test
```

See the [MCP guide](mcp/README.md) for server startup and client configuration. In this release the skill is `0.4.1` and the MCP package stays `0.3.0` (unchanged); their versions are independent, and UI resource revisions are tracked separately too.

</details>

[MIT](LICENSE) © sheepxux
