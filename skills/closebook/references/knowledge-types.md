# Knowledge types

Every knowledge point gets one **primary** type and optionally one **secondary** type. The type drives method choice, interaction choice and scoring, so it's decided once in the opening and stored in the progress file (`knowledge_type`, `secondary_types`). Reviews read it back; don't reclassify unless the learner changes the scope.

| id | 中文 | What it is | Typical cue in the material | How it's checked |
|---|---|---|---|---|
| `factual` | 事实记忆型 | Arbitrary or conventional facts: names, dates, numbers, terms, definitions to reproduce exactly | lists, tables, "X is called Y", formulas, legal articles, glossary | Exact recall; right/wrong |
| `conceptual` | 概念理解型 | How and why something works; relationships between ideas | "because", mechanisms, models, cause and effect, architectures | Explain, predict, apply to a new case |
| `procedural` | 程序技能型 | A sequence of steps or a skill you perform | how-to steps, code, calculations, lab procedures | Do it; predict the output; debug |
| `judgment` | 判断决策型 | Choosing between options under constraints; trade-offs with a defensible best answer | "when to use", case studies, design choices, diagnosis | Choose + justify; weigh trade-offs |
| `language_production` | 语言产出型 | Producing language: vocabulary in use, grammar, phrasing, pronunciation | foreign-language lessons, writing style rules | Produce a correct, natural utterance |
| `contested` | 主观/有争议型 | No consensus answer: values, interpretations, open debates | "some argue", ethics, literary interpretation, unsettled science | Coherence and fairness of reasoning, not correctness |

## Classification rules

1. Ask: *what would a good test of this point look like?* Exact reproduction → factual. Explain/predict → conceptual. Perform → procedural. Choose and defend → judgment. Produce language → language_production. Defend a position where experts disagree → contested.
2. A definition can be factual (must reproduce exact wording, e.g. a legal definition) or conceptual (must understand it). Pick by what the learner needs, and say which you chose if it's not obvious.
3. Use a secondary type when part of the point behaves differently, e.g. a vocabulary point (`language_production`) with an irregular form list (`factual`), or a procedure (`procedural`) whose steps only make sense with a model behind them (`conceptual`).
4. Methods may apply through the secondary type, but only to that part of the point (e.g. mnemonics for the irregular forms only).
5. If you can't decide, choose the type that implies the **more conservative** methods (usually `factual` or `conceptual`), and set `method_fit_flag: "needs_review"`.
6. `contested` is about the field, not about the learner's doubt. "The learner isn't sure" is not contested. "Historians disagree" is.

## Examples

| Point | Primary | Secondary | Why |
|---|---|---|---|
| HTTP 304 means "Not Modified" | factual | — | Arbitrary code-to-meaning mapping |
| Why a negotiated cache still costs a round trip | conceptual | — | Mechanism; test by explanation |
| Use `curl -I` to inspect cache headers | procedural | — | Performed skill |
| Choose cache strategy for HTML vs hashed JS bundles | judgment | conceptual | Trade-off with a defensible answer; relies on the mechanism |
| Spanish preterite vs imperfect | language_production | conceptual | Must produce; choice rests on aspect concept |
| Irregular preterite stems (tuv-, estuv-) | language_production | factual | Stems are arbitrary |
| Was the Treaty of Versailles the main cause of WWII? | contested | factual | Historians disagree; dates are facts |
| Article 5 of a regulation, exact wording | factual | — | Must be reproduced exactly; no analogies |
