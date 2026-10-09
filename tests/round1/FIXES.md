# Round 1: fixes

## What was changed in response (catalog v0.4.0)

Applied in commit ccc9a6f (v0.4.0, 216 entries), in the priority order below:
- **F1, outside-text conditions.** Each entry now has an `outside_text_conditions` field naming which numbered conditions may need facts outside the passage. METHOD step (f) says such a condition is met if the passage states the fact or it is common knowledge; otherwise the verdict is possible issue. This replaced a whole-entry `text_detectable` gate that reviewers had to read past.
- **F2, cherry-picking.** New entry for selection made in plain view (the contrary data are stated but ignored). The "cherry picking" alias moved off suppressed evidence. A selective-evidence family tie-break separates suppressed evidence, cherry-picking, Texas sharpshooter, survivorship bias and the lottery fallacy.
- **F3, middle ground.** A negotiated settlement is distinguished from claiming a position is right because it is in the middle.
- **F4, slippery slope.** Hedged predictions and a chain decided by the same body are handled explicitly.
- **F5–F13.** Condition and look-alike fixes to circumstantial ad hominem, appeal to accomplishment, courtier's reply, special pleading, appeal to force, tu quoque, red herring, double standard, observational interpretation, hasty generalization, appeal to nature and anecdotal evidence.
- **F14–F15 and method wording.** Tie-breaks for equivocation vs four terms (reported as "equivocation (four terms)"), base rate vs prosecutor's fallacy, correlation vs common cause, and a magical-thinking pointer. METHOD now records a no-issue verdict when a speaker correctly names a fallacy or argues by a fair reduction to absurdity, allows two labels in one sentence only for two separate errors, and says how to report split names.

The answer-key corrections listed below were applied to `answer_key.csv` (see its `original_key` and `overrule_reason` columns).

## Recommended fixes, as written by the scorer

*Original title: Round 1 fixes: catalog @ df075a2*

This list merges the scoring errors (errors.csv) with every problem raised in tests/round1/notes_A.md and tests/round1/notes_B.md, with duplicates removed. Priority is how many verdicts the fix would change or stabilise, and how badly. "Raised by" shows whether A, B or the scorer (S) found it. The catalog was not edited.

## P1: changes verdicts on clean fallacies or causes a scored error

**F1. METHOD (f): `text_detectable: partly` is a whole-entry cap, but should apply per condition.** (A1, B1, S)
- Problem: read literally, (f) caps every `partly` entry at possible issue, even when the passage or common knowledge supplies the fact. Both reviewers quietly used the same non-literal reading. A literal reviewer would turn 8 of the 50 fallacy hits into soft misses.
- Fix:
  - (a) In fallacies.json, replace `text_detectable: partly` with `outside_text_conditions: [n…]` on each of the 43 entries.
  - (b) Reword (f): "A condition marked outside-text is met if the passage states the needed fact or it is common knowledge under step (b). Otherwise record possible issue and name the fact that would settle it."
  - (c) Mark anecdotal-evidence C3 as outside-text. Its current `yes` is wrong.
  - (d) Under common-cause, say that an obvious common-knowledge confounder counts as "some evidence".
- Passages: P001, P017, P022, P046, P054, P068, P088, P113 (keeps them flags); P009 (correct possible issue); P032 (label stability).

**F2. Cherry-picking when the selection is in plain view has no entry, and the selective-evidence families have no tie-break.** (A3, B2, S)
- Problem: suppressed-evidence C2 requires the evidence to be "omitted", yet "cherry-picking" is listed as its alias. When the misses are stated but ignored, no entry fits cleanly. Texas sharpshooter, lottery fallacy, survivorship bias and suppressed evidence sit in four different families with no rule for choosing between them.
- Fix:
  - Add an entry **cherry-picking (selective use of stated evidence)**:
    - C1: the arguer selects a subset of the available or stated data.
    - C2: the rest of the data, stated or plainly known, points the other way or dilutes the subset.
    - C3: the conclusion rests on the subset and the rest gets no answer.
    - Look-alike: the subset is singled out for a stated, independent reason, such as a pre-registered subgroup.
  - Move the "cherry-picking" alias to the new entry.
  - Add a cross-family rule, "selective evidence": contrary evidence absent from the text → suppressed evidence. Contrary evidence stated but ignored → cherry-picking. Pattern or cluster found by searching and treated as predicted → Texas sharpshooter. Filter was success or survival → survivorship bias. "Something improbable happened, so design" → lottery fallacy.
  - Key fix: grade P001 and P068 the same way.
- Passages: P068 (resolves the only A/B label split), P001, P088.

**F3. Middle ground: the "practical compromise" look-alike is too vague.** (A7, B7, S)
- Fix: split the look-alike in two.
  - Look-alike (no issue): the midpoint is offered as a settlement both sides can accept ("let's settle at 4%").
  - C2 met (flag): the midpoint is asserted to be correct, fair, safe or true, and its being in the middle is the only reason given.
  - Add: "a midpoint that carries a factual claim (safety, cost) needs evidence for that claim".
- Passages: P107 (→ flag, matching the key), P085 (stays flag), P033 (stays no issue: midpoint backed by audits).

**F4. Slippery slope: hedges and first-link evidence are being allowed to cover the whole chain.** (S; reviewer error at P086)
- Fix: add to C3: "Evidence for the first link does not support later links. A hedge ('probably') lowers the claimed probability but does not supply a missing link."
- Add a look-alike contrast: "when each later step needs a new decision by the same body, the step is not likely unless a binding mechanism (a precedent rule or legal duty) is shown."
- Passages: P086 (A's no issue → possible issue or flag), P112 (stays no issue: bylaws bind), P045 and P111 (stay no issue: evidence or mechanism for every link), P017 (stays flag).

## P2: catalog gaps that both reviewers patched by hand (right verdict, fragile)

**F5. Circumstantial ad hominem C3 offers only "shows it false" or "reason to check".** (A5, B3)
- Fix: add three graded outcomes.
  - Withholding trust in claims that rest on the person's word is the look-alike → no issue.
  - Declaring the claim false or ignorable, or refusing to examine its evidence → flag.
  - Bare distrust of a report that has its own evidence → possible issue. Settle it by whether the evidence gets examined.
- Passages: P005 (possible issue becomes a codified result, not an improvised one), P095 (flag), P002, P010, P029 (no issue).

**F6. Appeal to accomplishment has no scope condition.** (A4, B5)
- Fix: add C3, "the achievement is treated as settling the matter or as the main reason to accept the claim."
- Add a look-alike: "the claim concerns a method (statistics, measurement, mathematics) that the person's field uses."
- Check appeal-to-celebrity for the same gap. Its C3 already requires "offered as a reason", so it's fine.
- Passages: P012, P091.

**F7. Courtier's reply C3 requires knowing what the criticism said.** (A10, B4)
- Fix: add to C3: "...or the reply denies the critic standing to criticise at all, regardless of content, without naming any misunderstanding."
- Key fix: map "credentials fallacy / inverse appeal to authority" to courtiers-reply.
- Passages: P092.

**F8. Special pleading C3 is met by any reason at all.** (B8)
- Fix: reword to "no reason relevant to the rule's purpose is given; rank, convenience or 'I'm busy' do not count."
- Passages: P084.

**F9. The appeal to force look-alike swallows the fallacy.** (A8, B6)
- Fix: "If the demand is to accept, agree with, endorse or stop questioning a proposition whose merits are at issue, the look-alike does not apply. Keep it for plain demands to act ('comply or be fined')."
- Passages: P057.

**F10. Tu quoque: how close must the inconsistency be, what counts as a credibility question, and where does whataboutism go?** (A9, B9, B16, S)
- Fix:
  - C2: the inconsistency must concern the same claim or the principle directly behind it. If it is looser (overweight vs "quit smoking"), use ad-hominem (abusive).
  - Look-alike test: if the reply's target is the message or policy, flag. If it is the person's sincerity or fitness for a role, it's the look-alike.
  - Add a note under red-herring and double-standard: "asking that a stated test be applied consistently is legitimate unless it is used to dismiss the original criticism."
- Passages: P118 (label), P006, P079, P110.

**F11. Observational interpretation C3 is all-or-nothing and has no hedge clause.** (A6, B11)
- Fix: "Confounders or reverse causation are not adequately addressed, and the causal claim is stated as established." Add: "partial adjustment with a hedged causal claim → possible issue, and name the alternative left unaddressed."
- Passages: P019, and for consistency P034, P081, P119.

**F12. Hasty generalization has no guidance on effect size or decision stakes.** (A13, B12)
- Fix: add a look-alike, "a small sample with a large, consistent effect, used for a reversible or low-stakes decision." Point to unrepresentative-sample when the doubt is about how the sample was chosen.
- Passages: P042 (→ no issue, matching the key), P007 (stays flag), P066.

**F13. Appeal to nature doesn't cover equivalent wording ("evolved"). Anecdotal evidence doesn't cover long experience.** (A2, A14, B10, B13)
- appeal-to-nature:
  - C1 also accepts equivalent wording: evolved, ancestral, "what our bodies are built for".
  - Add a look-alike: "evolutionary history offered as evidence of physiological fit, for a conclusion about fit."
  - Point to is-ought when the conclusion is moral.
- anecdotal-evidence:
  - Widen C2 to "one or a few stories, or unsystematic personal impressions".
  - Add a look-alike for long, systematically recorded professional observation.
  - Make C3 outside-text (F1).
- Passages: P097, P009, P075, P096, P016.

## P3: tie-breaks and method wording (label stability, presentation)

**F14. Four terms vs equivocation.** (A11, B14, S)
- Problem: the catalog routes this to four terms, but readers expect equivocation. For a vanilla, credible catalog the familiar name should lead.
- Fix: put the same rule in both families: "report as equivocation; add '(four terms)' when analysing a categorical syllogism."
- Passages: P013.

**F15. Other tie-breaks.** (B14, A12)
- base-rate vs prosecutor's: screening or test result with a population prevalence → base rate. "Chance of the evidence if innocent" given as the chance of innocence → prosecutor's.
- cum-hoc vs common-cause: prefer cum-hoc when only a correlation is shown. Use common-cause when the argument addresses causes and still misses an obvious third factor.
- Add the post-hoc pointer to magical-thinking, as superstitious-thinking already has it.
- Passages: P046, P067, P032, P076.

**F16. METHOD has no record for a speaker who correctly diagnoses a fallacy or runs a legitimate reductio.** (A15)
- Fix: add a line to the method: "If the speaker correctly identifies or rebuts a fallacy, or argues by reductio from the opponent's stated principle, the verdict is no issue; record the entry they invoked."
- Passages: P021, P115, P015, P036, P116.

**F17. METHOD (c): two errors in one sentence.** (B15)
- Fix: add an example. "Not proven safe, so they cause these headaches" contains an argument from ignorance plus a separate causal leap. Both labels are allowed if each is shown.
- Passages: P049.

**F18. METHOD (h): agreed rule when both reviewers flag with different labels.** (S)
- Fix: "Report the flag, list both labels as label disputed, and resolve with the family or cross-family tie-break. If the labels are still split, use the more general entry."
- Passages: P068.

## Answer-key corrections (not catalog changes)

These affect scoring only. They should be applied before round 2 so the key does not penalise answers the method requires.
- P013: accept four terms.
- P068: accept Texas sharpshooter, or remove it from P001.
- P009: drop confirmation bias from acceptable names (the catalog makes it question-only). Accept possible issue as the target verdict, since the counter-evidence is outside the text.
- P019 and P097: the lean-fallacy calls conflict with METHOD (b), which says to read hedges as hedges and to use the charitable reading. Re-grade the target as possible issue.
- P092: map "credentials fallacy" to courtier's reply.
- P003: the reason text says both "legit" and "borderline". State one lean.

## Test-design note for round 2

- **The reviewers weren't independent.** A and B agree on 119 of 120 verdicts and on all six possible-issue calls, and their notes are nearly identical. Use a reviewer setup that differs more (another prompt style, or a human).
- **Test the literal reading of (f).** Add at least one reviewer told to apply METHOD (f) literally, so the F1 failure shows up in the scores and not only in notes.
- **Add harder fallacy cases.** The 50 fallacy passages are mostly textbook-clean (0 misses). Add disguised and mixed cases, plus legit passages that use the trigger words of the overused entries.
