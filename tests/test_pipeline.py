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

from audit_assurance.core import Page, candidate_pages, evaluate, normalise, read_report, validate_predictions


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
