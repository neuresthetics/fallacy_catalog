"""Checker tests. METHOD fixtures plus the gates the design requires."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from idea_detection.check import check_passage, load_catalog, load_patterns, result_for
from idea_detection.eval_fixtures import FIXTURES, evaluate_file
from idea_detection.ir import normalize
from idea_detection.model import norm
from idea_detection.predicates import PREDICATES

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
            "claim_ids": [c["id"] for c in claims],
        }],
        "claims": claims,
        "edges": edges,
        "extractor": {"kind": "human", "charity_applied": True},
    }
    data.update(extra)
    return data


def _walk_predicates(node, found):
    if isinstance(node, dict):
        if isinstance(node.get("predicate"), str):
            found.add(node["predicate"])
        for value in node.values():
            _walk_predicates(value, found)
    elif isinstance(node, list):
        for value in node:
            _walk_predicates(value, found)


class CheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.patterns = load_patterns()

    def test_method_fixtures(self):
        for path in sorted(FIXTURES.glob("*.json")):
            ok, line = evaluate_file(path)
            self.assertTrue(ok, line)

    def test_ad_hominem_flag_is_only_flag_and_quotes_bind(self):
        report = check_passage(_load("method_ex1_ad_hominem.json"))
        self.assertTrue(report["ok"], report["errors"])
        row = result_for(report, "ad-hominem")
        self.assertEqual(row["verdict"], "flag")
        self.assertGreaterEqual(len(row["span_bindings"]), 5)
        source = norm(_load("method_ex1_ad_hominem.json")["source_text"])
        for span in row["span_bindings"]:
            self.assertIn(norm(span["quote"]), source)
        flags = [r["entry_id"] for r in report["results"] if r["verdict"] == "flag"]
        self.assertEqual(flags, ["ad-hominem"])

    def test_authority_lookalike_is_no_issue_because_forbid(self):
        report = check_passage(_load("method_ex2_authority.json"))
        row = result_for(report, "appeal-to-authority")
        self.assertEqual(row["verdict"], "no_issue")
        self.assertIn("ir_forbid", row["reason"])
        flags = [r["entry_id"] for r in report["results"] if r["verdict"] == "flag"]
        self.assertEqual(flags, [])

    def test_expert_agreement_with_settled_wording_still_no_issue(self):
        source = (
            "Every national health agency and the large reviews of the trial data "
            "agree that serious side effects from this vaccine are rare, so the risk is negligible."
        )
        ir = _passage(
            "expert_agree_settled",
            source,
            [
                _claim("c_src", "Agencies and trial reviews agree side effects are rare.", source.split(", so")[0], "premise"),
                _claim("c_k", "The risk is negligible.", "so the risk is negligible", "conclusion", scope="truth"),
            ],
            [_edge("e_auth", "appeals_to_source", "c_src", "c_k", "national health agency and the large reviews of the trial data agree", warrant="inductive")],
        )
        row = result_for(check_passage(ir), "appeal-to-authority")
        self.assertEqual(row["verdict"], "no_issue", row["reason"])

    def test_unstated_expertise_is_possible_issue_not_flag(self):
        source = "A famous physicist says this diet cures cancer, so it does."
        ir = _passage(
            "physicist_diet",
            source,
            [
                _claim("c_src", "A famous physicist says this diet cures cancer.", "A famous physicist says this diet cures cancer", "premise"),
                _claim("c_k", "This diet cures cancer.", "so it does", "conclusion"),
            ],
            [_edge("e_auth", "appeals_to_source", "c_src", "c_k", "A famous physicist says this diet cures cancer")],
        )
        row = result_for(check_passage(ir), "appeal-to-authority")
        self.assertEqual(row["verdict"], "possible_issue", row["reason"])
        self.assertTrue(row["missing_fact"])
        flags = [r["entry_id"] for r in check_passage(ir)["results"] if r["verdict"] == "flag"]
        self.assertEqual(flags, [])

    def test_stated_non_expert_flags_authority(self):
        source = "Lee is not an expert on bridges, but Lee says the bearings are fine, so they are fine."
        ir = _passage(
            "lee_not_expert",
            source,
            [
                _claim("c_src", "Lee is not an expert on bridges but says the bearings are fine.", "Lee is not an expert on bridges, but Lee says the bearings are fine", "premise"),
                _claim("c_k", "The bearings are fine.", "so they are fine", "conclusion"),
            ],
            [_edge("e_auth", "appeals_to_source", "c_src", "c_k", "Lee says the bearings are fine")],
        )
        report = check_passage(ir)
        row = result_for(report, "appeal-to-authority")
        self.assertEqual(row["verdict"], "flag", row["reason"])
        flags = [r["entry_id"] for r in report["results"] if r["verdict"] == "flag"]
        self.assertEqual(flags, ["appeal-to-authority"])

    def test_text_detectable_no_never_flags(self):
        source = "I already decided, so the report is wrong."
        ir = _passage(
            "bias_question",
            source,
            [_claim("c_k", "The report is wrong.", "so the report is wrong", "conclusion")],
            [],
        )
        patterns = self.patterns + [{
            "id": "confirmation-bias",
            "ir_pattern": {"all": [{"exists_claim": {"var": "K", "role_in": ["conclusion"]}}]},
            "ir_forbid": [],
        }]
        report = check_passage(ir, patterns=patterns)
        self.assertTrue(report["ok"], report["errors"])
        row = result_for(report, "confirmation-bias")
        self.assertEqual(row["verdict"], "possible_issue", row["reason"])
        self.assertIn("text_detectable", row["reason"])
        self.assertEqual(row["verdict"] == "flag", False)
        flags = [r["entry_id"] for r in report["results"] if r["verdict"] == "flag"]
        self.assertEqual(flags, [])
        self.assertEqual(self.catalog["confirmation-bias"]["text_detectable"], "no")

    def test_excerpt_and_contested_reading_cap_flags(self):
        base = _load("method_ex1_ad_hominem.json")
        excerpt = copy.deepcopy(base)
        excerpt["excerpt"] = True
        excerpt["passage_id"] = "ex1_excerpt"
        row = result_for(check_passage(excerpt), "ad-hominem")
        self.assertEqual(row["verdict"], "possible_issue", row["reason"])
        self.assertIn("excerpt", row["reason"])

        contested = copy.deepcopy(base)
        contested["contested_reading"] = "whether lateness bears on the inspection"
        contested["passage_id"] = "ex1_contested"
        row = result_for(check_passage(contested), "ad-hominem")
        self.assertEqual(row["verdict"], "possible_issue")
        self.assertIn("contested reading", row["reason"])

    def test_surface_insult_without_inference_does_not_flag(self):
        source = "Reyes is an idiot."
        ir = _passage(
            "insult_only",
            source,
            [_claim("c1", "Reyes is an idiot.", "Reyes is an idiot.", "report")],
            [],
        )
        flags = [r["entry_id"] for r in check_passage(ir)["results"] if r["verdict"] == "flag"]
        self.assertEqual(flags, [])

    def test_answered_reasons_block_ad_hominem(self):
        ir = _load("method_ex1_ad_hominem.json")
        ir = copy.deepcopy(ir)
        ir["edges"].append(_edge(
            "e_ans", "attacks_claim", "c_trait", "c_arg", "the corrosion readings",
        ))
        row = result_for(check_passage(ir), "ad-hominem")
        self.assertEqual(row["verdict"], "no_issue", row["reason"])

    def test_relevant_trait_blocks_ad_hominem(self):
        ir = copy.deepcopy(_load("method_ex1_ad_hominem.json"))
        ir["agents"][0]["traits"][0]["label"] = "the corrosion readings were mishandled"
        row = result_for(check_passage(ir), "ad-hominem")
        self.assertEqual(row["verdict"], "no_issue", row["reason"])

    def test_quote_not_in_passage_cannot_flag(self):
        ir = copy.deepcopy(_load("method_ex1_ad_hominem.json"))
        ir["edges"][1]["span"]["quote"] = "invented inferential wording"
        row = result_for(check_passage(ir), "ad-hominem")
        self.assertEqual(row["verdict"], "no_issue")

    def test_smuggled_verdict_is_rejected(self):
        ir = _load("method_ex1_ad_hominem.json")
        ir = copy.deepcopy(ir)
        ir["verdict"] = "flag"
        report = check_passage(ir)
        self.assertFalse(report["ok"])
        self.assertEqual(report["results"], [])

    def test_unknown_pattern_id_is_rejected(self):
        ir = _passage(
            "x",
            "The bridge is fine.",
            [_claim("c", "The bridge is fine.", "The bridge is fine.", "conclusion")],
            [],
        )
        report = check_passage(ir, patterns=[{"id": "not-a-real-fallacy", "ir_pattern": {"all": []}, "ir_forbid": []}])
        self.assertFalse(report["ok"])
        self.assertTrue(any("not in catalog" in err for err in report["errors"]))

    def test_hedge_language_blocks_settling(self):
        source = "A famous physicist says this diet cures cancer, so it may."
        ir = _passage(
            "physicist_may",
            source,
            [
                _claim("c_src", "A famous physicist says this diet cures cancer.", "A famous physicist says this diet cures cancer", "premise"),
                _claim("c_k", "This diet cures cancer.", "so it may", "conclusion", hedge="strong"),
            ],
            [_edge("e_auth", "appeals_to_source", "c_src", "c_k", "A famous physicist says this diet cures cancer")],
        )
        normalized = normalize(ir)
        self.assertEqual(normalized["claims"][1]["hedge"], "weak")
        row = result_for(check_passage(ir), "appeal-to-authority")
        self.assertEqual(row["verdict"], "no_issue", row["reason"])

    def test_normalizer_drops_illustration_supports_and_marks_defaults(self):
        source = "For example, cats. The burden of proof is on the county."
        ir = _passage(
            "norm",
            source,
            [
                _claim("c_ill", "For example, cats.", "For example, cats.", "illustration"),
                _claim("c_def", "The burden of proof is on the county.", "The burden of proof is on the county.", "premise"),
                _claim("c_k", "So the plant is unsafe.", "So the plant is unsafe.", "conclusion"),
            ],
            [_edge("e", "supports", "c_ill", "c_k", "For example, cats.")],
        )
        out = normalize(ir)
        self.assertEqual(out["edges"], [])
        default = next(c for c in out["claims"] if c["id"] == "c_def")
        self.assertEqual(default["role"], "default_rule")
        self.assertEqual(default["scope"], "procedural")

    def test_equivocation_flags_when_senses_shift(self):
        source = "A feather is light. What is light cannot be dark. So a feather cannot be dark."
        ir = _passage(
            "feather",
            source,
            [
                _claim("c1", "A feather is light.", "A feather is light", "premise"),
                _claim("c2", "What is light cannot be dark.", "What is light cannot be dark", "premise"),
                _claim("c3", "A feather cannot be dark.", "a feather cannot be dark", "conclusion"),
            ],
            [
                _edge("e1", "supports", "c1", "c3", "So a feather cannot be dark"),
                _edge("e2", "supports", "c2", "c3", "So a feather cannot be dark"),
            ],
            terms=[{
                "id": "t_light",
                "surface": "light",
                "senses": [
                    {"id": "s_weight", "gloss": "not heavy"},
                    {"id": "s_bright", "gloss": "not dark"},
                ],
            }],
            bindings=[
                {"term_id": "t_light", "claim_id": "c1", "sense_id": "s_weight", "span": {"quote": "A feather is light"}},
                {"term_id": "t_light", "claim_id": "c2", "sense_id": "s_bright", "span": {"quote": "What is light"}},
                {"term_id": "t_light", "claim_id": "c3", "sense_id": "s_bright", "span": {"quote": "a feather cannot be dark"}},
            ],
        )
        report = check_passage(ir)
        row = result_for(report, "equivocation")
        self.assertEqual(row["verdict"], "flag", row["reason"])
        flags = [item["entry_id"] for item in report["results"] if item["verdict"] == "flag"]
        self.assertEqual(flags, ["equivocation"])

    def test_begging_cycle_flags(self):
        source = "Her advice is trustworthy because she is honest, and she is honest because her advice is trustworthy."
        ir = _passage(
            "circle",
            source,
            [
                _claim("c_k", "Her advice is trustworthy.", "Her advice is trustworthy", "conclusion"),
                _claim("c_p", "She is honest.", "she is honest", "premise"),
            ],
            [
                _edge("e1", "supports", "c_p", "c_k", "because she is honest"),
                _edge("e2", "supports", "c_k", "c_p", "because her advice is trustworthy"),
            ],
        )
        row = result_for(check_passage(ir), "begging-the-question")
        self.assertEqual(row["verdict"], "flag", row["reason"])

    def test_cherry_picking_flags_and_pre_specification_blocks(self):
        source = "Scores rose at three schools and fell at the other seven. The programme works: look at those three schools."
        claims = [
            _claim("c_up", "Scores rose at three schools.", "Scores rose at three schools", "premise"),
            _claim("c_down", "Scores fell at the other seven.", "fell at the other seven", "premise"),
            _claim("c_k", "The programme works.", "The programme works", "conclusion"),
        ]
        edges = [
            _edge("e_sel", "selects_subset", "es1", "c_up", "look at those three schools"),
            _edge("e_sup", "supports", "c_up", "c_k", "The programme works"),
            _edge("e_ign", "ignores", "c_k", "c_down", "fell at the other seven", answered=False),
        ]
        evidence = {
            "id": "es1",
            "member_ids": ["c_up", "c_down"],
            "selection_time": "after_data",
            "stated_in_text": True,
            "direction": "against",
        }
        ir = _passage("cherry", source, claims, edges, evidence_sets=[evidence])
        row = result_for(check_passage(ir), "cherry-picking")
        self.assertEqual(row["verdict"], "flag", row["reason"])

        blocked = copy.deepcopy(ir)
        blocked["evidence_sets"][0]["selection_time"] = "before_data"
        row = result_for(check_passage(blocked), "cherry-picking")
        self.assertEqual(row["verdict"], "no_issue", row["reason"])
        self.assertIn("ir_forbid", row["reason"])

    def test_ignorance_flags_when_absence_is_the_proof(self):
        source = "No one has proved that ghosts don't exist, so they do."
        ir = _passage(
            "ghosts",
            source,
            [
                _claim("c_u", "No one has proved that ghosts don't exist.", "No one has proved that ghosts don't exist", "premise"),
                _claim("c_k", "Ghosts exist.", "so they do", "conclusion"),
            ],
            [_edge("e", "supports", "c_u", "c_k", "so they do")],
        )
        row = result_for(check_passage(ir), "argument-from-ignorance")
        self.assertEqual(row["verdict"], "flag", row["reason"])

    def test_false_cause_flags_correlation_and_not_a_hypothesis(self):
        source = "Ice cream sales rise in summer, and so do drownings, so ice cream causes drownings."
        ir = _passage(
            "ice",
            source,
            [
                _claim("c_corr", "Ice cream sales rise when drownings rise.", "Ice cream sales rise in summer, and so do drownings", "premise"),
                _claim("c_k", "Ice cream causes drownings.", "so ice cream causes drownings", "conclusion", asserts_cause=True),
            ],
            [_edge("e_cor", "correlates", "c_corr", "c_k", "Ice cream sales rise in summer, and so do drownings")],
        )
        row = result_for(check_passage(ir), "false-cause")
        self.assertEqual(row["verdict"], "flag", row["reason"])

        hedged = copy.deepcopy(ir)
        hedged["source_text"] = source + " This is a hypothesis worth testing."
        hedged["claims"][1]["text"] = "Ice cream causes drownings, as a hypothesis worth testing."
        hedged["claims"][1]["hedge"] = "weak"
        hedged["claims"][1]["scope"] = "investigate"
        row = result_for(check_passage(hedged), "false-cause")
        self.assertEqual(row["verdict"], "no_issue", row["reason"])

    def test_no_argument_passage_does_not_flag(self):
        source = "Identify the flaw in Ben's reply."
        ir = _passage(
            "lesson",
            source,
            [_claim("c", "Identify the flaw in Ben's reply.", "Identify the flaw in Ben's reply.", "report")],
            [],
        )
        ir["steps"][0]["no_argument"] = True
        flags = [r["entry_id"] for r in check_passage(ir)["results"] if r["verdict"] == "flag"]
        self.assertEqual(flags, [])

    def test_pilot_ids_and_predicates_stay_inside_the_catalog(self):
        names = set()
        outside = set()
        for entry in self.patterns:
            self.assertIn(entry["id"], self.catalog)
            _walk_predicates(entry.get("ir_pattern"), names)
            _walk_predicates(entry.get("ir_forbid"), names)
            outside.update(entry.get("outside_text_predicates") or [])
        self.assertTrue(names <= set(PREDICATES))
        self.assertTrue(outside <= set(PREDICATES))

    def test_package_does_not_consult_mindspace(self):
        package = ROOT / "idea_detection"
        for path in package.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("mindspace", text, path.name)


if __name__ == "__main__":
    unittest.main()
