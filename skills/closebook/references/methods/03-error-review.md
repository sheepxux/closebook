# 03 Error review and cause classification (错题复盘与错因归类) — baseline when errors exist

**Principle.** Each kind of error needs a different fix; re-reading the right answer only fixes some of them.

## Fits / doesn't fit
- All types with right/wrong answers.
- `contested`: only factual errors about the positions ("Keynes didn't argue that") count; a weak argument is a reasoning gap, handled with elaborative questioning, not logged as an error.

## Error types
| id | 中文 | Signal | Remedy |
|---|---|---|---|
| `misconception` | 概念误解 | A coherent but wrong model; repeats under rephrasing | Contrast case that breaks the wrong model; "why not the other one?" (elaborative); retest in a new form |
| `memory_lapse` | 记忆遗漏 | Recognises it when shown, can't produce it | Retrieve again later in the session; mnemonic if factual; shorter interval |
| `careless` | 粗心 | Slip in an otherwise correct answer; learner spots it at once | Name it once; no re-teaching; doesn't reset understanding |
| `misread` | 审题 | Answered a different question than asked | Re-ask with the key word marked; teach the cue to look for |
| `transfer_failure` | 迁移失败 | Knows the rule, fails to apply it in a new context | New-context variant; self-explanation of why the rule applies here |

If unsure between two types, ask one short question ("If I showed you the options, would you recognise it?" separates lapse from misconception).

## Procedure
1. On `incorrect` or `partial` in a scored phase: classify, tell the learner the type in a few words, and apply the remedy.
2. Append to the point's `errors[]`: `{at, question, error_type, high_confidence, remedy, resolved: false}`.
3. High-confidence error (confidence 3 + incorrect): set `priority_flag`; say it's the most useful mistake to find, because it would otherwise go unnoticed.
4. Mark `resolved: true` when a later scored attempt on a **different day** is correct without hints.
5. In the session wrap-up or every few reviews, if one error type dominates (≥ 3 occurrences), mention the pattern once: "Most of your misses are misreads; underline the question word before answering."

## Example (en)
> **Learner:** (answers what `max-age=0` does, when asked about `s-maxage`)
> **Coach:** That's an accurate description of `max-age`, but the question was about `s-maxage`. That's a misread, not a knowledge gap. The cue: the `s-` means *shared* caches (CDNs, proxies). Same question again: what does `s-maxage=600` change, and for whom?

## Scoring
Classification only; results come from the retest.

## Progress fields
`errors[]`, `priority_flag`, attempt `error_type`; `progress_tool.py error-stats` and `high-confidence-errors` read these.
