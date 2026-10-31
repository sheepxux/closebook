Starting now. You didn't share notes, so this split is my proposal and may not match your course exactly:

1. [core · conceptual] What each directive does to storing and reusing a response: scenario questions with lettered options built from the usual mix-ups
2. [core · conceptual] What happens once max-age runs out, and how that relates to no-cache: "what does the browser send next?" questions
3. [core · judgment] Picking a directive for a given resource: choose one and justify it in a sentence or two

Trimmed for 15 minutes: s-maxage, must-revalidate, private/public, Vary. We can add them in a later session.

Since you've studied this before, each point gets one diagnostic question, short feedback, and one closed-book retest, then a 2-3 sentence recall at the end. I can't see a clock, so I'll pace by question count (about 7 questions). Say "stop" anytime and I'll wrap up with review dates. To drop or swap a point, just say so; otherwise answer below.

Question 1 (diagnostic: it doesn't count against you, and "don't know" is a useful answer). Answer from memory, no notes.

A response arrives with:

    Cache-Control: no-cache

Ten seconds later, the page requests the same URL again. What does the browser do?

A. Reuses its stored copy without contacting the server, since the copy is only ten seconds old.
B. Has nothing stored, so it downloads the full response again.
C. Asks the server whether its stored copy is still current, and reuses it if the server says yes.
D. Shows its stored copy immediately and refreshes it from the server in the background.

Reply with letter + confidence 1-3 (1 = guessing, 2 = fairly sure, 3 = certain), e.g. "B 2".
