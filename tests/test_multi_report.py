"""Focused regression checks before running expanded five-report pilot."""
import json,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"src"),str(ROOT/".deps")]
from audit_assurance.core import Page
from audit_assurance.llm_discovery import rank_pages,discovery_prompt,validate_discovery
from audit_assurance.cross_report import index_findings,theme_prompt,validate_themes

class MultiReportTests(unittest.TestCase):
 def setUp(self):
  self.pages=[Page(1,"1","Summary: information security was not effective"),
    Page(2,"2","2.3 Agency has not documented its security event monitoring process."),
    Page(3,"3","2.4 The agency has completed the cybersecurity assessment.")]
 def test_shortlist_excludes_summary(self):
  out=rank_pages(self.pages,2,3,2)
  self.assertTrue(all(x["pdf_page"]>=2 for x in out))
  self.assertIn("=== PDF PAGE 2 ===",discovery_prompt(self.pages,[2]))
 def test_discovery_quote_and_page(self):
  good=json.dumps({"candidates":[{"pdf_page":2,
   "evidence_quote":"has not documented its security event monitoring process.",
   "why":"Missing monitoring documentation"}]})
  found,bad=validate_discovery(good,[2],self.pages)
  self.assertEqual(len(found),1);self.assertFalse(bad)
  found,bad=validate_discovery(good,[3],self.pages)
  self.assertFalse(found);self.assertEqual(len(bad),1)
 def test_recommendation_only_no_automatic_credit(self):
  self.assertIn("Exclude recommendations",discovery_prompt(self.pages,[2]))
 def test_theme_rejects_single_report_or_fabricated_id(self):
  r=lambda name,agency,weak:{"document_id":name,"source_verified":[{
      "entity":agency,"observation_id":"2.3","pdf_page":2,
      "control_area":"logging_monitoring","weakness":weak,
      "evidence_quote":"not documented"}]}
  rows=index_findings([r("a.pdf","Agency A","Missing logging policy"),
                       r("b.pdf","Agency B","Missing event review")])
  self.assertEqual(len(rows),2)
  raw=lambda ids:json.dumps({"themes":[{"name":"Monitoring",
    "description":"Insufficiently documented monitoring","finding_ids":ids}]})
  valid,bad=validate_themes(raw(["F001","F002"]),rows)
  self.assertEqual(len(valid),1);self.assertFalse(bad)
  self.assertEqual(valid[0]["report_count"],2)
  valid,bad=validate_themes(raw(["F001"]),rows)
  self.assertFalse(valid);self.assertEqual(len(bad),1)
  valid,bad=validate_themes(raw(["F001","F999"]),rows)
  self.assertFalse(valid);self.assertEqual(len(bad),1)
  self.assertIn("TWO distinct reports",theme_prompt(rows))
 def test_no_crossreport_claims_from_one_agency(self):
  base={"observation_id":"2.1","pdf_page":2,"control_area":"logging_monitoring",
        "weakness":"Missing monitoring","evidence_quote":"not implemented"}
  rows=index_findings([{"document_id":"x","source_verified":[{**base,"entity":"Same"}]},
                       {"document_id":"y","source_verified":[{**base,"entity":"Same"}]}])
  raw=json.dumps({"themes":[{"name":"Monitoring","description":"Overlap",
    "finding_ids":["F001","F002"]}]})
  valid,bad=validate_themes(raw,rows)
  self.assertFalse(valid);self.assertTrue(bad)

if __name__=="__main__":unittest.main()
