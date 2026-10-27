# idea_detection

Deterministic checker over an Idea IR. Read [IDEA_DETECTION.md](../IDEA_DETECTION.md) for the contract and [IDEA_LEVEL_DETECTION.md](IDEA_LEVEL_DETECTION.md) for the design.

```
python3 -m idea_detection.eval_fixtures
python3 -m unittest tests/idea_detection/test_checker.py
python3 -m idea_detection idea_detection/fixtures/method_ex1_ad_hominem.json
```

Run those from the repository root. The checker strips `expected_checker` (fixture metadata) and never treats it as a verdict. Pilot `ir_pattern` / `ir_forbid` values are a side file; do not bulk-merge them into `fallacies.json` from this package.
