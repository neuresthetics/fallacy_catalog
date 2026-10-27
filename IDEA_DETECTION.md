# Idea-level detection

Fallacy labels in this repository are decided from **claim and support structure**, not from sentence cadence. The catalog (`fallacies.json`) stays the source of truth. This layer makes [METHOD.md](METHOD.md)'s false-positive rules machine-checkable for a pilot set of entries. It does not replace METHOD.

## Who verdicts

| Role | May do | Must not do |
|---|---|---|
| **Extractor** (model or human) | Propose an Idea IR: steps, claims, edges, spans, under METHOD charity | Emit a fallacy id or verdict the pipeline treats as final |
| **Normalizer** | Downgrade hedges from the quoted words; mark burden/null language as procedural; drop illustration-only `supports` edges | Invent contrary evidence |
| **Checker** | Match `ir_pattern`, block on `ir_forbid`, apply outside-text and `text_detectable` gates | Trust extractor prose, or flag on an insult or a stock phrase alone |

A **flag** requires every pattern atom to bind a quote from the passage, no forbid to match, and the catalog gates to allow it. `text_detectable: no` (confirmation bias, selective attention, availability heuristic, rationalization) is never a flag. Unmet outside-text conditions are at most **possible issue**. Excerpt boundaries and contested readings cap a match the same way.

Patterns for eight pilot entries live in [`idea_detection/pilot_ir_patterns.json`](idea_detection/pilot_ir_patterns.json). They are not merged into `fallacies.json`. The layer does not add fallacy names and does not use MINDSPACE.

## Run the fixture eval

From the repository root:

```
python3 -m idea_detection.eval_fixtures
```

```
python3 -m unittest tests/idea_detection/test_checker.py
```

Check one IR file:

```
python3 -m idea_detection idea_detection/fixtures/method_ex1_ad_hominem.json
```

METHOD example 1 flags `ad-hominem`. METHOD example 2 is `no_issue` on `appeal-to-authority` (the illegitimacy condition is not met, and the expert-agreement look-alike matches).

Design, schema, and the extractor contract: [`idea_detection/IDEA_LEVEL_DETECTION.md`](idea_detection/IDEA_LEVEL_DETECTION.md), [`idea_detection/idea_ir.schema.json`](idea_detection/idea_ir.schema.json), [`idea_detection/EXTRACTOR_PROMPT.md`](idea_detection/EXTRACTOR_PROMPT.md).
