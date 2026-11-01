# closebook on ChatGPT and Codex

**Status:** skill format, install paths and `agents/openai.yaml` **verified 2026-10-31**; Visualize and `request_user_input` rows checked 2026-11-01; plan availability beyond the listed plans and rendering details are marked per line.
**Sources:** [Build skills (ChatGPT Learn)](https://learn.chatgpt.com/docs/build-skills) · [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) · [Code blocks in ChatGPT](https://help.openai.com/en/articles/20001246-working-with-writing-blocks-and-code-blocks-in-chatgpt) · [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) · [Codex `openai.yaml` reference](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/references/openai_yaml.md). Full log: [`docs/platform-verification.md`](../docs/platform-verification.md).

## Install

**Codex CLI / IDE extension** (verified)
```bash
# user-wide
mkdir -p ~/.agents/skills && cp -R skills/closebook ~/.agents/skills/
# or inside a repository (found from the working directory up to the repo root)
mkdir -p .agents/skills && cp -R skills/closebook .agents/skills/
```
Symlinks work too. Invoke with `$closebook` or `/skills`, or just ask to be quizzed (implicit invocation is on).
`~/.codex/skills` appears on an older use-case page but not in the main docs: **unverified**, prefer `~/.agents/skills`.

**ChatGPT** (verified for eligible **Business, Enterprise, Healthcare, Edu** users)
1. `python3 tools/package_skill.py` → `dist/closebook-chatgpt.zip` (the ChatGPT build: identical to `closebook.zip` minus `assets/lesson-template.html`, because ChatGPT's skill scan refuses any file containing JavaScript, checked 2026-11-01; the offline practice page is therefore not available in ChatGPT, everything else is).
2. Plugins → Skills → Create → Upload. Uploads are scanned before use.
3. Mention it with `@closebook`, or let ChatGPT pick it from the description.

On macOS the Codex desktop app and the ChatGPT desktop app are the same bundle (`com.openai.codex`): skills are installed inside it (Customize → Skills, or by attaching the ZIP in a Skill Creator chat), not from `~/.agents/skills`, and its chat runs in a sandbox without access to the Mac's files. Uploads pass a safety scan that refuses any JavaScript (an HTML `<script>` or a `.js` file), which is why the ChatGPT build drops the page template (see `docs/platform-verification.md`). Standalone skills run in the ChatGPT desktop app; skills bundled in a **plugin** also work on web and mobile (verified). Availability on Free, Plus and Pro plans is **unverified** (not stated on the help page). Without skills, use the paste-in in [`generic.md`](generic.md).

## Compatibility notes

- `description` front-loads the trigger words ("learn, study, memorize, review, exam, quiz…" and the Chinese triggers), because Codex shortens descriptions when many skills are installed (verified).
- `skills/closebook/agents/openai.yaml` sets the display name, a short description and a default prompt. Only documented fields are used.

## What works at which level

| Capability | Codex | ChatGPT |
|---|---|---|
| Level 0 plain text | yes | yes |
| Level 1 clickable options / quiz cards | **Codex app:** the bundled **Visualize** plugin (`$visualize`, seen at 1.0.66 on 2026-11-01) renders an HTML fragment inline and `window.openai.sendFollowUpMessage` returns the learner's answer to the chat, so it is closebook's first renderer there ([host widgets](../skills/closebook/references/host-widgets.md)). `request_user_input` (2–3 options per question) is listed in Plan mode; in Default mode only with `features.default_mode_request_user_input` (under development). **CLI / IDE extension:** neither renders Visualize; no cards. The closebook MCP demo displayed in the desktop app on 2026-11-01 (one flashcard response returned); other clicks and clients remain unverified | **Visualize** (`@Visualize`) renders interactive HTML in ChatGPT conversations (docs verified 2026-11-01), same fragment and `sendFollowUpMessage` model; no closebook test yet. Any other native quiz capability must be checked in the current session |
| Level 2 HTML page | `build_lesson.py` writes a file to open in a browser | Code blocks can **Preview** HTML pages (verified), but that means retyping the ~75 KB template, which the skill avoids. Whether skill scripts can build the file in ChatGPT is **unverified**. Canvas is gone from GPT-5.5 models (verified) |
| Progress file | `closebook-progress/<topic>.json` via `progress_tool.py` | Chat-only: compact JSON at the end, pasted back next time. ChatGPT memory is not used as progress storage |

Follow the [renderer rules](../skills/closebook/references/interaction-fit.md): the agent's own components come first ([host widgets](../skills/closebook/references/host-widgets.md): Visualize, then a question tool with options); the [MCP companion](../mcp/README.md) is optional and separate from the skill ZIP. Its desktop result does not establish availability on web, mobile or other clients.

## Quick check after installing

`$closebook quiz me on the attached notes` (Codex) or "考考我这份笔记" (ChatGPT). Expected: an outline with knowledge types and one question about time and familiarity, with no summary of the material.
