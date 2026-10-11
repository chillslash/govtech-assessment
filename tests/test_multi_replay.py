"""Replay checks for completed bounded five-report evaluation."""
import json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"src"),str(ROOT/".deps")]
from audit_assurance.core import read_report,validate_predictions
from audit_assurance.cross_report import validate_themes,index_findings
from scripts.run_anao_v2 import locator_error
from scripts.run_anao_multi import SOURCES

class LiveMultiReportReplay(unittest.TestCase):
 def test_all_five_reports_with_source_citations(self):
  count=0;reports=[]
  for year,(name,a,b) in SOURCES.items():
   f=ROOT/"data"/"evaluations"/f"anao-multi-{year}.json"
   pdf=ROOT/"data"/"raw"/name
   if not f.exists() or not pdf.exists():self.skipTest("Public source PDFs missing")
   d=json.loads(f.read_text(encoding="utf8"));reports.append(d)
   self.assertEqual(d["status"],"complete")
   self.assertFalse(d["discovery_errors"])
   self.assertTrue(all(a<=x<=b for x in d["selected_pages"]))
   self.assertTrue(len(d["discovery_batches"])>=2)
   for batch in d["discovery_batches"]:
    self.assertFalse(set(batch["pages"]) & set(range(7,14)))
    for item in batch["accepted"]:
     self.assertIn(item["pdf_page"],batch["pages"])
   pages=read_report(pdf)
   valid,rejected=validate_predictions(d["source_verified"],pages,name)
   self.assertFalse(rejected)
   for r in valid:
    self.assertIn(r["pdf_page"],d["selected_pages"])
    self.assertIsNone(locator_error(r,pages[r["pdf_page"]-1].text))
   count+=len(valid)
  self.assertEqual(count,50)
  self.assertEqual(len(reports),5)

 def test_report_theme_candidate_ids_grounded(self):
  data=json.loads((ROOT/"data"/"evaluations"/"anao-multi-themes.json")
                  .read_text(encoding="utf8"))
  rows=data["source_findings"];by={r["finding_id"]:r for r in rows}
  self.assertEqual(len(rows),50)
  self.assertEqual(data["report_count"],5)
  self.assertEqual(data["status"],"complete")
  self.assertGreaterEqual(len(data["candidate_groups"]),3)
  for group in data["candidate_groups"]:
   ids=group["finding_ids"]
   self.assertEqual(group["status"],"candidate_only_not_semantically_validated")
   self.assertTrue(all(x in by for x in ids))
   self.assertGreaterEqual(len({by[x]["document_id"] for x in ids}),2)
   self.assertGreaterEqual(len({by[x]["entity"].casefold() for x in ids}),2)
  for t in data["themes"]:
   self.assertGreaterEqual(len({by[x]["document_id"] for x in t["finding_ids"]}),2)

 def test_count_inconsistent_thematic_claim_rejected(self):
  records=[
   {"finding_id":f"F{i:03d}","document_id":f"report{i}","entity":f"Agency{i}"}
   for i in range(1,4)]
  claim={"themes":[{"name":"Gaps","description":"In two reports, gaps exist.",
     "finding_ids":[x["finding_id"] for x in records]}]}
  valid,rejected=validate_themes(json.dumps(claim),records)
  self.assertFalse(valid);self.assertEqual(len(rejected),1)

if __name__=="__main__":unittest.main()
