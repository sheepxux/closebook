# 12 Mini project (小项目驱动)

**Principle.** Using a skill on a small real task reveals gaps that isolated questions miss, and finishing something useful gives the knowledge a place to live.

## Fits / doesn't fit
- ○ `procedural` only, and only when the learner can actually do it (has the tools, the time, and wants to).
- ✗ everything else; for non-hands-on material a "project" is just an essay. Use self-explanation on a worked example instead, or schedule the project for later.

## Procedure
1. Offer at session end (60-minute sessions, or as homework): one task, 10–30 minutes, with a clear done-criterion.
   - Good: "Configure caching headers for a static site with `index.html` and two hashed bundles; show me the three `curl -I` outputs."
   - Bad: "Build a CDN."
2. Give requirements, not a solution. Ask for the artifact: code, command output, config, short text.
3. **Review the result as a reviewer**, not a grader of effort:
   - Does it meet the done-criterion?
   - Which knowledge points does it show correctly? Which are misapplied?
   - One concrete improvement.
4. Map each finding to a knowledge point and record it as an attempt (`phase: "project"`).
5. If the learner can't do it now, record it in `methods_skipped` with the reason and suggest it as optional homework.

## Example (zh)
> **Coach:** 小任务（约 15 分钟）：给一个静态站配置缓存头——`index.html` 每次都要验证，`app.[hash].js` 缓存一年。完成标准：贴出两个文件的 `curl -I` 结果。
> **Learner:** （贴出结果：index.html 为 `max-age=3600`）
> **Coach:** JS 的配置正确，用了 `immutable`，说明知识点 4 用对了。`index.html` 的 `max-age=3600` 意味着发布后最多一小时用户看到旧页面，这正是知识点 1 里强缓存的风险。改成 `no-cache` 再贴一次。

## Scoring
Per knowledge point the project touches: `correct` / `partial` / `incorrect`. Self-reported results (learner says "it works" without evidence) are recorded with `self_assessed: true`.

## Progress fields
Attempts with `phase: "project"`, `method: "mini_project"`; `methods_skipped` when not feasible.
