# closebook on Claude (claude.ai, Desktop, mobile, Claude Code)

**Status:** install path and frontmatter rules **verified 2026-10-31**; rendering details marked per line.
**Sources:** [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) · [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) · [Claude Code: skills](https://code.claude.com/docs/en/skills) · [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) · [What are artifacts](https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them). Full log: [`docs/platform-verification.md`](../docs/platform-verification.md).

## Install

**claude.ai / Claude Desktop** (Free, Pro, Max, Ultra, Team, Enterprise; verified)
1. Turn on code execution ("Code execution and file creation"); skills need it.
2. Build the ZIP: `python3 tools/package_skill.py` → `dist/closebook.zip` (its root is the `closebook/` folder, as required).
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
| Level 1 clickable options | not assumed | **Unverified**; the skill doesn't assume it |
| Level 2 HTML page | `build_lesson.py` writes a file the learner opens in a browser | Artifacts can be single-page websites (verified). Building one from the skill's template file rather than retyping it is **unverified**; if not possible, the skill stays at Level 0 (see `references/html-lesson.md`) |
| Progress file | `closebook-progress/<topic>.json` in the project, via `progress_tool.py` | Treat as chat-only: compact JSON at the end of each session, pasted back next time. Whether files persist between chats is **unverified** |
| `localStorage` / downloads in an artifact | n/a | **Unverified**; the page falls back to copy/paste export |

## Quick check after installing

Say: "考考我：HTTP 缓存里的 no-cache 和 no-store" (or "Quiz me on…"). Expected: an outline of 3–5 points with types, plus one question about time and familiarity, and no summary of the material.
