"""Conservative, transparent page discovery over full public audit reports.

Discovery uses document structure and negative-control language; it does not
claim that all relevant observations will be found, nor inspect model answers.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

NEGATIVE = (
    "has not", "have not", "does not", "did not", "not been",
    "could not", "cannot", "no process", "no documented", "not documented",
    "not defined", "without", "insufficient", "lack", "not fully",
    "partially implemented", "not comply", "not meet",
    "gaps in", "unable to", "not effective", "not implemented",
    "incomplete", "weakness", "vulnerable",
)
CONTROL = (
    "security", "cyber", "incident", "siem", "log", "patch",
    "backup", "system", "access", "network", "privilege", "data",
    "control", "event", "monitor", "risk", "recovery", "maturity",
    "configuration", "authentication", "continuity", "resilience",
)
FORBIDDEN = ("summary and recommendations", "contents")


def findings_bounds(pages) -> tuple[int, int]:
    """Find first substantive chapter 2 and appendices divider.

    Return physical 1-based inclusive bounds; fail closed if report structure
    is unknown instead of scanning the summary or guessing page offsets.
    """
    begin = None
    end = None
    for p in pages:
        body = p.text.lower()
        if begin is None and re.search(r"(?m)^\s*2\.\s+[a-z]", body):
            # Avoid a contents page accidentally mentioning chapter 2.
            if "contents" not in body[:400].lower() and p.pdf_page > 10:
                begin = p.pdf_page
        if begin is not None and p.pdf_page > begin:
            # A divider page, not the incidental word "appendices" in prose.
            if re.search(r"(?m)^\s*appendices\s*$", body):
                end = p.pdf_page - 1
                break
    if begin is None or end is None or end < begin:
        raise ValueError("Unable to identify bounded audit findings chapter")
    return begin, end


def page_discovery_score(text: str) -> tuple[int, list[str]]:
    """Score windows containing both a negative observation and IT context.

    Explicitly heuristic. The output does not establish that a cited phrase
    is an actual auditor finding, rather than a recommendation/agency reply.
    """
    body = re.sub(r"\s+", " ", text.casefold())
    hits = []
    for term in NEGATIVE:
        for m in list(re.finditer(re.escape(term), body))[:12]:
            near = body[max(0, m.start()-130): min(len(body), m.end()+190)]
            if any(token in near for token in CONTROL):
                context = body[max(0, m.start()-85):min(len(body), m.end()+110)]
                if context not in hits:
                    hits.append(context)
    # Distinct negative-control signal types + small density bonus.
    signals = sum(1 for term in NEGATIVE if any(term in item for item in hits))
    return signals*2 + min(len(hits), 6), hits[:3]


def discover_pages(pages, max_pages: int = 3, min_score: int = 3) -> dict:
    if not 1 <= max_pages <= 10:
        raise ValueError("max_pages must be 1..10")
    start, end = findings_bounds(pages)
    candidates = []
    for page in pages:
        if not start <= page.pdf_page <= end:
            continue
        if any(term in page.text[:350].lower() for term in FORBIDDEN):
            continue
        score, evidence = page_discovery_score(page.text)
        if score >= min_score:
            candidates.append({
                "pdf_page": page.pdf_page,
                "score": score,
                "signals": evidence,
            })
    ranked = sorted(candidates, key=lambda x: (-x["score"], x["pdf_page"]))
    return {
        "method": "full-report deterministic negative-control page ranking",
        "eligible_pdf_pages": [start, end],
        "ranked_candidates": ranked,
        "selected_pdf_pages": sorted(item["pdf_page"] for item in ranked[:max_pages]),
        "limitations": "Heuristic triage, no completeness/recall guarantee; scores may include recommendations or agency responses.",
    }
