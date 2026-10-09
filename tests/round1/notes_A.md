# Blind reviewer A: notes on applying fallacy_catalog (commit df075a2, v0.3.0)

Scope: 120 passages in `tests/round1/passages.csv`, judged one at a time by hand following METHOD.md steps (a) to (g). I read only the catalog (fallacies.json, FALLACIES.md, METHOD.md, README.md) and the blind passages. I did not open the answer key or any other reviewer's or audit folder, and I did not edit the catalog.
`_work/` holds my scratch files: a condensed dump of fallacies.json to read from, and the hand-written verdict rows. A script only checked the CSV format and that the entry ids exist. It made no verdicts.

**Totals: 52 flag, 6 possible issue, 62 no issue.**
Possible issue: P005, P009, P019, P042, P097, P107.

For a no-issue verdict, `entry_ids` gives the entry I checked and rejected, so a reader can see which look-alike was ruled out.

## Policy I had to adopt where the method was unclear

**`text_detectable: partly`.** METHOD (f) says these entries "need at least one fact from outside the text; check it, or record 'possible issue'". Read literally, that caps every `partly` entry at possible issue, including straw man, slippery slope, base rate, survivorship, suppressed evidence, false equivalence, appeal to fear and appeal to authority, even when the passage itself supplies the fact.
My rule: flag only when the fact the condition needs is in the passage itself, or is common knowledge under METHOD (b). Otherwise I recorded possible issue.
This rule produced flags at P001, P017, P022, P046, P054, P068, P088 and P113. A reviewer who reads (f) literally would downgrade all eight, so this is the single biggest source of reviewer disagreement.

## Catalog problems found (entry, what happened, proposed fix)

1. **METHOD (f) / every `partly` entry: the detectability rule is too blunt.**
   - Problem: the label sits on the whole entry, but usually only one condition needs outside facts, and the passage often supplies them. For example, straw-man C2 says "show the original wording". At P022 and P054 the original wording is in the passage, yet the entry is `partly`.
   - Fix: record for each entry which condition is outside-text (for example `outside_text_conditions: [2]`). Change (f) to: "if the passage or common knowledge supplies that fact, the condition can be met from the text."

2. **anecdotal-evidence (P009): marked `text_detectable: yes`, but C3 needs outside facts.**
   - Problem: C3 ("better systematic evidence exists or would be needed") is an outside-world fact. For the nurse's full-moon claim it can't be settled from the text. Meanwhile the parallel entry misleading-vividness is `partly`.
   - Fix: mark it `partly`, or reword C3 to "the conclusion is general and the only support is the stories".

3. **Hit-counting with misses ignored has no clean home (P001, P068).**
   - Problem: suppressed-evidence C2 says contrary evidence is "omitted". In P001 (6 of 400 predictions came true) and P068 (3 of 12 districts improved), the contrary evidence is stated but ignored in the inference, so C2 fails on a literal reading. texas-sharpshooter (multiple-testing family) and survivorship-bias (omitted-evidence family) both also fit, and no rule chooses between the families.
   - Fix: change suppressed-evidence C2 to "omitted *or set aside without answer*". Make "cherry-picking" point to it explicitly. Add a cross-family tie-break: subset chosen after seeing the data → texas-sharpshooter; filter was success/survival → survivorship-bias; otherwise suppressed-evidence.

4. **appeal-to-accomplishment (P012): no "treated as settling" condition.**
   - Problem: it has only two conditions (achievements cited; different field). Read literally, it flags "A Nobel physicist says the guidelines rest on flawed statistics, worth taking seriously", even though the conclusion is modest and statistics is within a physicist's competence. appeal-to-authority has a C3 that prevents this.
   - Fix: add C3, "the achievement is treated as settling the matter or as the main reason to accept the claim". Add a look-alike: "the claim is about a method (statistics, measurement) the person's field does use". appeal-to-celebrity has the same gap, so consider the same C3 there.

5. **circumstantial-ad-hominem C3 (P005): there is a gray zone between "false" and "check it".**
   - Problem: "He used to lobby for the maker, so I don't trust his conclusions" is neither "the report is false" nor "verify it independently".
   - Fix: say how a withdrawal of trust counts. Suggested: flag only if the speaker rejects the claim or refuses to look at its evidence. "Won't accept it on his say-so" is the look-alike.

6. **observational-interpretation (P019) vs cum-hoc: inconsistent handling of hedges.**
   - Problem: cum-hoc C3 is met only if the causal claim is "stated as established rather than as a hypothesis", but observational-interpretation has no hedge clause. Its C3 ("confounders not addressed") is also all-or-nothing. P019 adjusts for two confounders, ignores reverse causation, and says "probably". I could not tell whether to flag it.
   - Fix: give observational-interpretation the same "stated as established" wording. Add "confounders partly addressed: possible issue, name the unaddressed one".

7. **middle-ground look-alike (P085, P107): "practical compromise" is under-specified.**
   - Problem: posting a 15-ton bridge limit is a practical act, but it carries a factual safety claim (I flagged it). "A 4% raise is the fair outcome" in wage bargaining could be a bargaining convention or a claim about the correct wage (I recorded possible issue).
   - Fix: add to the look-alike: "...unless the compromise carries a factual claim (safety, cost, truth) that the midpoint does not support".

8. **appeal-to-force look-alike (P057).**
   - Problem: "A threat may give a practical reason to act" can be stretched to "You'd better agree...", since agreeing out loud is an act.
   - Fix: add "if the demand is to accept or agree that a proposition is true, the look-alike does not apply".

9. **tu-quoque C2 (P118): partial hypocrisy.**
   - Problem: a doctor who is overweight is not strictly inconsistent with "quit smoking", only with a broader health message. The family rule says use tu quoque for hypocrisy, but C2 is strained here. I flagged under tu quoque and noted that ad hominem fits either way.
   - Fix: say whether inconsistency with the *general principle behind* the advice counts. If not, redirect to ad-hominem.

10. **courtiers-reply C3 (P092): needs the content of the criticism.**
    - Problem: C3 requires showing the criticism "does not depend on the specialised knowledge", but blanket dismissals ("you've never run a business, so you can't criticize regulation") don't quote the criticism. I flagged on the blanket form of the dismissal. A literal reading forces possible issue.
    - Fix: add "or the reply rules out all criticism from the person regardless of content".

11. **Ambiguity family: four-terms vs equivocation (P013).**
    - Problem: the family rule sends syllogism middle-term shifts to four-terms, so I used four-terms for "every law has a lawmaker". Most readers and textbooks would call this equivocation.
    - Fix: either make equivocation the default and four-terms the label only for explicit formal syllogism analysis, or list four-terms as a redirect alias. Otherwise reviewers will split on label even when they agree on the error.

12. **Causation family: cum-hoc vs common-cause (P032).**
    - Problem: the common-cause look-alike says "raise only when there is some evidence of a common cause", but an obvious common cause (national wealth) is common knowledge rather than evidence in the text. It is unclear whether METHOD (b)'s common-knowledge rule counts.
    - Fix: state whether common knowledge satisfies "some evidence".

13. **hasty-generalization C3 (P042): no guidance beyond "too small".**
    - Problem: 11 of 12 users finishing faster is a small sample with a large effect, used for a reversible decision. C3 is a pure judgment call.
    - Fix: add a look-alike: "small sample with a large, consistent effect, used for a reversible or low-stakes decision", and point to unrepresentative-sample when the issue is how the sample was chosen.

14. **appeal-to-nature vs naturalistic-fallacy for "evolved" (P097).**
    - Problem: the naturalistic-fallacy definition lists "what evolved", but its own redirect sends "natural, so good" to appeal-to-nature. "Humans evolved eating meat, so a meat diet is appropriate" turns on whether "appropriate" means nutritionally suited (evolution is relevant evidence) or right.
    - Fix: add a look-alike to appeal-to-nature: "evolutionary history offered as evidence of physiological fit, for a conclusion about fit".

15. **METHOD gap: passages that diagnose a fallacy correctly (P021, P115) or use a legitimate reductio (P015, P036).**
    - Problem: the procedure starts from "a step you think goes wrong", and the record format has no slot for "speaker correctly identifies fallacy X".
    - Fix: add a line saying that when the speaker correctly diagnoses or rebuts a fallacy, the verdict is no issue, and record the entry they named.

## Passages I found hardest (lowest confidence)
- P006 (tu quoque vs a legitimate credibility question about a minister)
- P019 (hedged causal claim from observational data)
- P042 (small product test)
- P086 (food trucks: hedged slope with trend evidence; I said no issue)
- P092 (courtier's reply)
- P107 (fair midpoint)
- P110 (consistency challenge vs whataboutism; I said no issue)
- P118 (doctor hypocrisy)
