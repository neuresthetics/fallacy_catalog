# How to check an argument with this catalog

This is the procedure for using [FALLACIES.md](FALLACIES.md) on a real argument. Its purpose is to keep false positives down: a passage is flagged only when every condition for the fallacy can be shown from the words on the page, and every legitimate look-alike has been ruled out.

Naming a fallacy does not show that the conclusion is false. It shows only that this step does not support it (to claim more would be the [argument from fallacy](FALLACIES.md#argument-from-fallacy)).

A machine-checkable companion lives in [idea_detection/](idea_detection/README.md) and is summarized in [IDEA_DETECTION.md](IDEA_DETECTION.md). It does not replace this procedure. An extractor may propose an Idea IR; only the deterministic checker may issue a verdict.

## The procedure

Work one step of the argument at a time. For each step you think goes wrong:

**(a) Quote the exact passage.** Copy the words, with enough surrounding text that a reader can see what the speaker meant. Do not paraphrase at this stage.

**(b) Restate the argument in its strongest reasonable form.** Write out the premises and conclusion as the speaker would accept them. Be concrete:
- **Read hedges as hedges.** "Likely", "may", "should be investigated" and "I suspect" make a weaker claim than "proves" or "will". Judge the claim actually made, not a stronger one.
- **Supply common-knowledge premises the speaker would accept.** If a step needs a premise that any ordinary reader takes for granted (drunk driving is dangerous; water boils when heated), assume it, even though it is unstated. Do not count its absence as missing evidence. **Common knowledge** means something an educated general reader would know without looking it up. If reviewers could reasonably differ on whether a fact is common knowledge, treat it as not common knowledge.
- **Read recommendations as claims when they rest on a cause.** A recommendation whose only rationale is a causal effect ("so take vitamin D", "so close the school") counts as asserting that effect, and as asserting it as established unless it is hedged.
- **Supply the most plausible unstated premise, not the weakest.** If two readings fit the words, use the one that makes the argument better.
- **Treat stated defaults and procedural rules as such.** A burden of proof, a presumption of innocence, a null hypothesis, a house rule or a decision procedure tells you what to do when evidence is lacking. It is not a claim about what is true.
- **Respect the conclusion's scope.** A conclusion about what to do, what to investigate, or what is probable is not a claim that the matter is settled.
- **Keep the role of each statement.** An illustration, a joke or a figure of speech is not a premise unless the speaker relies on it.
- **Excerpts of real texts.** If the passage is an excerpt and a condition fails only because support may lie past the excerpt boundary (the reply or the evidence may come in the next sentence or chapter), record at most possible issue and say what the full text would need to show. Do not import your memory of the full text as if it were in the passage.
- **Contested readings.** For a well-known argument whose fallacy charge is disputed in the scholarly literature, name the classic charge, mark the row "contested reading", and give possible issue unless the passage's own words settle it. State the reading under which it is a fallacy.

Charity has a limit: use it to find what the speaker meant, not to rewrite a passage that clearly meets the conditions. If the strongest version has no problem, stop here: there is no issue.

**(c) Pick the most specific entry.** Use one label per step.
- Check the entry's **Related, use only one per step** list and pick the single entry in that family that fits best. Do not stack labels from the same family.
- Entries marked **Fallback** (`use_only_if_nothing_more_specific: true`), such as non sequitur, false cause and formal fallacy, may be used only when no more specific entry fits. Say which specific entries you considered and why they don't fit.
- Some families also give a cross-family tie-break (for example, the selective-evidence family separates suppressed evidence, cherry-picking, Texas sharpshooter, survivorship bias and the lottery fallacy). Follow it.
- Two labels in one sentence are allowed only if you can show two separate errors, each meeting its own conditions. Example: "They've never been proven safe, so they must be what's causing these headaches" contains an argument from ignorance ("never proven safe" treated as showing harm) and a separate causal leap (the headaches blamed on them with no evidence). Both labels may be recorded if each is shown.
- **Cross-family ties.** Some ties cross families; follow these rules:
  - Ambiguity vs accident: if the key term changes sense between the rule and the case, use equivocation; if it keeps the same sense but the rule's rationale doesn't fit the case, use accident.
  - Causal alternatives: follow the order in the causation family rule (Simpson's paradox when the passage gives a reversing breakdown; then an identifiable common cause, then reverse direction, then cum hoc; observational interpretation when the study design is the problem).
  - Nature vs tradition: naturalness or "built for" wording is appeal to nature; age or history alone is appeal to tradition; if both appear in one step, report appeal to nature and note tradition.
  - Probability: follow the probability family rule (prosecutor's fallacy, base-rate fallacy, confusion of the inverse).
  - Generalization vs comparison: an exceptional source case (a special population or special circumstances) used to set a rule for ordinary cases or for everyone is converse accident; one case carried over to another comparable case is false analogy.
  - Experts disagreeing: "experts disagree, so nothing can be known" is inflation of conflict; a claim that simply ignores well-established findings is disregarding known science.
- **Separate steps get separate rows.** A step that builds on an earlier error gets its own row if it commits a separate move of its own. Adjacent sentences are two steps when each meets its own entry. Example: "It's up to the county to prove the plant is safe. They haven't, so it isn't" contains a burden demand (misplaced burden of proof) and a conclusion from lack of proof (argument from ignorance); record both if each is shown.
- **Weak premises without a label.** A second weak link in a chain gets its own row only if it meets an entry's conditions. Otherwise note it as "weak premise" without a fallacy label.
- **Charged wording is not a second error.** Loaded words in the same step as a flagged error are not a second flag unless they carry their own inference.
- **Reporting names.** Use the entry's name, not an alias. Where a family rule says to report under a familiar name with a qualifier, do so: a shift of meaning in a syllogism's middle term is reported as "equivocation (four terms)".

**(d) Check every required condition.** For each numbered condition in the entry, cite the words in the passage that satisfy it. If any condition is not met, do not flag. If a condition depends on facts that are not in the text (what the speaker knew, what evidence exists, how a study was run), apply step (f).

**(e) Rule out each legitimate look-alike.** For each look-alike listed in the entry, say in one line why it does not apply. A look-alike can downgrade a flag only if the passage supplies its features, or those features are common knowledge in the sense of step (b). A look-alike you would have to imagine (a mechanism that might exist, a default that might have been set) does not count. If one does apply, downgrade to "possible issue" or drop the flag, as the look-alike says.

**(f) Handle conditions that may need facts outside the text.**
- Each entry lists, in `outside_text_conditions`, the numbered conditions that may need facts from outside the passage (they are marked in FALLACIES.md). Only those conditions are affected; every other condition must be met from the text as usual.
- A condition marked as outside-text **is met** if the passage itself states the needed fact, or if the fact is common knowledge in the sense of step (b). Then the entry can be flagged like any other.
- If the needed fact is neither stated nor common knowledge, record **possible issue** and name the fact that would settle it.
- Entries marked `text_detectable: no` (confirmation bias, selective attention, availability heuristic, rationalization) depend on motive or inner bias. Never flag them. You may record a question, for example: "Is contrary evidence on X being left out?", or use a text-level entry such as suppressed evidence or cherry-picking if its conditions are met.

**(g) Give a verdict.**
- **Flag**: every condition is met from the text and no look-alike applies.
- **Possible issue**: the text meets the conditions it can, but at least one condition depends on context that is not in the text, or a look-alike might apply. Say exactly what would settle it.
- **No issue**: a condition fails, or a look-alike applies.
- **No argument.** A passage that makes no argument, or only reports, quotes, teaches or satirises someone else's argument, is no issue. Record the fallacy it displays or mentions, if any, in the `reported_fallacy` field, so that a skim of the verdicts still shows it.
- **Dialogues and exchanges.** Score each participant's argument separately. A participant who advances an argument in direct speech is scored even when the author is satirising it (note the satire). Use "no argument" only when the passage's own voice narrates, teaches or mocks without a participant advancing the argument. An argument quoted inside a report, review, lesson or exercise (the passage's own voice is reporting, reviewing or teaching, as in "identify the flaw in Ben's reply") is no argument; record it under `reported_fallacy`.
- **Rebuttals and straw men.** When a passage rebuts a view, the rebuttal's own logic is judged under the usual steps. Whether the rebutted view is fairly attributed is a straw-man check, made only when a specific opponent and their words are identifiable in the passage.
- **Rhetorical notes (not fallacies).** Charged or sectarian wording, invective, and unsupported accusations that no inference rests on go in a "rhetorical notes" field, not in a fallacy flag. They do not change the verdict.
- **Other errors (not fallacies).** Arithmetic slips, wrong figures and factual mistakes that are not reasoning errors go in a separate "other errors" note. They do not change the verdict.
- **Correct use of a fallacy name, or a fair reduction to absurdity.** If the speaker correctly identifies or rebuts a fallacy, or argues by reduction to absurdity from the opponent's own stated principle, the verdict is no issue. Record the entry they invoked, so the reader can see it was checked.

**(h) Recommended: a second reviewer.** A second reviewer, who has not seen the first reviewer's verdicts, re-checks each flag using steps (a) to (g). Report only the flags both reviewers agree on; list the disagreements separately as possible issues.
- If both reviewers flag the same step but with different entries, report the flag, list both names as "label disputed", and resolve it with the family or cross-family tie-break. If the names are still split, report the more general of the two entries.

Contested entries (`status: contested`) are names that are disputed or not widely used. If you use one, say so in the write-up.

## Record format

```
Passage: "<exact quote>"
Strongest reading: <premises> -> <conclusion>
Entry: <name> (<id>)   Other entries considered: <ids and why not>
Conditions:
  1. <condition> — met by: "<words>"
  2. ...
Look-alikes:
  - <look-alike> — does not apply because ...
Speaker: <who advances this step, for dialogues; optional>
Verdict: flag | possible issue | no issue   (what would settle it, if possible issue)
Contested reading: <yes, with the reading under which it is a fallacy; optional>
Reported fallacy: <for no-argument or mention rows: the fallacy displayed or named; optional>
Rhetorical notes (not fallacies): <invective, charged wording, unsupported accusations no inference rests on; optional>
Other errors (not fallacies): <arithmetic or factual slips; optional>
```

## Worked example 1: a true flag

Passage: "Dr. Reyes says the bridge needs new bearings, and she points to the corrosion readings in the inspection report. But Reyes was fired from her last job for showing up late, so we can ignore her bridge argument."

Strongest reading: Reyes argues from the corrosion readings that the bearings need replacing. The reply concludes that her argument can be ignored because she was once fired for lateness.

Entry: [Ad hominem (abusive)](FALLACIES.md#ad-hominem). Other entries considered: circumstantial ad hominem (no stake or circumstance is mentioned, only a trait), poisoning the well (the attack comes after her argument, not before it), tu quoque (no inconsistency is alleged).

Conditions:
1. Someone has made a claim or argument: "the bridge needs new bearings ... points to the corrosion readings."
2. The reply attacks the person rather than the reasons: "fired from her last job for showing up late."
3. The attack is offered as a reason to reject the argument, and her reasons are left unanswered: "so we can ignore her bridge argument"; the corrosion readings are never discussed.
4. The trait is irrelevant to whether the argument's reasons are good: punctuality has no bearing on what the corrosion readings show.

Look-alikes:
- Questioning a witness's reliability: does not apply, because the argument rests on the inspection report's readings, not on her word.
- Arguing from the opponent's own commitments: does not apply; none are cited.
- An insult not offered as a reason: does not apply; "so" makes it a reason.

Verdict: **flag** (ad hominem).

## Worked example 2: a rejected false positive

Passage: "Every national health agency and the large reviews of the trial data agree that serious side effects from this vaccine are rare, so I'm not worried about getting it."

First impression: appeal to authority.

Strongest reading: The relevant experts broadly agree, on the basis of trial data, that serious side effects are rare; so the risk is low.

Entry checked: [Appeal to authority (illegitimate)](FALLACIES.md#appeal-to-authority).

Conditions:
1. A claim is supported by what some person or body says: met ("every national health agency ... agree").
2. At least one of: the source is not an expert on this question; experts substantially disagree; the source cannot be trusted; the source is misquoted: **not met**. Health agencies and reviews of trial data are expert sources on this question, the passage reports agreement, and nothing in the text suggests a misquote.

Look-alikes: relying on genuine experts within their field who broadly agree, which is the case the source says most appeals to authority fall under, applies here.

Verdict: **no issue**. If someone showed that the agencies do not in fact agree, condition 2 would be met; until then, this is ordinary reliance on expertise.
