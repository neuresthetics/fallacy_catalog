# Regression check, catalog v0.5.0 (commit 46e8036), not blind (applied by the catalog builder)

Intended = answer key plus FIXES key corrections (round 1 corrections; round 2 K1-K5).

## Round 1 (30 error/fragile + 10 random legit)
| id | intended | v0.5.0 result | match |
|---|---|---|---|
| P068 | flag cherry picking | flag cherry-picking (rest stated, ignored) | yes |
| P013 | flag equivocation | flag equivocation (four terms) | yes |
| P086 | possible issue or flag | flag slippery slope (first-link evidence only; same-body decisions, no binding mechanism) | yes |
| P005 | possible issue | possible issue, circumstantial ad hominem (bare distrust look-alike) | yes |
| P009 | possible issue | possible issue, anecdotal evidence (C3 outside text, not common knowledge) | yes |
| P019 | possible issue | possible issue, observational interpretation (partial adjustment + hedge) | yes |
| P042 | no issue | no issue (small sample, large effect, reversible) | yes |
| P097 | possible issue (corrected key) | flag appeal to nature (LA now needs physiological evidence; none given) | NO: stricter than corrected key, matches original lean |
| P107 | flag middle ground | flag | yes |
| P001 | flag | flag cherry-picking (misses stated) | yes |
| P017 | flag slippery slope | flag | yes |
| P022 | flag straw man | flag | yes |
| P054 | flag straw man | flag | yes |
| P046 | flag base rate | flag base-rate (after tie-break fix; before it, confusion of the inverse also fit) | yes |
| P088 | flag survivorship | flag (C2 common knowledge) | yes |
| P113 | flag false equivalence | flag (C2 common knowledge) | yes |
| P012 | no issue | no issue (method look-alike; not settling) | yes |
| P092 | flag (courtier's/credentials) | flag courtier's reply (standing denied) | yes |
| P084 | flag special pleading | flag | yes |
| P057 | flag appeal to force | flag | yes |
| P118 | flag tu quoque / ad hominem | flag ad hominem (inconsistency looser than same principle) | yes |
| P006 | flag (lean) | flag tu quoque (targets the message) | yes |
| P110 | no issue | no issue (consistency demand) | yes |
| P032 | flag cum hoc | flag cum hoc (wealth confounder not clearly common knowledge); common cause also defensible | yes, label at risk |
| P076 | flag post hoc | flag post hoc (magical-thinking pointer) | yes |
| P049 | flag argument from ignorance | flag argument from ignorance + separate causal leap | yes |
| P015 | no issue | no issue (fair reductio) | yes |
| P021 | no issue | no issue (correct diagnosis) | yes |
| P036 | no issue | no issue (reductio) | yes |
| P115 | no issue | no issue (correct diagnosis) | yes |
| P004 P023 P026 P029 P033 P052 P056 P060 P094 P111 (random legit) | no issue | no issue (each blocked by a failed condition or look-alike) | yes (10/10) |

## Round 2 (32 error/fragile + 10 random legit)
| id | intended | v0.5.0 result | match |
|---|---|---|---|
| Q012 | flag argument from ignorance | flag (default not independent; FCC standard points other way; precaution LA not met) | yes |
| Q010 | flag (K2) | flag confusion of the inverse | yes |
| Q050 | flag cherry picking | flag from text alone (window clause) | yes |
| Q049 | flag Simpson's (K5 also common cause) | flag Simpson's paradox (after tie-break fix) | yes |
| Q003 | flag (K4 common cause) | flag common cause (selection reason plainly known; recommendation rule) | yes |
| Q074 | flag nature/tradition | flag appeal to nature, note tradition | yes |
| Q014 | possible issue (K3) | possible issue, complex question (C2 outside text) | yes |
| Q054 | no issue (K1) | no issue; other errors note: 5.1% should be about 5.3% | yes |
| Q002 | flag | flag statistical vs practical significance | yes |
| Q027 | flag | flag relative-risk framing | yes |
| Q051 | flag affirming the consequent | flag (near-certain conclusion) | yes, small label risk vs confusion of the inverse |
| Q057 | flag gambler's | flag (mirror form) | yes; C1 (independence of floods) may need outside knowledge |
| Q035 | flag Texas sharpshooter | flag | yes |
| Q008 | flag cum hoc / confounding | flag cum hoc (or common cause; both accepted) | yes |
| Q082 | flag straw man | flag (opponent explicitly rejected 'cut') | yes |
| Q024 | flag post hoc | flag (mechanism not supplied, so no downgrade) | yes |
| Q064 | flag false dilemma | flag (implied two-option framing); charged words not a 2nd error | yes |
| Q086 | flag no true Scotsman | flag | yes |
| Q020 | flag begging the question | flag | yes |
| Q030 Q036 Q040 Q052 Q060 Q090 Q093 Q006 Q013 Q034 Q070 Q073 | no issue | no issue (no-argument / mention line) | yes (12/12) |
| Q037 | flag circumstantial | flag (declared ignorable) | yes |
| Q009 Q025 Q026 Q028 Q029 Q044 Q046 Q047 Q055 Q056 (random legit) | no issue | no issue | yes (10/10) |
