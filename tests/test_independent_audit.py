"""Reproducible checks of independent ANAO source-review artifacts."""
import json,unittest,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/".deps")]
from audit_assurance.core import read_report,normalise

class IndependentAuditTests(unittest.TestCase):
 def test_reference_source_quotes(self):
  d=json.loads((ROOT/"data"/"evaluations"/"independent-reference-selected-pages.json").read_text(encoding="utf8"))
  self.assertEqual(len(d["labels"]),58)
  self.assertFalse(d["invalid_quotes"])
  cache={}
  for l in d["labels"]:
   name=l["document_id"]
   if name not in cache:
    path=ROOT/"data"/"raw"/name
    if not path.exists():self.skipTest("Public report PDFs unavailable")
    cache[name]=read_report(path)
   self.assertIn(normalise(l["source_quote"]),cache[name][l["pdf_page"]-1].search_text)

 def test_all_50_prediction_reviews_align(self):
  ev=json.loads((ROOT/"data"/"evaluations"/"independent-evaluation-selected-pages.json").read_text(encoding="utf8"))
  reviews=ev["prediction_reviews"];self.assertEqual(len(reviews),50)
  self.assertEqual(Counter(x["verdict"] for x in reviews),{
   "clear_atomic":40,"merged":2,"attribution_uncertain":7,"unsupported":1})
  refs=json.loads((ROOT/"data"/"evaluations"/"independent-reference-selected-pages.json").read_text(encoding="utf8"))["labels"]
  byref={r["label_id"] for r in refs}
  for year in ("2018","2019","2021","2024","2026"):
   rows=json.loads((ROOT/"data"/"evaluations"/f"anao-multi-{year}.json").read_text(encoding="utf8"))["source_verified"]
   matches=[r for r in reviews if r["prediction_id"].startswith("P"+year+"-")]
   self.assertEqual(len(rows),len(matches))
   for n,(prediction,review) in enumerate(zip(rows,matches),1):
    self.assertEqual(review["prediction_id"],f"P{year}-{n:02d}")
    self.assertEqual(prediction["weakness"],review["model_weakness"])
    self.assertTrue(all(x in byref for x in review["reference_ids"]))
  self.assertEqual(ev["strict_clear_or_merged_reference_coverage"]["count"],44)
  self.assertEqual(ev["permissive_reference_coverage"]["count"],46)
  self.assertEqual(ev["reference_count"],58)

 def test_non_shortlisted_pages_sampling_and_evidence(self):
  doc=json.loads((ROOT/"data"/"evaluations"/"independent-discovery-holdout.json").read_text(encoding="utf8"))
  self.assertEqual(len(doc["reviews"]),10)
  self.assertEqual(Counter(x["classification"] for x in doc["reviews"]),
                   {"positive":7,"scope_uncertain":2,"negative":1})
  names={"2018":"ANAO_Report_2017-2018_53a.pdf",
         "2019":"Auditor-General_Report_2019-20_1.pdf",
         "2021":"anao-2021-strategies.pdf",
         "2024":"anao-2024-incidents.pdf",
         "2026":"Auditor-General_Report_2025-26_34.pdf"}
  for year,name in names.items():
   d=json.loads((ROOT/"data"/"evaluations"/f"anao-multi-{year}.json").read_text(encoding="utf8"))
   ranked={x["pdf_page"] for x in d["candidate_pages"]}
   a,b=d["findings_section_physical_pages"]
   excluded=[p for p in range(a,b+1) if p not in ranked]
   chosen=[excluded[len(excluded)//3],excluded[2*len(excluded)//3]]
   selected=[x for x in doc["reviews"] if x["report"]==year]
   self.assertEqual(sorted(x["pdf_page"] for x in selected),sorted(chosen))
   path=ROOT/"data"/"raw"/name
   if not path.exists():self.skipTest("Public PDFs unavailable")
   pages=read_report(path)
   for x in selected:
    self.assertNotIn(x["pdf_page"],ranked)
    if x["source_anchor"]:
     self.assertIn(normalise(x["source_anchor"]),
                   pages[x["pdf_page"]-1].search_text)

if __name__=="__main__":unittest.main()
