"""Tests for whole-report discovery, atomic extraction and source locators."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"src"))
if (ROOT/".deps").exists():
    sys.path.insert(0,str(ROOT/".deps"))
from audit_assurance.core import Page
from audit_assurance.discovery import discover_pages, findings_bounds, page_discovery_score
from scripts.run_anao_v2 import atomic_prompt, locator_error


class ImprovedPipelineTests(unittest.TestCase):
    def test_discovery_bounds_and_negative_signal(self):
        text=["No relevant audit observations" for _ in range(17)]
        text[0]="Summary and recommendations. Security events are not monitored."
        text[11]="2. Assessment of the cyber security controls."
        text[12]="AUSTRAC has not documented cybersecurity event monitoring processes."
        text[13]="Systems are monitored, controls are implemented, all good."
        text[14]="Appendices"
        text[15]="Appendices: unassessed security risks were not documented."
        pages=[Page(i+1,str(i+1),s) for i,s in enumerate(text)]
        self.assertEqual(findings_bounds(pages),(12,14))
        found=discover_pages(pages,max_pages=1,min_score=2)
        self.assertEqual(found["selected_pdf_pages"],[13])
        self.assertTrue(all(12<=x["pdf_page"]<=14 for x in found["ranked_candidates"]))
        self.assertGreater(page_discovery_score(text[12])[0],page_discovery_score(text[13])[0])

    def test_discovery_rejects_unknown_document_structure(self):
        with self.assertRaises(ValueError):
            discover_pages([Page(1,None,"security issues"),Page(2,None,"no access")])

    def test_atomic_prompt_withholds_summary_and_removes_sample_id(self):
        pages=[Page(1,None,"SECRET SUMMARY REFERENCE"),
               Page(2,None,"2.45 Agency lacks monitoring control.")]
        prompt=atomic_prompt(pages,[2],[1])
        self.assertNotIn("SECRET SUMMARY REFERENCE",prompt)
        self.assertIn("independently remediable",prompt)
        self.assertNotIn('STRING such as "2.56"',prompt)
        self.assertIn("2.45 Agency lacks monitoring control.",prompt)

    def test_source_locator_matches_actual_paragraph_and_table(self):
        page=("2.11 A failure in monitoring.\n"
              "2.12 A process was not documented.\n"
              "Table 2.4: Reporting on security\n"
              "The reporting timeframe was not defined.\n"
              "Table 2.5: Maturity\n"
              "The policy was not reviewed.")
        self.assertIsNone(locator_error({
            "observation_id":"2.12","evidence_quote":"A process was not documented."},page))
        self.assertIsNone(locator_error({
            "observation_id":"Table 2.4","evidence_quote":"The reporting timeframe was not defined."},page))
        self.assertEqual(locator_error({
            "observation_id":"2.56","evidence_quote":"A process was not documented."},page),
            "numbered paragraph identifier not found on cited page")
        self.assertEqual(locator_error({
            "observation_id":"Table 2.4","evidence_quote":"The policy was not reviewed."},page),
            "quote not within cited paragraph/table")
        self.assertEqual(locator_error({
            "observation_id":"2.11","evidence_quote":"A process was not documented."},page),
            "quote not within cited paragraph/table")

    def test_page_only_locator_is_page_scoped(self):
        row = {"observation_id":"PDF page 36","pdf_page":36,
               "evidence_quote":"PM&C did not implement the control."}
        self.assertIsNone(locator_error(row, "PM&C did not implement the control."))
        self.assertEqual(
            locator_error(dict(row,pdf_page=37), "PM&C did not implement the control."),
            "page-only locator does not match cited physical PDF page")

    def test_replay_final_v2_records(self):
        import json
        from audit_assurance.core import read_report, validate_predictions
        for year, name in (("2021","anao-2021-strategies.pdf"),
                           ("2024","anao-2024-incidents.pdf")):
            path=ROOT/"data"/"raw"/name
            if not path.exists():
                self.skipTest("Local public ANAO PDFs absent")
            pages=read_report(path)
            for mode in ("matched","discovered"):
                f=ROOT/"data"/"evaluations"/f"anao-v2-final-{mode}-{year}.json"
                if not f.exists():
                    self.skipTest("Final experiment unavailable")
                result=json.loads(f.read_text(encoding="utf8"))
                valid,rejected=validate_predictions(result["source_verified"],pages,name)
                self.assertFalse(rejected)
                self.assertEqual(len(valid),len(result["source_verified"]))
                for row in valid:
                    self.assertIn(row["pdf_page"],result["selected_pdf_pages"])
                    self.assertIsNone(locator_error(row,pages[row["pdf_page"]-1].text))

if __name__=="__main__":
    unittest.main()
