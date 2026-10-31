# Question design

A good question makes the learner retrieve the one thing that matters, and its wrong answers tell you *why* they're wrong.

## General rules
1. **One target per question.** If a question tests two things, a wrong answer doesn't tell you which one failed.
2. **Test the point, not the wording.** Rephrase rather than quoting the material; otherwise you test recognition of sentences.
3. **Prefer production over recognition.** Free recall > cloze > MCQ, unless the point is about telling confusable items apart.
4. **Concrete beats abstract.** "Which header makes a CDN cache for 10 min but browsers not at all?" beats "Explain s-maxage".
5. **State the answer format** so the learner doesn't guess what you want: "one word", "a number", "2–3 sentences", "option + confidence".
6. **No leaks.** The stem must not contain the answer or grammatical cues to it ("an ___" before a vowel-initial answer).
7. **Calibrated difficulty:** effortful but reachable (`methods/11-difficulty-tuning.md`).
8. **Transfer questions** use a new context with the same underlying rule; they're the best evidence of understanding.

## Formats by knowledge type
| Type | Good formats | Avoid |
|---|---|---|
| factual | cue → recall, cloze, flashcard; MCQ only for confusables | "explain why" (no why) |
| conceptual | explain in own words, predict, apply to new case, "what would change if…", MCQ with misconception distractors | pure definition recall |
| procedural | do it, predict output, find the bug, order the steps | describing the procedure in general terms |
| judgment | case → choose + justify, compare options, "what would make you change your choice?" | MCQ with one "right" answer |
| language_production | produce a sentence from a cue, translate into the target language, correct an error | recognising the right form only |
| contested | "state view A's strongest argument", "what evidence would weaken view B?", "where do you stand and why?" | anything with a single correct answer |

## Multiple choice: real-misconception distractors
Every wrong option must be something a real learner plausibly believes, and each one should map to a specific misconception.

**Sources for distractors (in order):**
1. The learner's own earlier wrong answers (best).
2. Known common confusions in the field (`no-cache` vs `no-store`, `=` vs copy).
3. A correct statement about a *neighbouring* concept that doesn't answer this question.
4. A plausible over-generalisation of the rule ("all 3xx responses redirect").

**Never:** joke options, "all of the above" / "none of the above", options that are wrong only because of a trivial wording trick, options of very different length or detail than the answer.

**Format:**
- 3–4 options. Random position for the correct one across questions.
- Confidence collected with the answer: "Reply with letter + confidence 1–3, e.g. `C 2`."
- **Explanation after answering** covers every option: why the right one is right **and what misconception each wrong one represents**.

**Example**
> Which statement about `Cache-Control: no-cache` is true? (letter + confidence 1–3)
> A. The browser must not store the response.
> B. The browser may store it but must check with the server before each reuse.
> C. The browser may reuse it without asking until it expires.
> D. Only CDNs are affected; browsers ignore it.
>
> *After the answer:* B is right. A describes `no-store`, the classic mix-up. C describes a fresh response under `max-age`, so the strong-cache model is applied to the wrong directive. D confuses it with `s-maxage`, which targets shared caches.

## Free-text questions: reference points
For any open question, write (privately, before asking) a short list of **required elements** and **nice-to-have elements**. Grade against it: all required → correct; some required → partial; none → incorrect. In HTML pages this list becomes the self-assessment checklist.

## Cloze rules
- Blank the meaningful part, not filler words.
- One blank per question in early retests; up to three in later ones.
- Accept synonyms and minor spelling slips for concept words; require exact form where exactness is the point (codes, formulas, legal terms, target-language spelling).

## Contested questions
- Never mark a position as wrong. Judge whether reasons support the conclusion, whether counter-arguments are acknowledged, and whether factual claims about the positions are accurate.
- Feedback names the strongest missing consideration on **both** sides.
