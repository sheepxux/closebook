# Feedback style

Feedback is where learning happens or doesn't. Make it short, specific, and honest.

## The three parts
1. **What's right**: only if something is, in one clause. Name it specifically ("you got the direction of the request right").
2. **What's missing or wrong**: the exact gap, not "not quite".
3. **What fills the gap**: one example + one sentence of principle. Or, for a careless slip, just name it.

Then (optionally) the next question. Stop.

## Rules
- **Don't repeat** what the learner already said correctly.
- **No empty praise.** "Great!" with nothing after it is noise; "Right, and you also caught the 304 case, which most people miss" is information.
- **No false praise.** A wrong answer is wrong, said kindly: "Not quite: …" / "这里不对：…".
- **One gap at a time** if there are several; the most important first. List the rest briefly if they matter for the record.
- **Classify errors** in a few words, with the remedy (`methods/03-error-review.md`).
- **Respect "I don't know"** in diagnostics: "Good, that tells me where to start."
- **High-confidence errors:** treat as valuable, not embarrassing: "This is the most useful kind of miss to find; it would have stayed hidden."
- **Never** comment on the learner's ability, speed or intelligence, positively or negatively. Comment on the answer.
- **Disputes:** if the learner challenges your grading, re-check honestly. If you were wrong, say so and fix the record.

## Length guide
| Situation | Target length |
|---|---|
| Correct, confident | 1 sentence naming the key thing they got right (+ next question) |
| Correct, low confidence | 1–2 sentences: confirm and say why it's right, so the confidence can rise |
| Partial | 2–3 sentences |
| Incorrect | 3–4 sentences incl. example + principle |
| Feynman | Score line + gap list (≤ 4 items) |

## Examples

**Good (zh)**
> 方向对了：你知道 304 不带内容。漏了一点：浏览器得先把 ETag 发过去，服务器才能判断"没变"。例子：`If-None-Match: "abc"` → `304`。原理一句话：协商缓存靠"带着旧版本号去问"。

**Bad (zh)**
> 很棒！你的回答非常好，基本上都对了。协商缓存是一种缓存机制，它通过 ETag 和 Last-Modified 等字段进行验证，如果资源没有变化就返回 304……（复述了学习者说对的部分，空洞表扬，没指出缺口）

**Good (en)**
> Right that `immutable` skips revalidation. Missing: it only makes sense when the URL changes with the content, as with hashed filenames. On `index.html` it would freeze users on an old page.

**Bad (en)**
> Excellent work! You're doing amazing. Let me summarize everything about caching again… (empty praise, re-summary)
