# Trigger proxy check (2026-10-31)

**What this is:** a stand-in for real skill routing. A fresh agent saw only the names and descriptions of four installed skills (closebook, pdf, docx, code-review), read none of the files, and decided for each of the 18 queries in [`skills/closebook/evals/trigger-queries.json`](../../../skills/closebook/evals/trigger-queries.json) which skill it would load.

**What it isn't:** a test of any platform's actual router. Claude, ChatGPT, Codex and Gemini each decide differently, and none of them was tested here.

**Result:** 18 / 18 matched `should_trigger` (9 loaded closebook, 9 loaded nothing).

| # | Query | Expected | Routed to |
|---|---|---|---|
| 1 | Quiz me on these lecture notes before Friday's exam. | closebook | closebook |
| 2 | 帮我复习一下这章有机化学，下周就考试了。 | closebook | closebook |
| 3 | I want to actually understand how React hooks work instead of copying code. Teach me. | closebook | closebook |
| 4 | 考考我：TCP 三次握手。 | closebook | closebook |
| 5 | Help me memorize these 30 Spanish irregular verbs. | closebook | closebook |
| 6 | Here's my closebook progress JSON, let's do today's review. | closebook | closebook |
| 7 | 用费曼学习法带我过一遍这篇论文。 | closebook | closebook |
| 8 | 说人话给我讲讲量子纠缠，讲完考我一下。 | closebook | closebook |
| 9 | Summarize this textbook chapter so I can study it for the midterm. | closebook (offer once) | closebook |
| 10 | What's the capital of Australia? | none | none |
| 11 | Summarize this meeting transcript into action items. | none | none |
| 12 | Write a Python function that parses ISO 8601 dates. | none | none |
| 13 | Translate this paragraph into English. | none | none |
| 14 | 帮我总结一下这份周报，发给老板。 | none | none |
| 15 | Fix the failing test in this repository. | none | none |
| 16 | What does HTTP status 304 mean? | none | none |
| 17 | 解释一下什么是区块链。 | none | none |
| 18 | Generate a 10-question multiple-choice quiz from this chapter for my students. | none | none |

Query 18 is a borderline case on purpose: a teacher writing a quiz for others isn't studying. A platform that loads closebook here would still work (the skill can produce questions), but the coaching flow would be wrong for the user.
