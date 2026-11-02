# closebook on Claude (claude.ai, Desktop, mobile, Claude Code)

**Status:** install path and frontmatter rules **verified 2026-10-31**; `show_widget` row seen 2026-11-01; rendering details marked per line.
**Sources:** [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) · [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) · [Claude Code: skills](https://code.claude.com/docs/en/skills) · [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) · [What are artifacts](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them). Full log: [`docs/platform-verification.md`](../docs/platform-verification.md).

## Install

**claude.ai / Claude Desktop** (Free, Pro, Max, Ultra, Team, Enterprise; verified)
1. Turn on code execution ("Code execution and file creation"); skills need it.
2. Build the ZIP: `python3 tools/package_skill.py` → `dist/closebook.zip` (its root is the `closebook/` folder, as required). This upload package has no offline page template and no `agents/openai.yaml` (other chat apps refuse them); the Claude Code directory install below keeps both.
3. Customize → Skills → upload the ZIP, then enable it.

Skills enabled on claude.ai sync into Claude Code when you sign in with the same account (Claude Code v2.1.273+; verified).

**Claude Code** (verified)
```bash
# personal, all projects
mkdir -p ~/.claude/skills && cp -R skills/closebook ~/.claude/skills/
# or for one project
mkdir -p .claude/skills && cp -R skills/closebook .claude/skills/
```
A symlink instead of a copy keeps it in sync with a git checkout.

## Compatibility notes

- Frontmatter uses only `name`, `description`, `license`, `metadata`, the subset claude.ai accepts (verified). `name` contains neither `claude` nor `anthropic` (verified rule).
- `agents/openai.yaml` is ignored by Claude; harmless to ship.

## What works at which level

| Capability | Claude Code | claude.ai / Desktop |
|---|---|---|
| Level 0 plain text | yes | yes |
| Level 1 clickable options | **Desktop app:** a `show_widget` tool (with a `read_me` guide) renders HTML/SVG inline and the global `sendPrompt(text)` sends the learner's answer to the chat (seen 2026-11-01), so it is closebook's first renderer there ([host widgets](../skills/closebook/references/host-widgets.md)). `AskUserQuestion` is reserved by its own rules for decisions the user must make and is not used as a quiz. Terminal CLI: unverified | **Unverified**; decided per session from the listed tools, never assumed |
| Level 2 HTML page | `build_lesson.py` writes a file the learner opens in a browser | Artifacts can be single-page websites (verified). Building one from the skill's template file rather than retyping it is **unverified**; if not possible, the skill stays at Level 0 (see `references/html-lesson.md`) |
| Progress file | `closebook-progress/<topic>.json` in the project, via `progress_tool.py` | Treat as chat-only: compact JSON at the end of each session, pasted back next time. Whether files persist between chats is **unverified** |
| `localStorage` / downloads in an artifact | n/a | **Unverified**; the page falls back to copy/paste export |

## Optional MCP cards

Use the agent's own components first ([host widgets](../skills/closebook/references/host-widgets.md)), following the [renderer rules](../skills/closebook/references/interaction-fit.md). The [closebook MCP companion](../mcp/README.md) is an optional fallback configured separately from the skill ZIP. Its cards and submission flow have **not been tested in these clients**. Check the actual client's MCP Apps support; connecting an MCP server does not establish that it can display cards. Plain-text teaching remains available.

## Quick check after installing

Say: "考考我：［主题］" (or "Quiz me on [topic]"), with a topic of your own. Expected: a concise typed outline for a topic, or the complete source inventory with today's subset for course material, plus any necessary time/familiarity questions, and no summary of the material.
