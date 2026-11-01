<p align="center"><img src="docs/images/logo.jpg" alt="closebook" width="160"></p>

<h1 align="center">closebook</h1>

<p align="center"><b>先学明白，再合上资料，自己讲出来。</b><br>
一个帮助 AI 助手分步教学、带你练习和安排复习的 Agent Skill。</p>

<p align="center"><a href="README.md">English</a> · 简体中文 · <a href="LICENSE">MIT</a></p>

closebook 给 AI 助手一套教学流程。发给它一个主题、一份笔记，或上次的学习进度，告诉它你想学什么就能开始。

- **学习新知识时**，先讲一小段，示范一个例子（agent 能画图时配上流程图、单步演示或可调参数的小实验），再用一道题检查理解；也可以选择一次讲完一节 2 到 4 个知识点，再用一张 3 到 5 题的题卡逐题当场判分。今天的知识点全部讲完后合上资料统一重测；一天或几天学过的内容可以做成闭卷考核页。
- **练习或复习时**，先作答，再针对答案里的漏洞讲解，最后换一道题确认是否掌握。

**无论使用哪个 agent 平台，都优先使用适合教学任务的内置组件、工具或插件。** 可选 MCP 卡片、HTML 和文字遵循统一的[交互选择规则](skills/closebook/references/interaction-fit.md)。

## 复制提示词，让 agent 安装

把下面整段复制给你正在使用的 agent，让它下载、安装、配置并验证 closebook。你无需下载提示词文件，也不用自己研究配置路径。提示词用英文，安装过程和需要你操作的步骤用中文说明。

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

agent 需要有平台支持的安装方式和相应权限。有些应用仍需要你点一下、上传文件或重启；无法持久安装时，它应明确说明，并提供标注清楚的“仅本次会话使用”方式。具体流程见[安装说明](INSTALL.md)。

**版本范围：** 提示词安装最新稳定版 [v0.3.0](https://github.com/sheepxux/closebook/releases/tag/v0.3.0)，包含本文介绍的新版分段教学流程和内置能力优先规则。可选的中英文 MCP 组件位于该版本源码的 `mcp/` 目录，需要单独配置，不包含在 skill 安装包里。

## 安装后，直接这样说

| 想做什么 | 可以发送 |
|---|---|
| 从零学习 | “用 closebook 教我 Python 列表推导式。我完全没学过，今天有 20 分钟。” |
| 复习笔记 | “用 closebook 考考我这份笔记，重点练我答错的地方。” |
| 换个容易懂的讲法 | “用大白话讲一次函数的斜率和截距，先举例，再让我试一道题。” |
| 接着上次学 | “这是我的 closebook 进度文件，带我复习今天到期的知识点。” |
| 离线练习 | “把现在完成时做成离线练习页，先讲解，再练习。” |

你说明的基础优先于请求里的动词：即使说“考考我”，同时说明完全没学过，也应该先教。学习一整门学科时，closebook 会按先修关系安排路线，把今天来不及学的部分留到后续。

练习时先由你作答，再展示参考答案。可以直接回答“不会”；有标准答案的题还可以记录你的把握程度。反馈会指出具体缺口，再给一次回忆和作答的机会。读完卡片、点击“继续”，都不算掌握。

术语可以用回忆卡，概念可以用自己的话解释，操作可以先预测再验证。你随时可以换学法、要求说人话，也可以只要总结。

## 交互方式怎么选

同一套教学流程可以使用不同界面；选择顺序与例外情况统一写在[交互指南](skills/closebook/references/interaction-fit.md)。

| 方式 | 什么时候用 | 谁来核对答案 |
|---|---|---|
| agent 自带的组件：内联组件（Codex 和 ChatGPT 的 Visualize、Claude Code 的 `show_widget`）或带选项的提问工具 | 只要 agent 有就优先用：题目画在对话里，作答以消息形式回到聊天 | 有标准答案的题在组件里当场判分，点“下一题”时一行结果回到聊天；书面回答由助手批改 |
| 可选 closebook MCP 卡片 | 内置能力不适用，且客户端支持 MCP Apps 时 | 提交后回到聊天，由助手核对 |
| 离线 HTML 练习页 | 你明确要求，或适合制作可重复使用的练习页时 | 支持的题型由页面自动判定，书面回答可导出给助手批改 |
| 纯文字对话 | 始终可用的备用方式 | 助手在对话中逐题反馈 |

仅限审批的工具，或自身规则禁止测验、只用于决策的工具，不会拿来充当测验。你明确指定某种界面时，例如测试 MCP 卡片或制作离线页面，按你的要求执行。

### 七种 MCP 组件

可选 MCP 目前实现了 **7 种组件**：

| 组件 | 你可以做什么 |
|---|---|
| 知识讲解卡 | 看一段讲解和示范，然后继续练习，或要求换个例子 |
| 选择题 | 选择并提交答案 |
| 简答 | 用自己的话解释、推理或写出回答 |
| 数值题 | 输入数值或表达式、单位，也可以补充计算过程 |
| 填空 | 直接在原文位置逐空填写 |
| 排序 | 排列词块、步骤或代码行，也可以留下干扰项 |
| 回忆卡 | 先写答案或选择“还不会”，提交成功后再翻面看参考 |

练习卡片也可以收集把握程度。它们把原始作答交回聊天，本身不自动判分、不更新学习进度。提交失败时保留输入，方便重试或复制。七种组件共用浅青蓝配色、系统字体，支持明暗主题和键盘操作。中英文界面通过 `locale` 跟随学习者的交流语言，和正在学习的材料语言分开。

代码追踪、模拟终端、坐标图和参数实验目前走 HTML 页面，尚未移植成 MCP 卡片；语音交互取决于宿主能力。配置方式、工具和验证范围见 [MCP 组件说明](mcp/README.md)。

### 离线练习页

<p align="center"><img src="docs/images/lesson-page.jpg" alt="离线 HTML 练习页：预测请求流程中的缺失步骤" width="720"></p>

*图中是 HTML 练习页；MCP 卡片使用独立界面。*

告诉 agent“做成练习页”，它可以生成一个离线打开的 HTML 文件，无需 API Key，也不发起网络请求。页面支持分段讲解（一段一题，或整节讲完再逐点检查）、问答、图解、回忆卡，以及不同学科的练习。**考试模式**下它是一份闭卷考核：作答后锁定不显示对错，可选计时，交卷后给出成绩报告、按知识点的表现、薄弱点和全部解析：

| 学科 | 练习示例 |
|---|---|
| 编程、Git | 预测代码输出、逐步看变量变化、排列代码行、在模拟终端练命令 |
| 数学、物理 | 输入数值或分数、匹配目标曲线、先预测再调整参数观察变化 |
| 语言、生物 | 补全文段、排列句子、回忆术语 |

模拟终端只核对预设命令、显示准备好的输出，不执行真实命令。生成页面时，Python 代码追踪核对器会运行受支持的教学代码，执行步骤与答案不一致就报错。其他语言，以及自然语言预测题的答案，仍需独立复核。

有答案表的题型由页面自动判定；简答和回忆卡可以自评，也可以把作答导出给聊天中的助手批改，再将批改结果粘贴回页面。这一步需要复制粘贴，因此页面可以保持离线。

下载后用浏览器打开示例：[先教后练](examples/new-learner-lesson.html)、[HTTP 缓存复习](examples/http-cache-lesson.html)、[各学科题型](examples/subject-widgets-lesson.html)、[考试模式的当日考核](examples/daily-assessment.html)。题型选择和纯文字替代方式见[交互指南](skills/closebook/references/interaction-fit.md)。

## 学习进度由你保存

closebook 记录知识点、作答、错误和下次复习日期。间隔复习使用 1、3、7、14、30 天的档位，根据作答记录调整；“很有把握却答错”的知识点优先复习。

能持久保存文件的环境，由 agent 维护 JSON 进度文件。只有聊天的环境，会在结束时给你一小段记录，下次粘贴回来即可。进度属于你，不假定平台能跨对话记住一切。具体字段见[进度格式](skills/closebook/schemas/progress.schema.json)。

## 平台说明与手动安装

文字教学流程不依赖卡片。能否安装、能用哪些交互，取决于宿主实际能力；连接上 MCP 服务也不代表客户端一定能显示卡片。

| Agent 或应用 | 说明 |
|---|---|
| Claude Code、Claude Desktop、claude.ai | [Claude 适配](adapters/claude.md) |
| Codex、ChatGPT | [OpenAI 客户端适配](adapters/chatgpt-codex.md) |
| Hermes Agent | [Hermes 适配](adapters/hermes.md) |
| Gemini CLI、Gemini Apps | [Gemini 适配](adapters/gemini.md) |
| 其他 agent，或仅本次会话使用 | [通用适配](adapters/generic.md) |

想手动安装，可以下载[标准 skill ZIP](https://github.com/sheepxux/closebook/releases/latest/download/closebook.zip) 或 [Gemini skill ZIP](https://github.com/sheepxux/closebook/releases/latest/download/closebook-gemini.zip)，按对应平台说明安装。安装包包含 skill，不包含 MCP 服务。平台能力的依据和核实日期见[平台核实记录](docs/platform-verification.md)。

## 已经验证到哪一步

[验证报告](docs/validation-report.md) 记录了教学行为、进度管理和 HTML 浏览器测试。[标准答案审计](docs/answer-key-validation.md) 包含独立运行代码、公式重算、真实 Git 操作和等价答案检查，也保留了发现的问题和修复结果。[MCP 改进报告](docs/mcp-hardening-validation.md) 记录了本版自动检查、新增六个工具选择场景、定向修复、桌面回传结果与待完成项。

截至 2026-11-01，可选 MCP 组件的验证情况为：

- 自动化检查覆盖协议、消息回传、DOM 交互、界面语言和启动。它们与 34 道 agent 行为评测分开记录，都不能代替各桌面客户端的真实验收。本地审计当时未运行 HTML 浏览器测试；随后提交 `445d330` 的 [Ubuntu 远程 CI](https://github.com/sheepxux/closebook/actions/runs/41266442700) 完整执行 `python3 tools/check.py`，135 项 Python（含 11 项浏览器测试）、打包检查及 41 项 MCP 测试全部通过，0 跳过。
- 在 Codex 桌面重载 MCP 后，七种卡片累计九次真实提交返回同一聊天，其中排序三次。样本保留了选项与信心、中英文多行文字、分数与单位，以及填空 ID 和弯撇号。用户还确认回忆卡参考答案只在提交后出现；阅读确认和验收作答均未计入学习进度。
- 最后的两项排序补检要求把 1 上移到 2 前，实际回传为 1 → 2，符合要求。前两次未能核实画面和用户误点的记录仍保留。点击过程未被独立观察，这不代表每个按钮及所有异常分支都已实机验证；另行执行的 DOM 定向检查通过。
- 当前浅青蓝样式和全部界面标签尚未独立目视复核，中英文回传消息已分别观察。Claude、Hermes 等其他客户端尚未完成这套组件的实机测试。

这些检查不能保证每次生成的标准答案都正确、完整；助手仍需独立核对，并接受合理等价答案。细节见 [MCP 验证范围](mcp/README.md#检查与验证范围)。

## 开发与贡献

<details>
<summary>查看源码结构和检查命令</summary>

```text
skills/closebook/        安装的 skill：核心指令、参考资料和可选辅助工具
  SKILL.md              教学流程与交互选择
  references/           学习方法、交互规则和平台备用方案
  schemas/              进度、课程、作答导出和批改格式
  scripts/              进度管理和 HTML 构建器（Python 3.8+，标准库）
  assets/               离线 HTML 模板
  evals/                34 个行为评测用例，不打入发布 ZIP
mcp/                    可选 MCP Apps 组件（Node.js 20+）
adapters/               各平台安装说明
docs/                   验证报告与设计决策
examples/               生成好的 HTML 练习页
tests/                  skill、打包、判分和浏览器测试
tools/package_skill.py  发布 ZIP 构建工具
```

在仓库根目录执行：

```sh
npm ci --prefix mcp --loglevel=error
python3 tools/check.py
```

完整命令包含 Python、打包、浏览器和 MCP 检查，测试被跳过时会报失败。浏览器依赖安装见 [CONTRIBUTING.md](CONTRIBUTING.md)。当前环境不能运行浏览器时，可以用 `--skip-browser`，并明确标注只完成部分检查。GitHub Actions 执行完整的确定性检查；34 道 [agent 行为评测](skills/closebook/evals) 单独运行。

可选 MCP 组件的检查：

```sh
cd mcp
npm ci --loglevel=error
npm run build
npm test
```

启动服务和客户端配置见 [MCP 指南](mcp/README.md)。本次发布的 MCP 包与 skill 均为 `0.3.0`，但两者仍独立编号；UI 资源修订号也单独维护。

</details>

[MIT](LICENSE) © sheepxux
