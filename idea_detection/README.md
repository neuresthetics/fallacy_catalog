# idea_detection

Deterministic checker over an Idea IR. Read [IDEA_DETECTION.md](../IDEA_DETECTION.md) for the contract, [IDEA_LEVEL_DETECTION.md](IDEA_LEVEL_DETECTION.md) for the design, and [DEV_PROCESS.md](DEV_PROCESS.md) for how a change is designed, tested, and scored.

```
python3 -m idea_detection.eval_fixtures
python3 -m unittest tests/idea_detection/test_checker.py
python3 -m unittest tests/idea_detection/test_method_record.py
python3 -m unittest tests/idea_detection/test_score_eval.py
python3 -m idea_detection idea_detection/fixtures/method_ex1_ad_hominem.json
python3 -m idea_detection --method-record idea_detection/fixtures/
python3 -m idea_detection.score_eval idea_detection/examples/score_eval_example.csv
```

Run those from the repository root. The checker strips `expected_checker` (fixture metadata) and never treats it as a verdict. Pilot `ir_pattern` / `ir_forbid` values are a side file; do not bulk-merge them into `fallacies.json` from this package.

`--method-record` prints METHOD-shaped records (passage, entry, conditions, look-alikes, verdict) for flag and possible-issue rows. It is an assist: a condition quote is a closed checker span, or the line says the condition is not span-mapped. `--method-format jsonl` emits one JSON object per record. A folder argument reads `*.json` in that directory. METHOD example 2 produces no flag record.
