# Round 2: fixes

## What was changed in response (catalog v0.5.0)

Applied in commits 347a415 and 46e8036 (v0.5.0, 220 entries):
- **Defaults vs precaution.** Argument from ignorance and related entries separate a stated default or burden of proof from a precautionary conclusion.
- **New entries:** confusion of the inverse (converse error), Simpson's paradox, statistical vs practical significance, and relative vs absolute risk framing, each with sources fetched and checked (the SEP entry on Simpson's paradox and individual Wikipedia articles).
- **Hedged conclusions.** Affirming the consequent and denying the antecedent now say that a hedged ("probably") conclusion is not the formal fallacy.
- **Cherry-picking window**, **loaded question vs avoiding the question** (the two entries no longer point at each other), **causation** (a recommendation whose only rationale is a causal effect counts as asserting it; most-specific-alternative order), **appeal to nature** (an exception and a nature vs tradition tie-break), and the **gambler's fallacy** mirror form.
- **METHOD wording.** A look-alike downgrades a flag only if the passage supplies its features or they are common knowledge; an optional "other errors (not fallacies)" note for arithmetic slips; no argument means no issue; cross-family tie-breaks.
- **Found in the v0.5.0 regression check and fixed (46e8036):** Simpson's paradox is checked before common cause, and any test or screening result read as the chance of having the condition routes to the base-rate fallacy.

The answer-key corrections listed below were applied to `answer_key.csv` (see its `original_key` and `overrule_reason` columns).

## Recommended fixes, as written by the scorer

*Original title: Round 2 fixes: catalog @ ccc9a6f (v0.4.0)*

This list merges the scoring errors (errors.csv) with every problem raised in tests/round2/notes_C.md (strict literal) and tests/round2/notes_D.md (practical), with duplicates removed. It is ordered by verdicts changed, then label stability, then latent fragility. The catalog was not edited.

## P1: changes a verdict (soft misses or C/D disagreements)

**G1. Argument from ignorance: a precautionary default vs inventing a default.** (C-A1, D5, S)
- LA2 applies only to a default established independently of this argument (law, regulation, a null hypothesis or house rule set beforehand). The conclusion must stay a decision and not assert the claim.
- If an established standard exists and points the other way, the look-alike can't apply.
- Add a separate precautionary look-alike: "a cautious decision under uncertainty, stated as a decision, with costs weighed."
- Passages: **Q012** (→ flag, matching the key), round-1 P069 and P098 (stay no issue).

**G2. A converse-error entry (probabilistic affirming the consequent, P(E|H) read as P(H|E)).** (C-A2, C-A4, D4, S)
- New entry in the probability family:
  - C1: all or most H have feature E.
  - C2: a case with E is concluded to be (probably) H.
  - C3: nothing is given or used about how common E is among non-H.
  - All three are textual.
- Probability family tie-break: "chance if innocent" → prosecutor's; a test result with prevalence → base rate; "all H have E; this has E; so (probably) H" → converse error.
- Also change affirming-the-consequent C3 to "certain or near-certain, or probable with no other explanation considered", and mirror it in denying-the-antecedent C3.
- Passages: **Q010** (C soft miss → flag), Q051 and Q033 (stabilised).

**G3. Cherry-picking needs a chosen-window clause, and "plainly known" / common knowledge needs a test.** (C-B start date, D unclear rules, D5, S)
- cherry-picking:
  - C1 is met when "a measurement period is chosen while the arguer's own stated record extends beyond it".
  - C2 is met when "a comparative claim is made with no comparison figure and the window excludes stated history".
- METHOD (b): common knowledge means "an educated general reader would know it without looking it up". If reviewers could reasonably differ, treat it as not common knowledge.
- Passages: **Q050** (→ flag from the text alone, so it no longer depends on knowing the 2009 market low), plus D's other common-knowledge calls (Q057, Q023, Q003, Q010, Q038).

**G4. Complex question vs avoiding the question loop back to each other.** (C-A3, D-Q014, S)
- Mark complex-question C2 as outside-text, reworded to "contested and not established in the passage".
- avoiding-the-question LA2 applies only if the respondent says the presupposition is false.
- Tie-break: an implicit factual rebuttal with the record not in the text → possible issue under complex question, settled by the record.
- Passages: **Q014** (stays possible issue, which is correct; see key correction K3), Q091 and Q093 (stay no issue).

## P2: label stability (both flagged, different entries) and missing entries

**G5. Simpson's paradox (aggregation reversal) entry.** (C-B, D1, S)
- C1: an aggregate comparison is made.
- C2: data broken down by some factor, stated or plainly known, reverse or remove it.
- C3: the groups differ in composition on that factor.
- C4: the conclusion is drawn from the aggregate.
- Look-alike: the aggregate is what's actually relevant to the decision.
- Tie-break against common cause.
- Passages: **Q049** (C wrong label, D near fit).

**G6. Causation: implicit causal claims and a tie-break based on which alternative can be identified.** (C-A5, C-A6, D unclear rules, D4 summary, S)
- METHOD (b): "a recommendation whose only rationale is a causal effect counts as asserting that effect (as established unless hedged)".
- Causation family, in order:
  - an obvious third factor that is named or plainly known, including the reason cases were selected into the group → common cause
  - a plausible reverse direction → reversing causation
  - no specific alternative → cum hoc
  - a study cited as showing causation, with the design itself as the problem → observational interpretation
- Passages: **Q003** (cum hoc / common cause split → common cause), Q008, Q045, Q075.

**G7. Appeal to nature's trigger vs its exception, and a nature vs tradition tie-break.** (C-A7, D-Q074, D unclear rules)
- LA2 requires independent physiological evidence of fit, not just history or the phrase "built for".
- Cross-family rule:
  - naturalness or "built for" wording → appeal to nature
  - age or history only → appeal to tradition
  - both in one step → report appeal to nature and note tradition
- Passages: **Q074** (resolves the split), Q056 (stays no issue).

**G8. Statistical vs practical significance entry.** (D3, S)
- C1: a result is called statistically significant.
- C2: it is presented as large or worth acting on.
- C3: the stated effect size doesn't support that.
- Passages: Q002 (now caught only because "significant" appears twice).

**G9. Relative vs absolute risk entry.** (C-B, D2, S)
- C1: a relative change is reported.
- C2: the absolute change is small, whether stated or omitted.
- C3: the conclusion relies on the relative figure.
- Look-alike: both figures are given and weighed.
- Passages: Q027 (now caught only because the bleeding rate happened to be stated).

## P3: method wording (right verdicts that are fragile)

**G10. METHOD (e) downgrade standard.** (C-C, D unclear rules)
- "A look-alike downgrades only if the passage supplies its features, or they are common knowledge. A look-alike the reviewer has to imagine doesn't count."
- Passages: Q024, Q082, Q012, Q074.

**G11. Record type for errors that aren't fallacies.** (C-B, D-Q054)
- Add an optional "other errors (not fallacies)" field for arithmetic and factual slips. It does not change the verdict.
- Passages: Q054 (the 5.1% should be 5.3%).

**G12. A "no argument" line in step (g).** (C-C)
- "A passage that makes no argument, or only reports, quotes, teaches or satirises someone else's argument, is no issue. Record the entry mentioned, if any."
- Passages: Q030, Q036, Q040, Q052, Q060, Q090, Q093, Q006, Q013, Q034, Q053, Q070, Q073.

**G13. Wording fixes on single entries.** (C-A8, C-A9, C-B, C-D)
- gamblers-fallacy C3: add "...or the same outcome concluded less likely because it just occurred" (Q057).
- texas-sharpshooter LA2: a conclusion that also asserts a cause or seeks remedies is not "only a lead" (Q035).
- straw-man: add a look-alike for established but contested usage, unless the opponent explicitly rejected that description (Q082).
- false-dilemma C1: cover an implied two-option framing (Q064).
- no-true-scotsman LA2: a criterion the speaker's earlier claim didn't depend on can't be used (Q086).
- begging-the-question: add an example of self-validation (Q020).

**G14. Cross-family ties and charged add-ons in METHOD (c).** (C-C, D unclear rules)
- Ties:
  - ambiguity vs accident: the key term changes sense → equivocation; same sense but the rationale doesn't fit → accident (Q083).
  - Point to the G6 and G7 cross-family rules.
- Charged wording in the same step as a flagged error isn't a second error unless it carries its own inference (Q037, Q064).

## Answer-key corrections

- **K1, Q054.** The reason is wrong. The midpoint is 5.0%, the inverse-variance mean is 5.31%, and the passage's 5.1% is itself an arithmetic error.
- **K2, Q010.** Add base rate / converse error / inverse probability to the acceptable names. "Undistributed middle" fits a "likely" conclusion badly, and the key's reason describes base-rate neglect.
- **K3, Q014.** Re-grade the target to possible issue. Whether enforcement stopped is outside the text, and four inspections doesn't establish enforcement either way.
- **K4, Q003.** Describe it as confounding by indication (severity causes both referral and death) and accept common cause.
- **K5, Q049.** Accept common cause, which counts as confounding.

## Round 1 vs round 2: did the v0.4.0 fixes hold?

Mostly yes. There were zero false positives across 60 legit and no-argument passages, even from the strict-literal reviewer. The round-1 F1 fix held: C still flagged Q015, Q023, Q066, Q071 and Q082 under a literal reading. These also gave the intended calls:
- F2: cherry-picking (Q027)
- F3: middle ground (Q054)
- F4: slippery slope (Q055, Q071)
- F5: circumstantial ad hominem (Q037, Q078, Q065)
- F6: appeal to accomplishment (Q098)
- F10: tu quoque (Q022, Q067, Q085)
- F12: hasty generalization (Q028, Q099)
- F16: correct use of a fallacy name (Q001, Q006, Q070, Q073)

Three round-1 fixes created or exposed new problems:
- F13 added trigger wording that LA2 can exempt (Q074).
- The F15 causation tie-break splits on partial adjustment (Q003).
- F2's "plainly known" pushed the common-knowledge threshold onto Q050.

The remaining misses are missing entries (G2, G5, G8, G9) and default handling (G1), not loose conditions.
