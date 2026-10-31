No outline, starting now. You have 15 minutes, so I'm covering the three points behind most rebase scares, with one check and one retest each: what each command does to history, when to rebase and when to merge, and how to get out of a rebase safely (conflicts, `--abort`, `--force-with-lease`). `rebase -i` squashing and rewording waits until next time. Progress will go in `closebook-progress/git-merge-vs-rebase.json`.

You've used git for a year, so I'll ask before I explain anything. Keep the notes closed, because looking things up turns this into reading practice. This first one is only a check and doesn't count, so "not sure" is a useful answer.

**Check 1: what happens to history**

```
main:      A---B---M
                \
feature:         F1---F2
```

Predict the result of each of these, starting from this state every time:

- (a) On `main`: `git merge feature`
- (b) On `feature`: `git rebase main`

For each one, sketch the history (in ASCII or one sentence), and say whether F1 and F2 are still the same commits afterwards.

After you answer, I can rebuild this in a throwaway repo under `/tmp` so you see the real `git log --graph` and don't have to take my word for it. Your repo won't be touched.
