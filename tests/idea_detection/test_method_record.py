"""METHOD record renderer. Quotes come only from closed checker spans."""

from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from idea_detection.check import check_passage, load_catalog, load_patterns, main as check_main, result_for
from idea_detection.eval_fixtures import FIXTURES
from idea_detection.model import norm
from idea_detection.record import (
    CONDITION_SPANS,
    LOOKALIKE_FORBID_INDEX,
    format_method_record,
    main as record_main,
    render_records,
)


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


def _condition(record, number):
    for item in record["conditions"]:
        if item["n"] == number:
            return item
    raise AssertionError(f"no condition {number}")


class MethodRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.patterns = load_patterns()

    def _records(self, raw, verdicts=("flag", "possible_issue")):
        report = check_passage(raw, catalog=self.catalog, patterns=self.patterns)
        self.assertTrue(report["ok"], report["errors"])
        return render_records(
            report,
            ir=raw,
            catalog=self.catalog,
            patterns=self.patterns,
            verdicts=verdicts,
        )

    def test_span_maps_stay_inside_catalog_and_pattern_bounds(self):
        by_pattern = {item["id"]: item for item in self.patterns}
        for entry_id, spec in CONDITION_SPANS.items():
            entry = self.catalog[entry_id]
            count = len(entry["required_conditions"])
            for number in spec:
                self.assertGreaterEqual(number, 1)
                self.assertLessEqual(number, count, entry_id)
            self.assertIn(entry_id, by_pattern)
        for entry_id, pairing in LOOKALIKE_FORBID_INDEX.items():
            entry = self.catalog[entry_id]
            forbid_count = len(by_pattern[entry_id].get("ir_forbid") or [])
            look_count = len(entry["legitimate_lookalikes"])
            for number, indexes in pairing.items():
                self.assertGreaterEqual(number, 1)
                self.assertLessEqual(number, look_count, entry_id)
                for index in indexes:
                    self.assertGreaterEqual(index, 0)
                    self.assertLess(index, forbid_count, entry_id)

    def test_method_example_1_flag_record_quotes_conditions(self):
        raw = _load("method_ex1_ad_hominem.json")
        records = self._records(raw)
        self.assertEqual([item["entry_id"] for item in records], ["ad-hominem"])
        record = records[0]
        self.assertEqual(record["entry_name"], "Ad hominem (abusive)")
        self.assertEqual(record["verdict"], "flag")
        self.assertEqual(record["passage"], raw["source_text"])
        self.assertEqual(record["passage_source"], "ir.source_text")
        self.assertTrue(record["spans_support_every_condition"])
        self.assertFalse(record["substitute_for_hand_method"])
        self.assertFalse(record["hand_method_required"])
        self.assertEqual(record["kind"], "idea_detection_assist")
        self.assertIn("lead-to-check", format_method_record(record).splitlines()[0])
        source = norm(raw["source_text"])
        for cond in record["conditions"]:
            self.assertEqual(cond["status"], "met_by_span", cond)
            self.assertTrue(cond["met_by"], cond)
            for quote in cond["met_by"]:
                self.assertIn(norm(quote), source)
        self.assertIn("the bridge needs new bearings", _condition(record, 1)["met_by"][0])
        self.assertIn("fired from her last job", _condition(record, 2)["met_by"][0])
        joined = " ".join(_condition(record, 3)["met_by"])
        self.assertIn("ignore her bridge argument", joined)
        self.assertIn("fired from her last job for showing up late", _condition(record, 4)["met_by"][0])
        text = format_method_record(record)
        self.assertIn("Entry: Ad hominem (abusive) (ad-hominem)", text)
        self.assertIn("Verdict: flag", text)
        self.assertIn("Look-alikes were checked via ir_forbid and none matched.", text)
        self.assertIn("ir_forbid `claim_rests_on_testimony` did not match", text)
        self.assertNotIn("does not apply because", text)
        self.assertNotIn("punctuality has no bearing", text)
        self.assertNotIn("divorced three times", text)
        self.assertIn("idea_detection assist", text)
        self.assertIn("not a hand family review", record["other_entries_considered"])
        self.assertIn("guilt-by-association", record["other_entries_considered"])

    def test_method_example_2_emits_no_flag_record(self):
        raw = _load("method_ex2_authority.json")
        records = self._records(raw)
        self.assertEqual(records, [])
        text = format_method_record({
            "passage": raw["source_text"],
            "entry_id": "appeal-to-authority",
            "entry_name": "Appeal to authority (illegitimate)",
            "verdict": "flag",
            "verdict_label": "flag",
            "conditions": [],
            "lookalikes": [],
            "lookalikes_note": "",
            "reason": "",
            "strongest_reading": {},
        })
        # The default batch must not build that flag. Render the real passage.
        from idea_detection.record import format_passage_section
        section = format_passage_section(raw["passage_id"], records, source_path=None, verdicts=("flag", "possible_issue"))
        self.assertIn("No record", section)
        self.assertNotIn("Verdict: flag", section)
        self.assertNotIn("Entry: Appeal to authority", section)
        self.assertNotIn(text, section)

    def test_example_2_no_issue_record_says_lookalike_applies(self):
        raw = _load("method_ex2_authority.json")
        records = self._records(raw, verdicts=("no_issue",))
        authority = next(item for item in records if item["entry_id"] == "appeal-to-authority")
        self.assertEqual(authority["verdict"], "no_issue")
        self.assertNotEqual(authority["verdict"], "flag")
        matched = [item for item in authority["lookalikes"] if item["status"] == "forbid_matched"]
        self.assertTrue(matched)
        self.assertIn("applies", matched[0]["note"])
        self.assertIn("source_expert_in_field+passage_reports_expert_agreement", matched[0]["note"])
        text = format_method_record(authority)
        self.assertIn("Verdict: no issue", text)
        self.assertNotIn("Verdict: flag", text)
        self.assertNotIn("Look-alikes were checked via ir_forbid and none matched.", text)
        self.assertNotIn("does not apply because", text)

    def test_missing_span_does_not_invent_a_quote(self):
        raw = _load("method_ex1_ad_hominem.json")
        report = check_passage(raw, catalog=self.catalog, patterns=self.patterns)
        row = copy.deepcopy(result_for(report, "ad-hominem"))
        row["span_bindings"] = [
            span for span in row["span_bindings"]
            if span.get("name") != "trait_irrelevant_to_reasons"
        ]
        report = {
            "passage_id": report["passage_id"],
            "ok": True,
            "errors": [],
            "results": [row],
        }
        record = render_records(report, ir=raw, catalog=self.catalog, patterns=self.patterns)[0]
        cond = _condition(record, 4)
        self.assertEqual(cond["status"], "unbound")
        self.assertEqual(cond["met_by"], [])
        self.assertNotIn("met by", cond["note"])
        self.assertIn("not span-mapped", cond["note"])
        self.assertIn("trait_irrelevant_to_reasons", cond["note"])
        self.assertNotIn("fired from her last job", cond["note"])
        self.assertTrue(record["hand_method_required"])
        self.assertFalse(record["spans_support_every_condition"])
        text = format_method_record(record)
        self.assertIn("Do not use this record as a substitute for a hand METHOD review.", text)
        line = next(line for line in text.splitlines() if line.startswith("  4. "))
        self.assertNotIn("met by", line)
        self.assertNotIn("fired from", line)

    def test_quote_absent_from_passage_is_not_shown(self):
        raw = _load("method_ex1_ad_hominem.json")
        report = check_passage(raw, catalog=self.catalog, patterns=self.patterns)
        row = copy.deepcopy(result_for(report, "ad-hominem"))
        planted = "a fabricated citation that is not in the passage"
        for span in row["span_bindings"]:
            if span.get("name") == "exists_claim":
                span["quote"] = planted
        report = {
            "passage_id": report["passage_id"],
            "ok": True,
            "errors": [],
            "results": [row],
        }
        record = render_records(report, ir=raw, catalog=self.catalog, patterns=self.patterns)[0]
        cond = _condition(record, 1)
        self.assertEqual(cond["met_by"], [])
        self.assertNotEqual(cond["status"], "met_by_span")
        blob = json.dumps(record["conditions"])
        self.assertNotIn(planted, blob)
        self.assertNotIn(planted, format_method_record(record))

    def test_open_outside_text_span_is_not_satisfaction(self):
        source = "A famous physicist says this diet cures cancer, so it does."
        raw = _passage(
            "physicist_diet",
            source,
            [
                _claim("c_src", "A famous physicist says this diet cures cancer.", "A famous physicist says this diet cures cancer", "premise"),
                _claim("c_k", "This diet cures cancer.", "so it does", "conclusion"),
            ],
            [_edge("e_auth", "appeals_to_source", "c_src", "c_k", "A famous physicist says this diet cures cancer")],
        )
        report = check_passage(raw, catalog=self.catalog, patterns=self.patterns)
        row = result_for(report, "appeal-to-authority")
        self.assertEqual(row["verdict"], "possible_issue")
        self.assertTrue(any(
            span.get("name") == "source_not_expert_on_question" and span.get("open") is True
            for span in row["span_bindings"]
        ))
        record = self._records(raw)[0]
        self.assertEqual(record["verdict"], "possible_issue")
        self.assertEqual(record["missing_fact"], row["missing_fact"])
        supported = _condition(record, 1)
        self.assertEqual(supported["status"], "met_by_span")
        gap = _condition(record, 2)
        self.assertEqual(gap["status"], "open_span")
        self.assertEqual(gap["met_by"], [])
        self.assertIn("not met from a closed span", gap["note"])
        self.assertIn("not satisfaction", gap["note"])
        self.assertIn("outside_text_conditions", gap["note"])
        text = format_method_record(record)
        self.assertIn(f"Verdict: possible issue ({row['missing_fact']})", text)
        gap_line = next(line for line in text.splitlines() if line.startswith("  2. "))
        self.assertNotIn("met by", gap_line)

        legacy = copy.deepcopy(row)
        for span in legacy["span_bindings"]:
            span.pop("open", None)
        legacy_report = {
            "passage_id": report["passage_id"],
            "ok": True,
            "errors": [],
            "results": [legacy],
        }
        legacy_record = render_records(
            legacy_report, ir=raw, catalog=self.catalog, patterns=self.patterns,
        )[0]
        self.assertEqual(_condition(legacy_record, 2)["status"], "open_span")
        self.assertEqual(_condition(legacy_record, 2)["met_by"], [])

    def test_unmapped_condition_stays_unquoted_on_a_flag(self):
        source = (
            "If we let students redo one test, soon they'll expect to redo every test, "
            "and degrees will be worthless."
        )
        raw = _passage(
            "slope_soon",
            source,
            [
                _claim("c1", "We let students redo one test.", "let students redo one test", "premise"),
                _claim("c2", "They'll expect to redo every test.", "they'll expect to redo every test", "premise"),
                _claim("c_k", "Degrees will be worthless.", "degrees will be worthless", "conclusion"),
            ],
            [
                _edge("e1", "causes", "c1", "c2", "soon they'll expect to redo every test"),
                _edge("e2", "causes", "c2", "c_k", "and degrees will be worthless"),
            ],
        )
        record = next(item for item in self._records(raw) if item["entry_id"] == "slippery-slope")
        self.assertEqual(record["verdict"], "flag")
        first = _condition(record, 1)
        self.assertEqual(first["status"], "not_span_mapped")
        self.assertEqual(first["met_by"], [])
        self.assertIn("No quote is attached", first["note"])
        self.assertEqual(_condition(record, 2)["status"], "met_by_span")
        self.assertEqual(_condition(record, 3)["status"], "met_by_span")
        for quote in _condition(record, 2)["met_by"] + _condition(record, 3)["met_by"]:
            self.assertIn(norm(quote), norm(source))
        self.assertTrue(record["hand_method_required"])
        note = record["lookalikes_note"]
        self.assertIn("none matched", note)
        self.assertIn("not ruled out", note)
        unpaired = next(item for item in record["lookalikes"] if item["n"] == 1)
        self.assertEqual(unpaired["status"], "not_paired")

    def test_cli_batch_folder_and_json_report(self):
        buf = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            code = check_main([
                "--method-record",
                str(FIXTURES),
            ])
        self.assertEqual(code, 0, err.getvalue())
        text = buf.getvalue()
        self.assertEqual(text.count("Verdict: flag"), 1)
        self.assertIn("ad-hominem", text)
        self.assertIn("method_ex2_authority", text)
        self.assertIn("No record", text)
        self.assertNotIn("divorced three times", text)

        raw = _load("method_ex1_ad_hominem.json")
        report = check_passage(raw)
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "report.json"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out), redirect_stderr(io.StringIO()):
                status = record_main([
                    "--json", str(report_path),
                    "--ir", str(FIXTURES / "method_ex1_ad_hominem.json"),
                    "--format", "jsonl",
                ])
            self.assertEqual(status, 0)
            rows = [json.loads(line) for line in out.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["entry_id"], "ad-hominem")
        self.assertEqual(rows[0]["passage_source"], "ir.source_text")
        self.assertEqual(rows[0]["verdict"], "flag")
        self.assertTrue(rows[0]["conditions"][0]["met_by"])


if __name__ == "__main__":
    unittest.main()
