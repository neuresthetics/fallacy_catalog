"""Render METHOD-shaped records from checker output.

This is an idea_detection assist / lead-to-check. It joins a checker row to
the catalog entry in ``fallacies.json`` and to the pilot pattern's span names.
A quote is copied only from a closed span binding that occurs in the passage.
A catalog condition with no declared span, or only an open outside-text span,
is reported as not shown. Look-alike lines state whether the paired
``ir_forbid`` atom matched. They do not invent a prose reason.

The hand procedure in METHOD.md is unchanged. ``substitute_for_hand_method``
is always false.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from idea_detection.check import check_passage, load_catalog, load_patterns
from idea_detection.match import atom_label
from idea_detection.model import MISSING_FACT, norm

DEFAULT_VERDICTS = ("flag", "possible_issue")

VERDICT_LABEL = {
    "flag": "flag",
    "possible_issue": "possible issue",
    "no_issue": "no issue",
}

# Catalog condition number -> span names the pilot pattern binds for it.
# A missing number is not span-mapped: the renderer attaches no quote.
# "all" names must each be closed. "any" needs one closed alternative.
# Names are the span ``name`` values the checker records (predicate name,
# edge type, ``exists_claim``, or ``exists_agent_trait``).
CONDITION_SPANS = {
    "ad-hominem": {
        1: "exists_claim",
        2: "attacks_person",
        3: ["supports", "reasons_unanswered"],
        4: "trait_irrelevant_to_reasons",
    },
    "appeal-to-authority": {
        1: "appeals_to_source",
        2: {"any": [
            "source_not_expert_on_question",
            "experts_substantially_disagree",
            "source_untrustworthy",
            "source_misquoted",
        ]},
        3: "authority_treated_as_settling",
    },
    "equivocation": {
        1: "term_occurs_at_least",
        2: "sense_shift",
        3: "conclusion_requires_sense_identity",
    },
    "false-cause": {
        1: {"any": ["causes", "exists_claim"]},
        2: ["support_only_correlate_or_sequence", "obvious_alternative_left_open"],
        3: "no_more_specific_causal_entry_matches",
    },
    "begging-the-question": {
        1: "exists_claim",
        2: {"any": ["depends_on_cycle", "premise_asserts_or_presupposes"]},
        3: "not_independently_supported",
    },
    "cherry-picking": {
        1: "selects_subset",
        2: "rest_against_or_dilutes",
        3: ["conclusion_rests_on_subset", "rest_unanswered"],
    },
    "straw-man": {
        1: "exists_claim",
        2: "misattributes",
        3: "attacks_claim",
        4: "presented_as_refuting_actual_position",
    },
    "argument-from-ignorance": {
        1: "exists_claim",
        2: ["supports", "absence_of_proof_used_as_proof"],
        3: "no_thorough_search_shown",
    },
    "hasty-generalization": {
        1: "exists_claim",
        2: "instantiates",
        3: "sample_too_small_for_sweep",
    },
    # Condition 1 (a first step is opposed) has no pattern atom.
    "slippery-slope": {
        2: "causal_chain_to_outcome",
        3: "later_link_unsupported",
    },
    "false-dilemma": {
        1: ["exists_claim", "exclusive_split_claimed"],
        2: "split_not_a_true_dichotomy",
        3: ["supports", "conclusion_relies_on_split"],
    },
    "appeal-to-the-people": {
        1: ["appeals_to_source", "source_is_number_of_people"],
        2: "popularity_treated_as_settling",
        3: "claim_not_about_popularity_itself",
    },
    # Condition 3 (the association does not bear on the claim) is the absence
    # the look-alike forbid checks. No positive span is declared for it.
    "guilt-by-association": {
        1: ["exists_agent_trait", "trait_is_association"],
        2: ["supports", "association_used_as_evaluative_reason"],
    },
}

# Look-alike number -> ir_forbid indexes (0-based) that implement it.
# A look-alike with no entry was not given an ir_forbid atom. The renderer
# does not say the checker ruled it out.
LOOKALIKE_FORBID_INDEX = {
    "ad-hominem": {1: [0], 2: [1], 3: [2]},
    "appeal-to-authority": {1: [0], 2: [1]},
    "equivocation": {1: [0], 2: [1]},
    "false-cause": {1: [0]},
    "begging-the-question": {1: [0], 2: [1], 3: [2]},
    "cherry-picking": {1: [0], 2: [1], 3: [2]},
    "straw-man": {1: [0], 2: [1], 3: [2]},
    "argument-from-ignorance": {1: [0], 2: [1], 3: [2]},
    "hasty-generalization": {1: [0], 2: [1], 4: [2], 5: [3]},
    "slippery-slope": {2: [1], 3: [0]},
    "false-dilemma": {1: [0, 1]},
    "appeal-to-the-people": {1: [0], 2: [1], 3: [2, 3]},
    "guilt-by-association": {1: [2], 2: [3]},
}


def parse_verdicts(text: str) -> tuple:
    found = []
    for part in (text or "").split(","):
        token = part.strip().lower().replace(" ", "_").replace("-", "_")
        if token in ("possible", "possibleissue"):
            token = "possible_issue"
        if token in ("no", "noissue"):
            token = "no_issue"
        if not token:
            continue
        if token not in VERDICT_LABEL:
            raise ValueError(f"unknown verdict {part!r}; use flag, possible_issue, no_issue")
        if token not in found:
            found.append(token)
    if not found:
        raise ValueError("at least one verdict is required")
    return tuple(found)


def render_records(
    report: dict,
    *,
    ir: dict | None = None,
    catalog: dict | None = None,
    patterns: list | None = None,
    verdicts=DEFAULT_VERDICTS,
    source_path: str | None = None,
) -> list:
    """Return METHOD-shaped records for the requested verdicts.

    ``no_issue`` rows whose pattern simply did not match are skipped even
    when ``no_issue`` is requested. Those rows have no spans and no forbid hit.
    """
    if not report or not report.get("ok"):
        return []
    if catalog is None:
        catalog = load_catalog()
    if patterns is None:
        patterns = load_patterns()
    by_pattern = {item.get("id"): item for item in patterns}
    selected = []
    for row in report.get("results") or []:
        if not _emit_row(row, verdicts):
            continue
        selected.append(
            _one_record(
                row,
                report,
                ir=ir,
                catalog=catalog,
                pattern=by_pattern.get(row.get("entry_id")),
                source_path=source_path,
            )
        )
    return selected


def format_method_record(record: dict) -> str:
    lines = [
        "idea_detection assist / lead-to-check",
        _assist_note(record),
    ]
    if record.get("layer_path"):
        lines.append("Layer path: " + str(record["layer_path"]))
    if record.get("peel_path"):
        lines.append("Peel path: " + str(record["peel_path"]))
    lines.append("")
    lines.append(
        f"Passage: {_quoted(record.get('passage') or '')}" if record.get("passage")
        else "Passage: (no passage quote in the IR or in closed span bindings)"
    )
    lines.append("Strongest reading: " + _reading_line(record.get("strongest_reading") or {}))
    lines.append(
        "Entry: {name} ({eid})   Other entries considered: {others}".format(
            name=record.get("entry_name") or "(name not in fallacies.json)",
            eid=record.get("entry_id"),
            others=record.get("other_entries_considered") or "not produced by the checker",
        )
    )
    lines.append("Conditions:")
    for cond in record.get("conditions") or []:
        lines.append(f"  {cond['n']}. {cond['text']} — {cond['note']}")
    if not record.get("conditions"):
        lines.append("  (no catalog conditions; entry id is not in fallacies.json)")
    unassigned = record.get("unassigned_spans") or []
    if unassigned:
        lines.append("Spans not assigned to a catalog condition (not used as met-by):")
        for span in unassigned:
            marker = "open span" if span.get("open") else "closed span"
            lines.append(f"  - {marker} `{span.get('name')}`: {_quoted(span.get('quote') or '')}")
    lines.append("Look-alikes:")
    lines.append(f"  {record.get('lookalikes_note')}")
    for item in record.get("lookalikes") or []:
        lines.append(f"  - {item['text']} — {item['note']}")
    if not record.get("lookalikes"):
        lines.append("  (no legitimate look-alikes on this catalog entry)")
    extra = record.get("unpaired_forbids_note")
    if extra:
        lines.append(f"  {extra}")
    if record.get("contested_reading"):
        lines.append(f"Contested reading: {record['contested_reading']}")
    if record.get("entry_status") == "contested":
        lines.append("Contested entry: yes (catalog status is contested)")
    lines.append(f"Verdict: {_verdict_text(record)}")
    lines.append(f"Checker reason: {record.get('reason') or ''}")
    return "\n".join(lines)


def format_method_records(records: list) -> str:
    return "\n\n".join(format_method_record(record) for record in records)


def empty_notice(verdicts) -> str:
    labels = [VERDICT_LABEL.get(item, item) for item in verdicts]
    if len(labels) == 1:
        shown = f"a {labels[0]}"
    elif len(labels) == 2:
        shown = f"a {labels[0]} or {labels[1]}"
    else:
        shown = ", ".join(labels[:-1]) + f", or {labels[-1]}"
    return (
        f"No record. The checker did not emit {shown} row for this passage. "
        "Pattern misses are not rendered."
    )


def format_passage_section(passage_id: str, records: list, *, source_path: str | None, verdicts) -> str:
    heading = passage_id or "(no passage_id)"
    if source_path:
        heading = f"{heading} ({source_path})"
    lines = [f"## {heading}", ""]
    if records:
        lines.append(format_method_records(records))
    else:
        lines.append(empty_notice(verdicts))
    return "\n".join(lines)


def format_batch(sections: list) -> str:
    body = "\n\n".join(sections)
    return "# METHOD records (idea_detection assist / lead-to-check)\n\n" + body + "\n"


def records_jsonl(records: list) -> str:
    return "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)


def iter_ir_paths(paths) -> list:
    found = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            found.extend(sorted(item for item in path.glob("*.json") if item.is_file()))
        else:
            found.append(path)
    return found


def load_reports(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "results" in data:
        return [data]
    if isinstance(data, dict) and "reports" in data and isinstance(data["reports"], list):
        return data["reports"]
    raise ValueError(f"{path} is not a checker report or a list of reports")


def index_irs(paths) -> dict:
    indexed = {}
    for path in iter_ir_paths(paths):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            indexed[data.get("passage_id")] = data
    return indexed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Render METHOD-shaped records from an Idea IR check or a saved checker report.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Idea IR JSON files, or a directory of them (non-recursive *.json)",
    )
    parser.add_argument(
        "--json",
        metavar="REPORT",
        help="Read a checker report JSON (one object or a list) instead of checking IR files",
    )
    parser.add_argument(
        "--ir",
        action="append",
        default=[],
        help="IR JSON file or directory to join to a --json report by passage_id (repeatable)",
    )
    parser.add_argument("--format", choices=("markdown", "jsonl"), default="markdown")
    parser.add_argument(
        "--verdicts",
        default="flag,possible_issue",
        help="Comma-separated verdicts to render: flag, possible_issue, no_issue",
    )
    parser.add_argument("--out", help="Write the records to this path instead of stdout")
    args = parser.parse_args(argv)
    try:
        verdicts = parse_verdicts(args.verdicts)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    catalog = load_catalog()
    patterns = load_patterns()
    exit_code = 0
    sections = []
    jsonl_rows = []

    if args.json:
        try:
            reports = load_reports(Path(args.json))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"{args.json}: {exc}", file=sys.stderr)
            return 1
        try:
            ir_index = index_irs(args.ir) if args.ir else {}
        except (OSError, json.JSONDecodeError) as exc:
            print(f"IR join failed: {exc}", file=sys.stderr)
            return 1
        if len(reports) == 1 and len(ir_index) == 1 and reports[0].get("passage_id") not in ir_index:
            only = next(iter(ir_index.values()))
            ir_index = {reports[0].get("passage_id"): only}
        for report in reports:
            if not report.get("ok"):
                exit_code = 1
                print(
                    f"{report.get('passage_id') or args.json}: {report.get('errors')}",
                    file=sys.stderr,
                )
            ir = ir_index.get(report.get("passage_id"))
            records = render_records(
                report, ir=ir, catalog=catalog, patterns=patterns, verdicts=verdicts,
                source_path=args.json,
            )
            _collect(report, records, sections, jsonl_rows, verdicts, args.format)
    else:
        ir_paths = iter_ir_paths(args.paths)
        if not ir_paths:
            print("pass Idea IR JSON files, a directory, or --json REPORT", file=sys.stderr)
            return 2
        for path in ir_paths:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"{path}: {exc}", file=sys.stderr)
                exit_code = 1
                continue
            report = check_passage(data, catalog=catalog, patterns=patterns)
            if not report.get("ok"):
                exit_code = 1
                print(f"{path}: {report.get('errors')}", file=sys.stderr)
            records = render_records(
                report, ir=data, catalog=catalog, patterns=patterns, verdicts=verdicts,
                source_path=str(path),
            )
            _collect(report, records, sections, jsonl_rows, verdicts, args.format)

    if args.format == "jsonl":
        text = records_jsonl(jsonl_rows)
    else:
        text = format_batch(sections) if sections else format_batch([])
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return exit_code


def emit_method_stdout(passages, *, fmt: str, verdicts, catalog, patterns) -> int:
    """Render already-loaded ``(source_path, ir, report)`` triples.

    Used by ``python3 -m idea_detection --method-record``.
    """
    exit_code = 0
    sections = []
    jsonl_rows = []
    for source_path, ir, report in passages:
        if not report.get("ok"):
            exit_code = 1
        records = render_records(
            report, ir=ir, catalog=catalog, patterns=patterns, verdicts=verdicts,
            source_path=source_path,
        )
        _collect(report, records, sections, jsonl_rows, verdicts, fmt)
    if fmt == "jsonl":
        sys.stdout.write(records_jsonl(jsonl_rows))
    else:
        sys.stdout.write(format_batch(sections))
    return exit_code


def _collect(report, records, sections, jsonl_rows, verdicts, fmt):
    if fmt == "jsonl":
        jsonl_rows.extend(records)
        if not records:
            print(
                f"{report.get('passage_id') or '(no passage_id)'}: {empty_notice(verdicts)}",
                file=sys.stderr,
            )
        return
    sections.append(
        format_passage_section(
            report.get("passage_id") or "",
            records,
            source_path=None,
            verdicts=verdicts,
        )
    )


def _emit_row(row: dict, verdicts) -> bool:
    verdict = row.get("verdict")
    if verdict not in verdicts:
        return False
    reason = row.get("reason") or ""
    if verdict == "no_issue" and "did not match" in reason:
        return False
    return True


def _assist_note(record: dict) -> str:
    base = (
        "Machine output from the deterministic checker joined to fallacies.json. "
        "Not a hand METHOD record."
    )
    if record.get("spans_support_every_condition"):
        return (
            base + " Every catalog condition below has a closed in-text span the checker bound. "
            "This remains an assist: it does not apply METHOD charity or a second reviewer."
        )
    return (
        base + " Spans cannot support every catalog condition. "
        "Do not use this record as a substitute for a hand METHOD review."
    )


def _reading_line(reading: dict) -> str:
    note = reading.get("note")
    text = reading.get("text") or "not produced by the checker"
    if note:
        return f"{text} ({note})"
    return text


def _verdict_text(record: dict) -> str:
    label = record.get("verdict_label") or record.get("verdict") or ""
    if record.get("verdict") == "possible_issue" and record.get("missing_fact"):
        return f"{label} ({record['missing_fact']})"
    return label


def _quoted(text: str) -> str:
    cleaned = " ".join((text or "").split()).replace('"', "'")
    return f'"{cleaned}"'


def _passage_from_spans(spans) -> tuple:
    quotes = []
    for span in spans:
        if span.get("open") is True:
            continue
        quote = span.get("quote")
        if isinstance(quote, str) and quote.strip() and quote.strip() not in quotes:
            quotes.append(quote.strip())
    if not quotes:
        return "", "missing"
    return " ".join(quotes), "span_bindings"


def _strongest_reading(ir) -> dict:
    if not isinstance(ir, dict):
        return {
            "text": "not produced by the checker",
            "source": "not_produced",
            "note": "no Idea IR was joined to this report",
        }
    claims = ir.get("claims") or []
    premises = [
        claim.get("text") for claim in claims
        if claim.get("role") in ("premise", "recommendation") and claim.get("text")
    ]
    conclusions = [
        claim.get("text") for claim in claims
        if claim.get("role") == "conclusion" and claim.get("text")
    ]
    if not premises and not conclusions:
        return {
            "text": "not produced by the checker",
            "source": "not_produced",
            "note": "IR has no premise or conclusion claim text",
        }
    left = "; ".join(premises) if premises else "(no premise claim text)"
    right = "; ".join(conclusions) if conclusions else "(no conclusion claim text)"
    return {
        "text": f"{left} -> {right}",
        "source": "ir.claim_text",
        "note": "Idea IR claim texts, not a hand METHOD strongest reading",
    }


def _other_entries(report, entry_id) -> str:
    notes = []
    for row in report.get("results") or []:
        if row.get("entry_id") == entry_id:
            continue
        reason = row.get("reason") or ""
        if row.get("verdict") == "no_issue" and "did not match" in reason:
            continue
        notes.append(f"{row.get('entry_id')}: {reason}")
    if not notes:
        return "not produced; no other pilot row carried a match or a forbid hit"
    return "machine rows only, not a hand family review: " + "; ".join(notes)


def _contested(ir, reason: str):
    if isinstance(ir, dict):
        value = ir.get("contested_reading")
        if isinstance(value, str) and value.strip():
            return value.strip()
    marker = "contested reading:"
    if marker in reason:
        return reason.split(marker, 1)[1].strip() or None
    return None


def _pool(spans, source, row) -> list:
    outside = set()
    missing = row.get("missing_fact") or ""
    verdict = row.get("verdict")
    prepared = []
    for index, span in enumerate(spans):
        quote = span.get("quote")
        quote = quote.strip() if isinstance(quote, str) else ""
        in_source = True
        if isinstance(source, str):
            in_source = bool(quote) and norm(quote) in norm(source)
        prepared.append({
            "index": index,
            "name": span.get("name") or span.get("atom") or "",
            "quote": quote,
            "open": _span_open(span, verdict, missing, outside),
            "in_source": in_source,
            "used": False,
        })
    return prepared


def _span_open(span, verdict, missing, outside) -> bool:
    if span.get("open") is True:
        return True
    if span.get("open") is False:
        return False
    if span.get("name") in outside and _legacy_open(span.get("name"), verdict, missing):
        return True
    return False


def _legacy_open(name, verdict, missing) -> bool:
    """Old reports omit ``open``. Do not treat an outside-text gap as met."""
    if verdict == "flag" or not missing or not name:
        return False
    fact = MISSING_FACT.get(name)
    if fact and fact in missing:
        return True
    if missing.strip() == "an outside-text condition":
        return True
    return False


def _conditions(entry, entry_id, pool, row):
    texts = list(entry.get("required_conditions") or [])
    spec_map = CONDITION_SPANS.get(entry_id) or {}
    outside_numbers = set(entry.get("outside_text_conditions") or [])
    conditions = []
    for number, text in enumerate(texts, 1):
        spec = spec_map.get(number)
        if spec is None:
            conditions.append({
                "n": number,
                "text": text,
                "status": "not_span_mapped",
                "met_by": [],
                "spans": [],
                "note": (
                    "not span-mapped. No pilot span is declared for this catalog condition. "
                    "No quote is attached."
                ),
            })
            continue
        taken = _match_spec(spec, pool)
        status = _status(taken)
        outside_note = ""
        if number in outside_numbers and status != "met_by_span":
            outside_note = " Catalog outside_text_conditions includes this condition."
        met_by = [item["quote"] for item in taken["closed"]] if status == "met_by_span" else []
        note = _condition_note(status, taken) + outside_note
        conditions.append({
            "n": number,
            "text": text,
            "status": status,
            "met_by": met_by,
            "spans": taken["closed"] + taken["open"],
            "note": note,
        })
    unassigned = []
    for item in pool:
        if item["used"] or not item["quote"] or not item["in_source"]:
            continue
        unassigned.append({
            "name": item["name"],
            "quote": item["quote"],
            "open": bool(item["open"]),
        })
    return conditions, unassigned


def _status(taken) -> str:
    if taken["closed"] and not taken["open"] and not taken["missing"] and not taken["rejected"]:
        return "met_by_span"
    if taken["open"] and not taken["closed"]:
        return "open_span"
    if taken["closed"] or taken["open"]:
        return "partial"
    return "unbound"


def _condition_note(status, taken) -> str:
    if status == "met_by_span":
        parts = [
            f"{_quoted(item['quote'])} (span `{item['name']}`)"
            for item in taken["closed"]
        ]
        return "met by: " + "; ".join(parts)
    if status == "open_span":
        parts = [
            f"`{item['name']}`: {_quoted(item['quote'])}" if item.get("quote")
            else f"`{item['name']}`"
            for item in taken["open"]
        ]
        shown = "; ".join(parts) if parts else "an open span"
        return (
            "not met from a closed span. "
            f"Open span {shown} is an outside-text gap, not satisfaction. "
            "No quote is treated as meeting this condition."
        )
    if status == "partial":
        bits = []
        for item in taken["closed"]:
            bits.append(f"closed span `{item['name']}`: {_quoted(item['quote'])}")
        for item in taken["open"]:
            bits.append(f"open span `{item['name']}` (not satisfaction)")
        if taken["missing"]:
            bits.append("unbound span names: " + ", ".join(f"`{name}`" for name in taken["missing"]))
        if taken["rejected"]:
            bits.append(
                "dropped span names not in the passage: "
                + ", ".join(f"`{name}`" for name in taken["rejected"])
            )
        return (
            "not fully span-mapped. " + "; ".join(bits) + ". "
            "Do not treat this condition as met."
        )
    missing = taken["missing"] or taken["rejected"]
    if taken["rejected"] and not taken["missing"]:
        names = ", ".join(f"`{name}`" for name in taken["rejected"])
        return (
            f"not span-mapped in this result. Declared span {names} "
            "had a quote that is not in the passage; it is not shown."
        )
    if missing:
        names = ", ".join(f"`{name}`" for name in missing)
        return (
            f"not span-mapped in this result. Declared span {names} was not bound. "
            "No quote is attached."
        )
    return "not span-mapped in this result. No quote is attached."


def _match_spec(spec, pool) -> dict:
    if isinstance(spec, str):
        return _take_name(spec, pool)
    if isinstance(spec, list):
        return _combine([_match_spec(part, pool) for part in spec])
    if isinstance(spec, dict) and "any" in spec:
        return _match_any(spec["any"], pool)
    return {"closed": [], "open": [], "missing": ["unsupported-spec"], "rejected": []}


def _blank():
    return {"closed": [], "open": [], "missing": [], "rejected": []}


def _combine(parts) -> dict:
    merged = _blank()
    for part in parts:
        merged["closed"].extend(part["closed"])
        merged["open"].extend(part["open"])
        merged["missing"].extend(part["missing"])
        merged["rejected"].extend(part["rejected"])
    return merged


def _match_any(alts, pool) -> dict:
    best = None
    best_rank = None
    best_snap = None
    for alt in alts:
        snap = [item["used"] for item in pool]
        taken = _match_spec(alt, pool)
        rank = _any_rank(taken)
        for item, used in zip(pool, snap):
            item["used"] = used
        if best is None or rank > best_rank:
            best = taken
            best_rank = rank
            best_snap = snap
            best_alt = alt
        else:
            continue
    if best is None:
        return {"closed": [], "open": [], "missing": [], "rejected": []}
    # Re-apply the winning alternative so its spans stay consumed.
    for item, used in zip(pool, best_snap):
        item["used"] = used
    return _match_spec(best_alt, pool)


def _any_rank(taken) -> tuple:
    full = bool(taken["closed"]) and not taken["open"] and not taken["missing"] and not taken["rejected"]
    return (1 if full else 0, len(taken["closed"]), len(taken["open"]), -len(taken["missing"]))


def _take_name(name, pool) -> dict:
    candidates = [item for item in pool if not item["used"] and item["name"] == name]
    if not candidates:
        return {"closed": [], "open": [], "missing": [name], "rejected": []}
    chosen = next((item for item in candidates if not item["open"] and item["in_source"] and item["quote"]), None)
    if chosen is None:
        chosen = candidates[0]
    chosen["used"] = True
    shown = {"name": chosen["name"], "quote": chosen["quote"]}
    if not chosen["quote"] or not chosen["in_source"]:
        return {"closed": [], "open": [], "missing": [], "rejected": [name]}
    if chosen["open"]:
        return {"closed": [], "open": [shown], "missing": [], "rejected": []}
    return {"closed": [shown], "open": [], "missing": [], "rejected": []}


def _lookalikes(entry, entry_id, pattern, row):
    items = []
    raw_items = entry.get("legitimate_lookalikes") or []
    pairing = LOOKALIKE_FORBID_INDEX.get(entry_id) or {}
    labels = []
    if pattern:
        labels = [atom_label(item) for item in (pattern.get("ir_forbid") or [])]
    matched, mode = _forbid_mode(row.get("reason") or "", row.get("verdict"))
    paired_indexes = set()
    for number, raw in enumerate(raw_items, 1):
        text = raw.get("text") if isinstance(raw, dict) else str(raw)
        indexes = pairing.get(number)
        if not labels and indexes:
            note = "pilot ir_forbid labels are unavailable for this row; the look-alike is not ruled out here"
            status = "not_paired"
            forbid_labels = []
        elif indexes is None:
            note = "no ir_forbid atom is paired with this look-alike; the checker did not rule it out"
            status = "not_paired"
            forbid_labels = []
        else:
            forbid_labels = [labels[index] for index in indexes if 0 <= index < len(labels)]
            paired_indexes.update(index for index in indexes if 0 <= index < len(labels))
            hit = [label for label in forbid_labels if label in matched]
            if hit:
                shown = " and ".join(f"`{label}`" for label in hit)
                note = f"applies: ir_forbid matched {shown}"
                status = "forbid_matched"
            elif mode == "none":
                shown = " and ".join(f"`{label}`" for label in forbid_labels) or "the paired atom"
                note = f"ir_forbid {shown} did not match"
                status = "forbid_did_not_match"
            elif mode == "reported":
                shown = ", ".join(f"`{label}`" for label in sorted(matched)) or "(none listed)"
                note = f"not among the ir_forbid labels reported as matched: {shown}"
                status = "not_reported_matched"
            else:
                note = "the checker did not report an ir_forbid result for this row; this look-alike is not ruled out here"
                status = "unknown"
        items.append({
            "n": number,
            "text": text,
            "status": status,
            "ir_forbid": forbid_labels,
            "note": note,
        })
    note = _lookalikes_note(items, mode, matched)
    extra = [
        labels[index] for index in range(len(labels))
        if index not in paired_indexes
    ]
    unpaired_note = None
    if extra:
        shown = ", ".join(f"`{label}`" for label in extra)
        if mode == "none":
            unpaired_note = (
                f"ir_forbid atoms with no catalog look-alike line: {shown}. "
                "They were checked and none matched. They are not a prose rule-out of an unpaired look-alike."
            )
        elif mode == "reported":
            hit = [label for label in extra if label in matched]
            if hit:
                unpaired_note = (
                    "ir_forbid matched "
                    + ", ".join(f"`{label}`" for label in hit)
                    + ", which has no catalog look-alike line on this entry."
                )
            else:
                unpaired_note = (
                    f"ir_forbid atoms with no catalog look-alike line: {shown}. "
                    "They were not among the labels reported as matched."
                )
    return items, note, unpaired_note


def _lookalikes_note(items, mode, matched) -> str:
    paired = [item for item in items if item["status"] != "not_paired"]
    unpaired = [item for item in items if item["status"] == "not_paired"]
    complete = bool(items) and not unpaired and all(item["ir_forbid"] for item in items)
    if mode == "none" and complete:
        return "Look-alikes were checked via ir_forbid and none matched."
    if mode == "none":
        return (
            "Declared ir_forbid atoms were checked and none matched. "
            "A look-alike with no paired ir_forbid atom was not ruled out."
        )
    if mode == "reported":
        shown = ", ".join(f"`{label}`" for label in sorted(matched))
        return (
            f"ir_forbid matched: {shown}. "
            "A matched look-alike applies; the checker does not flag past it."
        )
    if not paired:
        return "The checker did not report an ir_forbid result for this row. Look-alikes are not ruled out here."
    return "The checker did not report an ir_forbid result for this row. Paired look-alikes are not ruled out here."


def _forbid_mode(reason: str, verdict: str):
    marker = "ir_forbid matched:"
    if marker in reason:
        tail = reason.split(marker, 1)[1].strip()
        labels = {part.strip() for part in tail.split(",") if part.strip()}
        return labels, "reported"
    if verdict in ("flag", "possible_issue") or "no ir_forbid matched" in reason or "fallback suppressed" in reason:
        return set(), "none"
    return set(), "unknown"


def _apply_pattern_outside(pool, pattern, row) -> None:
    if not pattern:
        return
    outside = set(pattern.get("outside_text_predicates") or [])
    missing = row.get("missing_fact") or ""
    verdict = row.get("verdict")
    for item in pool:
        if item["open"]:
            continue
        if item["name"] in outside and _legacy_open(item["name"], verdict, missing):
            item["open"] = True


def _one_record(row, report, *, ir, catalog, pattern, source_path):
    entry_id = row.get("entry_id")
    entry = catalog.get(entry_id) or {}
    spans = [span for span in (row.get("span_bindings") or []) if isinstance(span, dict)]
    source = ir.get("source_text") if isinstance(ir, dict) else None
    if isinstance(source, str) and source.strip():
        passage = source.strip()
        passage_source = "ir.source_text"
    else:
        passage, passage_source = _passage_from_spans(spans)
        source = None
    pool = _pool(spans, source, row)
    _apply_pattern_outside(pool, pattern, row)
    conditions, unassigned = _conditions(entry, entry_id, pool, row)
    lookalikes, look_note, unpaired_note = _lookalikes(entry, entry_id, pattern, row)
    reading = _strongest_reading(ir)
    supported = bool(conditions) and all(item["status"] == "met_by_span" for item in conditions)
    contested = _contested(ir, row.get("reason") or "")
    return {
        "kind": "idea_detection_assist",
        "lead_to_check": True,
        "substitute_for_hand_method": False,
        "hand_method_required": not supported,
        "spans_support_every_condition": supported,
        "passage_id": report.get("passage_id"),
        "source_path": source_path,
        "passage": passage,
        "passage_source": passage_source,
        "strongest_reading": reading,
        "entry_id": entry_id,
        "entry_name": entry.get("name"),
        "entry_status": entry.get("status"),
        "other_entries_considered": _other_entries(report, entry_id),
        "conditions": conditions,
        "unassigned_spans": unassigned,
        "lookalikes_note": look_note,
        "lookalikes": lookalikes,
        "unpaired_forbids_note": unpaired_note,
        "verdict": row.get("verdict"),
        "verdict_label": VERDICT_LABEL.get(row.get("verdict"), row.get("verdict")),
        "missing_fact": row.get("missing_fact"),
        "reason": row.get("reason"),
        "contested_reading": contested,
    }


if __name__ == "__main__":
    sys.exit(main())
