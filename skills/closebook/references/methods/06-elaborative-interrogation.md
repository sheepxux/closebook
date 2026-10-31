# 06 Elaborative interrogation (精细询问)

**Principle.** Asking "why is this true, and why not the alternative?" ties a new idea to what the learner already knows, so it's understood instead of just stored.

## Fits / doesn't fit
- ✓ `conceptual`, `judgment`.
- ○ `procedural` ("why does this step come before that one?"), `contested` ("why would someone hold this view?", scored on coherence).
- ✗ `factual`, `language_production`. (Research reports benefits for factual lists when learners have relevant prior knowledge, per Dunlosky et al., 2013; closebook leaves it out of pure fact drills by design to keep them fast. If a fact has a real reason behind it, tag a secondary `conceptual` type.)

## Procedure
1. Pick the one claim in the point that has a real reason behind it.
2. Ask a *why* question, and when there's an obvious alternative, a *why not* question: "Why does a hashed bundle get `max-age=31536000, immutable`, and why not the same for `index.html`?"
3. Let the learner reason. Don't accept "because the material says so"; ask for the mechanism.
4. Feedback: confirm the correct link; correct a wrong link with a contrast case.
5. At most 2 why-questions per point. More turns into an interrogation.

## Example (zh, judgment point)
> **Coach:** 为什么带哈希的 JS 文件可以缓存一年，而 `index.html` 不行？为什么不能反过来？
> **Learner:** 因为 JS 改了文件名就变了，旧缓存不会被用到。HTML 的地址不变，缓存太久用户就看不到更新。
> **Coach:** 对，关键链条都在：文件名随内容变 → 旧缓存自然失效。补一点：HTML 正是告诉浏览器"去拿哪个新文件名"的入口，所以它必须每次都是新的，这就是它通常配 `no-cache` 的原因。

## Scoring
| Result | Criterion |
|---|---|
| `correct` | Gives the real causal link and rules out the alternative |
| `partial` | Causal link vague or only one side answered |
| `incorrect` | Wrong mechanism |
For `contested`: `coherent` / `partly_coherent` / `incoherent` based on whether the reasons support the stated view, independent of whether you agree.

## Progress fields
Attempts with `method: "elaborative_interrogation"`, `question_format: "why"`; misconceptions go to `errors[]`.
