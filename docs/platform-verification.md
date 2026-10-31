# Platform verification log

Every platform claim used by closebook, with how it was checked. **Verified** = read on an official documentation or help page on the date given. **Unverified** = reported by a model about itself, by user testing, or not found in official docs; treat as a hypothesis.

Verification date for this round: **2026-10-31**. Pages change; re-check before each release.

## Shared format

| Claim | Status | Source |
|---|---|---|
| A skill is a folder with `SKILL.md` (YAML frontmatter + Markdown) and optional `scripts/`, `references/`, `assets/` | Verified 2026-10-31 | [Agent Skills specification](https://agentskills.io/specification) |
| `name`: 1–64 chars, lowercase letters/digits/hyphens, no leading/trailing or double hyphen, must match the folder name | Verified 2026-10-31 | [Agent Skills specification](https://agentskills.io/specification) |
| `description`: 1–1024 chars, should say what the skill does and when to use it | Verified 2026-10-31 | [Agent Skills specification](https://agentskills.io/specification) |
| Optional fields: `license`, `compatibility` (≤ 500 chars), `metadata` (string map), `allowed-tools` (experimental) | Verified 2026-10-31 | [Agent Skills specification](https://agentskills.io/specification) |

## Claude (Anthropic)

| Claim | Status | Source |
|---|---|---|
| Skills available on Free, Pro, Max, Ultra, Team, Enterprise; require code execution ("Code execution and file creation") to be enabled | Verified 2026-10-31 | [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) |
| Custom skills are uploaded as a ZIP in Customize > Skills; the ZIP must contain the skill folder at its root; folder name must match the skill name | Verified 2026-10-31 | [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) |
| `name` must not contain XML tags or the reserved words `anthropic`, `claude`; `description` must not contain XML tags | Verified 2026-10-31 | [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| claude.ai uploads accept only frontmatter fields `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`; other fields fail with a hard error | Verified 2026-10-31 | [Claude Code: skills](https://code.claude.com/docs/en/skills) |
| Claude Code loads personal skills from `~/.claude/skills/<name>/SKILL.md` and project skills from `.claude/skills/<name>/SKILL.md`; plugins ship skills in `<plugin>/skills/<name>/SKILL.md` | Verified 2026-10-31 | [Claude Code: skills](https://code.claude.com/docs/en/skills) |
| Skills enabled on claude.ai sync into Claude Code when signed in with the same account (Claude Code v2.1.273+) | Verified 2026-10-31 | [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) |
| Descriptions should be written in third person | Verified 2026-10-31 | [Best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| Artifacts can be single-page websites or small interactive tools, opened beside the chat; available on Free, Pro, Max, Ultra, Team, Enterprise and in Claude Code; viewable and editable on iOS/Android | Verified 2026-10-31 | [What are artifacts and how do I use them?](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them) |
| An artifact can be created from a file produced by a skill script (rather than typed out by the model) | **Unverified**: not described on the help page | — |
| `localStorage` and file downloads work inside an HTML artifact | **Unverified**; the template degrades to copy/paste export if they don't | — |

## ChatGPT and Codex (OpenAI)

| Claim | Status | Source |
|---|---|---|
| ChatGPT and Codex both use `SKILL.md` skills based on the open agent skills standard | Verified 2026-10-31 | [Build skills (ChatGPT Learn)](https://learn.chatgpt.com/docs/build-skills.md) |
| Standalone skills: ChatGPT desktop app, Codex CLI, IDE extension. Skills bundled in **plugins** also work in ChatGPT web, desktop and mobile | Verified 2026-10-31 | [Build skills](https://learn.chatgpt.com/docs/build-skills.md) |
| Skills in ChatGPT are available to eligible **Business, Enterprise, Healthcare and Edu** users; upload via Plugins > Skills > Create > Upload; uploads are scanned | Verified 2026-10-31 | [Skills in ChatGPT (Help Center)](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) |
| Availability on personal plans (Free, Plus, Pro) for ChatGPT skills | **Unverified**: not stated on the help page | — |
| Codex discovery paths: `.agents/skills` from CWD up to repo root, `$HOME/.agents/skills` (user), `/etc/codex/skills` (admin) | Verified 2026-10-31 | [Build skills](https://learn.chatgpt.com/docs/build-skills.md) |
| Codex CLI 0.153.4 discovers a skill in `.agents/skills/<name>/` inside the current git repository and triggers it on a natural request | Verified 2026-10-31 by running it ([validation report §7](validation-report.md#7-hands-on-run-codex-cli)) | — |
| `~/.codex/skills` as a user path | **Unverified / possibly outdated**: mentioned on a use-case page, not in the main skills doc | [Save workflows as skills](https://learn.chatgpt.com/use-cases/reusable-codex-skills) |
| Codex shortens descriptions when many skills are installed, so trigger words should be front-loaded | Verified 2026-10-31 | [Build skills](https://learn.chatgpt.com/docs/build-skills.md) |
| Optional `agents/openai.yaml` for UI metadata and invocation policy | Verified 2026-10-31 | [Build skills](https://learn.chatgpt.com/docs/build-skills.md) |
| ChatGPT renders native clickable options / quiz cards (Level 1) | **Unverified**: user testing reports varied rendering | — |
| ChatGPT code blocks offer **Preview** for HTML pages (sandboxed; outside resources may need permission) | Verified 2026-10-31 | [Working with writing blocks and code blocks](https://help.openai.com/en/articles/20001246-working-with-writing-blocks-and-code-blocks-in-chatgpt) |
| Canvas is no longer available in GPT-5.5 Instant / Thinking; writing and code moved into chat blocks; legacy models keep canvas for a limited time | Verified 2026-10-31 | [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes) |

## Gemini (Google)

| Claim | Status | Source |
|---|---|---|
| Gemini Apps support skills on gemini.google.com, the Gemini mobile app and the Gemini app on Mac; you can upload a `SKILL.md`, or a folder or `.zip` with `SKILL.md` at its root | Verified 2026-10-31 | [Create & manage skills for Gemini Apps](https://support.google.com/gemini/answer/17094296) |
| Gemini Apps skill name must be lowercase with hyphens; total upload ≤ 100 MB; hidden binary files like `.DS_Store` or `.pyc` can make uploads fail; scripts can't access the internet | Verified 2026-10-31 | same page |
| Supported upload file types include `.md`, `.json`, `.py`, `.html`; `.ts`, `.tsx`, `.sql` are not supported | Verified 2026-10-31 | same page |
| Skills don't require a Google AI subscription | Verified 2026-10-31 | same page |
| Google plans to remove Gems and automatically recreate them as skills | Verified 2026-10-31 (no removal date given) | same page |
| Gemini CLI supports Agent Skills from `~/.gemini/skills`, `~/.agents/skills`, `.gemini/skills`, `.agents/skills`; activation asks for user consent | Verified 2026-10-31 | [Gemini CLI: Agent Skills](https://geminicli.com/docs/cli/skills/) |
| Whether Gemini Apps actually *executes* bundled Python scripts in chat | **Unverified**: the page only restricts internet access | — |
| Gemini renders at most 3 suggestion bubbles / no clickable quiz cards (Level 0–1) | **Unverified**: user testing | — |
| Gemini Canvas (gemini.google.com, signed in) can preview HTML and React web apps, with a console for errors | Verified 2026-10-31 | [Create docs, apps & more with Canvas](https://support.google.com/gemini/answer/16047321) |
| Skills and Canvas can be combined in one chat | **Unverified** | — |

## Consequences for closebook

- Package folder is `skills/closebook/` so the folder name equals `name` and the folder can be zipped as-is.
- Frontmatter uses only `name`, `description`, `license`, `metadata` (accepted by every platform above).
- No hidden files may ship in the package (`tests/test_skill_structure.py` checks this).
- The skill never assumes Level 1/2 rendering; it detects capability per session and defaults to Level 0.
- Scripts are optional helpers; the teaching flow works without executing anything.
- Every verified Level 2 surface (Claude artifacts, ChatGPT HTML preview, Gemini Canvas) renders HTML that the model writes into the reply. The lesson template is ~75 KB, so `references/html-lesson.md` only builds pages from a file (script or copy), never by retyping; on chat-only surfaces the default stays Level 0.
