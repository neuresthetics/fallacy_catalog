"""Run the METHOD Idea IR fixtures through the deterministic checker.

From the repository root:

    python3 -m idea_detection.eval_fixtures
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from idea_detection.check import check_passage, result_for

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def evaluate_file(path: Path) -> tuple:
    raw = json.loads(path.read_text(encoding="utf-8"))
    expected = raw.get("expected_checker") or {}
    report = check_passage(raw)
    entry_id = expected.get("entry_id")
    want = expected.get("verdict")
    if not report.get("ok"):
        return False, f"{path.name}: invalid IR: {report.get('errors')}"
    got = result_for(report, entry_id) if entry_id else None
    if got is None:
        return False, f"{path.name}: no result for {entry_id}"
    flags = [row["entry_id"] for row in report["results"] if row["verdict"] == "flag"]
    problems = []
    if got["verdict"] != want:
        problems.append(
            f"{path.name}: {entry_id} verdict {got['verdict']!r} != {want!r} ({got['reason']})"
        )
    if want == "flag":
        others = [item for item in flags if item != entry_id]
        if others:
            problems.append(f"{path.name}: unexpected flags {others}")
        if not got["span_bindings"]:
            problems.append(f"{path.name}: flag has no quote bindings")
    elif flags:
        problems.append(f"{path.name}: expected no flags, got {flags}")
    if problems:
        return False, "\n".join(problems)
    return True, f"{path.name}: {entry_id} {got['verdict']}"


def main() -> int:
    paths = sorted(FIXTURES.glob("*.json"))
    if not paths:
        print("no fixtures found", file=sys.stderr)
        return 1
    failed = False
    for path in paths:
        ok, line = evaluate_file(path)
        print(("ok  " if ok else "FAIL ") + line)
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
