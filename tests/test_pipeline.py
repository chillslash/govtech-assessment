"""Standard-library unit tests, plus real AGO PDF evidence checks when present."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
# Local restricted Gateway setup can install wheels under .deps rather than a venv.
if (ROOT / ".deps").exists():
    sys.path.insert(0, str(ROOT / ".deps"))

from audit_assurance.core import Page, candidate_pages, evaluate, normalise, read_report, validate_predictions, normalise_observation_ids, selected_anchor_coverage


def record(quote="Account review was incomplete across servers.", page=1):
    return {"entity": "Example Agency", "observation_id": "12", "weakness": "Account reviews incomplete",
            "control_area": "access_lifecycle", "evidence_quote": quote, "pdf_page": page}


class AuditPrototypeTests(unittest.TestCase):
    def setUp(self):
        self.pages = [Page(1, "10", "12. Account\nreview was incomplete across servers."),
                      Page(2, "11", "13. Management said the review was now complete.")]

    def test_whitespace_normalisation(self):
        self.assertEqual(normalise("Account\n review\twas"), "Account review was")

    def test_evidence_acceptance(self):
        accepted, rejected = validate_predictions([record()], self.pages, "sample.pdf")
        self.assertEqual(len(accepted), 1)
        self.assertFalse(rejected)
        self.assertEqual(accepted[0]["printed_page"], "10")
        self.assertEqual(accepted[0]["review_status"], "proposed")

    def test_incorrect_page_and_fabricated_quote_rejected(self):
        accepted, rejected = validate_predictions([record(page=2), record("Nonexistent security control failure.")], self.pages, "sample.pdf")
        self.assertEqual(accepted, [])
        self.assertEqual(len(rejected), 2)
        self.assertTrue(all("evidence quote not found on cited PDF page" in r["errors"] for r in rejected))

    def test_invalid_taxonomy_rejected(self):
        item = record()
        item["control_area"] = "totally_unrecognised"
        accepted, rejected = validate_predictions([item], self.pages, "sample.pdf")
        self.assertFalse(accepted)
        self.assertEqual(rejected[0]["errors"], ["unknown control_area"])

    def test_one_to_one_evaluation_no_double_credit(self):
        gold = [{**record(), "document_id": "sample.pdf"}]
        predicted = [gold[0], gold[0]]
        metrics = evaluate(gold, predicted)
        self.assertEqual(metrics["matched"], 1)
        self.assertEqual(metrics["false_positives"], 1)
        self.assertEqual(metrics["recall"], 1)
        self.assertEqual(metrics["precision"], .5)

    def test_candidate_discovery_not_a_completeness_claim(self):
        got = candidate_pages([Page(1, "1", "No technology issues"), Page(2, "2", "Privileged account access rights were excessive")])
        self.assertEqual(got[0]["pdf_page"], 2)

    def test_numeric_observation_id_repair_is_narrow_and_auditable(self):
        originals = [dict(record(), observation_id=78), dict(record(), observation_id=999),
                     dict(record(), observation_id=True)]
        converted, repaired = normalise_observation_ids(originals, {"78", "80"})
        self.assertEqual(repaired, [0])
        self.assertEqual(converted[0]["observation_id"], "78")
        self.assertEqual(converted[1]["observation_id"], 999)
        self.assertIs(converted[2]["observation_id"], True)
        self.assertEqual(originals[0]["observation_id"], 78)

    def test_selected_anchor_coverage_requires_matching_observation_and_category(self):
        target = dict(record(), document_id="sample.pdf", label_id="L1", observation_id="36b")
        proposal = dict(target, evidence_quote="Another valid excerpt", label_id=None)
        result = selected_anchor_coverage([target], [proposal])
        self.assertEqual(result["covered"], 1)
        self.assertEqual(result["matched_labels"], ["L1"])
        self.assertEqual(selected_anchor_coverage([target], [dict(proposal, observation_id="36a")])["covered"], 0)
        self.assertEqual(selected_anchor_coverage([target, target], [proposal])["covered"], 1)

    def test_recorded_luna_run_can_be_revalidated_without_model_call(self):
        snapshot = ROOT / "data" / "evaluations" / "phase1-dev-gpt6-luna-20261010.json"
        if not snapshot.exists():
            self.skipTest("Live run snapshot not present")
        data = json.loads(snapshot.read_text(encoding="utf-8"))
        labels = json.loads((ROOT / "data" / "labels-dev.json").read_text(encoding="utf-8"))
        total_good = total_repaired = strict_matches = covered = 0
        for group in data["groups"]:
            source = ROOT / "data" / "raw" / group["document_id"]
            if not source.exists():
                self.skipTest("Public AGO PDFs not downloaded")
            adjusted, indices = normalise_observation_ids(
                group["raw_model_records"], set(group["target_observations"])
            )
            self.assertEqual(indices, group["normalised_observation_indices"])
            valid, rejected = validate_predictions(
                adjusted, read_report(source), group["document_id"]
            )
            self.assertFalse(rejected)
            gold = [x for x in labels if x["document_id"] == group["document_id"]
                    and x["pdf_page"] in group["pdf_pages"]]
            total_good += len(valid)
            total_repaired += len(indices)
            strict_matches += evaluate(gold, valid)["matched"]
            covered += selected_anchor_coverage(gold, valid)["covered"]
        self.assertEqual((total_good, total_repaired, strict_matches, covered),
                         (17, 11, 8, 10))

    def test_anao_report_summaries_never_enter_prompt(self):
        from scripts.run_anao_pilot import prepare_prompt
        pages = [
            Page(1, "1", "The Auditor-General summary has the SECRET REFERENCE ANSWER."),
            Page(2, "2", "2.56 AUSTRAC has inadequate SIEM coverage."),
        ]
        prompt = prepare_prompt(pages, [2], [1])
        self.assertIn("2.56 AUSTRAC has inadequate SIEM coverage", prompt)
        self.assertNotIn("SECRET REFERENCE ANSWER", prompt)
        with self.assertRaises(ValueError):
            prepare_prompt(pages, [1], [1])

    def test_anao_page_selection_and_response_shape(self):
        from scripts.run_anao_pilot import page_numbers, parse_model_output
        self.assertEqual(page_numbers("4, 2,4", 5), [2, 4])
        with self.assertRaises(ValueError):
            page_numbers("2-5", 9)
        with self.assertRaises(ValueError):
            page_numbers("0, 1", 9)
        self.assertEqual(parse_model_output('{"weaknesses": []}'), [])
        with self.assertRaises(ValueError):
            parse_model_output('{"wrong": []}')

    def test_anao_paragraph_number_repair_requires_source(self):
        from scripts.run_anao_pilot import normalise_anao_ids
        pages = [Page(21, "21", "2.56 AUSTRAC control deficiency.")]
        original = [
            dict(record(), pdf_page=21, observation_id=2.56),
            dict(record(), pdf_page=21, observation_id=3.7),
            dict(record(), pdf_page=21, observation_id="2.56"),
        ]
        fixed, corrected = normalise_anao_ids(original, pages)
        self.assertEqual(corrected, [0])
        self.assertEqual(fixed[0]["observation_id"], "2.56")
        self.assertEqual(fixed[1]["observation_id"], 3.7)
        self.assertEqual(original[0]["observation_id"], 2.56)

    def test_saved_anao_pilots_have_verified_source_pages(self):
        cases = (("anao-2021-pilot.json", "anao-2021-strategies.pdf", 2),
                 ("anao-2024-pilot.json", "anao-2024-incidents.pdf", 7))
        for snapshot, source, expected in cases:
            with self.subTest(source=source):
                path = ROOT / "data" / "evaluations" / snapshot
                pdf = ROOT / "data" / "raw" / source
                if not path.exists() or not pdf.exists():
                    self.skipTest("ANAO pilot snapshot or public PDF is missing")
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["model"], "gpt-6-luna")
                self.assertEqual(payload["reasoning"], "medium")
                self.assertFalse(set(payload["detail_pdf_pages_supplied"])
                                 & set(payload["summary_pdf_pages_withheld"]))
                self.assertEqual(len(payload["source_verified"]), expected)
                self.assertFalse(payload["rejected"])
                pages = read_report(pdf)
                accepted, rejected = validate_predictions(
                    payload["source_verified"], pages, source)
                self.assertFalse(rejected)
                self.assertEqual(len(accepted), expected)
                self.assertTrue(all(
                    row["pdf_page"] in payload["detail_pdf_pages_supplied"]
                    for row in accepted))

    def test_manual_anchors_against_real_reports(self):
        path = ROOT / "data" / "labels-dev.json"
        if not path.exists():
            self.skipTest("Dev labels not present")
        records = json.loads(path.read_text(encoding="utf-8"))
        if not all((ROOT / "data" / "raw" / x["document_id"]).exists() for x in records):
            self.skipTest("Real local reports not present; download the official PDFs first")
        self.assertGreaterEqual(len(records), 12)
        cache = {}
        for item in records:
            filename = item["document_id"]
            if filename not in cache:
                cache[filename] = read_report(ROOT / "data" / "raw" / filename)
            accepted, rejected = validate_predictions([item], cache[filename], filename)
            self.assertFalse(rejected, f"{item['label_id']}: {rejected}")
            self.assertEqual(len(accepted), 1)


if __name__ == "__main__":
    unittest.main()
