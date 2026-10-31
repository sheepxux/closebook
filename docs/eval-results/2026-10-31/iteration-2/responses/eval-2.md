You've used git for a year, so I'll go straight to questions with no outline. With 15 minutes, I'll stick to three things: what each command does to your history, when rebasing is safe, and how to get out of a rebase that went wrong. `rebase -i` can wait for another session. I'll keep your progress in `closebook-progress/git-rebase-vs-merge.json` so we can pick up from there next time.

Please keep the notes closed. If you look things up, this turns into reading practice. For this first question, "I don't know" is a useful answer: it shows me where to start.

The first one is about how the history changes, so you predict the graph before I explain anything.

**Q1.** You're on `feature`:

```
          C---D        feature (HEAD)
         /
    A---B---E---F      main
```

You run `git rebase main`. Afterwards the graph looks like this:

```
    A---B---E---F      main
                 \
                  ?---?    feature (HEAD)
```

What goes in the two `?` slots? Are they the same commits C and D, or something else? Give a one-line answer with your confidence from 1 to 3 (1 = guessing, 3 = certain).
