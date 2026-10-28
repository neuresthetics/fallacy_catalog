"""Recursive nested-layer check over an Idea IR.

The flat checker in ``check.py`` is unchanged: an excerpt still caps a flag,
and an outside-text gap is still ``possible_issue``. This module re-checks
the premises, citations, sub-claims, and hit atoms that passage rests on,
using only text or a child IR supplied by a context expander.

It does not invent facts, loosen forbids, or rewrite METHOD. A leaf stays an
assist / lead-to-check until a child checker result is a hard flag whose
spans already closed under the existing gates.

Default depth is unlimited. Cycle detection (repeated peel target on the
path, or a repeated IR fingerprint) bounds a loop. ``--max-depth`` is an
ops safety valve, not a product cap.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

from idea_detection.check import check_passage, load_catalog, load_patterns
from idea_detection.ir import validate
from idea_detection.model import norm
from idea_detection.record import (
    format_batch,
    format_passage_section,
    iter_ir_paths,
    parse_verdicts,
    records_jsonl,
    render_records,
)

# Edges whose source is support the target rests on.
_BACK_EDGE = {
    "supports",
    "depends_on",
    "causes",
    "correlates",
    "instantiates",
    "selects_subset",
    "shifts_burden",
    "attacks_person",
    "attacks_claim",
    "misattributes",
    "ignores",
    "appeals_to_source",
}

_PREMISE_ROLES = {"premise", "attribution", "default_rule"}

_KIND_ORDER = {
    "cite": 0,
    "premise": 1,
    "subclaim": 2,
    "atom": 3,
    "excerpt": 4,
    "missing_fact": 5,
}

# Context-map kinds a client may write. The right-hand side is what they satisfy.
_KIND_COMPAT = {
    "excerpt": {"excerpt", "snapshot_window"},
    "premise": {"premise", "nearby_claim"},
    "subclaim": {"subclaim", "nearby_claim", "premise"},
    "cite": {"cite"},
    "atom": {"atom"},
    "missing_fact": {"missing_fact"},
}

KNOWN_CONTEXT_KINDS = {
    "snapshot_window",
    "cite",
    "nearby_claim",
    "premise",
    "subclaim",
    "atom",
    "excerpt",
    "missing_fact",
}

_STOP_DETAIL = {
    "hard_flag": "closed flag with nothing further to peel",
    "confirmed_no_issue": "no_issue and nothing further to peel",
    "empty_expander": "expander returned no text and no child IR",
    "cycle": "peel repeated an ancestor target or IR fingerprint",
    "max_depth": "safety valve; this depth was checked and not peeled",
    "invalid_ir": "IR failed validation",
}


class ContextExpander:
    """Pluggable source of wider text or a child IR.

    ``expand`` returns ``None`` when there is nothing further for this peel.
    A mapping has ``text`` and may have ``kind``, ``excerpt``, ``full``, and
    ``ir``. This package does not fetch a corpus.
    """

    def expand(self, request: dict) -> dict | None:
        raise NotImplementedError


class MapContextExpander(ContextExpander):
    """In-memory context map. First matching record wins."""

    def __init__(self, records: list):
        self.records = [normalize_context_record(item) for item in records]

    @classmethod
    def from_records(cls, records: list) -> "MapContextExpander":
        return cls(list(records or []))

    def expand(self, request: dict) -> dict | None:
        keys = []
        for key in list(request.get("lookup_ids") or []):
            if key and key not in keys:
                keys.append(key)
        for key in (request.get("passage_id"), request.get("root_id")):
            if key and key not in keys:
                keys.append(key)
        for key in request.get("ancestors") or []:
            if key and key not in keys:
                keys.append(key)
        for key in keys:
            found = self._best(key, request)
            if found is not None:
                return _expansion_from_record(found, request)
        return None

    def _best(self, passage_id: str, request: dict) -> dict | None:
        targets = {request.get("target_id")}
        if request.get("claim_id"):
            targets.add(request.get("claim_id"))
        targets.discard(None)
        kind = request.get("kind") or ""
        exact = []
        target_only = []
        passage_level = []
        for rec in self.records:
            if rec.get("passage_id") != passage_id:
                continue
            rec_target = rec.get("target_id")
            rec_kind = rec.get("kind")
            kind_ok = True if not rec_kind else _kind_match(rec_kind, kind)
            if rec_target:
                if rec_target in targets and kind_ok:
                    if rec_kind:
                        exact.append(rec)
                    else:
                        target_only.append(rec)
                continue
            # A record with no target is a passage window. It answers an
            # excerpt peel only. It does not smear onto every premise.
            if kind == "excerpt" and kind_ok:
                passage_level.append(rec)
        pool = exact or target_only or passage_level
        return pool[0] if pool else None


def normalize_context_record(rec: dict, *, default_passage_id: str | None = None) -> dict:
    if not isinstance(rec, dict):
        raise ValueError("context record must be an object")
    out = dict(rec)
    if not out.get("passage_id") and default_passage_id:
        out["passage_id"] = default_passage_id
    passage_id = out.get("passage_id")
    if not isinstance(passage_id, str) or not passage_id.strip():
        raise ValueError("context record missing passage_id")
    out["passage_id"] = passage_id.strip()
    if "text" in out and "expand" not in out:
        out["expand"] = out["text"]
    if "expand" in out and out["expand"] is not None and not isinstance(out["expand"], str):
        raise ValueError(f"context expand for {out['passage_id']} must be a string")
    kind = out.get("kind")
    if kind is not None:
        if kind not in KNOWN_CONTEXT_KINDS:
            raise ValueError(f"unknown context kind {kind!r}")
    if "excerpt" in out and not isinstance(out.get("excerpt"), bool):
        raise ValueError(f"context excerpt for {out['passage_id']} must be a boolean")
    if "full" in out and not isinstance(out.get("full"), bool):
        raise ValueError(f"context full for {out['passage_id']} must be a boolean")
    target = out.get("target_id")
    if target is not None and (not isinstance(target, str) or not target):
        raise ValueError(f"context target_id for {out['passage_id']} must be a string")
    if "ir" in out and out["ir"] is not None and not isinstance(out["ir"], dict):
        raise ValueError(f"context ir for {out['passage_id']} must be an object")
    return out


def load_context_map(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return _load_jsonl(text, path)
    stripped = text.strip()
    if not stripped:
        return []
    if suffix == ".json" or stripped[0] in "[{":
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            return _load_jsonl(text, path)
        return _coerce_context_payload(data, default_passage_id=None)
    return _load_jsonl(text, path)


def load_context_dir(path: Path) -> list:
    """Load a directory of context files.

    ``{passage_id}.json`` / ``.jsonl`` / ``.txt`` is passage-level.
    ``{passage_id}/{target_id}.json`` or ``.txt`` is one peel target.
    ``.txt`` is expansion text (a snapshot window at passage level).
    """
    if not path.is_dir():
        raise ValueError(f"context dir is not a directory: {path}")
    records = []
    for item in sorted(path.iterdir(), key=lambda p: p.name):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            passage_id = item.name
            for child in sorted(item.iterdir(), key=lambda p: p.name):
                if not child.is_file() or child.name.startswith("."):
                    continue
                records.extend(_file_records(child, passage_id=passage_id, target_id=child.stem))
            continue
        if item.is_file():
            records.extend(_file_records(item, passage_id=item.stem, target_id=None))
    return records


def check_nested(
    raw: dict,
    *,
    expander: ContextExpander | None = None,
    max_depth: int | None = None,
    catalog: dict | None = None,
    patterns: list | None = None,
) -> dict:
    """Peel ``raw`` until a stop rule. Does not mutate ``raw``."""
    _require_depth(max_depth)
    if expander is None:
        expander = MapContextExpander.from_records([])
    if catalog is None:
        catalog = load_catalog()
    if patterns is None:
        patterns = load_patterns()
    if not isinstance(raw, dict):
        node = _stopped_node(
            passage_id=None,
            depth=0,
            layer_path="L0",
            peel_path="",
            peel_from=None,
            lookup_ids=[],
            reason="invalid_ir",
            detail="IR must be a JSON object",
            ir=None,
        )
        return _wrap(node, max_depth)
    data = deepcopy(raw)
    root_id = data.get("passage_id") if isinstance(data.get("passage_id"), str) else ""
    node = _visit(
        data,
        depth=0,
        max_depth=max_depth,
        expander=expander,
        catalog=catalog,
        patterns=patterns,
        ancestry_fps=(),
        path_pairs=frozenset(),
        layer_names=(),
        peel_steps=(),
        root_id=root_id,
        ancestors=(),
        lookup_ids=_lookup_ids(data, (root_id,)),
        peel_from=None,
    )
    return _wrap(node, max_depth)


def format_tree(tree: dict) -> str:
    lines = [
        "nested max_depth={depth} stress={stress} outcome={outcome}".format(
            depth="unlimited" if tree.get("max_depth") is None else tree.get("max_depth"),
            stress=tree.get("stress"),
            outcome=tree.get("outcome"),
        )
    ]
    _format_node(tree.get("node") or {}, lines, 0, None)
    return "\n".join(lines) + "\n"


def nested_method_records(
    tree: dict,
    *,
    catalog: dict | None = None,
    patterns: list | None = None,
    verdicts=("flag", "possible_issue"),
    source_path: str | None = None,
) -> list:
    """METHOD records for every checked node, with the peel layer path set.

    ``no_issue`` rows whose pattern simply did not match stay out, same as
    the flat renderer. Nodes with no selected row are omitted.
    """
    if catalog is None:
        catalog = load_catalog()
    if patterns is None:
        patterns = load_patterns()
    found = []
    for node in iter_nodes(tree.get("node") or {}):
        report = node.get("report")
        if not report:
            continue
        records = render_records(
            report,
            ir=node.get("ir"),
            catalog=catalog,
            patterns=patterns,
            verdicts=verdicts,
            source_path=source_path,
        )
        for record in records:
            record["layer"] = node.get("layer")
            record["layer_path"] = node.get("layer_path")
            record["peel_path"] = node.get("peel_path") or ""
            record["nest_stress"] = node.get("stress")
            record["nest_outcome"] = node.get("outcome")
            found.append(record)
    return found


def format_nested_method(
    tree: dict,
    *,
    catalog: dict | None = None,
    patterns: list | None = None,
    verdicts=("flag", "possible_issue"),
    source_path: str | None = None,
) -> str:
    records = nested_method_records(
        tree, catalog=catalog, patterns=patterns, verdicts=verdicts, source_path=source_path,
    )
    if not records:
        return format_batch([])
    # Group consecutive records by passage so the section heading carries the path.
    sections = []
    bucket = []
    bucket_key = None
    for record in records:
        key = (record.get("layer_path"), record.get("passage_id"), record.get("peel_path"))
        if bucket and key != bucket_key:
            sections.append(_section(bucket, source_path, verdicts))
            bucket = []
        bucket_key = key
        bucket.append(record)
    if bucket:
        sections.append(_section(bucket, source_path, verdicts))
    return format_batch(sections)


def iter_nodes(node: dict):
    if not node:
        return
    yield node
    for peel in node.get("children") or []:
        child = peel.get("child")
        if child:
            yield from iter_nodes(child)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recursively peel an Idea IR over premises, citations, and sub-claims. "
            "Depth is unlimited unless --max-depth is set. Context is local; "
            "this command does not fetch a corpus."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Idea IR JSON files, or a directory of *.json",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Ops safety valve. Omit for unlimited depth (cycle detection still applies). 0 checks the seed only.",
    )
    parser.add_argument(
        "--context-map",
        help="JSONL or JSON context map: passage_id → expand text and/or a child IR",
    )
    parser.add_argument(
        "--context-dir",
        help="Directory of context files named by passage_id, or passage_id/target_id",
    )
    parser.add_argument("--json", action="store_true", help="Print the nested tree as JSON")
    parser.add_argument(
        "--method-record",
        action="store_true",
        help="Also emit METHOD-shaped records. With --json, records are included in the JSON.",
    )
    parser.add_argument(
        "--method-format",
        choices=("markdown", "jsonl"),
        default="markdown",
        help="With --method-record and without --json: markdown (default) or JSONL",
    )
    parser.add_argument(
        "--verdicts",
        default="flag,possible_issue",
        help="With --method-record: flag, possible_issue, no_issue (comma-separated)",
    )
    args = parser.parse_args(argv)
    if args.max_depth is not None and args.max_depth < 0:
        print("max-depth must be >= 0", file=sys.stderr)
        return 2
    try:
        verdicts = parse_verdicts(args.verdicts) if args.method_record else ("flag", "possible_issue")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    records = []
    try:
        if args.context_map:
            records.extend(load_context_map(Path(args.context_map)))
        if args.context_dir:
            records.extend(load_context_dir(Path(args.context_dir)))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"context: {exc}", file=sys.stderr)
        return 2
    expander = MapContextExpander.from_records(records)
    ir_paths = iter_ir_paths(args.paths)
    if not ir_paths:
        print("no Idea IR JSON files found", file=sys.stderr)
        return 2

    catalog = load_catalog()
    patterns = load_patterns()
    trees = []
    exit_code = 0
    for path in ir_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        tree = check_nested(
            data,
            expander=expander,
            max_depth=args.max_depth,
            catalog=catalog,
            patterns=patterns,
        )
        tree["source_path"] = str(path)
        if not tree.get("ok"):
            exit_code = 1
            print(f"{path}: {tree.get('errors')}", file=sys.stderr)
        trees.append(tree)

    if args.json:
        payload = {
            "max_depth": args.max_depth,
            "trees": trees,
        }
        if args.method_record:
            payload["records"] = []
            for tree in trees:
                payload["records"].extend(
                    nested_method_records(
                        tree,
                        catalog=catalog,
                        patterns=patterns,
                        verdicts=verdicts,
                        source_path=tree.get("source_path"),
                    )
                )
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return exit_code

    if args.method_record and args.method_format == "jsonl":
        rows = []
        for tree in trees:
            rows.extend(
                nested_method_records(
                    tree,
                    catalog=catalog,
                    patterns=patterns,
                    verdicts=verdicts,
                    source_path=tree.get("source_path"),
                )
            )
        sys.stdout.write(records_jsonl(rows))
        return exit_code

    if args.method_record:
        blocks = []
        for tree in trees:
            rendered = format_nested_method(
                tree,
                catalog=catalog,
                patterns=patterns,
                verdicts=verdicts,
                source_path=tree.get("source_path"),
            )
            blocks.append(rendered.rstrip("\n"))
        sys.stdout.write("\n\n".join(blocks) + ("\n" if blocks else ""))
        return exit_code

    parts = [format_tree(tree).rstrip("\n") for tree in trees]
    sys.stdout.write("\n\n".join(parts) + ("\n" if parts else ""))
    return exit_code


def _visit(
    ir,
    *,
    depth,
    max_depth,
    expander,
    catalog,
    patterns,
    ancestry_fps,
    path_pairs,
    layer_names,
    peel_steps,
    root_id,
    ancestors,
    lookup_ids,
    peel_from,
):
    passage_id = ir.get("passage_id") if isinstance(ir, dict) else None
    layer = f"L{depth}"
    names = layer_names + (layer,)
    layer_path = "→".join(names)
    peel_path = _format_peel_path(peel_steps)
    fp = fingerprint(ir)
    if fp in ancestry_fps:
        return _stopped_node(
            passage_id=passage_id,
            depth=depth,
            layer_path=layer_path,
            peel_path=peel_path,
            peel_from=peel_from,
            lookup_ids=lookup_ids,
            reason="cycle",
            detail="this IR fingerprint is already on the peel path",
            ir=ir,
        )

    report = check_passage(ir, catalog=catalog, patterns=patterns)
    aggregate = _aggregate(report)
    targets = [] if not report.get("ok") else peel_targets(ir, report)
    capped = max_depth is not None and depth >= max_depth
    peels = []
    if report.get("ok") and targets and not capped:
        next_fps = ancestry_fps + (fp,)
        next_ancestors = ancestors + ((passage_id,) if passage_id else ())
        for target in targets:
            pair = (target["kind"], target["target_id"])
            if pair in path_pairs:
                peels.append(_peel_stop(target, "cycle", "this premise, citation, or atom is already on the peel path"))
                continue
            request = {
                "passage_id": passage_id,
                "root_id": root_id,
                "ancestors": [item for item in next_ancestors if item],
                "lookup_ids": list(lookup_ids),
                "target_id": target["target_id"],
                "claim_id": target.get("claim_id"),
                "kind": target["kind"],
                "quote": target.get("quote") or "",
                "depth": depth + 1,
                "entry_ids": list(target.get("entry_ids") or []),
                "missing_fact": target.get("missing_fact"),
                "layer_path": layer_path,
            }
            try:
                expansion = expander.expand(request)
            except Exception as exc:  # expander bugs must not invent a verdict
                peels.append(_peel_stop(target, "invalid_ir", f"expander failed: {exc}"))
                continue
            if not _expansion_usable(expansion):
                peels.append(_peel_stop(target, "empty_expander", _STOP_DETAIL["empty_expander"]))
                continue
            child_ir, supplied_id, build_error = build_child_ir(ir, target, expansion, depth + 1)
            if build_error:
                peels.append(_peel_stop(target, "invalid_ir", build_error))
                continue
            errors = validate(child_ir)
            if errors:
                peels.append(_peel_stop(target, "invalid_ir", "; ".join(errors)))
                continue
            extra_ids = list(lookup_ids)
            if supplied_id:
                extra_ids.append(supplied_id)
            child_lookups = _lookup_ids(child_ir, extra_ids)
            child = _visit(
                child_ir,
                depth=depth + 1,
                max_depth=max_depth,
                expander=expander,
                catalog=catalog,
                patterns=patterns,
                ancestry_fps=next_fps,
                path_pairs=path_pairs | {pair},
                layer_names=names,
                peel_steps=peel_steps + ({"kind": target["kind"], "target_id": target["target_id"]},),
                root_id=root_id,
                ancestors=next_ancestors,
                lookup_ids=child_lookups,
                peel_from={"kind": target["kind"], "target_id": target["target_id"]},
            )
            peels.append({
                "kind": target["kind"],
                "target_id": target["target_id"],
                "claim_id": target.get("claim_id"),
                "quote": target.get("quote") or "",
                "entry_ids": list(target.get("entry_ids") or []),
                "atom_names": list(target.get("atom_names") or []),
                "missing_fact": target.get("missing_fact"),
                "expansion": _expansion_summary(expansion),
                "stop": child.get("stop") if child.get("report") is None and child.get("stop") else None,
                "child": child,
            })

    stop = _summarize_stop(aggregate, targets, peels, capped, report)
    node = {
        "passage_id": passage_id,
        "depth": depth,
        "layer": layer,
        "layer_path": layer_path,
        "peel_path": peel_path,
        "peel_from": peel_from,
        "lookup_ids": list(lookup_ids),
        "excerpt": bool(ir.get("excerpt")) if isinstance(ir, dict) else False,
        "aggregate": aggregate,
        "stop": stop,
        "report": report,
        "ir": ir,
        "source_text": ir.get("source_text") if isinstance(ir, dict) else "",
        "children": peels,
    }
    _annotate(node)
    return node


def peel_targets(ir: dict, report: dict) -> list:
    """Premises, citations, sub-claims, hit atoms, and open gaps.

    Collected from the IR structure and from flag / possible_issue rows.
    A confirmed pattern miss does not add atoms. A no_issue passage still
    peels the premises and citations it rests on.
    """
    claims = {}
    for claim in ir.get("claims") or []:
        if isinstance(claim, dict) and isinstance(claim.get("id"), str):
            claims[claim["id"]] = claim
    edges = [edge for edge in (ir.get("edges") or []) if isinstance(edge, dict) and edge.get("id")]
    outgoing = {}
    incoming = {}
    for edge in edges:
        outgoing.setdefault(edge.get("source"), []).append(edge)
        incoming.setdefault(edge.get("target"), []).append(edge)

    targets = []
    seen = set()

    def add(item):
        key = (item["kind"], item["target_id"])
        if not item.get("target_id") or key in seen:
            return None
        seen.add(key)
        item.setdefault("entry_ids", [])
        item.setdefault("atom_names", [])
        item.setdefault("claim_id", None)
        item.setdefault("missing_fact", None)
        targets.append(item)
        return item

    for edge in edges:
        if edge.get("type") != "appeals_to_source":
            continue
        source = claims.get(edge.get("source"))
        add({
            "kind": "cite",
            "target_id": edge["id"],
            "claim_id": edge.get("source") if edge.get("source") in claims else None,
            "quote": _quote(edge) or _quote(source),
        })

    for cid in claims:
        claim = claims[cid]
        outs = [edge for edge in outgoing.get(cid) or [] if edge.get("type") in _BACK_EDGE]
        ins = [edge for edge in incoming.get(cid) or [] if edge.get("type") in _BACK_EDGE]
        structural_out = [edge for edge in outs if edge.get("type") != "appeals_to_source"]
        only_cite = bool(outs) and not structural_out and all(
            edge.get("type") == "appeals_to_source" for edge in outs
        )
        if only_cite:
            continue
        role = claim.get("role")
        if not structural_out and role not in _PREMISE_ROLES:
            continue
        intermediate = bool(ins) and bool(structural_out)
        depended = any(edge.get("type") == "depends_on" and edge.get("target") == cid for edge in edges)
        if depended or intermediate:
            kind = "subclaim"
        else:
            kind = "premise"
        add({
            "kind": kind,
            "target_id": cid,
            "claim_id": cid,
            "quote": _quote(claim),
        })

    for row in report.get("results") or []:
        if row.get("verdict") not in ("flag", "possible_issue"):
            continue
        entry_id = row.get("entry_id")
        for span in row.get("span_bindings") or []:
            if not isinstance(span, dict):
                continue
            sid = span.get("id")
            quote = span.get("quote") or ""
            name = span.get("name")
            hosts = _hosts_for_span(targets, sid, quote)
            if hosts:
                for host in hosts:
                    _append_unique(host["entry_ids"], entry_id)
                    _append_unique(host["atom_names"], name)
                continue
            if not isinstance(sid, str) or not sid:
                continue
            claim_id = sid if sid in claims else None
            if claim_id is None:
                edge = next((edge for edge in edges if edge.get("id") == sid), None)
                if edge and edge.get("source") in claims:
                    claim_id = edge.get("source")
            add({
                "kind": "atom",
                "target_id": sid,
                "claim_id": claim_id,
                "quote": quote,
                "entry_ids": [entry_id] if entry_id else [],
                "atom_names": [name] if name else [],
            })

    if ir.get("excerpt") and any(_excerpt_row(row) for row in report.get("results") or []):
        add({
            "kind": "excerpt",
            "target_id": "excerpt",
            "claim_id": None,
            "quote": (ir.get("source_text") or "")[:240],
            "entry_ids": [
                row.get("entry_id") for row in report.get("results") or [] if _excerpt_row(row)
            ],
            "atom_names": ["excerpt"],
        })

    for row in report.get("results") or []:
        if row.get("verdict") != "possible_issue" or not row.get("missing_fact"):
            continue
        if any(row.get("entry_id") in (target.get("entry_ids") or []) for target in targets):
            continue
        add({
            "kind": "missing_fact",
            "target_id": row.get("entry_id"),
            "claim_id": None,
            "quote": "",
            "entry_ids": [row.get("entry_id")],
            "atom_names": ["missing_fact"],
            "missing_fact": row.get("missing_fact"),
        })

    targets.sort(key=lambda item: (_KIND_ORDER.get(item["kind"], 9), item["target_id"] or ""))
    return targets


def build_child_ir(parent: dict, target: dict, expansion: dict, depth: int):
    """Return ``(ir, supplied_passage_id, error)``.

    A supplied ``ir`` is the child, unchanged except for the generated
    passage id and an explicit excerpt/full override. Text-only expansion
    keeps parent structure that the peel rests on and writes the supplied
    text onto that claim. It does not mint claims or edges.
    """
    kind = target.get("kind")
    target_id = target.get("target_id") or "peel"
    passage_id = child_passage_id(parent.get("passage_id") or "passage", depth, kind, target_id)
    supplied = expansion.get("ir")
    if isinstance(supplied, dict):
        child = deepcopy(supplied)
        supplied_id = child.get("passage_id") if isinstance(child.get("passage_id"), str) else None
        child.pop("expected_checker", None)
        child["passage_id"] = passage_id
        if not child.get("source_text") and isinstance(expansion.get("text"), str):
            child["source_text"] = expansion["text"]
        _apply_excerpt_override(child, expansion, parent=None, kind=kind)
        return child, supplied_id, None

    text = expansion.get("text") if isinstance(expansion.get("text"), str) else ""
    if kind == "excerpt":
        child = deepcopy(parent)
        child.pop("expected_checker", None)
        child["passage_id"] = passage_id
        child["source_text"] = _cover(parent.get("source_text") or "", text)
        _apply_excerpt_override(child, expansion, parent=parent, kind=kind)
        return child, None, None

    claim_ids, edge_ids = _cone(parent, target)
    if not claim_ids:
        return None, None, "expansion did not land on a claim or edge in the parent IR"
    child = deepcopy(parent)
    child.pop("expected_checker", None)
    child["passage_id"] = passage_id
    child["source_text"] = _cover(parent.get("source_text") or "", text)
    child["claims"] = [claim for claim in child.get("claims") or [] if claim.get("id") in claim_ids]
    child["edges"] = [edge for edge in child.get("edges") or [] if edge.get("id") in edge_ids]
    child["steps"] = _filter_steps(child.get("steps") or [], claim_ids, child["source_text"])
    child["bindings"] = [
        binding for binding in (child.get("bindings") or [])
        if isinstance(binding, dict) and binding.get("claim_id") in claim_ids
    ]
    if "evidence_sets" in child:
        kept_sets = []
        for item in child.get("evidence_sets") or []:
            if not isinstance(item, dict):
                continue
            members = [member for member in item.get("member_ids") or [] if member in claim_ids]
            if not members:
                continue
            copied = deepcopy(item)
            copied["member_ids"] = members
            kept_sets.append(copied)
        child["evidence_sets"] = kept_sets
    attach_id = target.get("claim_id")
    if kind == "missing_fact" and not attach_id:
        attach_id = _missing_fact_claim(child)
    if attach_id and text.strip():
        for claim in child["claims"]:
            if claim.get("id") == attach_id:
                _attach_text(claim, text)
                break
    _apply_excerpt_override(child, expansion, parent=parent, kind=kind)
    return child, None, None


def child_passage_id(parent_id: str, depth: int, kind: str, target_id: str) -> str:
    safe_kind = _safe_token(kind or "peel")
    safe_target = _safe_token(target_id or "target")
    return f"{parent_id}__l{depth}__{safe_kind}-{safe_target}"


def fingerprint(ir: dict) -> tuple:
    claims = tuple(sorted(
        claim.get("id", "") for claim in (ir.get("claims") or []) if isinstance(claim, dict)
    ))
    edges = tuple(sorted(
        edge.get("id", "") for edge in (ir.get("edges") or []) if isinstance(edge, dict)
    ))
    contested = ir.get("contested_reading") if isinstance(ir.get("contested_reading"), str) else ""
    return (
        norm(ir.get("source_text") or ""),
        bool(ir.get("excerpt")),
        contested,
        claims,
        edges,
    )


def _cone(ir: dict, target: dict):
    claims = {
        claim["id"] for claim in (ir.get("claims") or [])
        if isinstance(claim, dict) and isinstance(claim.get("id"), str)
    }
    edges = [edge for edge in (ir.get("edges") or []) if isinstance(edge, dict)]
    kind = target.get("kind")
    tid = target.get("target_id")
    if kind in ("excerpt", "missing_fact"):
        return set(claims), {edge["id"] for edge in edges if edge.get("id")}
    seeds = set()
    forced_edges = set()
    if kind == "cite" or (kind == "atom" and any(edge.get("id") == tid for edge in edges)):
        edge = next((edge for edge in edges if edge.get("id") == tid), None)
        if edge:
            forced_edges.add(edge.get("id"))
            if edge.get("source") in claims:
                seeds.add(edge["source"])
            if edge.get("target") in claims:
                seeds.add(edge["target"])
    if target.get("claim_id") in claims:
        seeds.add(target["claim_id"])
    if kind == "atom" and tid not in claims and tid not in {edge.get("id") for edge in edges}:
        for edge in edges:
            if edge.get("source") == tid or edge.get("target") == tid:
                forced_edges.add(edge.get("id"))
                if edge.get("source") in claims:
                    seeds.add(edge["source"])
                if edge.get("target") in claims:
                    seeds.add(edge["target"])
    if not seeds:
        return set(), set()
    seen = set(seeds)
    changed = True
    while changed:
        changed = False
        for edge in edges:
            if edge.get("type") not in _BACK_EDGE:
                continue
            src, tgt = edge.get("source"), edge.get("target")
            if tgt in seen and src in claims and src not in seen:
                seen.add(src)
                changed = True
    edge_ids = set(forced_edges)
    for edge in edges:
        src, tgt = edge.get("source"), edge.get("target")
        if src in claims and src not in seen:
            continue
        if tgt in claims and tgt not in seen:
            continue
        if src in seen or tgt in seen:
            if edge.get("id"):
                edge_ids.add(edge["id"])
    return seen, edge_ids


def _cover(parent_source: str, expansion: str) -> str:
    window = (expansion or "").strip()
    base = parent_source or ""
    if not window:
        return base
    if norm(base) and norm(base) in norm(window):
        return window
    if window in base:
        return base
    if not base:
        return window
    return f"{base}\n{window}"


def _apply_excerpt_override(child: dict, expansion: dict, *, parent, kind: str):
    if expansion.get("full") is True or expansion.get("excerpt") is False:
        child["excerpt"] = False
        return
    if expansion.get("excerpt") is True:
        child["excerpt"] = True
        return
    if parent is None:
        return
    # Text-only children stay excerpts until the client says the window is whole.
    if parent.get("excerpt"):
        child["excerpt"] = True
    elif "excerpt" in child and kind != "excerpt":
        # Copied parent flag already false or absent.
        pass


def _attach_text(claim: dict, text: str):
    extra = text.strip()
    if not extra:
        return
    current = claim.get("text") or ""
    if extra in current:
        return
    claim["text"] = (current + " " + extra).strip()


def _missing_fact_claim(child: dict):
    for edge in child.get("edges") or []:
        if edge.get("type") == "appeals_to_source":
            return edge.get("source")
    for claim in child.get("claims") or []:
        if claim.get("role") in _PREMISE_ROLES:
            return claim.get("id")
    claims = child.get("claims") or []
    return claims[0].get("id") if claims else None


def _filter_steps(steps, claim_ids, source_text):
    kept = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        cids = [cid for cid in step.get("claim_ids") or [] if cid in claim_ids]
        if not cids:
            continue
        copied = deepcopy(step)
        copied["claim_ids"] = cids
        kept.append(copied)
    if kept:
        return kept
    quote = ""
    if source_text:
        quote = source_text if len(source_text) <= 240 else source_text[:240]
    return [{
        "id": "s1",
        "span": {"quote": quote},
        "claim_ids": sorted(claim_ids),
    }]


def _expansion_usable(expansion) -> bool:
    if not isinstance(expansion, dict):
        return False
    if isinstance(expansion.get("ir"), dict):
        return True
    text = expansion.get("text")
    return isinstance(text, str) and bool(text.strip())


def _expansion_from_record(rec: dict, request: dict) -> dict | None:
    text = rec.get("expand") if isinstance(rec.get("expand"), str) else ""
    supplied = rec.get("ir") if isinstance(rec.get("ir"), dict) else None
    if not text.strip() and supplied is None:
        return None
    out = {
        "text": text,
        "kind": rec.get("kind") or request.get("kind"),
        "full": bool(rec.get("full")),
    }
    if "excerpt" in rec:
        out["excerpt"] = rec["excerpt"]
    if supplied is not None:
        out["ir"] = deepcopy(supplied)
    return out


def _expansion_summary(expansion: dict) -> dict:
    text = expansion.get("text") if isinstance(expansion.get("text"), str) else ""
    summary = {
        "kind": expansion.get("kind"),
        "full": bool(expansion.get("full")),
        "chars": len(text.strip()),
        "supplied_ir": isinstance(expansion.get("ir"), dict),
    }
    if "excerpt" in expansion:
        summary["excerpt"] = expansion["excerpt"]
    return summary


def _summarize_stop(aggregate, targets, peels, capped, report):
    if not report.get("ok"):
        return {"reason": "invalid_ir", "detail": "; ".join(report.get("errors") or []) or _STOP_DETAIL["invalid_ir"]}
    if capped and targets:
        return {"reason": "max_depth", "detail": _STOP_DETAIL["max_depth"]}
    if not targets:
        if aggregate == "flag":
            return {"reason": "hard_flag", "detail": _STOP_DETAIL["hard_flag"]}
        if aggregate == "no_issue":
            return {"reason": "confirmed_no_issue", "detail": _STOP_DETAIL["confirmed_no_issue"]}
        if aggregate == "possible_issue":
            return {
                "reason": "empty_expander",
                "detail": "possible_issue with no peelable premise, citation, sub-claim, or gap",
            }
        return {"reason": "invalid_ir", "detail": _STOP_DETAIL["invalid_ir"]}
    if any(_child_checked(peel) for peel in peels):
        return None
    reasons = {(peel.get("stop") or {}).get("reason") for peel in peels}
    if reasons == {"cycle"}:
        return {"reason": "cycle", "detail": "every peel repeated an ancestor"}
    if aggregate == "flag" and reasons <= {"empty_expander", "cycle"}:
        return {"reason": "hard_flag", "detail": "closed flag; remaining peels had no further context"}
    if aggregate == "no_issue" and reasons <= {"empty_expander", "cycle"}:
        return {"reason": "confirmed_no_issue", "detail": "no_issue; remaining peels had no further context or cycled"}
    if "empty_expander" in reasons and aggregate == "possible_issue" and reasons <= {"empty_expander", "cycle"}:
        return {"reason": "empty_expander", "detail": "no further context for the open peels"}
    if reasons == {"invalid_ir"}:
        return {"reason": "invalid_ir", "detail": "child IR failed validation"}
    return None


def _child_checked(peel) -> bool:
    child = peel.get("child")
    return bool(child and child.get("report"))


def _annotate(node: dict):
    outcome = _outcome(node)
    node["outcome"] = outcome
    node["stress"] = "survives" if outcome in ("survives", "stopped") else "breaks"


def _outcome(node: dict) -> str:
    """Nested stress of one node.

    The flat ``report`` is never rewritten. ``survives`` means no checked
    node flagged, and every open excerpt / missing-fact row on this node was
    peeled into a child that itself survives. A contested reading or a
    ``text_detectable: no`` question stays open. ``flagged`` wins over that.
    """
    if node.get("report") is None:
        return "stopped"
    aggregate = node.get("aggregate")
    checked = []
    child_outcomes = []
    for peel in node.get("children") or []:
        child = peel.get("child")
        if not child:
            continue
        child_outcomes.append(child.get("outcome"))
        if child.get("report"):
            checked.append(peel)
    if aggregate == "error" or "error" in child_outcomes:
        return "error"
    if aggregate == "flag" or "flagged" in child_outcomes:
        return "flagged"
    if "open" in child_outcomes:
        return "open"
    if aggregate == "possible_issue":
        if _settled(node, checked):
            return "survives"
        return "open"
    if aggregate == "no_issue":
        return "survives"
    return "stopped"


def _settled(node: dict, checked: list) -> bool:
    """True when this node's open gaps were closed as no_issue by a real peel."""
    rows = [
        row for row in (node.get("report") or {}).get("results") or []
        if row.get("verdict") == "possible_issue"
    ]
    if not rows or not checked:
        return False
    if any(not _settleable_gap(row) for row in rows):
        return False
    if any(peel["child"].get("outcome") != "survives" for peel in checked):
        return False
    open_ids = {row.get("entry_id") for row in rows}
    for peel in checked:
        if peel.get("kind") in ("excerpt", "missing_fact", "cite"):
            return True
        if open_ids.intersection(peel.get("entry_ids") or []):
            return True
    return False


def _settleable_gap(row: dict) -> bool:
    reason = row.get("reason") or ""
    if "text_detectable" in reason or "contested" in reason or "same-family" in reason:
        return False
    if "excerpt boundary" in reason:
        return True
    return bool(row.get("missing_fact")) and "missing fact" in reason


def _aggregate(report: dict) -> str:
    if not report or not report.get("ok"):
        return "error"
    verdicts = {row.get("verdict") for row in report.get("results") or []}
    if "flag" in verdicts:
        return "flag"
    if "possible_issue" in verdicts:
        return "possible_issue"
    return "no_issue"


def _wrap(node: dict, max_depth):
    errors = []
    report = node.get("report") or {}
    if report and not report.get("ok"):
        errors = list(report.get("errors") or [])
    if node.get("stop") and node["stop"].get("reason") == "invalid_ir" and not report:
        errors = [node["stop"].get("detail") or "invalid ir"]
    return {
        "ok": node.get("aggregate") != "error" and node.get("outcome") != "error",
        "root_id": node.get("passage_id"),
        "max_depth": max_depth,
        "unlimited": max_depth is None,
        "stress": node.get("stress"),
        "outcome": node.get("outcome"),
        "errors": errors,
        "node": node,
    }


def _stopped_node(*, passage_id, depth, layer_path, peel_path, peel_from, lookup_ids, reason, detail, ir):
    node = {
        "passage_id": passage_id,
        "depth": depth,
        "layer": f"L{depth}",
        "layer_path": layer_path,
        "peel_path": peel_path,
        "peel_from": peel_from,
        "lookup_ids": list(lookup_ids or []),
        "excerpt": bool(ir.get("excerpt")) if isinstance(ir, dict) else False,
        "aggregate": None,
        "stop": {"reason": reason, "detail": detail},
        "report": None,
        "ir": ir,
        "source_text": ir.get("source_text") if isinstance(ir, dict) else "",
        "children": [],
    }
    _annotate(node)
    return node


def _peel_stop(target, reason, detail):
    return {
        "kind": target["kind"],
        "target_id": target["target_id"],
        "claim_id": target.get("claim_id"),
        "quote": target.get("quote") or "",
        "entry_ids": list(target.get("entry_ids") or []),
        "atom_names": list(target.get("atom_names") or []),
        "missing_fact": target.get("missing_fact"),
        "expansion": None,
        "stop": {"reason": reason, "detail": detail},
        "child": None,
    }


def _format_node(node, lines, indent, peel_label):
    pad = "  " * indent
    if node.get("report") is None and node.get("stop"):
        reason = node["stop"].get("reason")
        label = peel_label or node.get("passage_id") or "peel"
        lines.append(f"{pad}{label} → stop={reason} {node.get('layer_path') or ''}".rstrip())
        return
    bits = [
        node.get("layer_path") or "",
        node.get("passage_id") or "(no passage_id)",
        node.get("aggregate") or "",
        node.get("stress") or "",
    ]
    head = " ".join(bit for bit in bits if bit)
    if peel_label:
        head = f"{peel_label} → {head}"
    stop = (node.get("stop") or {}).get("reason")
    if stop:
        head += f" stop={stop}"
    lines.append(f"{pad}{head}")
    for peel in node.get("children") or []:
        label = f"{peel.get('kind')}:{peel.get('target_id')}"
        child = peel.get("child")
        if child:
            _format_node(child, lines, indent + 1, label)
        else:
            reason = (peel.get("stop") or {}).get("reason") or "stopped"
            lines.append(f"{pad}  {label} → {reason}")


def _section(records, source_path, verdicts):
    first = records[0]
    heading = f"{first.get('layer_path') or 'L0'} {first.get('passage_id') or ''}".strip()
    if first.get("peel_path"):
        heading += f" [{first['peel_path']}]"
    return format_passage_section(heading, records, source_path=source_path, verdicts=verdicts)


def _hosts_for_span(targets, sid, quote):
    hosts = []
    for target in targets:
        if sid and (sid == target.get("target_id") or sid == target.get("claim_id")):
            hosts.append(target)
            continue
        if _same_quote(quote, target.get("quote") or ""):
            hosts.append(target)
    return hosts


def _same_quote(a, b) -> bool:
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
    return len(shorter) >= 12 and shorter in longer


def _excerpt_row(row) -> bool:
    return row.get("verdict") == "possible_issue" and "excerpt" in (row.get("reason") or "")


def _append_unique(items, value):
    if value and value not in items:
        items.append(value)


def _quote(node) -> str:
    if not isinstance(node, dict):
        return ""
    span = node.get("span") or node.get("name_span") or {}
    quote = span.get("quote") if isinstance(span, dict) else ""
    return quote or ""


def _lookup_ids(ir: dict, extra) -> list:
    found = []
    for item in extra:
        if isinstance(item, str) and item and item not in found:
            found.append(item)
    passage_id = ir.get("passage_id") if isinstance(ir, dict) else None
    if isinstance(passage_id, str) and passage_id and passage_id not in found:
        found.append(passage_id)
    return found


def _kind_match(record_kind: str, request_kind: str) -> bool:
    if record_kind == request_kind:
        return True
    return record_kind in _KIND_COMPAT.get(request_kind, set())


def _safe_token(text: str) -> str:
    chars = []
    for ch in text:
        if ch.isalnum() or ch in "._-":
            chars.append(ch)
        else:
            chars.append("-")
    token = "".join(chars).strip("-") or "x"
    return token[:80]


def _format_peel_path(steps) -> str:
    if not steps:
        return ""
    return " → ".join(f"{step['kind']}:{step['target_id']}" for step in steps)


def _require_depth(max_depth):
    if max_depth is None:
        return
    if isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 0:
        raise ValueError("max_depth must be a non-negative int or None for unlimited")


def _load_jsonl(text: str, path: Path) -> list:
    records = []
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: {exc}") from exc
        records.extend(_coerce_context_payload(data, default_passage_id=None))
    return records


def _coerce_context_payload(data, *, default_passage_id):
    if isinstance(data, list):
        return [normalize_context_record(item, default_passage_id=default_passage_id) for item in data]
    if isinstance(data, dict) and isinstance(data.get("expansions"), list):
        passage_id = data.get("passage_id") or default_passage_id
        return [
            normalize_context_record(item, default_passage_id=passage_id)
            for item in data["expansions"]
        ]
    if isinstance(data, dict):
        return [normalize_context_record(data, default_passage_id=default_passage_id)]
    raise ValueError("context payload must be an object, a list, or JSONL")


def _file_records(path: Path, *, passage_id: str, target_id: str | None):
    suffix = path.suffix.lower()
    if suffix == ".txt":
        text = path.read_text(encoding="utf-8")
        rec = {"passage_id": passage_id, "expand": text}
        if target_id:
            rec["target_id"] = target_id
        else:
            rec["kind"] = "snapshot_window"
        return [normalize_context_record(rec)]
    if suffix == ".jsonl":
        return load_context_map(path)
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        # A bare IR (has claims and edges, no expand) is a child IR for this target.
        if isinstance(data, dict) and "claims" in data and "edges" in data and "expand" not in data and "expansions" not in data:
            rec = {"passage_id": passage_id, "ir": data}
            if target_id:
                rec["target_id"] = target_id
            return [normalize_context_record(rec)]
        records = _coerce_context_payload(data, default_passage_id=passage_id)
        if target_id:
            for rec in records:
                rec.setdefault("target_id", target_id)
        return records
    return []


if __name__ == "__main__":
    sys.exit(main())
