# 08 Predict then verify (预测再验证)

**Principle.** Committing to a prediction before seeing the result turns the result into feedback on your mental model, and a wrong prediction is memorable.

## Fits / doesn't fit
- ✓ `procedural` (code output, calculation result, command effect).
- ○ `conceptual` **only** when the outcome is checkable (a physics setup with a known result, a documented system behaviour).
- ✗ `contested` (never: no ground truth), `judgment` (decision outcomes aren't observable in a session; use case-based retrieval), `factual`, `language_production`.

## Procedure
1. Present a concrete setup: code, command, input values, a diagram state.
2. "Before we check: what will happen? Commit to an answer + confidence 1–3, and one sentence of why."
3. Verify against ground truth:
   - Learner can run it (has a terminal, the code is safe) → ask them to run it and paste the result.
   - You can run it (tool environment) → run it and show the output.
   - Neither → show the documented result and **say where it comes from** (spec, documentation, the material). Never fabricate an output.
4. Wrong prediction → ask the learner to explain the gap first ("what in your model produced that guess?"), then correct the model; log the error type (usually `misconception`).
5. Right prediction with confidence 1 → ask for the why; a lucky guess isn't understanding.

## Example (zh, procedural)
> **Coach:** 先预测再验证。下面这段运行后输出什么？给答案 + 信心 1–3 + 一句理由。
> ```python
> a = [1, 2]
> b = a
> b.append(3)
> print(a)
> ```
> **Learner:** [1, 2]，因为 b 是新的列表。2
> **Coach:** 你可以运行一下看看。（学习者贴回：`[1, 2, 3]`）你的模型里 `b = a` 做了什么？
> **Learner:** 我以为是复制……其实是同一个列表起了两个名字？
> **Coach:** 对。`=` 只是贴标签，不复制。错因：概念误解。想复制要用 `a.copy()`。下一题换个场景再测一次。

## Scoring
Prediction: `correct` / `partial` (right direction, wrong detail) / `incorrect`, with confidence. The explanation of the gap isn't scored; it's the learning step.

## Progress fields
Attempts with `method: "predict_verify"`, `question_format: "predict"`, `confidence`; `interaction` is often `plain_qa` or `simulation`.
