"""Nested dependence peels. Gates stay the flat checker's gates."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from idea_detection.check import result_for
from idea_detection.eval_fixtures import FIXTURES
from idea_detection.nested import (
    MapContextExpander,
    check_nested,
    format_tree,
    main as nested_main,
    nested_method_records,
    peel_targets,
)
from idea_detection.check import check_passage


ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _claim(cid, text, quote, role, hedge="none", scope="truth", **extra):
    item = {
        "id": cid,
        "text": text,
        "span": {"quote": quote},
        "role": role,
        "hedge": hedge,
        "scope": scope,
        "speaker": None,
    }
    item.update(extra)
    return item


def _edge(eid, etype, source, target, quote, **extra):
    item = {
        "id": eid,
        "type": etype,
        "source": source,
        "target": target,
        "span": {"quote": quote},
    }
    item.update(extra)
    return item


def _passage(pid, source, claims, edges, **extra):
    data = {
        "passage_id": pid,
        "source_text": source,
        "steps": [{
            "id": "s1",
            "span": {"quote": source},
            "claim_ids": [claim["id"] for claim in claims],
        }],
        "claims": claims,
        "edges": edges,
        "extractor": {"kind": "human", "charity_applied": True},
    }
    data.update(extra)
    return data


def _chain(index):
    premise = f"Step {index} holds"
    conclusion = f"step {index} concludes"
    source = f"{premise}, so {conclusion}."
    return _passage(
        f"chain{index}",
        source,
        [
            _claim(f"p{index}", f"Step {index} holds.", premise, "premise"),
            _claim(f"k{index}", f"Step {index} concludes.", f"so {conclusion}", "conclusion"),
        ],
        [_edge(f"e{index}", "supports", f"p{index}", f"k{index}", premise)],
    )


def _physicist():
    source = "A famous physicist says this diet cures cancer, so it does."
    return _passage(
        "physicist_diet",
        source,
        [
            _claim(
                "c_src",
                "A famous physicist says this diet cures cancer.",
                "A famous physicist says this diet cures cancer",
                "premise",
            ),
            _claim("c_k", "This diet cures cancer.", "so it does", "conclusion"),
        ],
        [_edge(
            "e_auth",
            "appeals_to_source",
            "c_src",
            "c_k",
            "A famous physicist says this diet cures cancer",
        )],
    )


def _clean():
    source = "The inspection report lists corrosion, so the bearings should be replaced."
    return _passage(
        "clean_surface",
        source,
        [
            _claim(
                "c_prem",
                "The inspection report lists corrosion.",
                "The inspection report lists corrosion",
                "premise",
            ),
            _claim(
                "c_k",
                "The bearings should be replaced.",
                "so the bearings should be replaced",
                "conclusion",
            ),
        ],
        [_edge(
            "e_sup",
            "supports",
            "c_prem",
            "c_k",
            "The inspection report lists corrosion",
        )],
    )


class _Count:
    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    def expand(self, request):
        self.calls += 1
        return self.inner.expand(request)


def _walk(node):
    yield node
    for peel in node.get("children") or []:
        child = peel.get("child")
        if child:
            yield from _walk(child)


def _flags(node):
    found = []
    for item in _walk(node):
        report = item.get("report") or {}
        for row in report.get("results") or []:
            if row.get("verdict") == "flag":
                found.append((item, row))
    return found


def _peel(node, kind, target_id):
    for peel in node.get("children") or []:
        if peel.get("kind") == kind and peel.get("target_id") == target_id:
            return peel
    return None


class NestedLayerTests(unittest.TestCase):
    def test_excerpt_cap_flags_when_the_window_is_the_whole_text(self):
        raw = _load("method_ex1_ad_hominem.json")
        raw["excerpt"] = True
        raw["passage_id"] = "ex1_excerpt"
        snapshot = json.dumps(raw, sort_keys=True)
        expander = MapContextExpander.from_records([{
            "passage_id": "ex1_excerpt",
            "kind": "snapshot_window",
            "full": True,
            "expand": raw["source_text"],
        }])
        tree = check_nested(raw, expander=expander)
        self.assertEqual(json.dumps(raw, sort_keys=True), snapshot)
        self.assertEqual(tree["node"]["aggregate"], "possible_issue")
        self.assertEqual(tree["node"]["layer_path"], "L0")
        excerpt = _peel(tree["node"], "excerpt", "excerpt")
        self.assertIsNotNone(excerpt)
        child = excerpt["child"]
        self.assertEqual(child["layer_path"], "L0→L1")
        self.assertEqual(child["peel_path"], "excerpt:excerpt")
        self.assertFalse(child["excerpt"])
        row = result_for(child["report"], "ad-hominem")
        self.assertEqual(row["verdict"], "flag", row["reason"])
        self.assertEqual(tree["outcome"], "flagged")
        self.assertEqual(tree["stress"], "breaks")
        rendered = format_tree(tree)
        self.assertIn("L0→L1", rendered)
        self.assertIn("excerpt:excerpt", rendered)
        self.assertIn("flag", rendered)
        self.assertTrue(tree["unlimited"])
        records = nested_method_records(tree)
        flagged = [rec for rec in records if rec["verdict"] == "flag" and rec["entry_id"] == "ad-hominem"]
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0]["layer_path"], "L0→L1")
        self.assertEqual(flagged[0]["peel_path"], "excerpt:excerpt")
        self.assertTrue(flagged[0]["lead_to_check"])
        self.assertFalse(flagged[0]["substitute_for_hand_method"])

    def test_missing_fact_cite_can_flag_and_a_weak_window_stays_open(self):
        raw = _physicist()
        self.assertEqual(
            result_for(check_passage(raw), "appeal-to-authority")["verdict"],
            "possible_issue",
        )
        closed = check_nested(raw, expander=MapContextExpander.from_records([{
            "passage_id": "physicist_diet",
            "target_id": "e_auth",
            "kind": "cite",
            "expand": "Pat is not an expert on this question.",
        }]))
        cite = _peel(closed["node"], "cite", "e_auth")
        self.assertIsNotNone(cite)
        self.assertIsNotNone(cite["child"])
        row = result_for(cite["child"]["report"], "appeal-to-authority")
        self.assertEqual(row["verdict"], "flag", row["reason"])
        self.assertEqual(cite["child"]["layer_path"], "L0→L1")
        self.assertIn("cite:e_auth", cite["child"]["peel_path"])
        self.assertEqual(closed["outcome"], "flagged")

        still_open = check_nested(raw, expander=MapContextExpander.from_records([{
            "passage_id": "physicist_diet",
            "target_id": "e_auth",
            "kind": "cite",
            "expand": "The diet is popular in magazines.",
        }]))
        child = _peel(still_open["node"], "cite", "e_auth")["child"]
        row = result_for(child["report"], "appeal-to-authority")
        self.assertEqual(row["verdict"], "possible_issue", row["reason"])
        self.assertEqual(still_open["outcome"], "open")
        self.assertFalse(_flags(still_open["node"]))

    def test_sound_authority_survives_a_deeper_agreement_window(self):
        raw = _load("method_ex2_authority.json")
        tree = check_nested(raw, expander=MapContextExpander.from_records([{
            "passage_id": "method_ex2_authority",
            "target_id": "e_auth",
            "kind": "cite",
            "expand": "A further systematic review of the trial data agrees.",
        }]))
        self.assertEqual(tree["node"]["aggregate"], "no_issue")
        cite = _peel(tree["node"], "cite", "e_auth")
        self.assertIsNotNone(cite["child"])
        self.assertEqual(cite["child"]["aggregate"], "no_issue")
        self.assertFalse(_flags(tree["node"]))
        self.assertEqual(tree["stress"], "survives")
        self.assertEqual(tree["outcome"], "survives")

    def test_clean_surface_breaks_when_a_premise_child_is_fallacious(self):
        raw = _clean()
        bad = _load("method_ex1_ad_hominem.json")
        tree = check_nested(raw, expander=MapContextExpander.from_records([{
            "passage_id": "clean_surface",
            "target_id": "c_prem",
            "kind": "premise",
            "ir": bad,
        }]))
        self.assertEqual(tree["node"]["aggregate"], "no_issue")
        child = _peel(tree["node"], "premise", "c_prem")["child"]
        self.assertEqual(result_for(child["report"], "ad-hominem")["verdict"], "flag")
        self.assertEqual(tree["stress"], "breaks")
        self.assertEqual(tree["outcome"], "flagged")
        self.assertIn("premise:c_prem", child["peel_path"])

    def test_hard_flag_still_peels_premises(self):
        raw = _load("method_ex1_ad_hominem.json")
        tree = check_nested(raw, expander=MapContextExpander.from_records([]))
        self.assertEqual(tree["node"]["aggregate"], "flag")
        kinds = {peel["kind"] for peel in tree["node"]["children"]}
        self.assertIn("premise", kinds)
        self.assertTrue(tree["node"]["children"])
        self.assertTrue(all(peel["child"] is None for peel in tree["node"]["children"]))
        self.assertEqual(tree["node"]["stop"]["reason"], "hard_flag")

    def test_empty_expander_stops_an_open_gap_without_rewriting_the_parent(self):
        raw = _physicist()
        snapshot = json.dumps(raw, sort_keys=True)
        tree = check_nested(raw, expander=MapContextExpander.from_records([]))
        self.assertEqual(json.dumps(raw, sort_keys=True), snapshot)
        self.assertEqual(tree["node"]["aggregate"], "possible_issue")
        self.assertEqual(tree["node"]["stop"]["reason"], "empty_expander")
        self.assertEqual(tree["outcome"], "open")
        cite = _peel(tree["node"], "cite", "e_auth")
        self.assertIsNotNone(cite)
        self.assertIsNone(cite["child"])
        self.assertEqual(cite["stop"]["reason"], "empty_expander")

    def test_default_depth_is_unlimited_and_max_depth_is_a_valve(self):
        records = []
        for index in range(6):
            records.append({
                "passage_id": f"chain{index}",
                "target_id": f"p{index}",
                "kind": "premise",
                "ir": _chain(index + 1),
            })
        inner = MapContextExpander.from_records(records)
        unlimited = _Count(inner)
        deep = check_nested(_chain(0), expander=unlimited)
        depths = [node["depth"] for node in _walk(deep["node"]) if node.get("report")]
        self.assertIn(6, depths)
        self.assertEqual(max(depths), 6)
        self.assertIsNone(deep["max_depth"])
        self.assertEqual(unlimited.calls, 7)
        self.assertEqual(deep["stress"], "survives")

        capped_exp = _Count(MapContextExpander.from_records(records))
        capped = check_nested(_chain(0), expander=capped_exp, max_depth=2)
        capped_depths = [node["depth"] for node in _walk(capped["node"]) if node.get("report")]
        self.assertEqual(max(capped_depths), 2)
        self.assertNotIn(3, capped_depths)
        self.assertEqual(capped_exp.calls, 2)
        leaf = [node for node in _walk(capped["node"]) if node["depth"] == 2][0]
        self.assertEqual(leaf["stop"]["reason"], "max_depth")
        self.assertEqual(leaf["children"], [])

        seed_only = check_nested(_chain(0), expander=_Count(inner), max_depth=0)
        self.assertEqual(seed_only["node"]["stop"]["reason"], "max_depth")
        self.assertEqual(seed_only["node"]["children"], [])
        with self.assertRaises(ValueError):
            check_nested(_chain(0), max_depth=-1)

    def test_cycle_on_a_repeated_fingerprint(self):
        raw = _chain(0)
        counter = _Count(MapContextExpander.from_records([{
            "passage_id": "chain0",
            "target_id": "p0",
            "kind": "premise",
            "ir": _chain(0),
        }]))
        tree = check_nested(raw, expander=counter)
        self.assertEqual(counter.calls, 1)
        child = _peel(tree["node"], "premise", "p0")["child"]
        self.assertEqual(child["stop"]["reason"], "cycle")
        self.assertIsNone(child["report"])
        self.assertFalse(any(node.get("depth") == 2 and node.get("report") for node in _walk(tree["node"])))

    def test_contested_reading_stays_capped_after_a_full_window(self):
        raw = _load("method_ex1_ad_hominem.json")
        raw["excerpt"] = True
        raw["passage_id"] = "ex1_contested"
        raw["contested_reading"] = "whether lateness bears on the inspection"
        tree = check_nested(raw, expander=MapContextExpander.from_records([{
            "passage_id": "ex1_contested",
            "kind": "excerpt",
            "full": True,
            "expand": raw["source_text"],
        }]))
        child = _peel(tree["node"], "excerpt", "excerpt")["child"]
        row = result_for(child["report"], "ad-hominem")
        self.assertEqual(row["verdict"], "possible_issue", row["reason"])
        self.assertIn("contested", row["reason"])
        self.assertFalse(_flags(tree["node"]))
        self.assertEqual(tree["outcome"], "open")

    def test_invalid_child_does_not_raise_or_flag(self):
        raw = _physicist()
        tree = check_nested(raw, expander=MapContextExpander.from_records([{
            "passage_id": "physicist_diet",
            "target_id": "e_auth",
            "kind": "cite",
            "ir": {
                "passage_id": "bad",
                "source_text": "x",
                "steps": [],
                "claims": [],
                "edges": [],
                "not_a_field": True,
            },
        }]))
        cite = _peel(tree["node"], "cite", "e_auth")
        self.assertEqual(cite["stop"]["reason"], "invalid_ir")
        self.assertIsNone(cite["child"])
        self.assertFalse(_flags(tree["node"]))

    def test_peel_order_and_subclaim(self):
        source = "Alpha holds and beta holds, so the plan stands."
        raw = _passage(
            "two",
            source,
            [
                _claim("p2", "Beta holds.", "beta holds", "premise"),
                _claim("p1", "Alpha holds.", "Alpha holds", "premise"),
                _claim("k", "The plan stands.", "so the plan stands", "conclusion"),
            ],
            [
                _edge("e2", "supports", "p2", "k", "beta holds"),
                _edge("e1", "supports", "p1", "k", "Alpha holds"),
            ],
        )
        report = check_passage(raw)
        targets = [item["target_id"] for item in peel_targets(raw, report) if item["kind"] == "premise"]
        self.assertEqual(targets, ["p1", "p2"])

        nested = "Alpha holds, so beta holds, so the plan stands."
        mid = _passage(
            "mid",
            nested,
            [
                _claim("pA", "Alpha holds.", "Alpha holds", "premise"),
                _claim("pB", "Beta holds.", "beta holds", "premise"),
                _claim("pC", "The plan stands.", "so the plan stands", "conclusion"),
            ],
            [
                _edge("eAB", "supports", "pA", "pB", "Alpha holds"),
                _edge("eBC", "supports", "pB", "pC", "so beta holds"),
            ],
        )
        kinds = {
            item["target_id"]: item["kind"]
            for item in peel_targets(mid, check_passage(mid))
        }
        self.assertEqual(kinds.get("pA"), "premise")
        self.assertEqual(kinds.get("pB"), "subclaim")
        self.assertNotIn("pC", kinds)

    def test_parent_file_is_not_modified_and_cli_emits_the_layer_path(self):
        import tempfile
        raw = _load("method_ex1_ad_hominem.json")
        raw["excerpt"] = True
        raw["passage_id"] = "ex1_excerpt"
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            ir_path = folder / "ex1_excerpt.json"
            ir_path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
            before = ir_path.read_bytes()
            context = folder / "contexts.jsonl"
            context.write_text(json.dumps({
                "passage_id": "ex1_excerpt",
                "kind": "snapshot_window",
                "full": True,
                "expand": raw["source_text"],
            }) + "\n", encoding="utf-8")
            ctx_dir = folder / "ctx"
            ctx_dir.mkdir()
            (ctx_dir / "ex1_excerpt.json").write_text(json.dumps({
                "kind": "snapshot_window",
                "full": True,
                "expand": raw["source_text"],
            }), encoding="utf-8")
            out = io.StringIO()
            err = io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = nested_main([
                    "--context-map", str(context),
                    "--json",
                    "--method-record",
                    str(ir_path),
                ])
            self.assertEqual(code, 0, err.getvalue())
            self.assertEqual(ir_path.read_bytes(), before)
            payload = json.loads(out.getvalue())
            self.assertIsNone(payload["max_depth"])
            self.assertEqual(payload["trees"][0]["outcome"], "flagged")
            flagged = [
                rec for rec in payload["records"]
                if rec["verdict"] == "flag" and rec["entry_id"] == "ad-hominem"
            ]
            self.assertEqual(flagged[0]["layer_path"], "L0→L1")
            self.assertEqual(flagged[0]["kind"], "idea_detection_assist")
            self.assertTrue(flagged[0]["lead_to_check"])
            self.assertFalse(flagged[0]["substitute_for_hand_method"])

            text_out = io.StringIO()
            with redirect_stdout(text_out), redirect_stderr(io.StringIO()):
                status = nested_main([
                    "--context-dir", str(ctx_dir),
                    "--method-record",
                    str(ir_path),
                ])
            self.assertEqual(status, 0)
            rendered = text_out.getvalue()
            self.assertIn("Layer path: L0→L1", rendered)
            self.assertIn("idea_detection assist / lead-to-check", rendered)
            self.assertEqual(ir_path.read_bytes(), before)

    def test_two_runs_match(self):
        raw = _physicist()
        expander = MapContextExpander.from_records([{
            "passage_id": "physicist_diet",
            "target_id": "e_auth",
            "kind": "cite",
            "expand": "Pat is not an expert on this question.",
        }])
        first = check_nested(raw, expander=expander)
        second = check_nested(raw, expander=expander)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
