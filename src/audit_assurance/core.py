"""Page-aware PDF reading, evidence checking, and exact audit-finding evaluation.

No model is called by this module. Inference is kept separate and its output is
always *provisional* until the auditor reviews the source evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

CONTROL_AREAS = (
    "access_lifecycle", "privileged_access", "authentication",
    "logging_monitoring", "change_management", "patch_configuration",
    "data_integrity", "other_uncertain",
)


def normalise(value: str) -> str:
    """Normalise whitespace for matching verbatim evidence split across PDF lines.

    Punctuation and words remain intact. This intentionally does not perform
    fuzzy or semantic matching: such a check would overstate source grounding.
    """
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


@dataclass(frozen=True)
class Page:
    pdf_page: int                # 1-based PDF page number
    printed_page: str | None    # as printed by the report, if detectable
    text: str                   # unmodified output from PDF text extraction

    @property
    def search_text(self) -> str:
        return normalise(self.text)


def read_report(pdf_path: Path) -> list[Page]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    result: list[Page] = []
    for idx, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        # AGO's body pages begin with an Arabic page number. Front matter can
        # carry Roman numerals; retain these too, without guessing offsets.
        header = re.match(r"\s*([0-9]{1,3}|[ivxlcdm]{1,6})\s*(?:\r?\n|\s{2,})", text, re.I)
        printed = header.group(1) if header else None
        result.append(Page(idx, printed, text))
    return result


def candidate_pages(pages: list[Page], max_results: int = 20) -> list[dict]:
    """Reconnaissance rank only; never a completeness or recall guarantee."""
    terms = (
        "privileged", "user access", "access rights", "it controls",
        "it general controls", "audit logs", "account review", "sudo",
        "password", "system administrator", "database account",
    )
    ranked: list[dict] = []
    for page in pages:
        body = page.search_text.casefold()
        hits = sorted(t for t in terms if t in body)
        if hits:
            ranked.append({
                "pdf_page": page.pdf_page,
                "printed_page": page.printed_page,
                "terms": hits,
                "term_count": len(hits),
            })
    return sorted(ranked, key=lambda x: (-x["term_count"], x["pdf_page"]))[:max_results]


def validate_predictions(predictions: list[dict], pages: list[Page], document_id: str) -> tuple[list[dict], list[dict]]:
    """Fail closed: only records with literally supported source quotes survive.

    This proves that a phrase occurs on the cited page, not that the LLM's
    interpretation, attribution or taxonomy is correct.
    """
    by_page = {p.pdf_page: p for p in pages}
    accepted, rejected = [], []
    required = ("entity", "observation_id", "weakness", "control_area", "evidence_quote", "pdf_page")
    for index, item in enumerate(predictions):
        errors = []
        if not isinstance(item, dict):
            rejected.append({"index": index, "errors": ["not an object"]})
            continue
        for key in required:
            if key not in item or isinstance(item[key], bool) or item[key] in (None, ""):
                errors.append(f"missing {key}")
        area = item.get("control_area")
        if area not in CONTROL_AREAS:
            errors.append("unknown control_area")
        pnum = item.get("pdf_page")
        if type(pnum) is not int or pnum not in by_page:
            errors.append("pdf_page not in source PDF")
        for key in ("entity", "observation_id", "weakness", "evidence_quote"):
            if key in item and not isinstance(item[key], str):
                errors.append(f"{key} must be a string")
        quote = item.get("evidence_quote")
        if isinstance(quote, str):
            if len(normalise(quote)) < 15:
                errors.append("evidence quote too short")
            if type(pnum) is int and pnum in by_page and normalise(quote) not in by_page[pnum].search_text:
                errors.append("evidence quote not found on cited PDF page")
        if errors:
            rejected.append({"index": index, "errors": sorted(set(errors)), "item": item})
        else:
            accepted.append({**item, "document_id": document_id,
                             "printed_page": by_page[pnum].printed_page,
                             "review_status": "proposed"})
    return accepted, rejected


def _matched(pred: dict, gold: dict) -> bool:
    """A deliberately strict evidence+category match, not a semantic judge."""
    if pred.get("document_id") != gold.get("document_id") or pred.get("pdf_page") != gold.get("pdf_page"):
        return False
    if normalise(pred.get("entity", "")).casefold() != normalise(gold.get("entity", "")).casefold():
        return False
    if pred.get("control_area") != gold.get("control_area"):
        return False
    a, b = normalise(pred.get("evidence_quote", "")).casefold(), normalise(gold.get("evidence_quote", "")).casefold()
    return bool(a and b) and (a in b or b in a)


def evaluate(gold: list[dict], predicted: list[dict]) -> dict:
    """One-to-one deterministic matching, conservative on changed quote spans."""
    matched_golds: set[int] = set()
    correct = 0
    for prediction in predicted:
        for idx, reference in enumerate(gold):
            if idx not in matched_golds and _matched(prediction, reference):
                matched_golds.add(idx)
                correct += 1
                break
    false_positive = len(predicted) - correct
    false_negative = len(gold) - correct
    return {
        "matched": correct, "gold_total": len(gold), "predicted_total": len(predicted),
        "false_positives": false_positive, "false_negatives": false_negative,
        "precision": correct / len(predicted) if predicted else 0.0,
        "recall": correct / len(gold) if gold else 0.0,
        "method": "exact document+PDF page+control area; nested evidence quotes; one-to-one",
        "caution": "Strict automated scores need manual adjudication when evidence spans differ or taxonomy labels are debatable.",
    }
