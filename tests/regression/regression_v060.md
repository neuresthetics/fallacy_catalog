# Regression check for v0.6.0 (not blind)

Catalog: fallacy_catalog v0.6.0 (round-3 fixes H1–H17 applied). The method was re-applied by the same agent that wrote the fixes, with the answer keys and the round-3 errors file in view. **This is not a blind test**: it can catch rules that now point the wrong way, but it cannot show that new reviewers would reach these verdicts.

## Selection

A passage was re-checked if any of these held:
- its answer key or either reviewer's verdict names an entry whose conditions, look-alikes or family rule changed in v0.6.0 (appeal to motive, ad hominem, false dilemma, amphiboly, appeal to nature, converse accident, false analogy, disregarding known science, inflation of conflict, modal scope, combination of words, appeal to accomplishment, special pleading, accent, appeal to wealth, lump of labour), or an entry in a family whose rule changed (causation: regression fallacy, ignoring a common cause; authority and popularity: appeal to authority, poverty, tradition; naturalism) or that sits next to a new entry or method rule (circumstantial ad hominem, bulverism, straw man, argument from ignorance, misplaced burden of proof);
- it is one of the 20 real excerpts in round 3;
- it is a no-argument passage (the no-argument and dialogue rules changed);
- it was cited in round-3 FIXES.md for a method rule (R016, R026, R030, R070, R082, R090, R092).

Totals: round 1, 43 passages; round 2, 51; round 3, 65 (58 by the automatic selection plus the 7 named above). 159 in all.

"Intended" is the adjudicated key (round-3 overrules: R021 and R040 not errors; R041 and R063 possible issue or flag; R092 S1 added; R082 ad hoc rescue accepted as a second label).

## Summary

| | passages | intended verdict | intended label | changed from v0.5.0 behaviour |
|---|---|---|---|---|
| Round 1 | 43 | 43 | 43 | 1 (P097 now possible issue, matching the adjudicated key) |
| Round 2 | 51 | 51 | 51 | 1 (Q016 now reaches regression fallacy by the literal rule) |
| Round 3 | 65 | 65 | 64 (+1 by design, R023) | 12 improved, 0 worse |

**Regressions found while checking, and fixed before commit:**
1. **Dialogue rule vs exercises (R093, Q073, Q034).** As first written, the H1 rule ("a participant who advances an argument in direct speech is scored") would score Ben in the R093 textbook exercise, the quoted argument in the Q073 homework item, and the con man quoted in the Q034 book review. All three are keyed no-argument. Fix: METHOD (g) now says an argument quoted inside a report, review, lesson or exercise is no argument and goes under `reported_fallacy`.
2. **Appeal to sincerity vs appeal to poverty (R023).** The new entry fits R023 exactly, but the authority-and-popularity family had no rule for which to report when poverty is cited as the reason the speaker has no motive to lie. Fix: family rule now says to use appeal to sincerity in that case. The label moves from appeal to poverty (keyed) to appeal to sincerity (the entry FIXES H12 added for this passage). The verdict is unchanged. The round-3 key was not edited, so as keyed this is a label change by design, not a miss.

3. **Carried over from v0.5.0: P097 (round 1).** The v0.5.0 regression check recorded one mismatch: "Humans evolved eating meat, so a diet that includes meat is appropriate for us" gave flag appeal to nature, where the adjudicated round-1 key says possible issue ("appropriate" can mean nutritional fit, for which evolutionary history is some evidence). It was not caused by a v0.6.0 change, but it was fixed here: appeal to nature has a new look-alike for evolutionary history offered for a conclusion that only says something suits us, which gives possible issue. Passages whose conclusion claims safety, health or rightness (P075, Q074) still flag.

No other passage changed verdict for the worse. No legit or no-argument passage picked up a flag or possible issue.

## Round 3 (65)

| id | type | intended | v0.6.0 result | note |
|---|---|---|---|---|
| R001 | no-arg | no issue | no issue; reported_fallacy: sunk cost | teaches the effect |
| R002 | legit | no issue | no issue | argument from ignorance C3 fails (thorough search) |
| R005 | real, legit | no issue | no issue | Darwin; conditional argument |
| R006 | mixed | ad hoc rescue S2–S3; burden S4; ignorance S5 | flag ad hoc rescue; flag misplaced burden; flag argument from ignorance | two adjacent steps now an explicit METHOD (c) example |
| R011 | legit | no issue | no issue | special pleading C3 fails: relevant reason (harm prevention) |
| R013 | mixed | McNamara S3–S4 | flag McNamara; S1–S2 no issue (authority look-alike) | |
| R014 | legit | no issue | no issue | testimony reliability look-alike |
| R016 | fallacy | appeal to novelty | flag appeal to novelty | unaffected |
| R019 | no-arg | no issue | no issue; reported_fallacy: post hoc | narrated, no participant in direct speech |
| R021 | real, mixed→adjudicated | no issue or possible issue | no issue; rhetorical note: sectarian motive accusation ("jesuitically", "papistical design") | **improved**: excerpt rule; denial given, argued past the excerpt boundary |
| R022 | fallacy | argument from silence | flag argument from silence | |
| R023 | fallacy | appeal to poverty (keyed) | flag appeal to sincerity | label change by design (see above) |
| R025 | fallacy | special pleading | flag special pleading | C3 now covers "I know I can be impartial" explicitly |
| R026 | fallacy | division | flag division; S2 "her lessons will be the best" noted as weak premise | performing is not teaching (accomplishment LA narrowed); entry is about the proposer, so no label |
| R027 | legit | no issue | no issue | stated default |
| R028 | real, legit | no issue | no issue | Clifford |
| R029 | fallacy | modal scope | flag modal scope; "might as well go home" weak premise (idle-argument note) | |
| R030 | mixed | sunk cost (Management) | flag sunk cost, speaker Management; union rep no issue | dialogue rule |
| R031 | fallacy | converse accident | flag converse accident | **improved**: tie-break (hospice patients are an exceptional source case) |
| R032 | no-arg | no issue | no issue | |
| R034 | no-arg | no issue | no issue | |
| R036 | mixed | etymological S3; false dilemma S4 | flag etymological; flag false dilemma | **improved**: C1 "must" after eliminating one option; derivative step gets its own row |
| R037 | legit | no issue | no issue | inflation of conflict C2 fails |
| R038 | legit | no issue | no issue | randomized control |
| R039 | real, legit | no issue | no issue | Mill, On Liberty |
| R040 | mixed→adjudicated legit | no issue | no issue; rhetorical note: "lapdogs, bought and paid for" | **improved**: rhetorical notes field |
| R041 | real, fallacy (contested) | possible issue or flag | possible issue equivocation (contested reading); possible issue composition | **improved**: contested-reading rule; both reviewers would now converge |
| R042 | real, no-arg | no issue | no issue; reported_fallacy: hasty extrapolation (Twain's mock) | author's own voice mocks |
| R044 | real, legit | no issue | no issue | Lincoln's highwayman analogy |
| R046 | real, legit | no issue | no issue | "Nature's effort" is a causal claim, not natural-so-good |
| R047 | real, legit | no issue | no issue; reported_fallacy: broken window fallacy | new entry lets the record name what Bastiat rebuts |
| R048 | real, no-arg | no issue | no issue; reported_fallacy: straw man | Schopenhauer teaches the trick |
| R049 | fallacy | appeal to wealth | flag appeal to wealth | C2 now "unrelated to how the person became rich" |
| R052 | no-arg | no issue | no issue; reported_fallacy: Simpson's paradox | |
| R053 | mixed | straw man (Brandt) | flag straw man, speaker Brandt | |
| R054 | fallacy | combination of words | flag combination of words | modern-form look-alike/pointer |
| R055 | real, legit | no issue | no issue | Russell's chicken |
| R056 | fallacy | accent | flag accent | C1 now covers real emphasis |
| R060 | mixed | regression (Coach) | flag regression fallacy, speaker Coach | causation rule: regression checked second |
| R061 | legit | no issue | no issue | authority look-alike |
| R062 | fallacy | amphiboly | flag amphiboly | **improved**: lease clause purpose counts as context |
| R063 | real, fallacy (contested) | possible issue or flag | possible issue tu quoque / bulverism (contested reading; "already exists" is argued after the excerpt) | **improved**: excerpt + contested rules make the verdict principled |
| R065 | real, legit | no issue | no issue | Douglass argues from opponents' own commitments |
| R067 | real, fallacy | false analogy | flag false analogy | Paine's island and continent |
| R069 | legit | no issue | no issue | options stated; new false-dilemma clause not triggered |
| R070 | mixed | base rate S4 | flag base rate; other error: ≈2% computed | |
| R071 | legit | no issue | no issue | |
| R072 | mixed | motive S4; slippery slope S5 | flag appeal to motive; flag slippery slope | **improved**: C1 covers proposals |
| R073 | legit | no issue | no issue | opponents' words quoted; rebuttal fair |
| R075 | no-arg | no issue | no issue | |
| R077 | real, legit | no issue | no issue | Hume |
| R080 | no-arg | no issue | no issue | |
| R081 | fallacy | inflation of conflict | flag inflation of conflict | **improved**: pointer from disregarding known science; family membership |
| R082 | fallacy | psychologist's fallacy (+ ad hoc rescue S3) | flag psychologist's fallacy; flag ad hoc rescue S3 | |
| R083 | legit | no issue | no issue | definitions resolve the ambiguity |
| R084 | real, fallacy | flag (possible issue defensible) | flag appeal to inevitability (S2: "It is here; we cannot evade it ... We accept and welcome, therefore"); possible issue appeal to nature (S1, "survival of the fittest") | **improved**: new entry; adapting look-alike fails because the conditions are "welcomed" as beneficial |
| R087 | real, legit | no issue | no issue; reported_fallacy: false dilemma | rebuttal judged under (g); no specific opponent's words, so no straw-man check |
| R089 | no-arg | no issue | no issue | news report |
| R090 | mixed | Texas sharpshooter (Resident) | flag Texas sharpshooter, speaker Resident | |
| R092 | fallacy | false precision S3 (+ S1) | flag false precision; possible issue unrepresentative sample S1; other error: count multiplied by area | |
| R093 | no-arg | no issue | no issue; reported_fallacy: straw man | needed the exercise clause (fixed) |
| R094 | real, legit | no issue | no issue; reported_fallacy: false dilemma | Lincoln rebuts a false dilemma |
| R096 | real, legit | no issue | no issue; reported_fallacy: cum hoc | Mill teaches |
| R099 | real, fallacy | flag at speaker level | flag combination of words, speaker Dionysodorus (satire noted) | **improved**: dialogue rule |
| R100 | fallacy | regression | flag regression fallacy | causation rule now matches the literal order |

Real excerpts (20): all 20 give the adjudicated answer. 14 legit/no-argument: 0 flags, 0 possible issues. 6 keyed fallacy/mixed: R021 no issue + rhetorical note, R041 and R063 possible issue (contested), R067, R084 and R099 flag.

## Round 2 (51)

All 51 give the intended verdict and label. Notes on the ones a changed rule touches:

| id | intended | v0.6.0 result | note |
|---|---|---|---|
| Q001 | no issue | no issue; reported_fallacy: ad hominem | correct use of a fallacy name |
| Q003 | reverse causation | flag reversing causation | causation order unaffected (no breakdown, no extreme selection) |
| Q006, Q013 | no issue | no issue; reported_fallacy: slippery slope / bandwagon | narrated history |
| Q011, Q064 | false dilemma | flag false dilemma | |
| Q012 | argument from ignorance | flag argument from ignorance | unchanged from the v0.5.0 regression check (the default is not independent; the precaution look-alike is not met) |
| Q016 | regression fallacy | flag regression fallacy | now by the literal causation order |
| Q034 | no issue | no issue; reported_fallacy: bandwagon | needed the review/exercise clause (fixed) |
| Q036, Q093 | no issue | no issue | transcripts with no argument advanced |
| Q049 | Simpson's paradox | flag Simpson's paradox | first in causation order |
| Q053 | no issue | no issue | satire in the author's own voice |
| Q061 | moving the goalposts | flag moving the goalposts, speaker Pratt | dialogue rule |
| Q066, Q082 | straw man | flag straw man | specific opponent and words identifiable |
| Q070, Q073 | no issue | no issue; reported_fallacy: gambler's fallacy / cum hoc | Q073 needed the exercise clause (fixed) |
| Q074 | appeal to nature | flag appeal to nature | |
| Q081 | no issue | no issue | quote is accurate |
| Q087 | no issue | no issue | legal two options stated; new clause not triggered |
| Q092 | no issue | no issue | regression look-alike (comparison group) |
| Q095 | no issue | no issue | soup analogy is an illustration of a relevant feature |
| Q098 | appeal to accomplishment / authority | flag appeal to accomplishment | |

Remaining round-2 passages in the set (Q008, Q017, Q019, Q021, Q025, Q030, Q032, Q037, Q040, Q041, Q047, Q052, Q056, Q060, Q062, Q065, Q072, Q075, Q077, Q078, Q079, Q080, Q084, Q086, Q089, Q090, Q094): unchanged from v0.5.0, intended verdict and label.

## Round 1 (43)

All 43 give the intended verdict and label (borderline items scored leniently as in round 1). Only P097 changed (see above). Ones checked most closely: P012 (Nobel physicist on statistics: accomplishment look-alike for a method the field uses still applies; "worth taking seriously" is hedged), P030 (false analogy, no exceptional source case, so the converse-accident tie-break does not move it), P073 (pass/fail is exhaustive; new false-dilemma clause not triggered), P097 (now possible issue under the new fit look-alike; flag in v0.5.0), P095 (circumstantial ad hominem chosen within the family, as before), P022 and P054 (straw man: specific opponent and words identifiable).

## Limits

The same agent wrote the fixes and ran this check, with the keys in view. Treat it as a consistency check on the rules, not as evidence of accuracy. The next blind round is the real test of v0.6.0.
