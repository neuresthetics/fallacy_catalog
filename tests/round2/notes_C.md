# Reviewer C (strict literal) — notes

Catalog: the catalog repository @ ccc9a6f (v0.4.0), working tree clean. Input: tests/round2/passages.csv only. No other file in the test set, and no other reviewer or eval output, was opened. The catalog was not edited. Scripts were used only to look up entries (`lk.py`) and to write the CSV. Every verdict was judged by hand.

**Totals:** 36 flag, 4 possible issue, 60 no issue.
- Possible issue: Q010, Q012, Q014, Q050.
- Flags with two labels: none. Where a second entry met its conditions, it is recorded in `notes`.

## A. Places where the literal rule forced (or nearly forced) a verdict I think is wrong

1. **Q012, argument from ignorance, procedural-default look-alike (LA2).** The passage says: "Until someone proves thirty-year exposure is harmless, the responsible assumption is that it isn't." Combined with METHOD (b) ("treat stated defaults ... as such"), LA2 lets a speaker turn a truth claim into a "default" simply by calling it an assumption. Literal verdict: possible issue. My view: flag. The speaker invents the default and also asserts that the exposure isn't harmless.
   **Fix:** LA2 should apply only to a default that is established or adopted independently of this argument (a legal presumption, a null hypothesis, a house rule set beforehand), and only when the conclusion stays a decision and does not also assert that the claim is false.

2. **Q010, reverse inference ("every fraud had X; this charity has X; so likely fraud").** The error is in plain view, but every candidate entry fails literally:
   - Inductive conversion C2 requires the conclusion "all/most B are A", while this conclusion is about one instance.
   - Undistributed middle: its probabilistic look-alike exempts a "likely" conclusion.
   - Affirming the consequent: C3 says "definitely".
   - Base-rate C2 is outside-text, so the verdict can be at most possible issue.

   Literal verdict: possible issue. My view: flag.
   **Fix:** extend inductive-conversion C2 to "or that a particular B is (probably) an A". Alternatively, mark base-rate C2 as met when the passage gives only P(feature | A) and offers no frequency of the feature among non-A.

3. **Q014, complex question vs. avoiding the question.** Each entry's look-alike points at the other. The deciding fact is whether non-enforcement had already been established, and neither entry marks that condition as outside-text (both are `text_detectable: yes`). Literal verdict: possible issue, with both entries recorded.
   **Fix:**
   - Avoiding-the-question LA2 should require the respondent to actually say the presupposition is false. An implicit side-step ("inspectors were there four times") should not count.
   - Complex-question C2 ("not accepted") should be marked outside-text, or reworded as "is contested and not established in the passage".

4. **Q051, affirming the consequent, C3 "definitely following".** The passage says "It's hard to avoid the conclusion that layoffs are on the way." I treated this as near-certain and flagged. A stricter reader could say C3 fails, and the IBE look-alike also fails because no alternatives are considered. That leaves a gap: a hedged conclusion with no alternatives considered fits neither.
   **Fix:** C3 should read "P is concluded as following (as certain or near-certain), or as probable without any other explanation considered".

5. **Q003 and Q008, implicit causal claims.** Cum-hoc C2/C3 ("concluded to cause", "stated as established") and common-cause C1 ("said to cause") assume an explicit causal claim. In both passages the causation is carried only by a recommendation ("think carefully before agreeing to a palliative referral"; "require a family-dinner campaign"). METHOD (b) ("A conclusion about what to do ... is not a claim that the matter is settled") pulls toward no issue. I flagged both under the charity limit, but the literal text is ambiguous.
   **Fix:** add "or an action is recommended that only makes sense if the causal claim is true" to cum-hoc C2/C3 and common-cause C1.

6. **Q003 vs. Q008, cum hoc vs. common cause.** The tie-break turns on "the argument does address causes". Q008 controls for one variable (race). I counted that as addressing causes and used common-cause. Q003 addresses nothing, so I used cum-hoc. Both passages contain the same underlying error, so the label split is arbitrary.
   **Fix:** state whether adjusting for some confounders counts as "addressing causes".

7. **Q074, appeal to nature.** C1 lists "what our bodies are built for" as trigger wording. But LA2 ("evolutionary history offered as evidence of physiological fit, for a conclusion about fit") plausibly covers that very sentence. The entry contradicts itself on its own example wording. I flagged appeal to tradition instead (same step) and recorded appeal to nature as possible only.
   **Fix:** LA2 should require independent physiological evidence of fit, not just a long history of use.

8. **Q035, Texas sharpshooter, LA2 "treated only as a lead to test".** The passage demands testing and also compensation. I read "only" literally and flagged.
   **Fix:** say explicitly that a conclusion which also asserts cause or seeks remedies is not "only a lead".

9. **Q057, gambler's fallacy, C3 "the opposite outcome is concluded to be more likely ... because it is 'due'".** The passage instead argues that the same rare outcome is less likely because it just happened. I flagged it by treating the two as equivalent.
   **Fix:** C3 should read "or the same outcome is concluded to be less likely because it just occurred".

## B. Missing entries or places to record errors

- **Simpson's paradox / confounded aggregate (Q049).** I flagged it as cherry-picking only by reading the crude overall rate as a "subset" of the stated data. **Fix:** add an entry (statistical) with these conditions: an aggregate comparison, stratified data reversing it, and a conclusion drawn from the aggregate.
- **Relative vs. absolute risk framing (Q027).** It was caught only because the harm rate happened to be stated. If the bleeding rate were absent, nothing would fit cleanly. **Fix:** add an entry, or add a look-alike/condition under cherry-picking or lack of proportion.
- **Plain calculation errors (Q054).** The inverse-variance-weighted mean of 4.2 ± 0.9 and 5.8 ± 0.6 is 5.3%, not the 5.1% reported. The method was sound, so the catalog verdict is no issue. **Fix:** METHOD should allow an "error, not a fallacy" note so factual and arithmetic slips are recorded without a fallacy label.
- **Start-date / endpoint selection (Q050).** "Measured from March 2009" plus "beats the market" with no benchmark figure. The selective-evidence tie-break sends it to suppressed evidence (outside-text), so the verdict is possible issue. If the start-date choice is meant to be flaggable from the text, cherry-picking needs a "chosen window" clause, for example: the period start is chosen and the arguer's own stated history extends earlier.
- **"Cut" vs. "slower growth" (Q082).** I flagged straw man. There is no look-alike for an established but contested usage (baseline budgeting). This should be considered for a possible-issue route.

## C. Unclear or under-specified rules

- **Cross-family ties.** Q083 meets equivocation (the word "ignorance": law vs. fact) and accident (the rule's rationale doesn't cover the case). METHOD (c) gives tie-breaks only within a family. **Fix:** add an ambiguity-vs-accident tie-break: use equivocation if the key term changes sense, and accident if the sense is the same but the rationale doesn't fit.
- **Passages with no argument** (recipes, minutes, specs, rules announcements, interview questions: Q030, Q036, Q040, Q052, Q060, Q090, Q093). METHOD has no explicit "no argument -> no issue" line. Step (g)'s "correct use of a fallacy name" covers mentions (Q006, Q013, Q034, Q070, Q073) only by analogy, since those passages report or teach a fallacy rather than "rebut" one. **Fix:** add a line saying a passage that makes no argument, or only reports someone else's, is no issue.
- **Outside-text markings are inconsistent with how conditions actually behave.** Complex-question C2 (acceptance), cum-hoc C2 (implicit causation) and no-true-scotsman LA2 (what a word "means") can all depend on outside facts but are marked `text_detectable: yes`.
- **The "plausibly applies" threshold in step (e)** is the main source of reviewer variance (Q012, Q014, Q074). A one-line test would help, for example: "the passage contains words that meet the look-alike's description".
- **Charged-language add-ons** ("union talking points" in Q037; "There's no hiding from that vote" in Q064) sit in the same step as a flagged error. I treated these as one step with one label. METHOD's two-label rule ("two separate errors") does not say whether charged wording in the same sentence counts as separate.

## D. Flags I hold with lower confidence under a literal reading

- **Q051:** C3 hedge (see A4).
- **Q003, Q008:** implicit causation (see A5).
- **Q049:** subset reading (see B).
- **Q082:** usage dispute (see B).
- **Q086:** the no-true-Scotsman LA2 "part of the word's meaning" is arguable for "fiscal conservative".
- **Q064:** false dilemma rests on an implied either/or ("voting to keep 26 million people uninsured"), not an explicit "either ... or".
