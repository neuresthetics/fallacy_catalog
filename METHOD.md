# How to check an argument with this catalog

This is the procedure for using [FALLACIES.md](FALLACIES.md) on a real argument. Its purpose is to keep false positives down: a passage is flagged only when every condition for the fallacy can be shown from the words on the page, and every legitimate look-alike has been ruled out.

Naming a fallacy does not show that the conclusion is false. It shows only that this step does not support it (to claim more would be the [argument from fallacy](FALLACIES.md#argument-from-fallacy)).

## The procedure

Work one step of the argument at a time. For each step you think goes wrong:

**(a) Quote the exact passage.** Copy the words, with enough surrounding text that a reader can see what the speaker meant. Do not paraphrase at this stage.

**(b) Restate the argument in its strongest reasonable form.** Write out the premises and conclusion as the speaker would accept them. Be concrete:
- **Read hedges as hedges.** "Likely", "may", "should be investigated" and "I suspect" make a weaker claim than "proves" or "will". Judge the claim actually made, not a stronger one.
- **Supply common-knowledge premises the speaker would accept.** If a step needs a premise that any ordinary reader takes for granted (drunk driving is dangerous; water boils when heated), assume it, even though it is unstated. Do not count its absence as missing evidence.
- **Supply the most plausible unstated premise, not the weakest.** If two readings fit the words, use the one that makes the argument better.
- **Treat stated defaults and procedural rules as such.** A burden of proof, a presumption of innocence, a null hypothesis, a house rule or a decision procedure tells you what to do when evidence is lacking. It is not a claim about what is true.
- **Respect the conclusion's scope.** A conclusion about what to do, what to investigate, or what is probable is not a claim that the matter is settled.
- **Keep the role of each statement.** An illustration, a joke or a figure of speech is not a premise unless the speaker relies on it.

Charity has a limit: use it to find what the speaker meant, not to rewrite a passage that clearly meets the conditions. If the strongest version has no problem, stop here: there is no issue.

**(c) Pick the most specific entry.** Use one label per step.
- Check the entry's **Related, use only one per step** list and pick the single entry in that family that fits best. Do not stack labels from the same family.
- Entries marked **Fallback** (`use_only_if_nothing_more_specific: true`), such as non sequitur, false cause and formal fallacy, may be used only when no more specific entry fits. Say which specific entries you considered and why they don't fit.
- Two labels on one step are allowed only if you can show two separate errors.

**(d) Check every required condition.** For each numbered condition in the entry, cite the words in the passage that satisfy it. If any condition is not met, do not flag. If a condition depends on facts that are not in the text (what the speaker knew, what evidence exists, how a study was run), the most you can record is "possible issue" (see (g)).

**(e) Rule out each legitimate look-alike.** For each look-alike listed in the entry, say in one line why it does not apply. If one plausibly applies, downgrade to "possible issue" or drop the flag.

**(f) Treat entries that are not detectable from the text as questions.** Entries marked `text_detectable: no` (confirmation bias, selective attention, availability heuristic, rationalization) depend on motive, inner bias or facts outside the text. Never flag them. You may record a question, for example: "Is contrary evidence on X being left out?" Entries marked `partly` need at least one fact from outside the text; check it, or record "possible issue."

**(g) Give a verdict.**
- **Flag**: every condition is met from the text and no look-alike applies.
- **Possible issue**: the text meets the conditions it can, but at least one condition depends on context that is not in the text, or a look-alike might apply. Say exactly what would settle it.
- **No issue**: a condition fails, or a look-alike applies.

**(h) Recommended: a second reviewer.** A second reviewer, who has not seen the first reviewer's verdicts, re-checks each flag using steps (a) to (g). Report only the flags both reviewers agree on; list the disagreements separately as possible issues.

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
Verdict: flag | possible issue | no issue   (what would settle it, if possible issue)
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
