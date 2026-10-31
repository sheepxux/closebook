# Git: merge vs rebase (team notes)

- `git merge feature` creates a merge commit with two parents; history shows that work happened in parallel.
- `git rebase main` (run on `feature`) replays feature's commits on top of `main`, creating **new** commits with new hashes. History becomes linear.
- Golden rule: don't rebase commits that others have already pulled (shared/public branches). Rewriting them forces everyone else to reconcile duplicated commits.
- `git rebase -i HEAD~3` lets you squash, reword, reorder or drop the last three commits before opening a PR.
- During a conflicted rebase: fix files, `git add <file>`, then `git rebase --continue`; `git rebase --abort` returns to the state before the rebase.
- After rebasing a branch you already pushed, a normal push is rejected; use `git push --force-with-lease` (refuses if the remote moved since your last fetch), not plain `--force`.
- Team policy: rebase your own feature branch onto `main` before review; merge into `main` with a merge commit.
