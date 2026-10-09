# Reviewer E (strict literal): notes

Catalog: the catalog repository at 46e8036 (v0.5.0), applied as METHOD.md says, rules read literally. Input: tests/round3/passages.csv (100 passages). Output: verdicts.csv, one row per step or error (114 rows).

I read only the catalog files and passages_blind.csv. Scripts only looked up entries and wrote the CSV. I made every judgment myself.

## Counts
- Rows: 114. 47 flag, 5 possible issue, 62 no issue.
- Passages, by worst verdict: 43 flag, 1 possible issue (R063), 56 no issue.
- Passages with more than one flag or possible issue: R006 (4 flags), R036 (flag + possible issue), R041 (flag + possible issue), R072 (flag + possible issue), R082 (2 flags), R092 (flag + possible issue).
- Most-used flags: ad-hoc-rescue 3, false-analogy 3, then 2 each for sunk-cost, mcnamara-fallacy, etymological-fallacy and regression-fallacy.

## Verdicts the rules forced that I think are wrong (logged conflicts)
1. **R021 (Paine): bulverism flag.** The excerpt states "it happens not to be true" and then explains the belief by the king's design. The look-alike (explaining a view after independent refutation) needs the refutation to be in the text. In the full pamphlet it comes in the next sentence ("Europe, and not England, is the parent country"). Because the excerpt was cut there, the rules force a flag. Proposed fix: say how to treat excerpts of real texts, e.g. "if the passage is an excerpt and the missing support plausibly follows, at most possible issue".
2. **R019 (grandfather's car-washing) and R099 (Plato's dog-father): no issue under rule (g).** Both passages put a fallacious argument on display. Rule (g) makes any reported, quoted or satirised argument no issue, so the error inside is never labelled except in notes. That's probably intended. But (g) gives no way to record "the reported argument commits X" as a structured field, so a reader skimming verdicts loses the information. Proposed fix: add a verdict or column "no issue (reported argument commits X)".
3. **R041 (Mill, 'desirable'): false-analogy flag.** Strict conditions are met. Mill scholarship disputes whether this is a fallacy at all, and textbooks usually call it equivocation. Charity rule (b) pushed me from equivocation to false-analogy. The label is disputed, and I'd accept "possible issue". The catalog has no guidance for famous contested historical arguments.

## Unclear rules
- **Motive attacks on proposals (R072).** appeal-to-motive C1 and ad-hominem C1 require "an argument" or "a claim". circumstantial-ad-hominem covers "a proposal" but only circumstances or stake, not imputed hostile motives ("power grab by bureaucrats who despise rural people"). Read literally, no entry fully fits, so I gave possible issue. Fix: extend appeal-to-motive C1 to "an argument, claim or proposal".
- **special-pleading C3 (R025).** "No reason relevant to the rule's purpose" is ambiguous when the exemption claims to serve the purpose ("I know I can be impartial"). I treated an unsupported self-assessment as not a reason. Fix: say "a bare self-assessment that the rule exists to avoid relying on does not count".
- **false-dilemma C1 "presented" (R036).** Implicit dichotomies ("can't be a mill, so it must be a family name") don't clearly meet "presented as though they were the only ones". I gave possible issue. Fix: allow "presented or relied on (e.g. 'must')".
- **Accent (R056).** The case is reading a contrast implicature into stress the speaker really used, not re-stressing. C3 ("original speaker did not mean it that way") fits, but the entry and its look-alike are written for re-stressing. I flagged accent and note the mismatch.
- **Equivocation in an excerpt (R063, Communist Manifesto).** The second sense of "community of women" is only explained after the excerpt ends. I gave possible issue, a similar excerpt problem to R021.
- **Composition with "good to" (R041).** Whether being good (to someone) carries from parts to whole like weight is exactly the disputed point. The look-alike "might apply", so I gave possible issue per (g).
- **Second weak links I didn't give their own row**, because no specific entry fits and the fallback felt like stacking: R026 (fine player, so best teacher), R029 ("excellent models" taken as knowledge), R090 (factory blamed on proximity and timing, covered by texas C2), R100 (rolling out statewide from 10 schools). Fix: the METHOD should say whether a second weak link in the same chain gets its own row or a note.
- **Rule (g) "correct identification" vs straw man (R087, Bastiat).** Rebutting an error you attribute to opponents without quoting them is no issue under (g), but straw-man C2 would make it "at most possible issue". The order of precedence isn't stated. I applied (g).

## Missing entries
- **Broken window / ignoring opportunity cost** ("that which is not seen") (R047). No entry; lump-of-labour and suppressed-evidence don't fit.
- **Argument from expert disagreement** ("experts disagree on the detail, so nothing is known") (R081). I routed it to disregarding-known-science, which works only because the finding is common knowledge. Without that, the only option is the non-sequitur fallback.
- **Appeal to sincerity / "no reason to lie, so true"** (R023). I routed it via appeal-to-poverty, which fits only because poverty was the cited trait.
- **Fatalism / idle argument** (R029, "nothing the engineers do could change it; they might as well go home"). It's covered partly by modal-scope-fallacy, but the practical conclusion isn't.

## Proposed fixes (summary)
1. METHOD (g): add structured recording for reported or satirised fallacies, and an excerpt rule for real historical texts (R019, R099, R021, R063).
2. appeal-to-motive C1: include proposals and policies.
3. special-pleading C3: clarify that self-assessment doesn't count.
4. false-dilemma C1: count implicit, relied-on dichotomies.
5. accent: add a look-alike or condition for inferring a contrast implicature from real stress.
6. Add entries: broken window, argument from expert disagreement (or a disregarding-known-science look-alike), appeal to sincerity, idle argument.
7. METHOD (c): say how to record a second weak link in the same chain.
8. State the precedence between (g) "correct identification" and misrepresentation entries.

## Other errors (not fallacies)
- R070: the right figure is about 2% (0.99 × 0.001 / (0.99 × 0.001 + 0.05 × 0.999) ≈ 0.019), not 95%.
- No arithmetic slips found elsewhere (R088 checked: 1,220 kg).
