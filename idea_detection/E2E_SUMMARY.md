# Held-out idea-detection run (eight pilots)

Blind extract, then `idea_detection.check.check_passage`. The checker in that run had the original eight patterns only: ad hominem, appeal to authority, equivocation, false cause, begging the question, cherry-picking, straw man, argument from ignorance. The five later pilots (hasty generalization, slippery slope, false dilemma, appeal to the people, guilt by association) are not in these numbers.

The IR dump and the row-level CSV were local working files (`tmp/e2e_irs/`, `tmp/e2e_idea_detection_results.csv`, `tmp/e2e_check_reports.jsonl`). They are not part of the clone. Reproduce from the passage files named in [DEV_PROCESS.md](DEV_PROCESS.md), then score with `python3 -m idea_detection.score_eval`.

## Totals

- **N tested:** 398 (round 1 = 120, round 2 = 100, round 3 = 100, fp test = 78)
- **Hits (right name):** 58
- **False positives:** 0
- **Misses:** 129, of which that run called 12 inside its alias list and 117 outside
- **Partial (`possible_issue` only):** 5
- **Clean (legit or no-argument, no flag):** 206
- **Extractor or checker failures:** 0

| set | n | hit | fp | miss | partial | clean | fail |
|---|---:|---:|---:|---:|---:|---:|---:|
| r1 | 120 | 18 | 0 | 49 | 3 | 50 | 0 |
| r2 | 100 | 17 | 0 | 23 | 0 | 60 | 0 |
| r3 | 100 | 9 | 0 | 33 | 2 | 56 | 0 |
| fp | 78 | 14 | 0 | 24 | 0 | 40 | 0 |

Zero false positives on legit and no-argument rows is the result to keep. The five partials were `possible_issue` on `appeal-to-authority` while the gold named another entry (division, pity, is-ought, McNamara, base rate). Score those as `wrong_possible`, not as hits. See [DEV_PROCESS.md](DEV_PROCESS.md).

Sample hits from that CSV: `r1/P001` cherry-picking; `r1/P005` and `r1/P006` ad hominem; `r1/P013` equivocation; `r1/P022` begging the question and straw man; `r1/P028` begging the question; `r1/P032` false cause; `r1/P049` argument from ignorance. No false-positive rows.

## The twelve "inside" misses, as reviewed

That run's inside/outside split used a broad alias list (guilt by association, genetic fallacy, tu quoque, and ad hoc / special pleading were allowed to count as ad hominem or ignorance). The hand classes below are the review of those twelve rows. They are not a fresh extract.

| id | truth | gold (short) | hand class |
|---|---|---|---|
| `r1/P012` | borderline | appeal to inappropriate authority | `expected_charity` |
| `r1/P019` | borderline | cum hoc; correlation implies causation | `expected_charity` |
| `r1/P048` | borderline | argument from ignorance; shifting the burden | `expected_charity` |
| `r1/P053` | borderline | guilt by association; ad hominem | `expected_charity` |
| `r1/P069` | borderline | argument from ignorance | `expected_charity` |
| `r1/P095` | fallacy | circumstantial ad hominem; appeal to motive | `pattern_gap` |
| `r1/P110` | borderline | whataboutism; tu quoque | `ir_gap` |
| `r2/Q010` | fallacy | formal names; guilt by association | outside the eight pilots (cousin list had pulled it inside) |
| `r3/R006` | mixed | ad hoc; special pleading; appeal to ignorance | `ir_gap` |
| `r3/R063` | contested | tu quoque; circumstantial ad hominem; bulverism | `contested_stay` |
| `r3/R072` | mixed | circumstantial ad hominem; slippery slope | `ir_gap` |
| `fp/F18` | fallacy | guilt by association; genetic fallacy | `pattern_gap` |

`score_eval` does not reproduce "12 inside". Cousin names count only for their own id, and tu quoque is not an ad hominem alias. On the published gold strings, with no `miss_class` set:

| id | eight pilots | thirteen pilots |
|---|---|---|
| P012, P019, P048, P069 | `expected_charity` | `expected_charity` |
| P053 | `expected_charity` (`ad-hominem`) | `expected_charity` (`ad-hominem` and `guilt-by-association`) |
| P095 | `inside_miss` | `inside_miss` — set `miss_class=pattern_gap` to keep the hand class |
| P110 | `expected_outside` | `expected_outside` — set `miss_class=ir_gap` to keep the hand class |
| Q010 | `expected_outside` | `inside_miss` on `guilt-by-association` only |
| R006 | `inside_miss` on ignorance (the key also says appeal to ignorance) | same — set `miss_class=ir_gap` for the hand class |
| R063 | `contested_stay` | `contested_stay` |
| R072 | `inside_miss` on ad hominem | `inside_miss` on ad hominem and slippery slope — set `miss_class=ir_gap` for the hand class |
| F18 | `expected_outside` | `inside_miss` on `guilt-by-association` — set `miss_class=pattern_gap` for the hand class |

P012, P019, P048, P053, and P069 stay misses on purpose. The forbids that produced them are listed in [DEV_PROCESS.md](DEV_PROCESS.md).
