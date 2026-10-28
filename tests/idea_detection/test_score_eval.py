"""Miss-taxonomy scoring. Synthetic rows plus published gold strings for the e2e misses."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from idea_detection.check import load_catalog, load_patterns
from idea_detection.score_eval import (
    COUSIN_IDS,
    build_alias_index,
    format_summary,
    load_results_csv,
    norm_label,
    pilots_for_acceptable,
    score_report,
    score_rows,
    summarize,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "idea_detection" / "examples" / "score_eval_example.csv"

ORIGINAL_EIGHT = (
    "ad-hominem",
    "appeal-to-authority",
    "equivocation",
    "false-cause",
    "begging-the-question",
    "cherry-picking",
    "straw-man",
    "argument-from-ignorance",
)


def _row(passage_id, truth, acceptable, flagged="", possible="", miss_class="", ok=""):
    item = {
        "id": passage_id,
        "truth": truth,
        "acceptable": acceptable,
        "flagged": flagged,
        "possible": possible,
        "miss_class": miss_class,
    }
    if ok != "":
        item["ok"] = ok
    return item


class ScoreEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.pilots = [entry["id"] for entry in load_patterns()]
        cls.index = build_alias_index(cls.catalog, cls.pilots)
        cls.eight = build_alias_index(cls.catalog, ORIGINAL_EIGHT)

    def _score(self, row, active_ids=None):
        ids = self.pilots if active_ids is None else active_ids
        return score_rows([row], catalog=self.catalog, active_ids=ids)[0]

    def test_thirteen_pilots_match_the_side_file(self):
        self.assertEqual(
            set(self.pilots),
            {
                "ad-hominem",
                "appeal-to-authority",
                "equivocation",
                "false-cause",
                "begging-the-question",
                "cherry-picking",
                "straw-man",
                "argument-from-ignorance",
                "hasty-generalization",
                "slippery-slope",
                "false-dilemma",
                "appeal-to-the-people",
                "guilt-by-association",
            },
        )

    def test_cousins_are_not_aliases_of_another_pilot(self):
        ad_hominem = self.index["ad-hominem"]
        ignorance = self.index["argument-from-ignorance"]
        for cousin_id in COUSIN_IDS:
            if cousin_id in self.index:
                continue
            for phrase in build_alias_index(self.catalog, [cousin_id])[cousin_id]:
                self.assertNotIn(phrase, ad_hominem, phrase)
                self.assertNotIn(phrase, ignorance, phrase)
        self.assertNotIn(norm_label("guilt by association"), ad_hominem)
        self.assertNotIn(norm_label("genetic fallacy"), ad_hominem)
        self.assertNotIn(norm_label("bulverism"), ad_hominem)
        self.assertNotIn(norm_label("ad hoc rescue"), ignorance)
        self.assertNotIn(norm_label("special pleading"), ignorance)
        self.assertIn(norm_label("guilt by association"), self.index["guilt-by-association"])

    def test_hit_uses_the_pilot_name_not_the_cousin(self):
        scored = self._score(_row("P005", "fallacy", "ad hominem (circumstantial); genetic fallacy", "ad-hominem"))
        self.assertEqual(scored["label"], "hit")
        self.assertEqual(scored["inside_pilots"], ["ad-hominem"])

    def test_genetic_alone_is_outside_and_not_an_ad_hominem_hit(self):
        missed = self._score(_row("g", "fallacy", "genetic fallacy"))
        self.assertEqual(missed["label"], "expected_outside")
        self.assertEqual(missed["inside_pilots"], [])
        flagged = self._score(_row("g2", "fallacy", "genetic fallacy", "ad-hominem"))
        self.assertEqual(flagged["label"], "wrong_flag")

    def test_guilt_by_association_follows_whether_it_is_a_pilot(self):
        current = self._score(_row("F18", "fallacy", "guilt-by-association|genetic-fallacy"))
        self.assertEqual(current["label"], "inside_miss")
        self.assertEqual(current["inside_pilots"], ["guilt-by-association"])
        earlier = self._score(
            _row("F18", "fallacy", "guilt-by-association|genetic-fallacy"),
            active_ids=ORIGINAL_EIGHT,
        )
        self.assertEqual(earlier["label"], "expected_outside")
        self.assertEqual(earlier["inside_pilots"], [])
        not_ad_hominem = self._score(_row("F18b", "fallacy", "guilt by association", "ad-hominem"))
        self.assertEqual(not_ad_hominem["label"], "wrong_flag")

    def test_other_cousins_stay_outside(self):
        for name in ("bulverism", "ad hoc rescue", "ad hoc hypothesis", "special pleading", "whataboutism"):
            scored = self._score(_row(name, "fallacy", name))
            self.assertEqual(scored["label"], "expected_outside", name)
            self.assertEqual(scored["inside_pilots"], [], name)

    def test_false_cause_family_names_count_for_that_pilot_only(self):
        scored = self._score(
            _row("P019", "borderline", "cum hoc ergo propter hoc; correlation implies causation")
        )
        self.assertEqual(scored["label"], "expected_charity")
        self.assertEqual(scored["inside_pilots"], ["false-cause"])
        hit = self._score(
            _row("P032", "fallacy", "cum hoc ergo propter hoc; correlation implies causation; false cause", "false-cause")
        )
        self.assertEqual(hit["label"], "hit")
        only_specific = self._score(
            _row("cum", "fallacy", "correlation implies causation", "false-cause")
        )
        self.assertEqual(only_specific["label"], "hit")

    def test_gate_labels(self):
        self.assertEqual(self._score(_row("l", "legit", "straw man", "straw-man"))["label"], "fp")
        self.assertEqual(self._score(_row("n", "no-argument", "", possible="appeal-to-authority"))["label"], "clean")
        self.assertEqual(
            self._score(_row("w", "fallacy", "division; appeal to pity", possible="appeal-to-authority"))["label"],
            "wrong_possible",
        )
        self.assertEqual(
            self._score(
                _row("p", "fallacy", "appeal to inappropriate authority", possible="appeal-to-authority")
            )["label"],
            "partial",
        )
        self.assertEqual(self._score(_row("bad", "fallacy", "straw man", ok="false"))["label"], "extractor_fail")

    def test_published_miss_strings(self):
        cases = {
            "P012": ("borderline", "appeal to inappropriate authority", "expected_charity", ["appeal-to-authority"]),
            "P048": (
                "borderline",
                "argument from ignorance; shifting the burden of proof",
                "expected_charity",
                ["argument-from-ignorance"],
            ),
            "P053": (
                "borderline",
                "guilt by association; ad hominem",
                "expected_charity",
                ["ad-hominem", "guilt-by-association"],
            ),
            "P069": ("borderline", "argument from ignorance", "expected_charity", ["argument-from-ignorance"]),
            "P095": (
                "fallacy",
                "ad hominem (circumstantial); appeal to motive",
                "inside_miss",
                ["ad-hominem"],
            ),
            "P110": (
                "borderline",
                "whataboutism; tu quoque (if used to deflect)",
                "expected_outside",
                [],
            ),
            "Q010": (
                "fallacy",
                "undistributed middle;affirming the consequent;formal fallacy;guilt by association;base rate fallacy",
                "inside_miss",
                ["guilt-by-association"],
            ),
            "R006": (
                "mixed",
                "ad hoc rescue;ad hoc hypothesis;special pleading;shifting the burden of proof;appeal to ignorance",
                "inside_miss",
                ["argument-from-ignorance"],
            ),
            "R063": (
                "contested",
                "tu quoque;circumstantial ad hominem;bulverism;two wrongs make a right",
                "contested_stay",
                ["ad-hominem"],
            ),
            "R072": (
                "mixed",
                "loaded language;circumstantial ad hominem;abusive ad hominem;slippery slope",
                "inside_miss",
                ["ad-hominem", "slippery-slope"],
            ),
        }
        for passage_id, (truth, acceptable, label, inside) in cases.items():
            scored = self._score(_row(passage_id, truth, acceptable))
            self.assertEqual(scored["label"], label, passage_id)
            self.assertEqual(scored["inside_pilots"], inside, passage_id)

    def test_eight_pilot_alias_narrowing_on_the_same_strings(self):
        q010 = self._score(
            _row(
                "Q010",
                "fallacy",
                "undistributed middle;affirming the consequent;formal fallacy;guilt by association",
            ),
            active_ids=ORIGINAL_EIGHT,
        )
        self.assertEqual(q010["label"], "expected_outside")
        self.assertEqual(
            pilots_for_acceptable("guilt by association; ad hominem", self.eight),
            ["ad-hominem"],
        )

    def test_miss_class_overrides_the_automatic_miss_label(self):
        ir_gap = self._score(
            _row("P110", "borderline", "whataboutism; tu quoque (if used to deflect)", miss_class="ir_gap")
        )
        self.assertEqual(ir_gap["label"], "ir_gap")
        pattern = self._score(_row("P095", "fallacy", "ad hominem (circumstantial); appeal to motive", miss_class="pattern_gap"))
        self.assertEqual(pattern["label"], "pattern_gap")
        stayed = self._score(_row("R063", "contested", "circumstantial ad hominem", miss_class="contested_stay"))
        self.assertEqual(stayed["label"], "contested_stay")
        with self.assertRaises(ValueError):
            self._score(_row("x", "fallacy", "straw man", miss_class="bug"))

    def test_miss_class_does_not_override_a_hit_or_a_false_positive(self):
        hit = self._score(_row("h", "fallacy", "straw man", "straw-man", miss_class="ir_gap"))
        self.assertEqual(hit["label"], "hit")
        fp = self._score(_row("f", "legit", "straw man", "straw-man", miss_class="expected_charity"))
        self.assertEqual(fp["label"], "fp")

    def test_check_report_adapter(self):
        report = {
            "passage_id": "ex",
            "ok": True,
            "results": [
                {"entry_id": "appeal-to-authority", "verdict": "possible_issue"},
                {"entry_id": "ad-hominem", "verdict": "no_issue"},
            ],
        }
        scored = score_report(
            report,
            truth="fallacy",
            acceptable="base-rate fallacy",
            catalog=self.catalog,
            active_ids=self.pilots,
        )
        self.assertEqual(scored["label"], "wrong_possible")
        self.assertEqual(scored["possible"], ["appeal-to-authority"])

    def test_example_csv_and_summary(self):
        rows = load_results_csv(EXAMPLE)
        scored = score_rows(rows, catalog=self.catalog, active_ids=self.pilots)
        labels = {row["id"]: row["label"] for row in scored}
        self.assertEqual(
            labels,
            {
                "ex-hit": "hit",
                "ex-fp": "fp",
                "ex-clean": "clean",
                "ex-charity": "expected_charity",
                "ex-outside": "expected_outside",
                "ex-wrong-possible": "wrong_possible",
                "ex-partial": "partial",
                "ex-ir-gap": "ir_gap",
                "ex-gba": "inside_miss",
                "ex-contested": "contested_stay",
            },
        )
        summary = summarize(scored)
        self.assertEqual(summary["n"], 10)
        self.assertEqual(summary["counts"]["fp"], 1)
        self.assertEqual(summary["counts"]["hit"], 1)
        text = format_summary(summary)
        self.assertIn("n=10", text)
        self.assertIn("wrong_possible=1", text)

    def test_round_trip_cli_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.csv"
            path.write_text(
                "id,set,truth,acceptable_fallacy_names,flagged,possible\n"
                "a,r1,fallacy,cherry picking,cherry-picking,\n"
                "b,fp,legit,guilt by association,,\n",
                encoding="utf-8",
            )
            scored = score_rows(load_results_csv(path), catalog=self.catalog, active_ids=self.pilots)
        self.assertEqual([row["label"] for row in scored], ["hit", "clean"])
        summary = summarize(scored)
        self.assertEqual(summary["by_set"]["r1"]["hit"], 1)
        self.assertEqual(summary["by_set"]["fp"]["clean"], 1)
        json.dumps(scored)
