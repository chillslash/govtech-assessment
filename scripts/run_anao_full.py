"""Coverage-complete ANAO findings-section run (separate from frozen bounded MVP).

Every physical page in each pre-inspected findings range is presented to LLM
discovery. All quote-verified discovery nominations are extracted, without
a top-k page shortlist or per-report extraction cap. This is exhaustive page
SCREENING, not a guarantee of exhaustive weakness recall.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(ROOT / ".deps")]
from audit_assurance.core import read_report, validate_predictions
from audit_assurance.llm_discovery import discovery_prompt, validate_discovery
from audit_assurance.cross_report import index_findings, category_coverage, thematic_batches, theme_prompt, validate_themes
from scripts.run_anao_multi import SOURCES, infer, save
from scripts.run_anao_pilot import parse_model_output, normalise_anao_ids
from scripts.run_anao_v2 import atomic_prompt, locator_error

EVAL = ROOT / "data" / "evaluations"
KEYS = tuple(SOURCES)
def batches(items, n):
    return [items[i:i+n] for i in range(0, len(items), n)]
def now():
    return datetime.now(timezone.utc).isoformat()
def out_path(key):
    return EVAL / f"anao-full-{key}.json"
def checkpoint(obj, key):
    obj["updated_utc"] = now()
    save(out_path(key), obj)

def run_retry(fn):
    errors = []
    for attempt in (1, 2):
        try:
            return fn()
        except Exception as e:
            errors.append(f"try {attempt}: {type(e).__name__}: {str(e)[:350]}")
            if attempt == 1:
                time.sleep(2)
    return {"error": " | ".join(errors)}

def discovery_task(pages, nums):
    def work():
        raw, seconds = infer(discovery_prompt(pages, nums), timeout=170)
        good, bad = validate_discovery(raw, nums, pages)
        return {"pages": nums, "raw_output": raw, "model_seconds": seconds,
                "accepted": good, "rejected": bad}
    result = run_retry(work)
    return {"pages": nums, **result}

def extraction_task(pages, nums, name):
    def work():
        raw, seconds = infer(atomic_prompt(pages, nums, list(range(7,14))), timeout=200)
        records = parse_model_output(raw)
        repaired, converted = normalise_anao_ids(records, pages)
        good, bad = validate_predictions(repaired, pages, name)
        accepted = []
        for item in good:
            issue = "page not provided to model" if item["pdf_page"] not in nums else locator_error(
                item, pages[item["pdf_page"]-1].text)
            if issue:
                bad.append({"reason": issue, "item": item})
            else:
                accepted.append(item)
        return {"pages": nums, "model_seconds": seconds, "raw_output": raw,
                "raw_predictions": records, "numeric_ids_normalised": converted,
                "accepted": accepted, "rejected": bad}
    result = run_retry(work)
    return {"pages": nums, **result}

def run_report(key: str, workers: int, discovery_batch: int, extract_batch: int):
    name, first, last = SOURCES[key]
    pdf = ROOT / "data" / "raw" / name
    pages = read_report(pdf)
    assert last <= len(pages)
    nums = list(range(first, last+1))
    path = out_path(key)
    if path.exists():
        result = json.loads(path.read_text(encoding="utf-8"))
        if result.get("method") != "all-pages-llm-screened-no-topk":
            raise ValueError("Refusing to overwrite unrelated experiment " + str(path))
    else:
        result = {
            "document_id": name, "report_id": key,
            "model": "gpt-6-luna", "reasoning": "medium",
            "run_utc": now(), "method": "all-pages-llm-screened-no-topk",
            "findings_section_physical_pages": [first, last],
            "all_screened_pages": nums, "discovery_batches": [],
            "extraction_batches": [], "status": "running",
            "limitations": ("LLM page-screening and conditional extraction; not "
                "expert-adjudicated nor proven complete at weakness level.")
        }
    def run_stage(stage, groups, job):
        seen = {tuple(b["pages"]) for b in result[stage] if "error" not in b}
        todo = [g for g in groups if tuple(g) not in seen]
        print(f"{key} {stage}: {len(groups)-len(todo)} cached, {len(todo)} pending", flush=True)
        if not todo:
            return
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(job, g): g for g in todo}
            for f in as_completed(futures):
                group = futures[f]
                record = f.result()
                result[stage] = [b for b in result[stage] if b["pages"] != group]
                result[stage].append(record)
                checkpoint(result,key)
                a = len(record.get("accepted", []))
                b = len(record.get("rejected", []))
                print(f"{key} {stage}: pages {group[0]}-{group[-1]} "
                      f"accepted={a} rejected={b} "
                      f"{'ERROR ' + record['error'] if 'error' in record else ''}",
                      flush=True)
    run_stage("discovery_batches", batches(nums,discovery_batch),
              lambda group:discovery_task(pages,group))
    disc = sorted(result["discovery_batches"], key=lambda b:b["pages"][0])
    discovered = [x for b in disc for x in b.get("accepted",[])]
    selected = sorted({x["pdf_page"] for x in discovered})
    result["discovery_verified"] = discovered
    result["selected_pages"] = selected
    result["discovery_errors"] = [{"pages":b["pages"],"error":b["error"]}
                                  for b in disc if "error" in b]
    checkpoint(result,key)
    if result["discovery_errors"]:
        result["status"]="partial_discovery"
        checkpoint(result,key)
        print(f"{key}: INCOMPLETE: discovery errors={len(result['discovery_errors'])}",flush=True)
        return
    run_stage("extraction_batches", batches(selected,extract_batch),
              lambda group:extraction_task(pages,group,name))
    ext = sorted(result["extraction_batches"],key=lambda b:b["pages"][0])
    result["source_verified"]=[x for b in ext for x in b.get("accepted",[])]
    result["rejected"]=[x for b in ext for x in b.get("rejected",[])]
    result["extraction_errors"]=[{"pages":b["pages"],"error":b["error"]}
                                 for b in ext if "error" in b]
    result["status"]="complete" if not result["extraction_errors"] else "partial_extraction"
    checkpoint(result,key)
    print(f"{key} DONE: screened={len(nums)} nominated={len(selected)} "
          f"verified={len(result['source_verified'])} rejected={len(result['rejected'])} "
          f"status={result['status']}",flush=True)

def run_themes():
    reports=[json.loads(out_path(k).read_text(encoding="utf-8")) for k in KEYS]
    if any(r["status"]!="complete" for r in reports):
        raise ValueError("All five full report runs must be complete before synthesis")
    rows = index_findings(reports)
    result = {"status":"running", "source_report_count":5,
        "source_finding_count":len(rows), "source_findings":rows,
        "category_coverage":category_coverage(rows),
        "candidate_groups":[],"batches":[],"themes":[],"rejected_themes":[],
        "method":"source-verified full-page-screening topical candidate groups + LLM proposals",
        "limitations":"Theme validators establish provenance/breadth, not semantic validity; human review required."}
    for group in thematic_batches(rows):
        name=group["candidate_area"]
        selected=group["findings"]
        result["candidate_groups"].append({
            "candidate_area":name,"finding_ids":[x["finding_id"] for x in selected],
            "report_count":len({x["document_id"] for x in selected}),
            "agency_count":len({x["entity"].casefold() for x in selected}),
            "status":"candidate_only_not_semantically_validated"})
        try:
            raw,seconds=infer("CANDIDATE CONTROL AREA: "+name+"\n"+theme_prompt(selected),timeout=200)
            good,bad=validate_themes(raw,selected)
            result["themes"].extend(good)
            result["rejected_themes"].extend(bad)
            result["batches"].append({"candidate_area":name,"input_findings":len(selected),
                                      "raw_output":raw,"model_seconds":seconds,
                                      "accepted":len(good),"rejected":len(bad)})
            print(f"themes {name}: proposals={len(good)} rejected={len(bad)}",flush=True)
        except Exception as e:
            result["batches"].append({"candidate_area":name,"error":str(e)})
            print(f"themes {name}: error={e}",flush=True)
        save(EVAL/"anao-full-themes.json",result)
    result["status"]="complete" if all("error" not in b for b in result["batches"]) else "partial"
    save(EVAL/"anao-full-themes.json",result)
    print("THEMES DONE",result["status"],"themes",len(result["themes"]),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--report-id",choices=KEYS)
    g.add_argument("--all",action="store_true")
    g.add_argument("--themes",action="store_true")
    ap.add_argument("--workers",type=int,default=3)
    ap.add_argument("--discovery-batch",type=int,default=4)
    ap.add_argument("--extract-batch",type=int,default=2)
    args=ap.parse_args()
    if args.workers not in (1,2,3,4) or args.discovery_batch not in (1,2,3,4) or args.extract_batch not in (1,2,3,4):
        ap.error("out of range batch/workers")
    if args.themes:
        run_themes()
    else:
        for k in KEYS if args.all else (args.report_id,):
            run_report(k,args.workers,args.discovery_batch,args.extract_batch)

