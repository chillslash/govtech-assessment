"""Focus cross-report LLM analysis on independently auditable candidate groups."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"src"),str(ROOT/".deps")]
from audit_assurance.cross_report import (index_findings,theme_prompt,
    validate_themes,category_coverage,thematic_batches)
from scripts.run_anao_multi import infer,save
P=ROOT/"data"/"evaluations"
reports=[json.loads((P/f"anao-multi-{k}.json").read_text(encoding="utf8"))
         for k in ("2018","2019","2021","2024","2026")]
if any(x["status"]!="complete" for x in reports):
    raise SystemExit("All report stages must pass before cross-report analysis")
rows=index_findings(reports)
result={"status":"running","finding_count":len(rows),"report_count":5,
  "category_coverage":category_coverage(rows),"source_findings":rows,
  "method":"deterministic topical candidate sets plus LLM semantic grouping",
  "batches":[],"candidate_groups":[],"themes":[],"rejected_themes":[],
  "limitations":"Provisional source-checked records, not independently auditor-adjudicated."}
for candidate in thematic_batches(rows):
    name=candidate["candidate_area"];selected=candidate["findings"]
    result["candidate_groups"].append({
      "candidate_area":name,
      "finding_ids":[x["finding_id"] for x in selected],
      "report_count":len({x["document_id"] for x in selected}),
      "entity_count":len({x["entity"].casefold() for x in selected}),
      "status":"candidate_only_not_semantically_validated"})
    try:
        raw,seconds=infer("CANDIDATE CONTROL AREA: "+name+"\n"
            +theme_prompt(selected),timeout=120)
        good,bad=validate_themes(raw,selected)
        result["batches"].append({"candidate_area":name,
            "input_findings":len(selected),"raw":raw,
            "accepted":len(good),"rejected":len(bad),"model_seconds":seconds})
        result["themes"]+=good
        result["rejected_themes"]+=bad
        print(f"{name}: {len(good)} valid themes / {len(bad)} rejected",flush=True)
    except Exception as e:
        result["batches"].append({"candidate_area":name,"error":str(e)})
        print(f"{name}: error={e}",flush=True)
    save(ROOT/"outputs"/"theme-focused-progress.json",result)
result["status"]=("complete" if all("error" not in b for b in result["batches"])
                  else "partial")
save(P/"anao-multi-themes.json",result)
print("DONE",result["status"],len(result["themes"]),"verified thematic proposals",flush=True)
