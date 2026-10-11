"""Run reproducible 5-report ANAO pipeline (LLM discovery -> extraction -> themes).

Use --smoke to validate one known excerpt, --report-id for one complete
bounded report test, --themes once all reports finished.
"""
from __future__ import annotations
import argparse,json,sys,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/".deps"))
from audit_assurance.core import read_report,validate_predictions
from audit_assurance.llm_discovery import rank_pages,discovery_prompt,validate_discovery
from audit_assurance.cross_report import index_findings,theme_prompt,validate_themes
from scripts.run_anao_v2 import atomic_prompt,locator_error
from scripts.run_anao_pilot import parse_model_output,normalise_anao_ids

# Bounded findings sections, inspected against each report's physical pages.
SOURCES={
 "2018":("ANAO_Report_2017-2018_53a.pdf",21,48),
 "2019":("Auditor-General_Report_2019-20_1.pdf",21,48),
 "2021":("anao-2021-strategies.pdf",35,82),
 "2024":("anao-2024-incidents.pdf",30,88),
 "2026":("Auditor-General_Report_2025-26_34.pdf",22,47),
}
CODEX=Path(r"C:\Users\ryano\.codex\packages\standalone\current\bin\codex.exe")
EVAL=ROOT/"data"/"evaluations"

def infer(prompt:str,timeout=100)->tuple[str,float]:
    cmd=[str(CODEX),"exec","--ephemeral","--ignore-user-config",
         "--sandbox","read-only","--model","gpt-6-luna",
         "-c",'model_reasoning_effort="medium"',"-C",str(ROOT),"-"]
    t=time.monotonic()
    p=subprocess.run(cmd,input=prompt,capture_output=True,text=True,
       encoding="utf-8",errors="replace",cwd=ROOT,timeout=timeout)
    if p.returncode or not p.stdout.strip():
        raise RuntimeError(f"Codex failure, exit={p.returncode}, stderr={p.stderr[-450:]}")
    return p.stdout.strip(),round(time.monotonic()-t,2)

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def run_report(key,smoke=False,budget=8,cap=3):
    name,first,last=SOURCES[key];pdf=ROOT/"data"/"raw"/name
    if not pdf.exists():raise FileNotFoundError(pdf)
    pages=read_report(pdf)
    if not 1<=first<=last<=len(pages):raise ValueError("Invalid source bounds")
    if smoke:
        if key!="2024":raise ValueError("Smoke only on known 2024 source")
        ranked=[{"pdf_page":48,"score":100},{"pdf_page":49,"score":99}]
    else:ranked=rank_pages(pages,first,last,budget)
    result={"document_id":name,"report_id":key,"model":"gpt-6-luna",
      "reasoning":"medium","run_utc":datetime.now(timezone.utc).isoformat(),
      "method":"hybrid: bounded heuristic shortlist + LLM discovery",
      "findings_section_physical_pages":[first,last],
      "candidate_pages":ranked,"discovery_batches":[],"discovery_errors":[],
      "discovery_verified":[],"selected_pages":[],"raw_predictions":[],
      "source_verified":[],"rejected":[],"status":"incomplete",
      "limitations":"Not an exhaustive scan, labels or auditor-approved result."}
    print(f"{key}: discovery on {len(ranked)} ranked pages",flush=True)
    for off in range(0,len(ranked),4):
        nums=[x["pdf_page"] for x in ranked[off:off+4]]
        try:
            raw,sec=infer(discovery_prompt(pages,nums))
            accepted,rejected=validate_discovery(raw,nums,pages)
            result["discovery_batches"].append({"pages":nums,"accepted":accepted,
                "rejected":rejected,"model_seconds":sec,"raw_output":raw})
            result["discovery_verified"]+=accepted
            print(f"{key}: pages {nums} discovered {len(accepted)}, bad {len(rejected)}",flush=True)
        except Exception as e:
            result["discovery_errors"].append({"pages":nums,"error":str(e)})
            print(f"{key}: discovery error {e}",flush=True)
    hits={x["pdf_page"] for x in result["discovery_verified"]}
    result["selected_pages"]=sorted(x["pdf_page"] for x in ranked if x["pdf_page"] in hits)[:cap]
    out=(ROOT/"outputs"/"smoke-llm-pipeline.json" if smoke
         else EVAL/f"anao-multi-{key}.json")
    if not result["selected_pages"]:
        result["status"]="no_eligible_pages";save(out,result)
        print(f"{key}: no selected pages; saved diagnostic",flush=True)
        return result
    selected=result["selected_pages"]
    if any(not first<=n<=last for n in selected):raise ValueError("Outside findings section")
    # Summary not supplied. The extraction prompt's separate withheld set is a guard.
    withheld=list(range(7,14))
    prompt=atomic_prompt(pages,selected,withheld)
    raw_answer,sec=infer(prompt,timeout=125)
    records=parse_model_output(raw_answer)
    repaired,conversions=normalise_anao_ids(records,pages)
    verified,rejected=validate_predictions(repaired,pages,name)
    for item in verified:
        problem=(None if item["pdf_page"] in selected else "page not provided")
        if problem is None:
            problem=locator_error(item,pages[item["pdf_page"]-1].text)
        if problem:
            rejected.append({"reason":problem,"item":item})
        else:result["source_verified"].append(item)
    result.update({"raw_predictions":records,"numeric_ids_normalised":conversions,
       "rejected":rejected,"extraction_seconds":sec,"status":(
       "complete" if not result["discovery_errors"] else "partial_discovery")})
    save(out,result)
    print(f"{key}: DONE selected={selected} verified={len(result['source_verified'])} rejected={len(rejected)} state={result['status']}",flush=True)
    return result

def run_themes(smoke=False):
    paths=([EVAL/f"anao-v2-final-matched-{y}.json" for y in ("2021","2024")] if smoke else [EVAL/f"anao-multi-{k}.json" for k in SOURCES])
    if any(not x.exists() for x in paths):
        raise ValueError("All five report runs must exist before themes")
    reports=[json.loads(p.read_text(encoding="utf8")) for p in paths]
    if not smoke and any(r["status"]!="complete" for r in reports):
        raise ValueError("Some report runs incomplete; resolve before themes")
    rows=index_findings(reports)
    if not rows:raise ValueError("No verified findings")
    raw,sec=infer(theme_prompt(rows),timeout=135)
    good,bad=validate_themes(raw,rows)
    payload={"status":"complete","model":"gpt-6-luna","reasoning":"medium",
        "source_report_count":len(reports),"source_findings":rows,
        "themes":good,"rejected_themes":bad,"raw_response":raw,
        "model_seconds":sec,
        "warning":"Interpretations and grouping need independent auditor review."}
    save((ROOT/"outputs"/"smoke-themes.json") if smoke else (EVAL/"anao-multi-themes.json"),payload)
    print(f"THEMES: {len(good)} accepted, {len(bad)} rejected, {len(rows)} source findings",flush=True)

def main():
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--report-id",choices=list(SOURCES))
    g.add_argument("--themes",action="store_true")
    g.add_argument("--themes-smoke",action="store_true")
    parser.add_argument("--smoke",action="store_true")
    parser.add_argument("--budget",type=int,default=8)
    parser.add_argument("--max-pages",type=int,default=3)
    a=parser.parse_args()
    if a.themes:
        subprocess.run([sys.executable,str(ROOT/"scripts"/"run_anao_themes_focused.py")],
                       check=True,cwd=ROOT)
    elif a.themes_smoke:run_themes(smoke=True)
    else:run_report(a.report_id,a.smoke,a.budget,a.max_pages)
if __name__=="__main__":main()
