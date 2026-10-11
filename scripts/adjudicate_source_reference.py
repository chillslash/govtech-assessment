"""Manual source-to-prediction adjudication: no model-generated grading.

Reference anchors were frozen first. This grades stored model records using
the source reading decisions and exposes both strict and lenient coverage.
"""
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"data"/"evaluations"
ref=json.loads((E/"independent-reference-selected-pages.json").read_text(encoding="utf8"))["labels"]
by_ref={r["label_id"]:r for r in ref}
# One entry per stored source-verified output in original order:
# rating is clear_atomic / merged / attribution_uncertain / unsupported.
R={
 "2018":[
 ("clear_atomic",["R003"],"Architecture deficiency supported; one of the two identified affected agencies."),
 ("clear_atomic",["R003"],"Architecture deficiency supported; second affected agency."),
 ("attribution_uncertain",["R004"],"Control-documentation gap is real, but source does not clearly assign it specifically to Treasury."),
 ("attribution_uncertain",["R004"],"Scope of missing supporting documentation is not explicitly allocated per agency."),
 ("attribution_uncertain",["R004"],"Scope of missing supporting documentation is not explicitly allocated per agency."),
 ("attribution_uncertain",["R005"],"Absence of endorsed storage strategy not clearly attributed specifically to Treasury."),
 ("attribution_uncertain",["R005"],"Storage-strategy omission is not explicitly allocated to named agencies."),
 ("attribution_uncertain",["R005"],"Storage-strategy omission is not explicitly allocated to named agencies."),
 ("clear_atomic",["R001"],"Report describes a shared nonsystematic cyber risk approach; related to the explicit summary deficiency."),
 ("clear_atomic",["R007"],"National Archives enterprise-register consolidation gap expressly named."),
 ("clear_atomic",["R008"],"Geoscience Australia enterprise-register consolidation gap expressly named."),
 ("unsupported",[],"Treasury had recently appointed a CIO to take CISO responsibilities; source does not establish CISO post unfilled at assessment."),
 ("attribution_uncertain",[],"Geoscience COO was assigned CISO responsibility; describing this as an unfilled position is not demonstrated."),
 ("clear_atomic",["R009"],"National Archives was explicitly recruiting a CIO at time of audit.")
 ],
 "2019":[
 ("clear_atomic",["R010"],"Correct critical-system vulnerability assessment gap."),
 ("clear_atomic",["R011"],"Correct incomplete vulnerability documentation."),
 ("clear_atomic",["R012"],"Correct critical asset identification gap."),
 ("clear_atomic",["R013"],"Correct lack of tailored risk profiles."),
 ("clear_atomic",["R015"],"Correct incomplete critical-asset risk documentation."),
 ("merged",["R018","R019","R020"],"Three distinct entities' patch-delay findings compressed into one record."),
 ("clear_atomic",["R021"],"Correct restricted server patch remediation scope."),
 ("clear_atomic",["R022"],"Correct insufficient compensating controls.")
 ],
 "2021":[
 ("clear_atomic",["R025"],"Correct missing documentation and approval of SIEM reviews."),
 ("clear_atomic",["R027"],"Correct unclear strategy for maturity."),
 ("clear_atomic",["R028"],"Correct absence of demonstrable maturity improvement processes."),
 ("clear_atomic",["R029"],"Correct lack of independent Top Four assurance."),
 ("clear_atomic",["R030"],"Correct absent progress reporting to committee.")
 ],
 "2024":[
 ("clear_atomic",["R039"],"Correct undocumented threat/vulnerability approach."),
 ("clear_atomic",["R040"],"Correct absent critical information and asset registers."),
 ("clear_atomic",["R041"],"Correct missing security documentation lifecycle plan."),
 ("clear_atomic",["R042"],"Correct unreviewed/untested incident-management procedure framework."),
 ("clear_atomic",["R043"],"Correct missing monitored-email triage procedure."),
 ("clear_atomic",["R044"],"Correct absence of security maturity plan."),
 ("clear_atomic",["R031"],"Correct CISO role documentation gap."),
 ("clear_atomic",["R032"],"Correct continuous monitoring documentation gap."),
 ("clear_atomic",["R033"],"Correct undefined reporting timeframes."),
 ("clear_atomic",["R034"],"Correct insufficient log coverage."),
 ("clear_atomic",["R035"],"Correct absent event logging policy."),
 ("clear_atomic",["R036"],"Correct incomplete documented event analysis."),
 ("clear_atomic",["R037"],"Correct recovery procedures omit security/testing backups."),
 ("clear_atomic",["R038"],"Correct incomplete critical-system recovery mapping."),
 ("clear_atomic",["R045"],"Correct lack of routine disaster recovery testing."),
 ("clear_atomic",["R046"],"Correct absent backup data extraction and analysis process.")
 ],
 "2026":[
 ("merged",["R048","R049"],"Combined unlinked risk assessment and missing risk-register fields in one finding."),
 ("clear_atomic",["R051"],"Correct risk owners undocumented."),
 ("clear_atomic",["R052"],"Correct missing guidance for timing/detail of risk updates."),
 ("clear_atomic",["R054"],"Correct missing documented response to three risk requests."),
 ("clear_atomic",["R055"],"Correct missing cybersecurity detail in most updates."),
 ("clear_atomic",["R056"],"Correct stale reporting data."),
 ("clear_atomic",["R058"],"Correct controls incompletely implemented.")
 ],
}
results=[];ratings=Counter();covered_any=set();covered_clear=set()
for year,expected in R.items():
 d=json.loads((E/f"anao-multi-{year}.json").read_text(encoding="utf8"))
 predictions=d["source_verified"]
 assert len(predictions)==len(expected),(year,len(predictions),len(expected))
 for i,(verdict,matches,why) in enumerate(expected,1):
  for m in matches:
   assert m in by_ref and by_ref[m]["year"]==year,(year,i,m)
  if verdict in ("clear_atomic","merged"):covered_clear.update(matches)
  covered_any.update(matches)
  ratings[verdict]+=1
  results.append({
   "prediction_id":f"P{year}-{i:02d}",
   "document_id":d["document_id"],
   "pdf_page":predictions[i-1]["pdf_page"],
   "verdict":verdict,
   "reference_ids":matches,"review_note":why,
   "model_weakness":predictions[i-1]["weakness"]
  })
uncovered=[x for x in ref if x["label_id"] not in covered_any]
strict_uncovered=[x for x in ref if x["label_id"] not in covered_clear]
report_stats=[]
for year in R:
 refs=[x for x in ref if x["year"]==year]
 ypred=[x for x in results if x["prediction_id"].startswith("P"+year)]
 report_stats.append({"year":year,"reference_count":len(refs),"prediction_count":len(ypred),
  "clear_atomic":sum(x["verdict"]=="clear_atomic" for x in ypred),
  "merged":sum(x["verdict"]=="merged" for x in ypred),
  "attribution_uncertain":sum(x["verdict"]=="attribution_uncertain" for x in ypred),
  "unsupported":sum(x["verdict"]=="unsupported" for x in ypred),
  "reference_detected_strict":sum(x["label_id"] in covered_clear for x in refs),
  "reference_detected_permissive":sum(x["label_id"] in covered_any for x in refs)})
payload={
 "method":"AI manual semantic source review of 14 automatically selected pages. References frozen before mapping saved predictions; evaluator had earlier broad exposure, so not blind. No professional auditor. Interpret scores as exploratory sample coverage, not full-report precision/recall.",
 "reference_count":len(ref),
 "source_verified_model_records":len(results),
 "verdict_counts":dict(ratings),
 "strict_clear_or_merged_reference_coverage":{
  "count":len(covered_clear),"denominator":len(ref)},
 "permissive_reference_coverage":{
  "count":len(covered_any),"denominator":len(ref)},
 "uncovered_reference_ids":[x["label_id"] for x in uncovered],
 "strict_uncovered_reference_ids":[x["label_id"] for x in strict_uncovered],
 "per_report":report_stats,
 "prediction_reviews":results
}
out=E/"independent-evaluation-selected-pages.json"
out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("REFERENCE:",len(ref),"MODEL:",len(results),"RATINGS:",dict(ratings))
print("REFERENCE COVERED CLEAR/MERGED:",len(covered_clear),"/",len(ref),"PERMISSIVE:",len(covered_any),"/",len(ref))
print("UNDETECTED:",len(uncovered))
for x in report_stats:print(x)
print("SAVED:",out)
