# closebook 可选 MCP 学习组件

内置教学能力优先，MCP 是可选备用；完整选择顺序见 [交互规则](../skills/closebook/references/interaction-fit.md)。组件独立于 skill ZIP，纯文字教学不需要安装它。

目前提供七种形式：

| 组件 | 学习者操作 | 适用场景 |
|---|---|---|
| 知识讲解卡 | 看讲解和示范，选择继续练习或换个例子 | 新知识的分段教学；阅读完成不算掌握 |
| 选择题 | 选择答案并提交 | 易混概念与常见误区 |
| 简答 | 用自己的话写，多行作答 | 费曼讲解、推理、语言输出 |
| 数值题 | 填数值或表达式、单位和可选过程 | 数学和物理 |
| 填空 | 在原文位置逐空填写 | 语法、术语、概念关系 |
| 排序 | 点选、上移、下移、移回待选区 | 程序步骤、词序、代码块拼排，可含干扰项 |
| 回忆卡 | 先写答案，再提交翻面；也可选择还不会 | 事实和词汇回忆；提交获确认后才显示参考 |

练习通过 MCP Apps `ui/message` 把原始作答交回对话，由助手判断。组件本身不自动判分、不修改进度、不把提交成功当答对。提交失败时保留答案并给出可复制文字；不支持卡片界面的客户端仍能收到题目文字。

代码追踪、模拟终端、坐标图和参数实验尚未移植到 MCP，可使用原有 HTML/文字路径；语音依宿主能力。

## 语言与样式

在 `lesson`、`exercise` 或兼容入口的 `quiz` 中传入 `locale: "zh-CN"` 或 `locale: "en"`，选择学习者的**交流语言**。中文用户做英语填空，仍可使用中文按钮和反馈。题干、选项、代码与原始作答不会被翻译或改写。没有显式设置时，客户端语言和内容检测只作兼容兜底；双语课程应明确传入 locale。

界面标签、状态提示、备用文字和提交回聊天的消息使用同一语言设置。文档语言标记随卡片更新，便于辅助技术识别。

七种组件共用浅青蓝主题，主色为 `#B7F1FD`，搭配深色文字、系统字体和轻边框。支持宿主明暗主题、键盘焦点、窄屏布局和减少动画偏好，不加载外部字体、CDN 或样式。

样式位于 `ui/card.html`，构建输出为自包含资源。修改后需重载 MCP 并生成新卡片；当前资源版本为 `learning-card-v5`。构建会生成 `dist/bundle-report.json`，用于查看依赖对体积的贡献。

## 工具与数据

- `show_lesson({lesson})`：一个知识小段。字段为 `id`、`title`、`explanation`，可选 `locale`、`example: {title, text}` 和 `takeaway`。
- `show_exercise({exercise})`：一个练习。共有 `id`、`title`、`type`、`question`，可选 `locale` 和 `collectConfidence`（默认 true）。支持 `mcq`、`free_text`、`numeric`、`cloze_passage`、`order_steps`、`flashcard`。
- `show_quiz({quiz})`：兼容原来的单选题接口；支持 `locale`。空参数仅显示固定 Python 连通性演示，真实课程应传实际题目。

完整字段与教学约束见 [组件指南](../skills/closebook/references/mcp-cards.md)，可运行样例见 [测试数据](tests/fixtures.mjs)，输入校验见 [cards.mjs](cards.mjs)。每道新题使用新 ID；同一张未改变的卡片重试可复用 ID。未完成作答或未选所需信心时不能提交，所有练习均允许回答不会。

`flashcard.reference` 只放在工具结果的组件专用 `_meta`，不放在题目文字和 `structuredContent`；提交获确认前，界面不创建参考答案的 DOM。其他题型不接受正确答案字段。卡背是回忆后的对照材料，不是安全考试机制。结构校验不证明答案正确，助手仍需独立核对并接受合理等价解答。

收到继续练习的回应，只能进入新检查题，不能记作答对；重复收到同一回应编号时不能重复记分。界面会忽略重复数据通知，旧题的迟到确认不会锁住新题。

## 安装与启动

需要 Node.js 20+。从仓库根目录安装依赖：

```sh
npm ci --prefix mcp
```

直接启动 STDIO 服务：

```sh
node mcp/server.mjs --stdio
```

启动时会校验源码、依赖锁文件和构建产物的内容指纹；文件缺失、过期或损坏时先重新构建。失败时在 stderr 给出原因并停止，stdout 只用于 MCP 协议。也可进入 `mcp/` 后执行 `npm start`；本目录的 npm 配置关闭普通生命周期提示。注册客户端时推荐使用直接 Node 启动方式。

预构建产物与当前源码匹配时，启动无需构建工具；只安装生产依赖的部署也必须保留源码、锁文件和构建报告。

如需提前构建并检查：

```sh
npm --prefix mcp run build
npm --prefix mcp test
```

可选的回环 HTTP 服务：

```sh
npm --prefix mcp run start:http
# http://127.0.0.1:43129/mcp
# http://127.0.0.1:43129/health
```

HTTP 只监听回环地址，检查 Host/Origin 和请求体大小；`PORT` 可修改端口。启动前先确认组件可加载，构建失败时不提供健康状态成功的服务。此项目不包含公网隧道或线上部署。

## 在客户端配置

客户端必须分别支持 MCP 工具连接和 MCP Apps 界面。只有工具调用结果而没有卡片时，仍可用文字学习；不能把服务已连接当作界面可用。

支持相应命令的本地 Codex 环境，可在 shell 中执行下列配置命令，替换仓库绝对路径：

```sh
codex mcp add closebook_card -- "$(command -v node)" "/absolute/path/to/closebook/mcp/server.mjs" --stdio
```

`command -v node` 必须解析为当前环境中真实可执行的 Node 路径。其他客户端使用其官方配置方式，把已经解析出的绝对路径填入配置；不要把 shell 表达式原样填进 JSON。

若当前 Codex 版本将 MCP Apps 放在 `enable_mcp_apps` 功能开关后，先通过 CLI 帮助确认支持，再执行：

```sh
codex features enable enable_mcp_apps
```

工具或参数更新后，通过客户端支持的重启 MCP 或重新加载方式刷新。测试请求可直接发送：

```text
请用 closebook_card 的 show_lesson 显示一小段自由落体讲解和一个例子，locale 使用 zh-CN。先不要出题，等我选择继续练习。
```

选择继续后，应收到一条真实回传并进入练习；阅读完成不计掌握。宿主可能提前启动已注册的 STDIO 进程，组件选择优先级不控制进程启动时机。

## 检查与验证范围

仓库的统一检查命令与 CI 设置见 [贡献指南](../CONTRIBUTING.md)。MCP 自动化检查覆盖输入校验、真实 STDIO/回环 HTTP、官方 `App`/`AppBridge` 测试宿主消息回传、DOM 控件、语言切换、失败恢复和迟到确认。DOM 和测试宿主结果不等同于实际桌面显示与点击。

截至 2026-11-01 已观察的客户端结果：

| 项目 | 结果 |
|---|---|
| 新版桌面提交回传 | 用户重载服务后，七种卡片累计九次真实提交返回同一聊天，其中排序三次；讲解继续、选择题、简答、数值、填空、排序及回忆卡均有记录 |
| 原始作答与语言 | 英文选择题的选项和信心、中英文多行文字、分数与单位、三个填空 ID 及弯撇号均已传回；没有将验收操作写入学习成绩 |
| 回忆卡翻面 | 原始作答返回同一聊天；用户确认参考答案提交前不可见、提交后才出现 |
| 排序移动操作 | 最后两项补检要求把 1 上移到 2 前，实际回传 one → two（数字 1 → 数字 2），符合要求。此前未能核实画面和用户误点的两次记录保留；点击过程未被独立观察，不代表全部控件及异常分支都已实测。DOM 定向检查另行通过 |
| 新主题与双语界面 | 中英文回传已观察，整体样式与全部界面标签仍未独立目视复核 |
| 本轮浏览器与 CI | 没有重跑 HTML 浏览器测试；新 CI 工作流尚未远程执行 |
| Claude、Hermes、Gemini 等客户端 | 尚未实机验证这套组件 |

新规则另有 [agent 行为评测](../skills/closebook/evals/README.md)，检查实际工具选择及学习状态处理。本轮提交记录与待完成项见 [MCP 改进验证](../docs/mcp-hardening-validation.md)。工具替身证明的是决策，不证明某平台已具备对应界面。发布前应分别记录自动化、行为和真实客户端验收结果。

## 版本与卸载

包名为 `closebook-mcp`；本次 MCP 与 skill 的版本均为 `0.3.0`，但仍独立编号。UI 资源后缀用于更新缓存，也不是 skill 版本。MCP 随 [v0.3.0 Release](https://github.com/sheepxux/closebook/releases/tag/v0.3.0) 的源码提供，不包含在 skill ZIP 中，需单独配置。现有客户端注册名 `closebook_card` 和工具名保持兼容。

在使用上述 Codex 注册方式的环境中可移除服务：

```sh
codex mcp remove closebook_card
```

仅当没有其他 MCP Apps 依赖该开关时，才考虑停用 `enable_mcp_apps`；其他客户端按其设置移除服务即可。

## 协议依据

组件使用标准 MCP Apps `ui/message`，`openai/outputTemplate` 仅作为兼容字段。

- [OpenAI：MCP 本地接入](https://learn.chatgpt.com/docs/extend/mcp)
- [OpenAI：MCP Apps UI 与状态管理](https://developers.openai.com/plugins/build/chatgpt-ui)
- [OpenAI：工具设计](https://developers.openai.com/plugins/plan/tools)
- [MCP Apps 官方示例](https://github.com/modelcontextprotocol/ext-apps/tree/main/examples/basic-server-vanillajs)
