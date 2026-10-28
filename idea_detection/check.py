"""Deterministic idea-level checker.

An extractor may propose an Idea IR. This module alone emits flag,
possible_issue, or no_issue. It matches pilot ir_pattern atoms only when each
atom binds a quote from the passage, blocks on ir_forbid, and applies the
catalog's text_detectable / outside-text gates. It does not name new fallacies.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

from idea_detection.ir import normalize, validate
from idea_detection.match import closed_forbid, pattern_status, structural_envs
from idea_detection.model import CAUSAL_FAMILIES, Ctx, IndexedIR

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "fallacies.json"
PATTERNS_PATH = Path(__file__).resolve().parent / "pilot_ir_patterns.json"


def load_catalog(path: Path = CATALOG_PATH) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in doc["entries"]}


def load_patterns(path: Path = PATTERNS_PATH) -> list:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return list(doc["entries"])


def check_passage(raw: dict, *, catalog: dict | None = None, patterns: list | None = None) -> dict:
    data = deepcopy(raw)
    errors = validate(data)
    passage_id = data.get("passage_id") if isinstance(data, dict) else None
    if errors:
        return {"passage_id": passage_id, "ok": False, "errors": errors, "results": []}
    data.pop("expected_checker", None)
    if catalog is None:
        catalog = load_catalog()
    if patterns is None:
        patterns = load_patterns()
    unknown = [p.get("id") for p in patterns if p.get("id") not in catalog]
    if unknown:
        return {
            "passage_id": passage_id,
            "ok": False,
            "errors": [f"pattern id not in catalog: {item}" for item in unknown],
            "results": [],
        }
    normalized = normalize(data)
    ir = IndexedIR.from_data(normalized)
    if _no_argument(ir):
        results = [
            _row(p["id"], "no_issue", "no argument (report, lesson, or no participant advancing a claim)", [], None)
            for p in patterns
        ]
        return {"passage_id": passage_id, "ok": True, "errors": [], "results": results}

    non_fallback = []
    fallback = []
    for pattern in patterns:
        if catalog[pattern["id"]].get("use_only_if_nothing_more_specific"):
            fallback.append(pattern)
        else:
            non_fallback.append(pattern)

    results = [judge(ir, pattern, catalog[pattern["id"]], ()) for pattern in non_fallback]
    causal_hits = tuple(
        row["entry_id"] for row in results
        if row["verdict"] == "flag" and _families(catalog[row["entry_id"]]) & CAUSAL_FAMILIES
    )
    results.extend(judge(ir, pattern, catalog[pattern["id"]], causal_hits) for pattern in fallback)
    _apply_fallback(results, catalog)
    _apply_family_ties(results, catalog)
    order = {pattern["id"]: index for index, pattern in enumerate(patterns)}
    results.sort(key=lambda row: order.get(row["entry_id"], 10**6))
    return {"passage_id": passage_id, "ok": True, "errors": [], "results": results}


def judge(ir: IndexedIR, pattern: dict, catalog_entry: dict, causal_specific) -> dict:
    outside = frozenset(pattern.get("outside_text_predicates") or [])
    ctx = Ctx(
        ir=ir,
        entry=pattern,
        catalog_entry=catalog_entry,
        mode="full",
        outside=outside,
        causal_specific=tuple(causal_specific),
    )
    tree = pattern.get("ir_pattern")
    closed, opened = pattern_status(tree, ctx)
    bases = structural_envs(tree, ctx) or [None]
    forbid_labels = []
    for base in bases:
        if base is None:
            continue
        labels = closed_forbid(pattern.get("ir_forbid"), ctx, base)
        if labels:
            forbid_labels = labels
            break

    def blocked(env):
        return bool(closed_forbid(pattern.get("ir_forbid"), ctx, env))

    good_closed = [env for env in closed if not blocked(env)]
    good_open = [env for env in opened if not blocked(env)]

    if good_closed:
        env = good_closed[0]
        verdict, reason, spans, missing = _accept(ir, pattern, env, "flag")
    elif forbid_labels or (closed and not good_closed):
        # A look-alike the passage actually supplies beats an outside-text gap.
        verdict = "no_issue"
        reason = "no issue; ir_forbid matched: " + ", ".join(forbid_labels or ["look-alike"])
        spans, missing = [], None
    elif good_open:
        env = good_open[0]
        verdict, reason, spans, missing = _accept(ir, pattern, env, "possible_issue")
    else:
        verdict = "no_issue"
        reason = "no issue; ir_pattern did not match"
        spans, missing = [], None

    verdict, reason, missing = _gates(ir, catalog_entry, verdict, reason, missing)
    return _row(pattern["id"], verdict, reason, spans, missing)


def _accept(ir, pattern, env, verdict):
    spans = [span for span in env.atom_spans if span.get("quote") and ir.quote_ok({"quote": span["quote"]})]
    if verdict == "flag":
        if not spans or len(spans) != len(env.atom_spans):
            return "no_issue", "no issue; pattern match lacked in-text quote spans", [], None
        if "unanswered_reasons" in (pattern.get("support_must_be_absent") or []):
            if not any(span.get("name") == "reasons_unanswered" for span in spans):
                return "no_issue", "no issue; required unanswered reasons were not shown", [], None
        if pattern.get("term_identity_required") and not any(span.get("name") == "sense_shift" for span in spans):
            return "no_issue", "no issue; term identity shift was not shown", [], None
        missing = "; ".join(env.missing_facts) or None
        return "flag", "flag; ir_pattern matched with in-text quote spans; no ir_forbid matched", spans, missing
    missing = "; ".join(env.missing_facts) or "an outside-text condition"
    reason = f"possible issue; missing fact: {missing}"
    return "possible_issue", reason, spans, missing


def _gates(ir, catalog_entry, verdict, reason, missing):
    if catalog_entry.get("text_detectable") == "no":
        if verdict == "flag":
            return (
                "possible_issue",
                "possible issue; text_detectable no — question only, never a flag",
                missing or "motive or inner bias, which this catalog does not flag",
            )
        if verdict == "possible_issue":
            return (
                "possible_issue",
                "possible issue; text_detectable no — question only, never a flag",
                missing,
            )
        return verdict, reason, missing
    if verdict == "flag" and ir.excerpt:
        return (
            "possible_issue",
            "possible issue; excerpt boundary — support may lie outside the passage",
            "whether the full text supplies the unmet support",
        )
    if verdict == "flag" and ir.contested_reading:
        return (
            "possible_issue",
            f"possible issue; contested reading: {ir.contested_reading}",
            ir.contested_reading,
        )
    return verdict, reason, missing


def _apply_fallback(results, catalog):
    flags = [row for row in results if row["verdict"] == "flag"]
    for row in list(flags):
        entry = catalog[row["entry_id"]]
        if not entry.get("use_only_if_nothing_more_specific"):
            continue
        fam = _families(entry)
        specific = [
            other["entry_id"] for other in flags
            if other["entry_id"] != row["entry_id"]
            and not catalog[other["entry_id"]].get("use_only_if_nothing_more_specific")
            and _families(catalog[other["entry_id"]]) & fam
        ]
        if specific:
            row["verdict"] = "no_issue"
            row["reason"] = "no issue; fallback suppressed; more specific family entry matched: " + ", ".join(specific)
            row["span_bindings"] = []
            row["missing_fact"] = None


def _apply_family_ties(results, catalog):
    flags = [row for row in results if row["verdict"] == "flag"]
    parent = {row["entry_id"]: row["entry_id"] for row in flags}

    def find(entry_id):
        while parent[entry_id] != entry_id:
            parent[entry_id] = parent[parent[entry_id]]
            entry_id = parent[entry_id]
        return entry_id

    for index, left in enumerate(flags):
        for right in flags[index + 1:]:
            if _families(catalog[left["entry_id"]]) & _families(catalog[right["entry_id"]]):
                parent[find(right["entry_id"])] = find(left["entry_id"])
    groups = {}
    for row in flags:
        groups.setdefault(find(row["entry_id"]), []).append(row)
    for group in groups.values():
        if len(group) < 2:
            continue
        names = sorted(row["entry_id"] for row in group)
        note = "same-family tie; label disputed among " + ", ".join(names)
        for row in group:
            row["verdict"] = "possible_issue"
            row["reason"] = "possible issue; " + note
            row["missing_fact"] = note


def _families(entry) -> set:
    return set(entry.get("families") or [])


def _no_argument(ir: IndexedIR) -> bool:
    return bool(ir.steps) and all(step.get("no_argument") for step in ir.steps)


def _row(entry_id, verdict, reason, spans, missing):
    return {
        "entry_id": entry_id,
        "verdict": verdict,
        "reason": reason,
        "span_bindings": spans,
        "missing_fact": missing,
    }


def result_for(report: dict, entry_id: str):
    for row in report.get("results") or []:
        if row["entry_id"] == entry_id:
            return row
    return None


def format_report(report: dict) -> str:
    lines = [report.get("passage_id") or "(no passage_id)"]
    if not report.get("ok"):
        for error in report.get("errors") or []:
            lines.append(f"  error: {error}")
        return "\n".join(lines)
    for row in report["results"]:
        if row["verdict"] == "no_issue" and "did not match" in row["reason"]:
            continue
        lines.append(f"  {row['entry_id']}: {row['verdict']} — {row['reason']}")
        for span in row.get("span_bindings") or []:
            label = span.get("name") or span.get("atom")
            lines.append(f"    {label}: \"{span.get('quote')}\"")
    if len(lines) == 1:
        lines.append("  no pilot entry matched")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check an Idea IR against pilot fallacy patterns.")
    parser.add_argument(
        "paths",
        nargs="+",
        help="Idea IR JSON files. With --method-record, a directory of *.json is also accepted.",
    )
    parser.add_argument("--json", action="store_true", help="Print the raw report as JSON")
    parser.add_argument(
        "--method-record",
        action="store_true",
        help="Emit METHOD-shaped records for flag and possible_issue rows (idea_detection assist)",
    )
    parser.add_argument(
        "--method-format",
        choices=("markdown", "jsonl"),
        default="markdown",
        help="With --method-record, markdown (default) or JSONL. --json forces JSONL.",
    )
    parser.add_argument(
        "--verdicts",
        default="flag,possible_issue",
        help="With --method-record: flag, possible_issue, no_issue (comma-separated)",
    )
    args = parser.parse_args(argv)
    if args.method_record:
        from idea_detection.record import emit_method_stdout, iter_ir_paths, parse_verdicts
        try:
            verdicts = parse_verdicts(args.verdicts)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        catalog = load_catalog()
        patterns = load_patterns()
        ir_paths = iter_ir_paths(args.paths)
        if not ir_paths:
            print("no Idea IR JSON files found", file=sys.stderr)
            return 2
        passages = []
        exit_code = 0
        for path in ir_paths:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"{path}: {exc}", file=sys.stderr)
                exit_code = 1
                continue
            report = check_passage(data, catalog=catalog, patterns=patterns)
            if not report["ok"]:
                exit_code = 1
                print(f"{path}: {report.get('errors')}", file=sys.stderr)
            passages.append((str(path), data, report))
        fmt = "jsonl" if args.json else args.method_format
        rendered = emit_method_stdout(
            passages, fmt=fmt, verdicts=verdicts, catalog=catalog, patterns=patterns,
        )
        return 1 if exit_code or rendered else 0

    exit_code = 0
    reports = []
    for raw_path in args.paths:
        path = Path(raw_path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"{raw_path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        report = check_passage(data)
        reports.append(report)
        if not report["ok"]:
            exit_code = 1
        if not args.json:
            print(format_report(report))
    if args.json:
        json.dump(reports if len(reports) != 1 else reports[0], sys.stdout, indent=2)
        sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
