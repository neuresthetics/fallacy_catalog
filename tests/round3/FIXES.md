# Round 3: fixes

## What was changed in response (catalog v0.6.0)

Applied in the v0.6.0 commit (223 entries):
- **H1, dialogues.** METHOD (g): each participant's argument in a dialogue is scored, even when the author is satirising it. "No argument" is used only when the passage's own voice narrates, teaches or mocks, or when an argument is quoted inside a report, review, lesson or exercise. The fallacy such a passage displays goes in a new `reported_fallacy` field. (The exercise clause was added after the regression check showed that the first wording would have scored the quoted exchange in R093, Q073 and Q034.)
- **H2, excerpts.** METHOD (b): if a condition fails only because support may lie past the excerpt boundary, record at most possible issue and say what the full text would need to show.
- **H3, contested readings.** METHOD (b): for a well-known argument whose fallacy charge is disputed in the literature, name the classic charge, mark the row "contested reading", and give possible issue unless the passage's words settle it.
- **H4, rhetorical notes.** A "rhetorical notes (not fallacies)" field for invective, charged wording and unsupported accusations that no inference rests on.
- **H5–H8, H13–H15, conditions.** Appeal to motive and ad hominem C1 cover proposals (a rule or policy counts); false dilemma C1 covers an unstated two-way split signalled by "must"; amphiboly C3 counts the evident purpose of a document as context, with a look-alike for two equally good readings; appeal to nature adds "survival of the fittest" and "law of nature"; special pleading C3 excludes a bare self-assessment; accent C1 covers real emphasis read as an unintended contrast; appeal to wealth C2 reads "unrelated to how the person became rich".
- **H8, H12, new entries.** Appeal to inevitability and appeal to sincerity (no published source found that lists either as a fallacy, so both are marked `sources: TODO`); broken window fallacy (Wikipedia, "Parable of the broken window"; Bastiat, "What Is Seen and What Is Not Seen").
- **H9–H11, tie-breaks.** Converse accident vs false analogy; inflation of conflict joins the authority-and-popularity family, with a pointer from disregarding known science; the causation rule checks regression to the mean before common cause; the authority-and-popularity rule routes "poor, so no reason to lie" to appeal to sincerity.
- **H12, notes.** Modal scope fallacy notes that fatalist arguments are often charged with it, and that the ancient idle argument is a contested reading (Wikipedia, "Modal fallacy"; SEP, "Fatalism"). Combination of words gets a note on its modern form (combining permissions or possibilities). Appeal to accomplishment's look-alike is narrowed to the same field and the same skill.
- **H16–H17, METHOD (c) and (g).** A step that builds on an earlier error gets its own row if it commits a separate move; a second weak link without an entry is noted as "weak premise"; worked example of a burden demand followed by an argument from ignorance; a rebuttal's own logic is judged under the usual steps, and fair attribution is checked only when a specific opponent's words are in the passage.

- **Found in the v0.6.0 regression check and fixed:** the dialogue rule's exercise/review clause (see H1), the appeal-to-sincerity routing rule, and an appeal-to-nature look-alike for evolutionary history offered for a fit-only conclusion (resolving P097 from round 1). See [../regression/regression_v060.md](../regression/regression_v060.md).

**Not applied as written:**
- The aliases "appeal to controversy", "argument from expert disagreement" and "manufactured doubt" were not added to inflation of conflict, because no fetched source uses them for this fallacy. The first two appear in the pointer text in disregarding known science instead, so a text search still finds the entry. "Manufactured doubt" names a deliberate strategy, not this inference.
- "Idle argument" was not added as an alias of modal scope fallacy: the SEP entry on fatalism says it is unclear where the idle argument goes wrong, so it is recorded as a contested-reading note.
- "Conjunction of permissions / possibilities" was not added as an alias, because it is not an established name; the modern form is described in a look-alike note instead.

The answer-key corrections listed below were applied to `answer_key.csv` (see its `original_key` and `overrule_reason` columns). R031 was left as keyed (converse accident), as the scorer recommended.

## Recommended fixes, as written by the scorer

*Original title: Round 3 fixes: catalog @ 46e8036 (v0.5.0)*

This list merges the scoring errors (errors.csv) with every problem raised in tests/round3/notes_E.md (strict) and tests/round3/notes_F.md (practical), with duplicates removed. It is ordered by verdicts changed, then label stability, then latent fragility. The catalog was not edited.

## P1: changes a verdict, mostly on real texts

**H1. METHOD (g): dialogue participants vs reported, satirised or taught arguments, plus a `reported_fallacy` field.** (E-2, F unclear-1, S)
- Rule: "In a dialogue or exchange, score each participant's argument. A participant who advances an argument in direct speech is scored even when the author is satirising it (note the satire). Use no argument only when the passage's own voice narrates, teaches or mocks without a participant advancing the argument."
- Add a `reported_fallacy` column for no-issue rows that display a fallacy, so a skim of the verdicts still shows it.
- Passages: **R099** (E no issue → flag at speaker level). Unchanged and now principled: R019, R042, R093 (no issue + reported_fallacy), and R030, R053, R060, R090 (speaker-level flags).

**H2. METHOD (b): excerpt-of-real-text rule.** (E-1, E unclear on R063, F unclear-8, S)
- "If the passage is an excerpt and a condition fails only because support may lie past the excerpt boundary, record at most possible issue, and say what the full text would need to show. Don't import the reviewer's memory of the full text as if it were in the passage."
- Passages: **R021** (E's forced flag → possible issue / no issue), **R063** (possible issue, settled), R041.

**H3. METHOD: scholarly-disputed readings.** (E-3, F unclear-8, S)
- "For a well-known argument whose fallacy charge is disputed in the literature, name the classic charge, mark the row `contested reading`, and give possible issue unless the passage's words settle it. State the reading under which it is a fallacy."
- Add `status: contested-reading` as a row flag.
- Passages: **R041** (E flag / F possible issue → both converge on possible issue + contested), R084, R063.

**H4. A "rhetorical notes (not fallacies)" field.** (S; F and E on R021/R040)
- Charged or sectarian wording, invective, and unsupported accusations that no inference rests on are recorded here, not as fallacies. This matches the existing "other errors" field for arithmetic.
- Passages: **R040** and **R021** (key overruled). This gives users a place to see "unsupported corruption claim" without a false fallacy flag.

**H5. Appeal to motive (and abusive ad hominem) C1 should cover proposals.** (E unclear, F unclear-3)
- C1: "an argument, claim or proposal (a rule or policy counts)", matching circumstantial ad hominem.
- Passages: **R072 S4** (E possible issue → flag).

**H6. False dilemma with implied options, and derivative steps.** (E unclear, F unclear-9)
- false-dilemma C1: add "...or the conclusion relies on an unstated two-way split, signalled by 'must' after one option is eliminated".
- METHOD (c): "a step that builds on an earlier error gets its own row if it commits a separate move".
- Passages: **R036 S4** (both possible issue → flag).

**H7. Amphiboly C3: the document's purpose counts as context.** (S, F-R062)
- C3: "...the context, including the evident purpose of the document or rule, supports the other reading".
- New look-alike: "both readings fit equally and nothing favours either → possible issue".
- Passages: **R062** (F possible issue → flag), R083 (stays no issue).

**H8. Appeal to inevitability entry, and appeal-to-nature equivalents.** (F missing-2, S)
- New entry:
  - C1: something is described as unavoidable or already here.
  - C2: it is concluded to be good, beneficial or to be welcomed.
  - C3: the inevitability is the reason given for that step.
  - Look-alike: accepting and adapting to it without approving.
- Add "survival of the fittest" and "law of nature" to the appeal-to-nature C1 equivalents.
- Passages: **R084** (F possible issue → flag).

## P2: label stability and discoverability

**H9. Converse accident vs false analogy, a cross-family tie-break.** (S)
- "An exceptional source case (special population or circumstance) with a rule for ordinary cases or everyone → converse accident. One case carried to another comparable case → false analogy."
- Passages: **R031** (both wrong label).

**H10. Make inflation of conflict findable.** (E missing-2, F first-judgment table)
- Add aliases: "appeal to controversy", "argument from expert disagreement", "manufactured doubt".
- Put it in a family, and add a pointer from disregarding-known-science.
- Passages: **R081** (E wrong label), R037 (stays no issue).

**H11. Causation family rule: check regression before common cause.** (F unclear-4)
- "Cases selected for an extreme value that then moved toward average → regression fallacy" comes before the "selected into a group → common cause" step.
- Passages: R100 and R016 (both correct, but against the literal rule), R038 and R060.

**H12. New entries and aliases for moves that currently ride on a lucky fit.** (E missing, F missing)
- Broken window (ignoring opportunity cost / the unseen): R047, so (g) can record what Bastiat names.
- Appeal to sincerity ("no reason to lie, so it's true"): R023.
- Idle argument (fatalism) alias on modal-scope-fallacy: R029.
- Modern aliases for combination-of-words ("conjunction of permissions / possibilities"): R054.
- appeal-to-accomplishment LA1 narrowed to "same field and same skill (performing is not teaching)": R026, second link.

## P3: wording (right verdicts that are fragile)

**H13. special-pleading C3.** (E, F-5)
- "A bare self-assessment that one meets the purpose the rule exists to verify does not count."
- Passages: R025.

**H14. accent with real stress.** (E, F-6)
- C1 also covers real emphasis read as implying a contrast the speaker plainly did not intend.
- Passages: R056.

**H15. appeal-to-wealth C2.** (F-7)
- "Unrelated to how the person became rich."
- Passages: R049.

**H16. METHOD (c) multi-row conventions.** (E, F-2)
- A second weak link gets its own row if it meets an entry's conditions; otherwise note it as "weak premise" without a label (R026, R029, R090, R100).
- Adjacent sentences are two steps when each meets its own entry; add a burden-demand + argument-from-ignorance example (R006).

**H17. (g) vs straw man precedence.** (E)
- The rebuttal's logic is judged under (g). Fair attribution is a straw-man check, made only when a specific opponent and their words are identifiable.
- Passages: R087.

## Answer-key corrections

- **R021:** remove the error, or make it possible issue + a rhetorical note. The refutation follows in the next sentence of Common Sense, and the motive clause comes after two independent replies.
- **R040:** re-grade as legit + a rhetorical note. The insult isn't offered as a reason, so this isn't an ad hominem.
- **R041:** accept possible issue (contested reading) as well as flag.
- **R063:** re-grade to contested, with possible issue correct. S3 is a direct rebuttal, and the "already exists" point is argued after the excerpt ends.
- **R092:** add S1 as a second error. One corner counted for ten seconds isn't a representative sample, and the method multiplies a count by an area instead of a density.
- **R082:** accept ad hoc rescue as a second label on S3.
- **R031:** the key is right (converse accident). Consider accepting false analogy as a near label until H9 lands.

## Cumulative results, rounds 1–3

| | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| Catalog version (commit) | v0.3.0 (df075a2) | v0.4.0 (ccc9a6f) | v0.5.0 (46e8036) |
| Entries | 215 | 216 | 220 |
| Reviewers | A, B (same style) | C strict, D practical | E strict, F practical |
| Passages | 120 | 100 | 100 (114 / 108 rows) |
| Mix | 50 legit, 50 fallacy, 20 borderline | 40 legit, 20 no-argument, 40 fallacy | 43 legit, 11 no-argument, 35 fallacy, 11 mixed; 20 real excerpts |
| Hard FP on legit + no-argument | 0/50, 0/50 | 0/60, 0/60 | 0/54, 0/54 |
| Soft FP on legit + no-argument | 0, 0 | 0, 0 | 0, 0 |
| Fallacy hit with acceptable label | 50/50, 49/50 | 35/40, 38/40 | 31/35, 30/35 (as keyed) |
| Wrong label | 0, 1 | 1, 0 | 2, 1 |
| Soft miss (as keyed) | 0, 0 | 4, 2 | 1, 4 |
| Hard miss (as keyed) | 0, 0 | 0, 0 | 1, 0 |
| Misses after key adjudication | 0, 0 | 3, 1 (Q012 both; Q010 and Q050 C only) * | 1, 2 |
| Mixed: error units found | n/a | n/a | 11/14, 11/14 as keyed; 10/12, 11/12 adjudicated |
| Borderline matching the key | 19/20, 20/20 (lenient) | n/a | n/a |
| Passage verdict agreement | 119/120 (κ 0.985) | 98/100 (κ 0.960) | 95/100 (κ 0.903) |
| Label agreement on joint flags or steps | 51/52 (98%) | 33/36 (92%) | 48/51 (94%) |
| Key errors found | 6 | 5 | 6 (R021, R040, R041, R063, R092, R082) |

\* Round 2, after adjudication: Q014 was overruled to possible issue for both reviewers. Q012 stayed a soft miss for both. Q010 and Q050 were soft misses for C only.

Trend:
- False positives have stayed at zero across 328 reviewer judgments of legit or no-argument passages, on progressively harder sets. The false-positive step is holding.
- Misses fell as each round's fixes landed, then reappeared in new places each round. Round 2's misses were missing entries. Round 3's were excerpt boundaries, dialogue speakers and contested historical readings.
- Agreement drops as the material gets more realistic. In round 3, 4 of the 5 passage disagreements were real excerpts.
- The next gains are method rules for real texts (H1–H4), not more conditions on individual entries.
