# 01 Retrieval practice / closed-book retest (提取练习/回测考核) — baseline

**Principle.** Pulling an answer out of memory strengthens that memory far more than reading it again, and it shows both of you what's actually there.

## Fits / doesn't fit
- Fits every type. For `contested`, the learner retrieves positions and arguments ("what are the two main readings, and what supports each?"), never "the right answer".
- It's the fallback when nothing else fits.

## Formats (pick by type, see `question-design.md`)
| Format | Use for | Hint-free version | With hints |
|---|---|---|---|
| Free recall | Whole point or topic; synthesis | "Write down everything you remember about X" | Give the headings (level 2) |
| Cue recall / cloze | Factual, vocab | "The status code for 'Not Modified' is ___" | First letter / number of digits (level 1) |
| Short answer | Conceptual, judgment | "Why does `no-cache` still hit the server?" | Keyword (1), answer skeleton (2) |
| Production | Language | "Say 'I had to leave' in Spanish" | Infinitive given (1), structure given (2) |
| Apply | Procedural, conceptual | "What does this command print?" | Point at the relevant line (1) |

## Procedure
1. Ask with the material closed. One question.
2. Right/wrong questions: answer + confidence (1–3) in the same reply.
3. If stuck, offer a hint only when asked or after one stall; escalate 1 → 2 → 3. Record the highest level.
4. Judge: `correct` / `partial` / `incorrect` / `dont_know`.
5. Feedback (`feedback-style.md`); classify errors (`03-error-review.md`).
6. A failed retrieval gets one more try later in the session, after at least one other point (spacing within the session).

## Example (zh)
> **Coach:** 合上材料。`Cache-Control: no-cache` 的意思是"完全不缓存"吗？回答"是/否 + 一句理由 + 信心1–3"。
> **Learner:** 是，不存储。2
> **Coach:** 不对，这是很常见的混淆。`no-cache` 会存储，但每次用之前必须先向服务器确认（协商）；"完全不存"的是 `no-store`。记法：no-**cache** 是"不直接用缓存"，no-**store** 是"不存"。这题记为错，原因是概念误解（把两个指令混在一起了），几分钟后再问你一次。

## Scoring
| Result | Meaning |
|---|---|
| `correct` | All required elements, no factual error |
| `partial` | Core idea present, a required element missing or imprecise |
| `incorrect` | Core idea wrong or absent |
| `dont_know` | Learner declined; counts as incorrect for scheduling, never as high-confidence error |

Hint adjustment for scheduling: correct with hint 2 counts as partial; any answer after hint 3 counts as incorrect (see `spaced-repetition.md`).

## Progress fields
`attempts[]` with `phase`, `result`, `hint_level`, `confidence`, `question_format`, `method: "retrieval"`; `efficiency.first_retest_correct`.
