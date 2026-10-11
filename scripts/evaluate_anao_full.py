"""Evaluate expanded run against the previously frozen source-first reference
anchors and deliberately excluded-page holdouts. This is an AI semantic review,
not a blinded expert gold standard or a whole-report recall estimate.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"src"),str(ROOT/".deps")]
from scripts.run_anao_multi import SOURCES, infer, save
EVAL=ROOT/"data"/"evaluations"
KEYS=tuple(SOURCES)
def judge_report(key):
    full=json.loads((EVAL/f"anao-full-{key}.json").read_text(encoding="utf8"))
    if full["status"]!="complete":raise ValueError(key+" incomplete")
    ref=json.loads((EVAL/"independent-reference-selected-pages.json").read_text(encoding="utf8"))
    held=json.loads((EVAL/"independent-discovery-holdout.json").read_text(encoding="utf8"))
    labels=[r for r in ref["labels"] if r["year"]==key]
    holdouts=[h for h in held["reviews"] if h["report"]==key]
    pages={r["pdf_page"] for r in labels}|{h["pdf_page"] for h in holdouts}
    predictions=[{"record_id":f"{key}-F{i+1:03d}","pdf_page":x["pdf_page"],
        "entity":x["entity"],"weakness":x["weakness"],"evidence_quote":x["evidence_quote"],
        "observation_id":x["observation_id"]} for i,x in enumerate(full["source_verified"])
        if x["pdf_page"] in pages]
    prompt=("You are independently comparing a FROZEN, source-first audit reference catalogue "
        "against a newly generated model register. Original reference labels were created "
        "BEFORE this new model run. The prediction quotes have been verified to exist on the "
        "cited pages, but their interpretation and agency attribution have NOT been verified. "
        "Assess semantic coverage cautiously. Return ONLY JSON with keys 'references' and "
        "'holdouts'. For EACH reference label, return {'label_id':string,'verdict':"
        "'clear'|'merged'|'attribution_uncertain'|'absent','matched_record_ids':list "
        "of ID strings,'reason':brief string}. 'clear' requires an explicit match to the "
        "specific weakness AND sufficiently supported entity scope, in a stand-alone atomic "
        "finding. 'merged' means the correct weakness is present but lumped with another "
        "independent problem. 'attribution_uncertain' means the record captures the issue "
        "but improperly assumes an entity unsupported by the available reference. "
        "'absent' if only same topic or unrelated quote. Distinguish cyber control failures "
        "from generic recommendations and positive findings. Match ONLY records on the "
        "SAME physical pdf_page as the reference. An entry MAY map to several reference "
        "labels only when legitimately merged. For EACH holdout, return {'pdf_page':int,"
        "'verdict':'detected'|'partial'|'missed'|'scope_uncertain',"
        "'matched_record_ids':list,'reason':brief string}. 'detected' requires a matching "
        "specific weakness, NOT merely any record on that page; partial indicates "
        "one of several weaknesses was captured. Use 'scope_uncertain' for the original "
        "uncertain source anchors. 'missed' when no matching prediction. "
        "Use ONLY the frozen references, annotations, and new predictions below. "
        "Do not invent claims or cite other documents. All expected label IDs and "
        "holdout page numbers must appear exactly once.\n\nREFERENCE_LABELS\n"
        +json.dumps(labels,ensure_ascii=False)+"\n\nHOLDOUt_PAGES\n"
        +json.dumps(holdouts,ensure_ascii=False)+"\n\nMODEL_PREDICTIONS\n"
        +json.dumps(predictions,ensure_ascii=False))
    print(f"{key}: judging {len(labels)} refs, {len(holdouts)} holdouts, {len(predictions)} candidate findings",flush=True)
    raw,seconds=infer(prompt,timeout=250)
    obj=json.loads(raw)
    refs=obj.get("references"); holds=obj.get("holdouts")
    if not isinstance(refs,list) or not isinstance(holds,list):raise ValueError("Missing arrays")
    rid={r["label_id"]:r for r in labels}; hp={h["pdf_page"]:h for h in holdouts}
    pm={p["record_id"]:p for p in predictions}
    if {r.get("label_id") for r in refs}!=set(rid) or len(refs)!=len(labels):
        raise ValueError("Reference ID coverage mismatch")
    if {h.get("pdf_page") for h in holds}!=set(hp) or len(holds)!=len(holdouts):
        raise ValueError("Holdout page coverage mismatch")
    for item in refs+holds:
        is_ref="label_id" in item
        if item.get("verdict") not in (("clear","merged","attribution_uncertain","absent") if is_ref else ("detected","partial","missed","scope_uncertain")):
            raise ValueError("Bad verdict "+str(item))
        ids=item.get("matched_record_ids")
        if not isinstance(ids,list) or any(i not in pm for i in ids):
            raise ValueError("Unknown referenced model record")
        page=rid[item["label_id"]]["pdf_page"] if is_ref else item["pdf_page"]
        if any(pm[i]["pdf_page"]!=page for i in ids):
            raise ValueError("Cross-page match invalid")
    ret={"report_id":key,"evaluation_method":"source-first-frozen-reference-AI-assisted-matching",
         "reference_count":len(labels),"holdout_count":len(holdouts),
         "model_predictions_on_anchor_pages":len(predictions),
         "references":refs,"holdouts":holds,"raw_model_response":raw,
         "model_seconds":seconds,
         "limitations":"Unblinded AI judge without full source context; NOT expert adjudication or full-report recall."}
    save(EVAL/f"anao-full-eval-{key}.json",ret)
    print(key,"reference verdicts", {c:sum(x["verdict"]==c for x in refs)
              for c in ("clear","merged","attribution_uncertain","absent")},flush=True)
    print(key,"holdouts", {c:sum(x["verdict"]==c for x in holds)
              for c in ("detected","partial","missed","scope_uncertain")},flush=True)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--all",action="store_true")
    ap.add_argument("--report-id",choices=KEYS)
    a=ap.parse_args()
    if not (a.all or a.report_id):ap.error("Specify --all or --report-id")
    for k in KEYS if a.all else (a.report_id,):
        if (EVAL/f"anao-full-eval-{k}.json").exists():
            print(k,"cached semantic assessment; skipping",flush=True)
        else:
            judge_report(k)
if __name__=="__main__":main()

