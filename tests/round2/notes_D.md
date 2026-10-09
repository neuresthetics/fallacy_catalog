# Blind reviewer D (practical analyst): notes

Catalog: the catalog repository at ccc9a6f (v0.4.0, 216 entries). Input: tests/round2/passages.csv only. No other test or review files opened. Catalog not edited.
Process: read all 100 passages and wrote down my own call for each before opening any entry, then checked candidate entries (conditions, look-alikes, family rules) using a lookup script (`lookup.py`). `write_verdicts.py` only serializes my judgments to CSV.

**Totals: 38 flag, 2 possible issue, 60 no issue.**
In `verdicts.csv`, for no-issue rows `entry_ids` lists the entries I checked and ruled out (or the entry a speaker correctly invoked, per METHOD (g)). It does not list errors.

## Where my first view and the catalog disagreed
My first-pass verdict (flag / possible / no issue) matched my final verdict on all 100. Where they differed, it was over **which label** to use or **how firm** the call was:

| Id | My first view | Catalog pushed toward | Went with | Why |
|---|---|---|---|---|
| Q008 | correlation → causation (cum hoc) | family rule: "addresses causes but misses an obvious third factor" → common-cause; observational-interpretation also fits | common-cause | Race was controlled, so they did address some causes. Income and family stability are obvious confounders that were missed. |
| Q010 | affirming the consequent / base rate | AC C3 requires "definitely follows", and the passage says "likely" | base-rate-fallacy | The catalog has no probabilistic version of AC. Base rate fits the substance (P(traits given fraud) read as P(fraud given traits)). inductive-conversion also fits. |
| Q049 | Simpson's paradox | no entry | common-cause (confounding by case mix, stated in the text) | This is the nearest fit. cherry-picking is defensible, but the aggregate isn't a "subset". |
| Q027 | relative vs absolute risk framing | no entry | cherry-picking | The bleeding figure is in the text and goes unanswered. |
| Q002 | statistical vs practical significance | no entry | equivocation | "significant" is used in two senses, linked by "In other words". |
| Q074 | appeal to nature + appeal to tradition | they're in different families, so two labels would need two separate errors | appeal-to-nature only | It's one step. The catalog's C1 wording ("what our bodies are built for") matches exactly. |
| Q012 | argument from ignorance (lean flag) | the procedural-default look-alike plausibly applies | possible issue | METHOD (b)/(e). See unclear rules below. |
| Q051 | affirming the consequent | AC C3 "definitely"; the IBE look-alike | flag | I read "hard to avoid the conclusion" as near-definite, and no alternative explanations are considered. This call depends on how the words are read. |
| Q033 | denying the antecedent | "shouldn't count on her" is a mild hedge | flag | Contrasting her with Tate ("safer") treats non-endorsement as evidence against her. |
| Q082 | straw man | "cut vs baseline" is a common budget usage | flag | Wade explicitly says spending "still grows", and "plain and simple" rejects that nuance. Weighting the baseline usage more would give possible issue. |
| Q050 | cherry-picked start date | cherry-picking C2 needs contrary data "stated or plainly known" | flag | I treated March 2009 as the plainly known market bottom. The 2001 start of the team's record is stated in the text. If the bottom isn't plainly known → suppressed evidence, possible issue. |
| Q024 | post hoc | the "timing plus known mechanism" look-alike | flag | The text gives only timing plus "clearly". A plausible mechanism exists, but the speaker never argues it. |
| Q003 | confounding | common-cause C1 needs a causal claim, and this one is implicit and hedged | flag | No non-causal reading makes the mortality figure relevant to the referral advice. |

## Places I had to interpret (full log)
- **Implicit causal claims** (Q003, Q008, Q049): the advice ("think carefully", "should require", "should choose") only makes sense if there's a causal link, so I treated common-cause C1 as met.
- **Implicit dilemma** (Q064): "voting to keep 26 million uninsured" read as a two-option framing.
- **Common-knowledge facts used for outside-text conditions:** what "hundred-year flood" means (Q057); that many 1850s buildings no longer stand (Q023); that palliative patients are sicker (Q003); March 2009 as the market low (Q050); that legitimate charities often share the "fraud" traits (Q010); that national-system claims need systematic data (Q038).
- **Hedges vs strong claims:** Q051 ("hard to avoid"), Q033 ("shouldn't count on"), Q098 ("take seriously"), Q045 ("may want to"). I flagged the first three, because the hedge doesn't change the fact that the only support is the flawed step. For Q045 the flag rests on multiple comparisons, not the causal leap.
- **Q014:** the question may be loaded, and the answer may be evasive. Which party erred depends on the enforcement record, so possible issue.
- **Q054:** not a fallacy, but the arithmetic looks off. Reading ± as SEs, inverse-variance weighting gives ~5.3%, not 5.1%. Logged in notes; verdict no issue.

## Missing entries (proposed additions)
1. **Simpson's paradox / aggregation reversal** (Q049). Currently it can only be forced into common-cause or cherry-picking.
2. **Relative vs absolute risk (risk framing)** (Q027). Cherry-picking works only because the harm figure happens to be on the page. A pure "50% reduction!" with no absolute numbers would have no clean entry.
3. **Statistical vs practical significance** (Q002). It currently runs through equivocation, which only works when the word "significant" appears twice.
4. **Probabilistic affirming the consequent / confusing P(E given H) with P(H given E)** outside the courtroom (Q010, Q051). Prosecutor's fallacy is framed around innocence, and AC requires "definitely". A general "inverse probability / converse error" entry, or an AC look-alike for "likely/probably" conclusions, would remove the guesswork.
5. **Precautionary-principle look-alike** for argument-from-ignorance and misplaced-burden (Q012): who may set a default, and when "assume harmful until proven safe" is a legitimate decision rule vs a truth claim.
6. **Circular validation / self-validation** (Q020: a model "validated" against its own outputs). Begging-the-question covers it, but its conditions are written for premises and conclusions, not for checking a measurement against itself. An example or look-alike note would help.

## Unclear rules
- **Causation family rule** doesn't say where observational-interpretation sits relative to cum-hoc and common-cause. Three entries fit Q008 equally well.
- **"Stated as established"** (cum-hoc C3, observational-interpretation C3) vs policy recommendations: does "the district should require X" count as asserting causation? METHOD (b) "respect the conclusion's scope" pulls one way, and the charity limit pulls the other. A rule would help: *a recommendation whose only rationale is a causal effect counts as asserting that effect.*
- **Affirming-the-consequent C3 ("definitely")** leaves "hard to avoid the conclusion", "almost certainly" and "clearly" in a grey zone.
- **Cherry-picking C2 "plainly known"** (Q050): there's no guidance on how widely known a fact must be. This is the same issue as the "common knowledge" threshold in METHOD (b)/(f).
- **One label per step across families** (Q074, nature + tradition): METHOD (c) allows two labels only for "two separate errors", but it's unclear whether two rationales in adjacent sentences supporting one conclusion count as one step or two.
- **Look-alike downgrade threshold:** METHOD (e) says downgrade if a look-alike "plausibly applies". For Q082 (baseline "cut") and Q024 (lighting mechanism) a look-alike is arguable but not supported by the text. I didn't downgrade, because the look-alike would have to be supplied by the reviewer. Proposed wording: *downgrade only if the passage itself supplies the look-alike's features.*
- **No-issue `entry_ids`:** the output format doesn't say whether to list checked entries for no-issue rows. I did, and marked them in notes as "checked/ruled out".

## Proposed fixes (summary)
1. Add entries for Simpson's paradox, relative/absolute risk framing, and statistical vs practical significance.
2. Add a probabilistic AC look-alike, or a general converse-probability entry.
3. Add a precautionary-default look-alike to argument-from-ignorance.
4. Add observational-interpretation to the causation family rule. Suggested: *observational study → observational-interpretation, unless an obvious confounder is named or plainly known (common-cause).*
5. Define "plainly known" / "common knowledge" with a test (e.g., "an educated general reader would know it without looking it up").
6. Clarify the look-alike downgrade threshold (supplied by the text vs imagined by the reviewer).
