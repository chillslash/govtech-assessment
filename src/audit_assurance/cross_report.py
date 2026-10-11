"""LLM thematic synthesis over verified finding IDs with deterministic provenance."""
import json
def index_findings(reports):
    rows=[]
    for report in reports:
        for finding in report.get("source_verified",[]):
            rows.append({**{k:finding[k] for k in (
                "entity","observation_id","pdf_page","control_area",
                "weakness","evidence_quote")},
                "document_id":report["document_id"],
                "finding_id":f"F{len(rows)+1:03d}","review_status":"proposed"})
    return rows
def theme_prompt(rows):
    evidence=[{k:v for k,v in r.items() if k in (
       "finding_id","document_id","entity","control_area","weakness","evidence_quote")}
       for r in rows]
    return ("Group these UNTRUSTED but quote-checked audit findings into defensible recurring "
            "IT-control weakness themes across at least TWO distinct reports and TWO distinct "
            "agencies. Different agencies with unrelated issues are not a theme. "
            "Do not state any numerical count of reports or agencies in prose; those counts are computed in software. Do not claim sector-wide prevalence or invent facts. Use only exact finding IDs "
            "supplied. Return ONLY JSON object with key 'themes': array of objects with "
            "'name' (brief), 'description' (cautious explanation), and 'finding_ids' "
            "(array of strings). Prefer fewer well-grounded themes or [] if none. "
            "No tools.\n\n"+json.dumps(evidence,ensure_ascii=False))
def validate_themes(raw,rows):
    s=raw.strip()
    if s.startswith(chr(96)*3):s="\n".join(s.splitlines()[1:-1])
    obj=json.loads(s)
    if not isinstance(obj,dict) or not isinstance(obj.get("themes"),list):
        raise ValueError("Expected themes array")
    by={r["finding_id"]:r for r in rows}
    good=[];bad=[]
    for theme in obj["themes"]:
        ids=theme.get("finding_ids") if isinstance(theme,dict) else None
        valid=(isinstance(theme,dict) and isinstance(ids,list) and ids
            and all(isinstance(i,str) and i in by for i in ids)
            and len(ids)==len(set(ids))
            and isinstance(theme.get("name"),str) and theme["name"].strip()
            and isinstance(theme.get("description"),str) and theme["description"].strip())
        if valid:
            cited=[by[x] for x in ids]
            valid=(len({x["document_id"] for x in cited})>=2 and
                   len({x["entity"].casefold() for x in cited})>=2)
        if valid:
            import re
            written=theme.get("description","")
            counts={"one":1,"two":2,"three":3,"four":4,"five":5}
            m=re.search(r"\b(?:in|across|from)\s+(one|two|three|four|five|[1-9])\s+reports?\b",written,re.I)
            if m:
                claimed=counts.get(m.group(1).lower(),int(m.group(1)) if m.group(1).isdigit() else -1)
                if claimed!=len({r["document_id"] for r in cited}):
                    valid=False
        if not valid:
            bad.append({"theme":theme,"reason":"invalid citations, unsupported breadth, or report-count mismatch"})
        else:
            good.append({**theme,"report_count":len({x["document_id"] for x in cited}),
              "agency_count":len({x["entity"].casefold() for x in cited}),
              "source_citations":[{"finding_id":x["finding_id"],
                "document_id":x["document_id"],"entity":x["entity"],
                "pdf_page":x["pdf_page"],"observation_id":x["observation_id"]}
                for x in cited],"review_status":"proposed"})
    return good,bad

from collections import Counter
import re
def category_coverage(rows):
    return [{"control_area":cat,"finding_count":sum(r["control_area"]==cat for r in rows),
      "report_count":len({r["document_id"] for r in rows if r["control_area"]==cat}),
      "entity_count":len({r["entity"].casefold() for r in rows if r["control_area"]==cat})}
      for cat in sorted({r["control_area"] for r in rows})]
def thematic_batches(rows):
    specs=[
      ("risk and asset governance",lambda r:r["control_area"]=="governance_assurance"
       and re.search(r"risk|asset|vulnerab|assess|register|owner|threat",r["weakness"],re.I)),
      ("documentation and oversight",lambda r:r["control_area"]=="governance_assurance"
       and re.search(r"document|plan|policy|review|report|strateg|monitor|committee|role",r["weakness"],re.I)),
      ("monitoring and incident handling",lambda r:r["control_area"] in ("logging_monitoring","incident_response")),
      ("patching and configuration",lambda r:r["control_area"]=="patch_configuration")
    ]
    batches=[]
    for name,rule in specs:
        picked=[r for r in rows if rule(r)]
        if len({r["document_id"] for r in picked})>=2 and len({r["entity"].casefold() for r in picked})>=2:
            batches.append({"candidate_area":name,"findings":picked})
    return batches
