# closebook on ChatGPT and Codex

**Status:** skill format, install paths and `agents/openai.yaml` **verified 2026-10-31**; plan availability beyond the listed plans and rendering details are marked per line.
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
1. `python3 tools/package_skill.py` → `dist/closebook.zip`.
2. Plugins → Skills → Create → Upload. Uploads are scanned before use.
3. Mention it with `@closebook`, or let ChatGPT pick it from the description.

Standalone skills run in the ChatGPT desktop app; skills bundled in a **plugin** also work on web and mobile (verified). Availability on Free, Plus and Pro plans is **unverified** (not stated on the help page). Without skills, use the paste-in in [`generic.md`](generic.md).

## Compatibility notes

- `description` front-loads the trigger words ("learn, study, memorize, review, exam, quiz…" and the Chinese triggers), because Codex shortens descriptions when many skills are installed (verified).
- `skills/closebook/agents/openai.yaml` sets the display name, a short description and a default prompt. Only documented fields are used.

## What works at which level

| Capability | Codex | ChatGPT |
|---|---|---|
| Level 0 plain text | yes | yes |
| Level 1 clickable options / quiz cards | no | **Unverified** (user reports vary); not assumed |
| Level 2 HTML page | `build_lesson.py` writes a file to open in a browser | Code blocks can **Preview** HTML pages (verified), but that means retyping the ~75 KB template, which the skill avoids. Whether skill scripts can build the file in ChatGPT is **unverified**. Canvas is gone from GPT-5.5 models (verified) |
| Progress file | `closebook-progress/<topic>.json` via `progress_tool.py` | Chat-only: compact JSON at the end, pasted back next time. ChatGPT memory is not used as progress storage |

## Quick check after installing

`$closebook quiz me on the attached notes` (Codex) or "考考我这份笔记" (ChatGPT). Expected: an outline with knowledge types and one question about time and familiarity, with no summary of the material.
