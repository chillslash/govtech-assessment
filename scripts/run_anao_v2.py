"""Two-stage ANAO prototype: full-report discovery, then atomic extraction.

Matched-page mode is the controlled prompt comparison against saved pilots.
Discovery mode processes top-ranked pages from the entire findings chapter.
Neither mode uses the withheld executive summaries during inference.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"src"))
if (ROOT/".deps").exists():
    sys.path.insert(0,str(ROOT/".deps"))

from audit_assurance.core import read_report, validate_predictions
from audit_assurance.discovery import discover_pages
from scripts.run_anao_pilot import prepare_prompt, parse_model_output, normalise_anao_ids

FIXED_PAGES={
    "anao-2021-strategies.pdf": [43,44,45],
    "anao-2024-incidents.pdf": [48,49],
}
ATOMIC_RULES = (
    "Extract one independently remediable, explicitly observed weakness per record. "
    "If one audit observation reports several distinct failures, create separate "
    "records with specific evidence for each; do not collapse independent failures "
    "into a compound description. Conversely, do not split a single underlying "
    "deficiency into synonyms, consequences, or repeated wording. "
    "Treat a list of actions needed to fix one lifecycle control as one deficiency "
    "unless distinct independently testable control gaps are explicitly stated. "
    "Do not infer observations solely from recommendations, general standards, "
    "or agency responses. For findings in tables use the actual printed table "
    "identifier as observation_id. For numbered narrative findings use the "
    "actual paragraph identifier. For unnumbered narrative findings with no "
    "printed locator, use PDF page N, where N is that passage's physical PDF "
    "page; this fallback requires reviewer attention. Never invent an ID. "
    "The evidence quote must occur within the identified paragraph or table, "
    "not merely elsewhere on the PDF page. "
)
def atomic_prompt(pages, selected, withheld):
    original=prepare_prompt(pages,selected,withheld)
    anchor="Return ONLY valid JSON with key 'weaknesses'"
    if original.count(anchor)!=1:
        raise ValueError("Unexpected extraction prompt version")
    original = original.replace(
        'observation_id (STRING such as "2.56")',
        'observation_id (STRING copied from the actual numbered paragraph '
        'or table heading on the cited source page; for an unnumbered '
        'finding use PDF page N with its exact physical page number)',
    )
    if 'STRING such as "2.56"' in original:
        raise ValueError("Example observation number must not enter source prompts")
    return original.replace(anchor, ATOMIC_RULES+anchor, 1)

def locator_error(item:dict, source_page:str) -> str | None:
    """Independently verify the quoted evidence belongs to the cited locator."""
    import re
    from audit_assurance.core import normalise
    locator=item.get("observation_id")
    quote=normalise(item.get("evidence_quote",""))
    if not isinstance(locator,str) or not quote:
        return "missing source locator or quote"
    page_only=re.fullmatch(r"(?i)pdf\s+page\s+(\d+)",locator.strip())
    if page_only:
        if int(page_only.group(1)) != item.get("pdf_page"):
            return "page-only locator does not match cited physical PDF page"
        return None  # page-level quote verified by validate_predictions
    if re.fullmatch(r"(?i)table\s+\d+\.\d+",locator.strip()):
        pattern=re.compile(r"(?i)\b"+re.escape(locator.strip()).replace(r"\ ",r"\s+")+r"\s*:")
        match=pattern.search(source_page)
        if not match:
            return "table identifier not found on cited page"
        next_table=re.search(r"(?i)\btable\s+\d+\.\d+\s*:",source_page[match.end():])
        end=match.end()+next_table.start() if next_table else len(source_page)
        excerpt=source_page[match.start():end]
    elif re.fullmatch(r"\d+\.\d+",locator.strip()):
        starts=list(re.finditer(r"(?m)^\s*\d+\.\d+\s+",source_page))
        found=[i for i,m in enumerate(starts) if re.match(
            r"\s*"+re.escape(locator.strip())+r"\s+",m.group())]
        if not found:
            return "numbered paragraph identifier not found on cited page"
        i=found[0]
        excerpt=source_page[starts[i].start():
                            starts[i+1].start() if i+1<len(starts) else len(source_page)]
    else:
        return "unknown observation locator format"
    if quote not in normalise(excerpt):
        return "quote not within cited paragraph/table"
    return None


def preview_report(pdf_path:Path, mode:str, n:int):
    if pdf_path.name not in FIXED_PAGES:
        raise ValueError("Report not on evaluated-source allowlist")
    pages=read_report(pdf_path)
    discovery=discover_pages(pages,max_pages=n)
    chosen=(FIXED_PAGES[pdf_path.name] if mode=="matched"
            else discovery["selected_pdf_pages"])
    if not chosen:
        raise ValueError("Discovery returned no candidate pages")
    excluded=[7,8,9,10,11]
    if set(chosen) & set(excluded):
        raise ValueError("Discovery selected executive-summary pages")
    prompt=atomic_prompt(pages,chosen,excluded)
    return pages,discovery,chosen,excluded,prompt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--mode",choices=("matched","discovered"),required=True)
    p.add_argument("--max-pages",type=int,default=2)
    p.add_argument("--codex",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--preview",action="store_true")
    args=p.parse_args()
    if not args.report.exists():
        raise SystemExit(f"Missing local PDF: {args.report}")
    pages,discovery,chosen,excluded,prompt=preview_report(args.report,args.mode,args.max_pages)
    overview={
        "document_id":args.report.name,
        "mode":args.mode,
        "selected_pdf_pages":chosen,
        "summary_pdf_pages_withheld":excluded,
        "discovery":discovery,
        "prompt_character_count":len(prompt),
    }
    if args.preview:
        print(json.dumps(overview,indent=2))
        return
    cmd=[
        str(args.codex),"exec","--ephemeral","--ignore-user-config",
        "--sandbox","read-only","-m","gpt-6-luna",
        "-c",'model_reasoning_effort="medium"',
        "-C",str(ROOT),"-"
    ]
    start=time.monotonic()
    try:
        result=subprocess.run(cmd,input=prompt,capture_output=True,text=True,
            encoding="utf-8",errors="replace",cwd=ROOT,timeout=145)
    except subprocess.TimeoutExpired:
        raise SystemExit("Model timed out, no evaluation saved")
    if result.returncode:
        raise SystemExit(f"Codex failed with exit code {result.returncode}")
    raw=parse_model_output(result.stdout)
    adjusted,converted=normalise_anao_ids(raw,pages)
    accepted,rejected=validate_predictions(adjusted,pages,args.report.name)
    # Model quote provenance is verified only against the selected input pages,
    # not just somewhere else in the same report.
    retained=[]
    for item in accepted:
        if item["pdf_page"] not in chosen:
            rejected.append({"reason":"quote cited outside model's supplied pages","item":item})
            continue
        error=locator_error(item,pages[item["pdf_page"]-1].text)
        if error:
            rejected.append({"reason":error,"item":item})
        else:
            retained.append(item)
    accepted=retained
    flags=[{"index":i,"observation_id":x.get("observation_id"),
        "reason":"potential multi-part weakness or unnumbered page-only source; needs human review"}
        for i,x in enumerate(accepted)
        if (" and " in x.get("weakness","").lower()
            or "; " in x.get("weakness","")
            or x.get("observation_id","").lower().startswith("pdf page "))]
    data={
        **overview,
        "model":"gpt-6-luna",
        "reasoning_effort":"medium",
        "run_utc":datetime.now(timezone.utc).isoformat(),
        "duration_seconds":round(time.monotonic()-start,2),
        "atomic_prompt_rules":ATOMIC_RULES,
        "raw_predictions":raw,
        "numeric_ids_normalised":converted,
        "source_verified":accepted,
        "rejected":rejected,
        "atomic_review_flags":flags,
        "caution":"Heuristic discovery and valid page quotes are not exhaustive recall or auditor validation.",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({"file":str(args.output),"mode":args.mode,
        "pages":chosen,"records":len(accepted),"rejected":len(rejected),
        "atomic_flags":len(flags),"duration_seconds":data["duration_seconds"]}))
if __name__=="__main__":
    main()
