# Platform verification log

Every platform claim used by closebook, with how it was checked. **Verified** = read on an official documentation or help page on the date given. **Unverified** = reported by a model about itself, by user testing, or not found in official docs; treat as a hypothesis.

Verification date for this round: **2026-10-31**; host-widget rows added **2026-11-01**. Pages change; re-check before each release.

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
| The Claude Code desktop app lists a `show_widget` tool that renders HTML/SVG inline, with a global `sendPrompt(text)` that sends a message to the chat as the user, and a `read_me` guidance tool | Seen in a Claude Code desktop session on 2026-11-01 (tool list); not on a public help page, so **unverified** for other clients | — |
| Claude Code's `AskUserQuestion` tool is reserved by its description for decisions the user must make | Seen 2026-11-01 (tool description) | — |

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
| Visualizations: interactive charts, maps, diagrams and explainers rendered inside a ChatGPT conversation via `@Visualize`; Codex CLI and the IDE extension do not render them | Verified 2026-11-01 | [Visualizations](https://learn.chatgpt.com/docs/visualizations) |
| The Codex desktop app bundles a `visualize` plugin (marketplace `openai-bundled`, version 1.0.66 on 2026-11-01). Its skill writes an HTML fragment, references it with `visualize{"path": …}` in the reply, and offers `window.openai.sendFollowUpMessage({prompt, title})` (sends a chat message after a confirmation dialog) and `window.openai.setWidgetState` | Verified 2026-11-01 from the installed plugin files (`~/.codex/plugins/cache/openai-bundled/visualize/1.0.66/`); no public page found | local `plugin.json` and `skills/visualize/SKILL.md` |
| On macOS the "Codex desktop app" is the ChatGPT desktop app (`/Applications/ChatGPT.app`, bundle id `com.openai.codex`, launched by `codex app`); its chat runs in an isolated Linux sandbox that cannot read the Mac's disks, and skills there are installed through the app (Customize → Skills, chat-driven Skill Creator with a ZIP attachment), not from `~/.agents/skills` | Verified 2026-11-01 by inspecting the app and installing through it | local app bundle; the app's own reply |
| The ChatGPT app's skill upload runs a safety scan on save; the closebook ZIP packaged at 784cd8d (and a reworded repackage) was refused twice with HTTP 422 `invalid push content: skill did not pass the safety scan`, with no file, line or rule named. The previously installed 0.3.0 release had passed | Observed 2026-11-01 | the app's reply quoting the platform response |
| Control on 2026-11-01 (later the same day): re-pushing the unchanged 0.3.0 release package through the same Skill Creator chat is refused with the identical 422, although that very version is installed and in use. So the refusal is not caused by the 2026-11-01 content changes; the scan or the save path changed on the platform side. Five variants were refused in total (new, reworded twice, without `host-widgets.md`, with the 0.3.0 page template, and 0.3.0 itself) | Observed 2026-11-01 | the app's replies quoting the platform response |
| The ChatGPT skill scan is an automated content review with categories such as "Fraud scams" and "Security risk"; one maintainer reports skills were held for wording like "never mention it" and "call again … without asking again" and passed after rewriting those phrases | Community report, **unverified** by OpenAI docs (2026-11-01) | [Creatorline/skills PR 4](https://github.com/Creatorline/skills/pull/4), [last30days-skill issue 1351](https://github.com/mvanhorn/last30days-skill/issues/1351) |
| Narrowing the refusal with new skill names built from the 0.3.0 files (same day): a one-file skill installs; SKILL.md + references + agents installs; adding schemas and both Python scripts still installs; adding `assets/lesson-template.html` is refused; the same template with its `<script>` removed installs (the `<script type="application/json">` data block is fine); a template with only a ten-line benign script is refused. So the scan refuses any HTML file that contains executable JavaScript, regardless of what the script does; Python scripts and Markdown are accepted; a separate `.js` file with the same ten lines is refused as well, so JavaScript is refused in any form. `closebook-chatgpt.zip` (same files minus `assets/lesson-template.html`) was then accepted and is the installed version. In the same app's **Codex mode** (local agent, skills read from `~/.agents/skills`, no upload scan), the browser pane opened `http://localhost:8766/daily-assessment.html` served from the repository's `examples/` folder and rendered the exam-mode page with its countdown and questions; `file://` is refused by the pane. Uninstalling through the same push path is refused with `aggregate skills install, uninstall, and delete are not enabled`; test skills must be removed from the skills page | Observed 2026-11-01 | the app's replies quoting the platform responses |
| In the same app, a skill ZIP attached to a chat is read and followed without being installed, and the bundled Visualize renders the skill's question cards: in-card checking, one host confirmation dialog on the card's continue button, and the result line arriving in the chat as the learner's message were all seen working | Verified 2026-11-01 by clicking through two cards in the app | the app session (validation report, 2026-11-01 真实客户端尝试) |
| Codex `request_user_input`: 1–3 questions with 2–3 options each, "Other" added by the client; available in Plan mode by default, in Default mode only with `features.default_mode_request_user_input` (shown as "under development" by `codex features list`, Codex CLI 0.153.4) | Verified 2026-11-01 in the openai/codex source and the local CLI | [request_user_input spec](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input_spec.rs), [default-mode template](https://github.com/openai/codex/blob/main/codex-rs/collaboration-mode-templates/templates/default.md) |
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

## Hermes Agent (NousResearch)

以下项目于 **2026-10-31** 通过官方文档与源码核实；不是 closebook 的 Hermes 实机测试。

| 结论 | 状态 | 来源 |
|---|---|---|
| 默认技能目录为 `~/.hermes/skills/`；有效目录以当前 profile 的 `HERMES_HOME` 为准，命名 profile 通常使用 `~/.hermes/profiles/<name>/` | 文档已核实 | [Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)、[技能指南](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills) |
| 支持 `hermes skills install <identifier-or-url>`，GitHub 子目录标识为 `owner/repo/path/to/skill-dir`；已查看的实现读取默认分支，不能据此声称安装指定 Release | 文档与源码已核实；固定 tag 的 CLI 参数未核实 | [GitHub 安装](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#4-direct-github-skills-github)、[下载源码](https://github.com/NousResearch/hermes-agent/blob/main/tools/skills_hub_github.py) |
| 可用 `hermes skills list`、`skills_list()` 和 `skill_view()` 检查发现及读取；`--source hub` 只适合筛选 Hub 安装项 | 文档已核实 | [技能指南](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills) |
| 最新技能文档描述下一条消息接收技能变化，`/reload-skills` 刷新斜杠命令；旧指南描述新会话行为，安装流程应按实际版本判断 | 文档存在版本差异，不能统一写成必须重置会话 | [对话中的技能变化](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#skill-changes-during-a-conversation) |
| 支持 `skills.external_dirs` 与符号链接，可沿用已有共享目录和外置存储配置 | 文档已核实 | [外部技能目录](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#external-skill-directories)、[外置存储](https://hermes-agent.nousresearch.com/docs/getting-started/installation#symlinked-home-directories-and-external-storage) |
| closebook 在 Hermes 中实际完成安装、自动触发、Python 脚本执行和 HTML 页面生成 | **未实测** | — |

## 通用安装提示词

[INSTALL.md](../INSTALL.md) 统一安装入口；宿主、配置、权限与实际发现结果决定完成状态。它不代表所有平台都能仅靠聊天自动持久安装。Codex 的用户目录、符号链接和技能发现机制在本轮按 [OpenAI 官方文档](https://learn.chatgpt.com/docs/build-skills) 再次核对。提示词未进行多平台实机安装测试，不能将文档核对或文件检查记作安装成功率。

## Consequences for closebook

- Package folder is `skills/closebook/` so the folder name equals `name` and the folder can be zipped as-is.
- Frontmatter uses only `name`, `description`, `license`, `metadata` (accepted by every platform above).
- No hidden files may ship in the package (`tests/test_skill_structure.py` checks this).
- The skill never assumes Level 1/2 rendering; it detects capability per session and defaults to Level 0.
- Scripts are optional helpers; the teaching flow works without executing anything.
- Every verified Level 2 surface (Claude artifacts, ChatGPT HTML preview, Gemini Canvas) renders HTML that the model writes into the reply. The lesson template is ~75 KB, so `references/html-lesson.md` only builds pages from a file (script or copy), never by retyping; on chat-only surfaces the default stays Level 0.
