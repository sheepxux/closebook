# 04 Feynman explanation (费曼讲述)

**Principle.** Explaining something in the simplest words exposes exactly where understanding stops, because jargon can't cover the gaps.

## Fits / doesn't fit
- ✓ `conceptual`, `judgment`.
- ○ `contested`: explain each position plainly; score coherence and fairness, not correctness.
- ✗ `factual` (no "why" to explain → invented reasons; use retrieval + mnemonics), `procedural` (use self-explanation on a worked example), `language_production`.
- Also the default **synthesis** at the end of a session that contains any conceptual or judgment point.

## Procedure
1. **Prompt:** "Explain X to a smart friend who has never studied it. No jargon unless you explain it first. 3–6 sentences." Material closed.
2. **Coach plays the curious outsider.** Ask follow-ups in this order, **one per reply**, and only where the explanation is thin:
   1. *What is it?* ("So what *is* a negotiated cache, in one sentence?")
   2. *Why?* ("Why would a browser bother asking if it already has the file?")
   3. *Example?* ("Give me a case where that happens.")
   4. *What if conditions change?* ("What if the server doesn't send an ETag?")
   Stop early if the explanation is already solid; 0–3 follow-ups is normal.
3. **Mark the gaps:** a short list of concrete gaps ("didn't say what the server returns when nothing changed"; "used 'validation' without explaining it").
4. **Fill the gaps** with minimal teaching (one example + one sentence per gap).
5. **Re-explain:** ask for the explanation again, only the gap parts if time is short.
6. **Score** (rubric below) and record.

## Jargon masking check
The explanation repeats terms without unpacking them ("it uses conditional requests for validation"). Test: ask "what does *validation* mean here, without that word?" If they can't, mark `jargon_masking: true` and treat the term as a gap.

## Example (zh, concept point)
> **Coach:** 用费曼的方式：假设我是没学过网络的朋友，用 3–6 句话给我讲讲"协商缓存"。先别看材料。
> **Learner:** 协商缓存就是浏览器用 ETag 做验证，没变就返回 304。
> **Coach:** 我是外行，"验证"具体是谁问谁、问什么？
> **Learner:** 浏览器把之前拿到的 ETag 发给服务器，问这个版本还是不是最新的。服务器说是，就只回一个 304，不带内容。
> **Coach:** 清楚多了。还差一个缺口：你没说这样做比直接下载省在哪、又比强缓存多花了什么。补一句就行。
> **Learner:** 省的是重新下载文件的流量，多花的是一次来回请求。
> **Coach:** 完整了。评估：准确 2/2，完整 2/2，通俗 1/2（第一版用"验证"蒙混，追问后讲清了）。缺口清单：①一开始没说明"验证"的含义（已补上）。

## Scoring rubric (each 0–2)
| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| `accuracy` | Contains a wrong claim | Minor imprecision | No errors |
| `completeness` | Core mechanism missing | One required element missing | All required elements |
| `plainness` | Mostly jargon | Some unexplained terms | Plain words, terms explained when used |
| `jargon_masking` | boolean: a term was used to hide a gap | | |

Map to a result for scheduling: all 2s → `correct`; any 0 in accuracy or completeness → `incorrect`; otherwise `partial`.

## Insensitivity
Two Feynman attempts that stall at term-repetition → switch to `elaborative_interrogation` or `self_explanation` on a concrete example; record in `methods_insensitive`.

## Progress fields
`feynman: {at, accuracy, completeness, plainness, jargon_masking, gaps[], rounds}`; attempt with `method: "feynman"`, `phase: "retest"` or `"synthesis"`, `question_format: "explain"`, no confidence rating.
