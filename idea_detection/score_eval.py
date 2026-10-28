"""Score idea-detection results against a gold key.

The checker is unchanged. This module only labels a results row. It does not
weaken forbids, and it does not treat a cousin fallacy as coverage for a
different pilot.

From the repository root:

    python3 -m idea_detection.score_eval idea_detection/examples/score_eval_example.csv

A results CSV uses these columns (header names are flexible; see COLUMN_ALIASES):

    id, truth, acceptable, flagged, possible, miss_class

`flagged` and `possible` are catalog ids separated by `|`, `;`, or `,`.
`miss_class` is optional and is used only when the row is not a hit, false
positive, clean, partial, or wrong label. Allowed values: expected_outside,
expected_charity, ir_gap, pattern_gap, contested_stay.

Labels
------
hit
    A flag's name meets the acceptable list. A legit or no-argument row is
    never a hit.
fp
    A flag on legit or no-argument. This is the gate metric.
wrong_flag
    A flag on a fallacy-like row whose name is not acceptable. Not a hit.
wrong_possible
    No flag, and every possible_issue name misses the acceptable list.
partial
    No flag, and a possible_issue name is acceptable.
clean
    Legit or no-argument, and no flag. A possible_issue does not flip the gate.
extractor_fail
    The row says the IR or checker failed.
expected_outside
    No flag worth a hit, and no acceptable name is an active pilot.
expected_charity
    Inside an active pilot, truth is borderline, and nothing was flagged.
    Automatic. Override with miss_class when the IR shows a different gap.
contested_stay
    Truth is contested (METHOD contested-reading cap).
ir_gap, pattern_gap
    Not inferred. Set miss_class after reading the IR.
inside_miss
    Inside an active pilot, unflagged, and not yet given a miss_class.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from idea_detection.check import load_catalog, load_patterns

# Separate catalog entries. A key names one of these only when that id is
# itself an active pilot. They are never copied onto ad hominem or ignorance.
COUSIN_IDS = (
    "guilt-by-association",
    "genetic-fallacy",
    "bulverism",
    "ad-hoc-rescue",
    "special-pleading",
)

# false-cause is the catalog fallback. Held-out keys name these specifics.
FALSE_CAUSE_SPECIFIC_IDS = ("cum-hoc", "post-hoc")

# Key phrasing that is the same pilot, and is not a catalog alias string.
EXTRA_CORE_PHRASES = {
    "appeal-to-authority": (
        "appeal to inappropriate authority",
        "inappropriate authority",
    ),
    "cherry-picking": ("selective evidence",),
}

TAXONOMY = (
    "expected_outside",
    "expected_charity",
    "ir_gap",
    "pattern_gap",
    "contested_stay",
)

LABELS = (
    "hit",
    "fp",
    "wrong_flag",
    "wrong_possible",
    "partial",
    "clean",
    "extractor_fail",
    *TAXONOMY,
    "inside_miss",
)

LEGIT_TRUTHS = {"legit", "no-argument"}

COLUMN_ALIASES = {
    "id": ("id", "passage_id"),
    "truth": ("truth", "ground_truth"),
    "acceptable": (
        "acceptable",
        "accept",
        "acceptable_fallacy_names",
        "key",
        "intended_entry_or_lookalike",
    ),
    "flagged": ("flagged", "flags", "flag", "flagged_ids"),
    "possible": ("possible", "possible_issue", "possible_issues"),
    "ok": ("ok", "checker_ok"),
    "miss_class": ("miss_class", "taxonomy"),
    "set": ("set", "source_set"),
}

_EMPTY = {"", "—", "-", "–", "n/a", "na", "none", "no flag"}
_NAME_SPLIT = re.compile(r"\s*(?:;|\||\n)\s*|\s+/\s+")
_FLAG_SPLIT = re.compile(r"\s*(?:;|\||,)\s*")


def norm_label(text: str) -> str:
    """Lowercase label with parentheticals and punctuation removed."""
    raw = text or ""
    raw = raw.replace("—", " ").replace("–", " ")
    raw = re.sub(r"\([^)]*\)", " ", raw)
    raw = raw.lower()
    raw = re.sub(r"[^a-z0-9]+", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def phrases_match(left: str, right: str) -> bool:
    """True when two normalized labels are the same name, or one contains the other.

    The shorter side must be at least two words so a one-word alias such as
    "smear" or "opposition" does not match inside an unrelated name.
    """
    if not left or not right:
        return False
    if left == right:
        return True
    short, long = (left, right) if len(left) <= len(right) else (right, left)
    if len(short.split()) < 2 or len(short) < 8:
        return False
    return f" {short} " in f" {long} "


def split_names(text: str) -> list:
    raw = str(text or "").strip()
    if raw.lower() in _EMPTY:
        return []
    return [part.strip() for part in _NAME_SPLIT.split(raw) if part.strip()]


def split_flags(text: str) -> list:
    raw = str(text or "").strip()
    if raw.lower() in _EMPTY:
        return []
    found = []
    for part in _FLAG_SPLIT.split(raw):
        part = part.strip()
        if part and part.lower() not in _EMPTY:
            found.append(part)
    return found


def norm_truth(value: str) -> str:
    text = norm_label(value).replace(" ", "-")
    if text in {"no-arg", "non-argument", "noargument"}:
        return "no-argument"
    if text == "legitimate":
        return "legit"
    return text


def _phrases_for_entry(entry: dict) -> set:
    found = set()
    raws = [entry.get("name") or ""]
    raws.extend(entry.get("aliases") or [])
    raws.append((entry.get("id") or "").replace("-", " "))
    for raw in raws:
        phrase = norm_label(raw)
        if phrase:
            found.add(phrase)
    return found


def _cousin_phrases(catalog: dict) -> dict:
    owned = {}
    for entry_id in COUSIN_IDS:
        entry = catalog.get(entry_id)
        if entry:
            owned[entry_id] = _phrases_for_entry(entry)
    return owned


def build_alias_index(catalog: dict, active_ids) -> dict:
    """Map each active pilot id to the names that count as that pilot.

    Cousin names are removed from every other pilot. Guilt by association
    counts only when `guilt-by-association` is in `active_ids`.
    """
    active = [entry_id for entry_id in active_ids if entry_id in catalog]
    blocked_for = {}
    cousins = _cousin_phrases(catalog)
    for pilot_id in active:
        blocked = set()
        for cousin_id, phrases in cousins.items():
            if cousin_id != pilot_id:
                blocked |= phrases
        blocked_for[pilot_id] = blocked

    index = {}
    for pilot_id in active:
        phrases = set(_phrases_for_entry(catalog[pilot_id]))
        for extra in EXTRA_CORE_PHRASES.get(pilot_id, ()):
            phrase = norm_label(extra)
            if phrase:
                phrases.add(phrase)
        if pilot_id == "false-cause":
            for specific_id in FALSE_CAUSE_SPECIFIC_IDS:
                specific = catalog.get(specific_id)
                if specific:
                    phrases |= _phrases_for_entry(specific)
        phrases -= blocked_for[pilot_id]
        index[pilot_id] = phrases
    return index


def pilots_for_acceptable(acceptable: str, index: dict) -> list:
    """Active pilots named by the gold list, in index order."""
    found = []
    segments = [norm_label(part) for part in split_names(acceptable)]
    segments = [part for part in segments if part]
    for pilot_id, phrases in index.items():
        if any(phrases_match(segment, phrase) for segment in segments for phrase in phrases):
            found.append(pilot_id)
    return found


def _phrases_named_by_token(token: str, index: dict, catalog: dict) -> set:
    normalized = norm_label(token)
    raw_id = normalized.replace(" ", "-")
    phrases = set()
    named = False
    for pilot_id, pilot_phrases in index.items():
        if (
            raw_id == pilot_id
            or normalized == norm_label(pilot_id.replace("-", " "))
            or any(phrases_match(normalized, phrase) for phrase in pilot_phrases)
        ):
            phrases |= pilot_phrases
            named = True
    if raw_id in catalog and raw_id not in index:
        phrases |= _phrases_for_entry(catalog[raw_id])
        named = True
    if not named and normalized:
        phrases.add(normalized)
    return phrases


def flag_hits_acceptable(token: str, acceptable: str, index: dict, catalog: dict) -> bool:
    segments = [norm_label(part) for part in split_names(acceptable)]
    segments = [part for part in segments if part]
    phrases = _phrases_named_by_token(token, index, catalog)
    return any(phrases_match(segment, phrase) for segment in segments for phrase in phrases)


def _as_bool(value, default=True) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in {"0", "false", "no", "fail", "failed"}


def _cell(row: dict, key: str, default=""):
    wanted = COLUMN_ALIASES[key]
    lowered = {str(name).strip().lower(): value for name, value in row.items() if name}
    for name in wanted:
        if name in row and row[name] not in (None,):
            return row[name]
        if name in lowered and lowered[name] not in (None,):
            return lowered[name]
    return default


def score_row(row: dict, *, catalog: dict, active_ids, index: dict | None = None) -> dict:
    """Label one gold-versus-check row.

    `row` accepts the CSV columns above, or a check report under `report`
    (the dict returned by `check_passage`). An explicit `flagged` / `possible`
    wins over `report` when both are set.
    """
    if index is None:
        index = build_alias_index(catalog, active_ids)
    passage_id = str(_cell(row, "id", "") or "").strip()
    truth = norm_truth(str(_cell(row, "truth", "") or ""))
    acceptable = str(_cell(row, "acceptable", "") or "")
    miss_class = norm_label(str(_cell(row, "miss_class", "") or "")).replace(" ", "_")
    if miss_class in {"", "none"}:
        miss_class = ""
    elif miss_class not in TAXONOMY:
        raise ValueError(
            f"{passage_id or '(no id)'}: miss_class {miss_class!r} is not one of {', '.join(TAXONOMY)}"
        )

    if not _as_bool(_cell(row, "ok", True)):
        return _result(passage_id, truth, "extractor_fail", [], [], [], miss_class, _cell(row, "set", ""))

    flagged = split_flags(_cell(row, "flagged", ""))
    possible = split_flags(_cell(row, "possible", ""))
    report = row.get("report")
    if report is not None and not flagged and not possible and _cell(row, "flagged", None) is None:
        if not report.get("ok", True):
            return _result(passage_id, truth, "extractor_fail", [], [], [], miss_class, _cell(row, "set", ""))
        flagged = [item["entry_id"] for item in report.get("results") or [] if item.get("verdict") == "flag"]
        possible = [
            item["entry_id"] for item in report.get("results") or [] if item.get("verdict") == "possible_issue"
        ]

    inside = pilots_for_acceptable(acceptable, index)
    matching_flags = [
        token for token in flagged if flag_hits_acceptable(token, acceptable, index, catalog)
    ]
    matching_possible = [
        token for token in possible if flag_hits_acceptable(token, acceptable, index, catalog)
    ]

    if flagged and truth in LEGIT_TRUTHS:
        label = "fp"
    elif matching_flags:
        label = "hit"
    elif flagged:
        label = "wrong_flag"
    elif truth in LEGIT_TRUTHS:
        label = "clean"
    elif possible and not matching_possible:
        label = "wrong_possible"
    elif matching_possible:
        label = "partial"
    elif miss_class:
        label = miss_class
    elif truth == "contested":
        label = "contested_stay"
    elif not inside:
        label = "expected_outside"
    elif truth == "borderline":
        label = "expected_charity"
    else:
        label = "inside_miss"

    return _result(passage_id, truth, label, inside, flagged, possible, miss_class, _cell(row, "set", ""))


def _result(passage_id, truth, label, inside, flagged, possible, miss_class, source_set) -> dict:
    return {
        "id": passage_id,
        "truth": truth,
        "label": label,
        "inside_pilots": list(inside),
        "flagged": list(flagged),
        "possible": list(possible),
        "miss_class": miss_class or "",
        "set": str(source_set or ""),
    }


def score_report(report: dict, *, truth: str, acceptable: str, catalog: dict, active_ids, miss_class: str = "", passage_id: str = "") -> dict:
    """Score one `check_passage` report against a gold key."""
    row = {
        "id": passage_id or report.get("passage_id") or "",
        "truth": truth,
        "acceptable": acceptable,
        "miss_class": miss_class,
        "report": report,
        "ok": report.get("ok", True),
    }
    return score_row(row, catalog=catalog, active_ids=active_ids)


def load_results_csv(path) -> list:
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def score_rows(rows, *, catalog=None, active_ids=None) -> list:
    if catalog is None:
        catalog = load_catalog()
    if active_ids is None:
        active_ids = [entry["id"] for entry in load_patterns()]
    index = build_alias_index(catalog, active_ids)
    return [score_row(row, catalog=catalog, active_ids=active_ids, index=index) for row in rows]


def summarize(scored: list) -> dict:
    counts = {label: 0 for label in LABELS}
    by_set = {}
    for row in scored:
        label = row["label"]
        counts[label] = counts.get(label, 0) + 1
        source_set = row.get("set") or ""
        if source_set:
            bucket = by_set.setdefault(source_set, {name: 0 for name in LABELS})
            bucket[label] = bucket.get(label, 0) + 1
    return {"n": len(scored), "counts": counts, "by_set": by_set}


def format_summary(summary: dict) -> str:
    lines = [f"n={summary['n']}"]
    for label in LABELS:
        lines.append(f"{label}={summary['counts'].get(label, 0)}")
    if summary.get("by_set"):
        lines.append("by_set")
        for name in sorted(summary["by_set"]):
            bucket = summary["by_set"][name]
            parts = [f"{label}={bucket.get(label, 0)}" for label in LABELS if bucket.get(label, 0)]
            lines.append(f"  {name}: " + ", ".join(parts))
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Score idea-detection results against a gold key.")
    parser.add_argument("csv_path", help="Results CSV (id, truth, acceptable, flagged, possible, miss_class)")
    parser.add_argument("--json", action="store_true", help="Print scored rows as JSON")
    parser.add_argument("--pilots", help="Comma-separated active pilot ids (default: the side file)")
    args = parser.parse_args(argv)
    path = Path(args.csv_path)
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 1
    try:
        catalog = load_catalog()
        if args.pilots:
            active_ids = [part.strip() for part in args.pilots.split(",") if part.strip()]
        else:
            active_ids = [entry["id"] for entry in load_patterns()]
        scored = score_rows(load_results_csv(path), catalog=catalog, active_ids=active_ids)
    except (OSError, csv.Error, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json:
        json.dump(scored, sys.stdout, indent=2)
        sys.stdout.write("\n")
    print(format_summary(summarize(scored)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
