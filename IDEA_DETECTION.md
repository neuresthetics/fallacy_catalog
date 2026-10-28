# Idea-level detection

Fallacy labels in this repository are decided from **claim and support structure**, not from sentence cadence. The catalog (`fallacies.json`) stays the source of truth. This layer makes [METHOD.md](METHOD.md)'s false-positive rules machine-checkable for a pilot set of entries. It does not replace METHOD.

## Who verdicts

| Role | May do | Must not do |
|---|---|---|
| **Extractor** (model or human) | Propose an Idea IR: steps, claims, edges, spans, under METHOD charity. A premise→conclusion cue (`so` / `must` / `therefore` / dismiss / ignore) must not collapse to a lone `report` with zero edges | Emit a fallacy id or verdict the pipeline treats as final |
| **Normalizer** | Downgrade hedges from the quoted words; mark burden/null language as procedural; drop illustration-only `supports` edges | Invent contrary evidence |
| **Checker** | Match `ir_pattern`, block on `ir_forbid`, apply outside-text and `text_detectable` gates | Trust extractor prose, or flag on an insult or a stock phrase alone |

A **flag** requires every pattern atom to bind a quote from the passage, no forbid to match, and the catalog gates to allow it. `text_detectable: no` (confirmation bias, selective attention, availability heuristic, rationalization) is never a flag. Unmet outside-text conditions are at most **possible issue**. Excerpt boundaries and contested readings cap a match the same way.

Patterns for thirteen pilot entries live in [`idea_detection/pilot_ir_patterns.json`](idea_detection/pilot_ir_patterns.json). They are not merged into `fallacies.json`. The layer does not add fallacy names and does not use MINDSPACE.

The original eight are unchanged, including ad hominem’s `trait_irrelevant_to_reasons` and `claim_rests_on_testimony`, the authority settling hedge, false cause’s `tentative_hypothesis_for_testing`, and the ignorance procedural and precautionary forbids. The added pilots are hasty generalization, slippery slope, false dilemma, appeal to the people (the catalog id; “appeal to popularity” is an alias), and guilt by association. Guilt by association is a separate pattern: an association trait plus `supports` into an evaluative conclusion. It does not require `attacks_person` and it does not loosen ad hominem.

Each new pilot has an `ir_forbid` for the catalog look-alikes: a uniform population, a cautious or low-stakes generalization, or a selection-not-size doubt; a causal chain whose links are each given a mechanism, or line-drawing with no prediction; options that are not claimed to be the only ones, or a true dichotomy; expert agreement, a question about taste or popularity itself, popularity as one piece among others, or a non-decisive hedge; association offered only as disclosure or caution, or merits that are actually engaged. A slippery chain with no stated leap is at most possible issue (catalog outside-text condition on whether each later step is likely). A “probably” hedge does not fill that gap. Hedge, `default_rule`, and precautionary mappings stay as in the extractor prompt.

## Development process

The loop is design note, refine from a run, implement pilots and forbids, fixture tests, held-out scoring, miss taxonomy, then the next pilot. Full steps, the charity forbids that stay in place, and the rules for adding a pilot: [`idea_detection/DEV_PROCESS.md`](idea_detection/DEV_PROCESS.md).

Held-out scoring labels are `hit`, `fp`, `clean`, `partial`, `wrong_possible`, `expected_outside`, `expected_charity`, `ir_gap`, `pattern_gap`, `contested_stay`, and `inside_miss` (an inside miss that still needs `ir_gap` or `pattern_gap`). A wrong-label `possible_issue` is `wrong_possible`, not a hit. Genetic fallacy, bulverism, ad hoc rescue, and special pleading count as inside a pilot only when that id is itself a pilot. Guilt by association is a pilot, so its own name counts; it does not count as ad hominem. Details and the eight-pilot N=398 numbers: [`idea_detection/E2E_SUMMARY.md`](idea_detection/E2E_SUMMARY.md).

```
python3 -m idea_detection.score_eval idea_detection/examples/score_eval_example.csv
```

[METHOD.md](METHOD.md) stays the procedure for hand audits, including Genius Study audits. This layer does not rewrite it.

## Run the fixture eval

From the repository root:

```
python3 -m idea_detection.eval_fixtures
```

```
python3 -m unittest tests/idea_detection/test_checker.py
```

```
python3 -m unittest tests/idea_detection/test_score_eval.py
```

Check one IR file:

```
python3 -m idea_detection idea_detection/fixtures/method_ex1_ad_hominem.json
```

METHOD example 1 flags `ad-hominem`. METHOD example 2 is `no_issue` on `appeal-to-authority` (the illegitimacy condition is not met, and the expert-agreement look-alike matches).

Design, schema, and the extractor contract: [`idea_detection/IDEA_LEVEL_DETECTION.md`](idea_detection/IDEA_LEVEL_DETECTION.md), [`idea_detection/idea_ir.schema.json`](idea_detection/idea_ir.schema.json), [`idea_detection/EXTRACTOR_PROMPT.md`](idea_detection/EXTRACTOR_PROMPT.md).

## Bulk METHOD records

The short checker report is a verdict and a reason. A METHOD record is the audit shape in [METHOD.md](METHOD.md): the passage quote, the catalog entry name and id, each required condition, each legitimate look-alike, and the verdict. [`idea_detection/record.py`](idea_detection/record.py) renders that shape from checker rows plus `fallacies.json`. It does not rewrite METHOD, and it is not a hand review.

Every record is labeled **idea_detection assist / lead-to-check**. A "met by" quote is copied only from a closed span the checker bound for a span name declared for that condition. If a condition has no declared span, or the span is an outside-text gap, the line says so and attaches no satisfying quote. When the verdict is flag, look-alikes that have a paired `ir_forbid` atom are reported as checked with none matched. The renderer does not write a separate prose reason for each look-alike. METHOD example 2 stays `no_issue` and is not emitted as a flag.

From the repository root, one IR, a list, or a folder of IR JSON files:

```
python3 -m idea_detection --method-record idea_detection/fixtures/method_ex1_ad_hominem.json
```

```
python3 -m idea_detection --method-record path/to/irs/
```

```
python3 -m idea_detection --method-record --method-format jsonl path/to/irs/
```

A saved checker report (`python3 -m idea_detection --json`) can be rendered the same way. Pass `--ir` when the report has no `source_text`:

```
python3 -m idea_detection.record --json report.json --ir path/to/irs/
```

`--verdicts flag,possible_issue` is the default. `no_issue` adds rows the checker blocked with `ir_forbid` or a fallback. Rows whose pattern simply did not match stay out.

## Nested layers

A folder of excerpt IRs can come back as possible issue only, because the flat checker will not treat outside-text gaps as flags. The nested pass peels premises, citations, and sub-claims and re-checks text a client supplies (a snapshot window or a child IR). It does not fetch a corpus and it does not loosen the flat gates. Depth is unlimited unless `--max-depth` is set. Records from that pass carry a layer path (`L0→L1→…`).

```
python3 -m idea_detection.nested --context-map path/to/contexts.jsonl path/to/irs/
```

Design: [`idea_detection/NESTED_LAYERS.md`](idea_detection/NESTED_LAYERS.md).
