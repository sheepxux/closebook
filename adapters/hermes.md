# 在 Hermes Agent 中使用 closebook

**核实日期：**2026-10-31。以下安装机制依据 NousResearch 官方文档与源码核实；**尚未实机验证 closebook 在 Hermes 中的安装、触发和页面生成**。

优先把[通用安装提示词](../INSTALL.md)发给 Hermes，由它识别当前 profile 并安装。

## 安装位置

Hermes 默认从 `~/.hermes/skills/` 读取技能。实际目录应以当前运行配置的 `HERMES_HOME` 为准：

```text
<当前 HERMES_HOME>/skills/closebook/SKILL.md
```

命名 profile 通常使用 `~/.hermes/profiles/<name>/` 作为自己的 Hermes 主目录。确认当前 profile 的有效路径，不能只看普通 shell 中未设置的环境变量，就认定应安装到默认 profile。保留用户已有的 `skills.external_dirs` 和符号链接配置；不要为了安装技能切换默认 profile。

依据：[Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)、[外部技能目录](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#external-skill-directories)。

## 安装正式版

从 [closebook 最新正式 Release](https://github.com/sheepxux/closebook/releases/latest) 确定 tag 并下载 `closebook.zip`，把包内完整的 `closebook/` 安装到已确认的技能目录。保留 `references/`、`schemas/`、`scripts/`、`assets/`；覆盖规则与验证步骤遵循 [INSTALL.md](../INSTALL.md)。

Hermes 提供 `hermes skills install <identifier-or-url>`，GitHub 子目录标识形如 `owner/repo/path/to/skill-dir`。按官方源码，这种标识默认读取仓库的默认分支；尚未核实可固定 tag 的命令参数。因此，本指南不将 `hermes skills install sheepxux/closebook/skills/closebook` 当作安装正式 Release 的命令。若后续版本支持固定 ref，应先检查当前 CLI 帮助，再使用与 Release 一致的 tag。

依据：[直接从 GitHub 安装](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#4-direct-github-skills-github)、[GitHub 下载实现](https://github.com/NousResearch/hermes-agent/blob/main/tools/skills_hub_github.py)。

## 验证与调用

在同一 profile 中使用 `hermes skills list` 或宿主的 `skills_list()`，确认能找到 `closebook`；再用 `skill_view("closebook")` 确认正文能读取。手动复制的技能不要用仅筛选 Hub 安装项的 `--source hub` 来验证。

安装后可使用 `/closebook` 或自然语言请求，例如“用 closebook 帮我学 Python 列表推导式”。这些是 Hermes 文档支持的调用方式，尚未作为本项目的实测结果。

最新技能文档说明对话中的技能变化会在下一条消息通知，`/reload-skills` 刷新斜杠命令；较早的使用指南仍描述新会话的方式。以当前版本的实际发现结果为准，未加载时给用户相应重载步骤，不要自动 `/reset` 清空聊天。

依据：[技能使用指南](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills)、[对话中的技能变化](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#skill-changes-during-a-conversation)。

纯文本学习不依赖 Python。生成 HTML 页面还需要实际可用的文件操作、Python 3.8+ 和页面打开能力；这些能力应在当前 Hermes 环境中检查，不能仅凭安装成功就声称全部可用。
