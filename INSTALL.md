# 发一句话，让 agent 安装 closebook

复制下面整段发给 agent，由它下载并配置 closebook。用户无需下载提示词文件。

```text
Install and configure closebook for the agent I am using now:
https://github.com/sheepxux/closebook

Assume I have no technical background. Handle environment checks, downloads, installation paths, configuration, activation, and verification yourself. Do not ask me to choose technical settings, edit configuration files, or run terminal commands when your tools can do that work.

Fetch and follow the installation workflow:
https://raw.githubusercontent.com/sheepxux/closebook/main/INSTALL.md

Identify your actual host and active profile. Download the latest stable release yourself, install the complete skill in the correct persistent location, enable it using the host's supported mechanism, and verify that the host can discover it. Use your tools to complete the work; do not stop at instructions or ask me to download files that you can download yourself.

Preserve my existing settings, local skill modifications, and learning records. Involve me only for required permissions, unavoidable UI actions, or unresolved conflicts. If persistent installation is impossible, explain the specific limitation and the minimum remaining step; do not claim success or mistake a temporary sandbox for an installed skill.

When I must act, give one concrete step at a time in everyday Chinese: where to click or what to paste, and what I should see next. Use the actual interface or verified documentation; do not invent controls. If the platform has no supported installation path, offer a clearly labeled session-only learning option instead of leaving me with a technical setup tutorial.

Use Simplified Chinese for all progress updates, questions, and the final response. Lead with whether closebook is actually ready to use, any action I still need to take, and one ready-to-copy learning request. Keep version, path, and verification details brief and secondary. Complete installation first; do not begin a lesson yet.
```

以下流程供 agent 读取并执行。

## 给执行安装的 agent

目标是让 **当前正在与用户对话的 agent** 能发现并使用 closebook。只安装到当前宿主及当前配置使用的一个位置；不要因为机器上存在多个 CLI 就给它们全部安装。先完成安装，不自动开始教学。

### 1. 确认宿主和安装能力

结合宿主提供的技能工具、当前配置、官方帮助和实际目录确定安装方式。模型名称不能证明宿主：使用 Claude 模型的 Hermes 仍按 Hermes 安装，ChatGPT 也不能直接套用 Codex 的本地目录。

- 有原生技能安装工具时优先使用，确认它会安装完整技能目录，并能指定目标版本与当前配置。
- 有持久文件系统且宿主会扫描本地技能时，使用下表定位。自定义配置、用户明确指定的位置和当前 profile 优先于默认值。
- 只有聊天或临时计算沙箱时，走第 4 节。临时容器里的文件不能证明用户账号已经安装了技能。
- 宿主身份或目标目录有多个合理选择、又无法从上下文确定时，只问一个必要问题。

| 宿主 | 默认安装位置或方式 | 依据 |
|---|---|---|
| Claude Code | `~/.claude/skills/closebook/` | [Claude 说明](adapters/claude.md) |
| Codex 本地技能环境 | `~/.agents/skills/closebook/`；优先服从已确认的宿主配置和安装工具 | [OpenAI 官方文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) |
| Hermes Agent | 当前 profile 的 `$HERMES_HOME/skills/closebook/`；未自定义的默认 profile 通常为 `~/.hermes/skills/closebook/` | [Hermes 说明](adapters/hermes.md) |
| Gemini CLI | `~/.gemini/skills/closebook/` | [Gemini 说明](adapters/gemini.md) |
| Claude、ChatGPT、Gemini 的账号技能界面 | 使用当前账号提供的上传或安装工具，不假定有本地扫描目录 | [Claude](adapters/claude.md)、[ChatGPT](adapters/chatgpt-codex.md)、[Gemini](adapters/gemini.md) |
| 其他 agent | 读取当前版本的官方技能说明或 CLI 帮助，确认发现目录、格式和启用方式 | 未确认时不猜目录 |

路径中的 `~` 表示当前用户主目录，按实际操作系统解析。只在用户要求项目级安装时使用项目目录。若用户要求持久文件放在外置盘等位置，先确认该位置可用；仅在宿主支持时通过符号链接或其配置连接到发现目录，不能静默改存其他位置。

### 2. 下载并安装完整的正式版本

1. 查询本仓库的[最新正式 Release](https://github.com/sheepxux/closebook/releases/latest)（也可读取 `https://api.github.com/repos/sheepxux/closebook/releases/latest`），记录确定的 tag；若用户指定版本则使用指定版本。后续下载都固定到这个 tag，不能把 `main` 的开发代码当作正式版本。
2. 从该 Release 下载 `closebook.zip`；Gemini Apps 使用 `closebook-gemini.zip`。公开下载无需向用户索取 API Key。若原生安装器从源码安装，指定同一 tag 下的 `skills/closebook` 子目录；不要只复制 `SKILL.md`。
3. 在临时位置解压并检查。Release ZIP 的根目录已是 `closebook/`；最终应为 `<技能目录>/closebook/SKILL.md`，不是再套一层 `closebook/closebook/`。确认 `references/`、`schemas/`、`scripts/`、`assets/` 一起存在。若 Release 提供附件摘要，核对下载文件的摘要。
4. 安装前检查同名技能和符号链接。版本、文件均相同就复用；能确认是未修改的旧官方版本时，在宿主扫描范围之外备份旧版再更新。存在本地修改、来源不明或链接目标不清楚时保留原件，说明具体冲突后再决定。不要改动学习进度或其他技能，也不要把备份留在会被当成第二份技能发现的位置。
5. 使用宿主支持的安装、扫描或启用机制。当前会话不能刷新时，标记“文件已安装，待重新加载”，给出该宿主需要的新对话或重启步骤；不要中断用户正在进行的会话。

下载失败时明确报告实际失败点与可用下载链接。不要自动退回未经指定的版本，也不要把 GitHub 错误页面保存成 `SKILL.md`。

### 3. 验证并交付

分别核对文件和宿主发现情况：

- **文件验证：**检查 `SKILL.md` 的 `name` 为 `closebook`、`metadata.version` 与选定版本相符，完整内容与下载源一致，引用文件存在。
- **脚本检查（可选）：**已有 Python 3.8+ 时，从安装位置执行下列命令；缺少 Python 时说明仍可使用纯文本教学，无需为了安装技能自动安装开发依赖。

  ```text
  python3 <closebook安装目录>/scripts/progress_tool.py --help
  python3 <closebook安装目录>/scripts/build_lesson.py <closebook安装目录>/schemas/examples/lesson.http-cache.json --check
  ```

  上面是路径占位符；实际执行时替换成安装路径并正确处理空格。`--check` 只验证示例数据，不生成课程或学习记录。

- **宿主验证：**在当前宿主提供的技能列表、选择器或读取工具中确认 `closebook` 出现且可用。有正式启用开关时检查状态。只能看到磁盘文件时，只报告文件已就位，不声称已验证自动触发；单独读取文件并按它回答，也不能证明宿主会自动发现它。

按用户指定的语言简短交付：宿主及配置范围、版本和来源、实际安装路径或账号范围、验证了什么，以及仍需用户完成的步骤。本项目的安装提示词默认要求简体中文，用户明确指定其他语言时照办。按证据给出状态：**已安装并可被发现**、**文件已安装，待重新加载/验证发现**、**待用户上传/启用**，或 **仅当前对话生效**。

给一句启动示例：“用 closebook 帮我学习 Python 列表推导式，我有 20 分钟，学过但不牢。” Codex CLI/IDE 可使用 `$closebook`，其他宿主按各自的调用方式，不把某个平台的命令套到所有平台。

### 4. 不能自动持久安装时

如果宿主有账号技能入口但当前工具无法操作，提供本次固定 tag 的 ZIP 下载链接和该平台最少的上传、启用步骤。入口名称以当前账号界面和官方文档为准；不能因用户有聊天账号就假定该功能可用。

如果没有技能机制，可以读取 [generic.md 的中文指令](adapters/generic.md#中文)，在当前对话按该流程工作，并说明这只是本次对话的临时用法。需要跨对话复用时，给用户该指令块及其宿主支持的自定义指令或项目配置方式。完整练习页和脚本能力不随这个精简版提供。

不能联网读取安装说明或技能内容时，不编造已读取的内容；提供[发布页](https://github.com/sheepxux/closebook/releases/latest)，让用户上传安装包或粘贴相应指令，再继续。

## 验证范围

本页是供 agent 执行的安装流程，不是绕过平台权限的统一安装器。Codex 的技能目录和发现方式已依据 OpenAI 官方文档核对，Hermes 的目录、profile 和技能管理方式已依据其官方文档与源码核对，但未进行 Hermes 实机安装；其他平台的依据与边界见上方适配说明及[平台核实记录](docs/platform-verification.md)。不能据此声称这段提示词已经在所有 agent、操作系统和账号上实测成功。

2026-10-31 使用已发布的 v0.2.0 ZIP，在独立临时目录中核对了目录结构并执行第 3 节的两条检查命令，均通过。这项检查没有安装到任何宿主，也不验证技能的自动发现或触发。
