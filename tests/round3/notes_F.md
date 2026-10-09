# Reviewer F (practical analyst): notes on held-out round 3

Catalog: catalog v0.5.0 at commit 46e8036 (fallacies.json, FALLACIES.md, METHOD.md, README.md). Input: tests/round3/passages.csv only. I did not open the answer key or any other reviewer's work. I read each passage and wrote down my own view before checking the catalog's conditions.

## Totals

- 108 rows across 100 passages: **45 flag, 7 possible issue, 56 no issue**.
- By passage: 40 have at least one flag, 4 have only possible issues (R041, R062, R063, R084), and 56 are no issue.
- Passages with more than one row: R006 (4 flags), R072 (2 flags), R082 (2 flags), R036 (flag plus possible issue), R092 (flag plus possible issue) and R041 (2 possible issues).
- No-issue passages include 7 with no argument at all (R001, R032, R034, R052, R075, R080, R089) and 11 that teach, satirise or correctly rebut a fallacy (R005, R042, R047, R048, R055, R071, R087, R093, R094, R096, plus R019 as a joke).

## Where my first judgment and the catalog disagreed

| id | First judgment | Catalog route | Went with |
|---|---|---|---|
| R033 | No true Scotsman | Persuasive definition. No counterexample is redefined on the spot; the slanted definition comes first. | Catalog |
| R049 | Appeal to authority (irrelevant expertise) | The authority family offers wealth or accomplishment. The stated warrant is "you don't get that rich by being wrong", which is money. | Catalog (appeal to wealth; accomplishment noted) |
| R097 | Appeal to ridicule | Appeal to the stone. It declares the claim absurd without mocking it for a laugh. | Catalog |
| R081 | Generic overgeneralization from disagreement | Inflation of conflict, an exact fit. | Catalog |
| R054 | A modal error with no specific name (possibly A, possibly B, so possibly both) | Combination of words, whose own example has the same structure. | Catalog, with a note that the label is archaic |
| R100 | Regression fallacy | The causation family rule says to use "ignoring a common cause" when cases were selected into a group. | My judgment: regression fallacy is the more specific entry for selection on an extreme. The rule's wording invites a wrong route; see fixes. |
| R021, R040 | Ad hominem or appeal to motive (insults) | Ad hominem C3 and appeal to motive C3 aren't met because the insult isn't offered in place of reasons. | Catalog: no issue. A stricter reviewer might call R040 a possible issue. |
| R041 (Mill) | Equivocation on "desirable" and composition, both textbook charges | Under the strongest reading ("desire is the evidence of desirability", and "aggregate" read as a sum), neither condition is shown from the words alone. | Possible issue for both |
| R062 | Amphiboly flag (self-serving reading) | Amphiboly C3 needs the context to support the other reading, and nothing in R062 does. | Catalog: possible issue |
| R084 (Carnegie) | Appeal to nature or naturalistic fallacy | C3 is only partly met, because a strongest economic-efficiency reading exists. | Possible issue |
| R099 (Euthydemus) | No issue (Plato satirises sophistry) | METHOD (g) says satire is no issue. My other multi-speaker items, though, are flagged at the speaker level. | Flag at speaker level for consistency, with a note. Real tension; see unclear rules. |
| R019 | Superstitious thinking or post hoc (grandfather) | A joke or reported anecdote is no issue. | No issue. This is inconsistent in spirit with R099; see below. |

## Missing entries

1. **Broken window fallacy / seen and unseen** (R047). Bastiat correctly identifies it, but the catalog has no entry to record. It's a standard named fallacy, in Wikipedia's list.
2. **Appeal to inevitability / fait accompli** (R084): "It is here; we cannot evade it; ... so we welcome it as beneficial." Is-ought is the nearest entry and doesn't quite fit.
3. **Possibility agglomeration in modern terms** (R054): "can A and can B, so can do A and B together". Combination of words covers it, but under an archaic Aristotelian name a modern reader won't recognise. Add an alias such as "free-choice / conjunction of possibilities" or a modern entry.
4. **Sincerity is not accuracy** (R023): "has no reason to lie, so his prediction is true". Appeal to poverty covers the poverty part. The underlying move, honesty taken as a guarantee of correctness, has no entry.
5. **Expertise transfer within a domain** (R026, second step): "finest violist, so her lessons are the best". Performing and teaching are different skills, but appeal to accomplishment's look-alike ("achievement in the same field") would clear it. Nothing captures this.

## Unclear rules

1. **Embedded speakers vs satire.** METHOD (g) says to give no issue when a passage "reports, quotes ... or satirises someone else's argument". It doesn't say what to do with multi-speaker exchanges (R030, R053, R060, R090, R036) or a dialogue excerpt (R099), where the fallacy is committed by a named participant and the narrator doesn't endorse it. I flagged errors at the speaker level and gave no issue to a narrator's joke (R019) or authorial satire whose irony is explicit in the excerpt (R042). R099 sits in between. **Fix:** add a rule such as "score each speaker's argument; use no issue only when the passage's own voice is teaching or mocking the argument and the irony is visible in the excerpt".
2. **The ignorance-and-burden family's one-label-per-step rule** (R006). "It's up to the county to prove that" (misplaced burden) and "until someone demonstrates it can't work, we're ... entitled to keep advertising it as reliable" (argument from ignorance) are adjacent sentences. I treated them as two moves. **Fix:** give an example of burden demand plus conclusion as either one step or two.
3. **Appeal to motive C1, "someone has made an argument"** (R072). Here the opponent is an agency rule, not an argument, so I read a proposal with an implied rationale as meeting C1. Circumstantial ad hominem already says "claim or proposal". **Fix:** align appeal to motive to "claim, argument or proposal".
4. **The causation family rule** includes "the reason cases were selected into a group" under "ignoring a common cause". Read literally, it routes regression-on-selection cases (R100) away from the regression fallacy. **Fix:** "If cases were selected for an extreme value and then improved, use regression fallacy before common cause."
5. **Special pleading C3** (R025): does "I know I can be impartial" count as "a reason relevant to the rule's purpose"? It names the purpose but rests on self-assessment, which the rule exists to replace. **Fix:** add "a bare self-assessment that one meets the rule's purpose does not count".
6. **Accent C3** (R056): the speaker asserts the pharmacist did stress the word. I used common knowledge (warnings don't certify other drugs as safe) to meet C3. **Fix:** state that even real emphasis can't support a contrastive implication the speaker plainly would not intend.
7. **Appeal to wealth C2, "unrelated to money"** (R049): the claim is "bridge inspections are a waste of money". A literal reader could say the respect is money. **Fix:** "unrelated to how the person became rich".
8. **Historical texts and charity** (R041, R063, R067, R084): METHOD has no guidance on scholarly reconstruction. Should a reviewer apply the author's known later clarifications (Mill on "aggregate")? I used only the words on the page, so I gave possible issue where the classic charge depends on one disputed reading. For R067 (Paine's satellite analogy) I flagged false analogy because "it is evident" shows reliance on it.
9. **The false dilemma inherited from an earlier error** (R036): when the "only two options" step fails only because of an earlier error, is it a separate error? I recorded it as a possible issue. A rule would help.

## Other errors (not fallacies)

- R092: "counted the people ... for ten seconds and multiplied by the area" is garbled. It multiplies a count by an area instead of a density by an area, and the ten seconds is irrelevant to a head count.
- R070: the true chance of having the condition after a positive result is about 2% (990 true positives among about 50,940 positives per million people tested), not 95%.
- R029: "her models are excellent" doesn't establish that she *knows* the outcome. It's a weak premise feeding the modal error.

## Suggested fixes (summary)

Add entries or aliases for the broken window fallacy, the appeal to inevitability, and a modern name for combination of words. Fix the causation-rule ordering for selection on an extreme. Add rules for embedded speakers and satire, and for a bare self-assessment under special pleading. Align appeal to motive C1. Add guidance on historical texts and scholarly readings.
