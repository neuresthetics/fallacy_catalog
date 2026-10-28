# Idea-detection development process

How this layer is designed, checked, and extended. The contract for a single passage is [IDEA_DETECTION.md](../IDEA_DETECTION.md). The predicate design is [IDEA_LEVEL_DETECTION.md](IDEA_LEVEL_DETECTION.md). [METHOD.md](../METHOD.md) stays the human procedure.

## What it is

`idea_detection` is a deterministic checker over an Idea IR.

- The catalog (`fallacies.json`) is the source of truth for names, conditions, and look-alikes.
- The extractor (a model or a person) proposes the IR only: claims, edges, spans, hedges, under METHOD charity. It does not emit the verdict.
- The checker matches `ir_pattern`, blocks on `ir_forbid`, and applies the catalog's outside-text and `text_detectable` gates. A flag must bind quotes from the passage.
- Patterns live in [`pilot_ir_patterns.json`](pilot_ir_patterns.json). They stay in that side file until someone reviews them against the catalog prose.
- The layer is vanilla catalog. It does not read `frameworks/mindspace.json`.

Thirteen pilots are active: the original eight (`ad-hominem`, `appeal-to-authority`, `equivocation`, `false-cause`, `begging-the-question`, `cherry-picking`, `straw-man`, `argument-from-ignorance`) and five added after the held-out run below (`hasty-generalization`, `slippery-slope`, `false-dilemma`, `appeal-to-the-people`, `guilt-by-association`). Appeal to the people is the catalog id; "appeal to popularity" is an alias. Guilt by association is its own pattern. It is not an edit to ad hominem.

## Development loop

Work in this order. Evidence from a run decides the next edit. A recall gap is not, by itself, a reason to edit a forbid.

1. **Design note.** State the IR shape, the `ir_pattern` atoms, and the `ir_forbid` look-alikes for any new pilot before changing the checker. Keep the note next to the code it describes (`IDEA_LEVEL_DETECTION.md` for the predicate design).
2. **Refine from evidence.** After a fixture run or a held-out run, classify each miss with the taxonomy below. Separate charity that fired correctly, an IR the extractor under-built, a pattern that cannot express the structure, and a gold name with no pilot.
3. **Implement.** Add or adjust predicates and side-file patterns. Leave catalog prose in `fallacies.json` alone unless a reviewed catalog edit is the actual task.
4. **Unit and fixture tests.** Cover the new flag and each look-alike the forbid is there to block. Commands are in the next section.
5. **Held-out end-to-end.** Blind rounds plus the false-positive set, scored with [`score_eval.py`](score_eval.py). The full extract is local; see below. It is not a CI job.
6. **Classify misses.** Fill `miss_class` from the IR. `ir_gap` and `pattern_gap` are review labels. The scorer does not invent them.
7. **Expand pilots.** Pick the next ids from outside-pilot misses. Each new id gets its own pattern and its own forbids. Then return to step 4.

The five pilots added in the batch after the N=398 run followed that loop: hasty generalization, slippery slope, false dilemma, appeal to the people, and guilt by association, plus the extractor rule that a premise→conclusion cue (`so` / `must` / `therefore` / dismiss / ignore) must not collapse to a lone `report` with zero edges.

## Precision first

METHOD step (b) is the charity rule: hedges stay hedges, procedural defaults stay procedural, and a precaution is not a proof of the feared claim. The checker encodes that in forbids. These stay as they are:

| Forbid or predicate | What it blocks |
|---|---|
| `authority_treated_as_settling` | A weak hedge ("worth taking seriously") counted as an authority settling the question |
| `tentative_hypothesis_for_testing` | A hedged cause ("probably") counted as false cause |
| `procedural_default_action_only` | A `default_rule` ("I'll assume it doesn't work until a trial") counted as ignorance |
| `precautionary_decision_with_costs_weighed` | A precaution under unknown risk counted as ignorance |
| `trait_irrelevant_to_reasons` | An interest that bears on the reasons counted as ad hominem |
| `claim_rests_on_testimony` | Doubt about testimony counted as ad hominem |
| `uses_opponents_own_commitments` | Tu quoque / whataboutism forced through the ad hominem pattern |

The held-out run's zero flags on legit and no-argument passages are the gate. A later run that flags those passages is a regression. Closing a miss by deleting or weakening one of the rows above is a regression of the same kind.

Passage ids from that run that the charity rules correctly left unflagged: P012, P019, P048, P053, P069. They are `expected_charity` (P053 also names guilt by association, which is a pilot now; the hedge still holds). P095 stays unresolved until a separate circumstantial or motive pattern exists. Do not flip `trait_irrelevant_to_reasons` to catch it.

## Tests

From the repository root. Python 3 standard library only.

```
python3 -m unittest tests/idea_detection/test_checker.py
```

```
python3 -m unittest tests/idea_detection/test_score_eval.py
```

```
python3 -m idea_detection.eval_fixtures
```

```
python3 -m idea_detection idea_detection/fixtures/method_ex1_ad_hominem.json
```

```
python3 -m unittest tests/idea_detection/test_method_record.py
```

```
python3 -m idea_detection.score_eval idea_detection/examples/score_eval_example.csv
```

Full-detail output for a folder of Idea IR files (METHOD record shape, not the one-line verdict):

```
python3 -m idea_detection --method-record path/to/irs/
```

```
python3 -m idea_detection --method-record --method-format jsonl path/to/irs/
```

`eval_fixtures` checks the two METHOD fixtures: example 1 flags `ad-hominem`; example 2 is `no_issue` on `appeal-to-authority`. The checker strips `expected_checker` and does not treat it as a verdict.

Catalog audits and the blind human rounds are a different procedure. They are in the main [README](../README.md#testing) and under [`tests/`](../tests/).

## Held-out end-to-end

The measurement set is the passages already in the repo:

| Set | File | Rows |
|---|---|---|
| r1 | [`tests/round1/passages.csv`](../tests/round1/passages.csv) | 120 |
| r2 | [`tests/round2/passages.csv`](../tests/round2/passages.csv) | 100 |
| r3 | [`tests/round3/passages.csv`](../tests/round3/passages.csv) | 100 |
| fp | [`tests/audit/fp_test_passages.csv`](../tests/audit/fp_test_passages.csv) | 78 |

N = 398. Gold for the rounds is `acceptable_fallacy_names` and `truth` in each round's `answer_key.csv`. Gold for the fp set is `ground_truth` and `intended_entry_or_lookalike` in `fp_test_passages.csv`.

Run shape:

1. Build one Idea IR per passage from the passage text alone, using [EXTRACTOR_PROMPT.md](EXTRACTOR_PROMPT.md). The extractor proposes structure. It does not write a fallacy id into the IR.
2. Call `idea_detection.check.check_passage` on each IR.
3. Write a results CSV with `id`, `set`, `truth`, `acceptable`, `flagged`, `possible`, and (after review) `miss_class`. `flagged` and `possible` are catalog ids, `|`-separated.
4. Score it:

```
python3 -m idea_detection.score_eval path/to/results.csv
```

Keep the IR trees and the raw CSV under `tmp/` on the machine that ran the extract. They are local working files. The repo keeps this process, the summary numbers, and the small example CSV. Re-running all 398 extracts is not part of CI.

The numbers in [E2E_SUMMARY.md](E2E_SUMMARY.md) are from the eight-pilot checker, before hasty generalization, slippery slope, false dilemma, appeal to the people, and guilt by association existed. They are not a score of the current thirteen.

## Miss taxonomy

[`score_eval.py`](score_eval.py) labels each row. A **hit** is a flag whose name meets the acceptable list. A **false positive** is a flag on `legit` or `no-argument`. That count is the gate. `clean` is legit or no-argument with no flag.

`wrong_possible` is a `possible_issue` whose entry id misses the acceptable list. The eight-pilot run had five of these, all `appeal-to-authority`, while the gold named something else (division, pity, is-ought, McNamara, base rate). They are a soft miss on the label. They are not hits. A `possible_issue` whose name is acceptable stays `partial`.

When nothing was flagged, the miss labels are:

| Label | When |
|---|---|
| `expected_outside` | No acceptable name is an active pilot |
| `expected_charity` | An active pilot is named, `truth` is `borderline`, and no `miss_class` was set |
| `contested_stay` | `truth` is `contested` (METHOD contested-reading cap) |
| `ir_gap` | Set `miss_class` after reading the IR: a known pilot shape is missing because the extract collapsed |
| `pattern_gap` | Set `miss_class` after reading the IR: the structure is there and no current pattern can express it |
| `inside_miss` | An active pilot is named, and the row still needs `ir_gap` or `pattern_gap` |

`miss_class` overrides those six miss labels. It does not turn a hit or a false positive into something else. Unknown `miss_class` values are an error.

**Inside a pilot.** A gold name counts for a pilot when it matches that pilot's catalog name or aliases (parentheticals stripped, so "ad hominem (circumstantial)" meets `ad-hominem`). Two extras are deliberate:

- `appeal to inappropriate authority` meets `appeal-to-authority`.
- `selective evidence` meets `cherry-picking`.
- Cum hoc and post hoc names meet `false-cause`, because that pilot is the catalog fallback (`use_only_if_nothing_more_specific`) and the keys use the specific names.

**Cousins stay out.** These ids count only when they themselves are active pilots: `guilt-by-association`, `genetic-fallacy`, `bulverism`, `ad-hoc-rescue`, `special-pleading`. Their names are not aliases of ad hominem or of argument from ignorance. Guilt by association is an active pilot, so a key that says "guilt by association" is inside that pilot. Genetic fallacy, bulverism, ad hoc rescue, and special pleading are not pilots, so a key that names only those is `expected_outside`. Tu quoque and whataboutism are not ad hominem either (`uses_opponents_own_commitments` is a forbid). A key that names only them is `expected_outside` until a tu-quoque pilot exists. Set `miss_class=ir_gap` when the extract also dropped the move.

The eight-pilot run's "12 inside" count used a wider alias list than this. [E2E_SUMMARY.md](E2E_SUMMARY.md) has the hand labels from that review and the labels this scorer assigns to the same gold strings.

## Pilot expansion

Add a pilot by editing `pilot_ir_patterns.json` and the predicate tests. Do not paste the pattern into `fallacies.json` as part of that change. A merge into the catalog is a separate review: the prose `required_conditions` and `legitimate_lookalikes` stay authoritative, and the pattern must not contradict them.

Use a catalog id that already exists. This layer does not invent fallacy names, Latin or otherwise.

Each new pattern needs an `ir_forbid` for the look-alikes METHOD already treats as legitimate, written before the pattern is treated as done. The batch that landed used: uniform population, cautious or low-stakes generalization, selection-not-size; a mechanism on each slope link, or line-drawing with no prediction; options not claimed to be the only ones, or a true dichotomy; expert agreement, a question about taste or popularity, popularity as one piece among others, a non-decisive hedge; association as disclosure or caution, or merits that are actually engaged.

The N=398 review's remaining outside-pilot candidates, in the order that review recorded, are: appeal to nature, sunk cost, genetic fallacy, composition, affirming the consequent, no true Scotsman, red herring, special pleading, tu quoque / whataboutism, base-rate neglect. They are candidates for a later design note. They are not patterns in the side file.

## METHOD

[METHOD.md](../METHOD.md) is the procedure for checking an argument by hand, including Genius Study audits. This layer does not rewrite it.

A machine flag is readable as a METHOD record through [`record.py`](record.py): entry id and name, passage quote, each catalog condition, each legitimate look-alike, and the verdict. The record is an idea_detection assist / lead-to-check. "Met by" uses a closed checker span only. A condition with no declared span, or only an open outside-text span, is marked not shown, and no quote is invented. Flagged look-alikes say the paired `ir_forbid` atoms were checked and none matched. They do not grow a handwritten reason. `no_issue` passages, including METHOD example 2, are not emitted as flags. Bulk use is `python3 -m idea_detection --method-record` on one IR, many IR paths, or a directory of `*.json`. JSONL is `--method-format jsonl`. A saved `--json` report is `python3 -m idea_detection.record --json report.json --ir <irs>`.
