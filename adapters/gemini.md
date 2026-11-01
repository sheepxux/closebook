# closebook on Gemini (Gemini Apps, Gemini CLI)

**Status:** Gemini Apps skill upload and Gemini CLI paths **verified 2026-10-31**; script execution, `.yaml` uploads and rendering are marked per line.
**Sources:** [Create & manage skills for Gemini Apps](https://support.google.com/gemini/answer/17094296) · [Gemini CLI: Agent Skills](https://geminicli.com/docs/cli/skills/) · [Canvas in Gemini Apps](https://support.google.com/gemini/answer/16047321). Full log: [`docs/platform-verification.md`](../docs/platform-verification.md).

## Install

**Gemini Apps: skill upload (primary path)**. Works on gemini.google.com, the mobile app and the Mac app; no Google AI subscription needed (verified).
1. `python3 tools/package_skill.py` → `dist/closebook-gemini.zip`. This build leaves out `agents/openai.yaml`, because `.yaml` isn't on Gemini's list of supported upload types (**unverified** whether it would be rejected), and it never contains `.DS_Store` or `.pyc` files, which can make uploads fail (verified).
2. Upload the ZIP (or the `closebook/` folder) where Gemini lets you create skills.

Notes (verified): the name must be lowercase with hyphens (it is); uploads are limited to 100 MB; scripts can't reach the internet. Whether Gemini Apps actually **runs** the bundled Python scripts is **unverified**, which is fine because the teaching flow never depends on them.

**Gemini CLI** (verified)
```bash
mkdir -p ~/.gemini/skills && cp -R skills/closebook ~/.gemini/skills/
# also read: ~/.agents/skills, and per project .gemini/skills or .agents/skills
```
The CLI asks for consent before activating a skill.

## Fallback: a Gem with the paste-in

If skills aren't available to you, create a Gem and paste the instruction block from [`generic.md`](generic.md) (English or Chinese) as its instructions. The block keeps the anti-spoiler rule (never reveal an unanswered answer, never two open questions), confidence ratings and the compact progress export.

Google has said it plans to remove Gems and recreate them automatically as skills (verified, no date given). When that happens, prefer the skill upload above; the full skill is much more precise than the paste-in.

## What works at which level

| Capability | Gemini Apps | Gemini CLI |
|---|---|---|
| Level 0 plain text | yes | yes |
| Level 1 suggestion chips / quiz cards | **Unverified** (user reports of at most 3 chips); not assumed | no |
| Level 2 HTML page | Canvas previews HTML and React apps (verified), but that means retyping the ~75 KB template, which the skill avoids. Using Canvas from inside a skill is **unverified** | `build_lesson.py` writes a file to open in a browser |
| Progress file | Chat-only: compact JSON at the end, pasted back next time | `closebook-progress/<topic>.json` via `progress_tool.py` |

## Optional MCP cards

Use suitable built-in teaching tools first, following the [renderer rules](../skills/closebook/references/interaction-fit.md). The [closebook MCP companion](../mcp/README.md) is an optional fallback configured separately from the skill ZIP. Its cards and submission flow have **not been tested in these clients**. Check the actual client's MCP Apps support; connecting an MCP server does not establish that it can display cards. Plain-text teaching remains available.

## Quick check after installing

"考考我：光合作用的光反应和暗反应" or "Quiz me on these notes". Expected: an outline with knowledge types and one question about time and familiarity, with no summary of the material.
