We’ll start with a history prediction to see where rebase gets confusing. Keep the notes closed; “I don’t know” is fine.

Your private feature branch looks like this:

```text
A---B---C  main
     \
      D---E  feature (checked out)
```

Imagine running `git rebase main` with no conflicts:

```text
History leading to feature afterward: ?
```

**What would that history look like?** Sketch it or describe it, indicating which commits, if any, get new hashes.

Reply with your prediction, a sentence explaining why, and **confidence 1–3** (1 = guessing, 2 = fairly sure, 3 = certain).