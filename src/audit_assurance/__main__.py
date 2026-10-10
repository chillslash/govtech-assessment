"""Small local CLI for audit-report reconnaissance and evidence-first extraction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import candidate_pages, evaluate, read_report, validate_predictions


def json_load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def selected(pages, spec: str):
    numbers = [int(x.strip()) for x in spec.split(",")]
    if not numbers or any(n < 1 or n > len(pages) for n in numbers):
        raise ValueError(f"--pages must be PDF page numbers between 1 and {len(pages)}")
    return [pages[n - 1] for n in sorted(set(numbers))]


def main() -> int:
    parser = argparse.ArgumentParser(description="Public AGO audit finding prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Show candidate pages (discovery aid, NOT recall proof)")
    inspect.add_argument("--report", type=Path, required=True)
    inspect.add_argument("--limit", type=int, default=18)

    check = sub.add_parser("check-labels", help="Validate researcher labels against actual PDF pages")
    check.add_argument("--labels", type=Path, required=True)
    check.add_argument("--report-dir", type=Path, default=Path("data/raw"))

    run = sub.add_parser("extract", help="Optional live LLM extraction; API credentials required")
    run.add_argument("--report", type=Path, required=True)
    run.add_argument("--pages", required=True, help="1-based PDF pages, comma-separated")
    run.add_argument("--model", required=True, help="Explicit provider-supported model ID")
    run.add_argument("--reasoning", default="medium", choices=("low", "medium", "high"))
    run.add_argument("--output", type=Path, default=Path("outputs/extraction.json"))

    verify = sub.add_parser("validate", help="Offline source verification of candidate JSON")
    verify.add_argument("--report", type=Path, required=True)
    verify.add_argument("--input", type=Path, required=True, help="JSON list of provisional weaknesses")
    verify.add_argument("--output", type=Path, default=Path("outputs/validation.json"))

    score = sub.add_parser("evaluate", help="Deterministic comparison; only use real model predictions")
    score.add_argument("--gold", type=Path, required=True)
    score.add_argument("--predictions", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "evaluate":
        print(json.dumps(evaluate(json_load(args.gold), json_load(args.predictions)), indent=2))
        return 0
    if args.command == "check-labels":
        from collections import defaultdict
        grouped = defaultdict(list)
        for record in json_load(args.labels):
            grouped[record["document_id"]].append(record)
        invalid = []
        for filename, records in sorted(grouped.items()):
            pages = read_report(args.report_dir / filename)
            accepted, rejected = validate_predictions(records, pages, filename)
            print(f"{filename}: {len(accepted)}/{len(records)} evidence anchors validated; {len(pages)} PDF pages")
            invalid.extend(rejected)
        if invalid:
            print(json.dumps(invalid, indent=2, ensure_ascii=False))
            return 1
        return 0

    pages = read_report(args.report)
    if args.command == "inspect":
        print(json.dumps({"document": args.report.name, "pdf_pages": len(pages),
                          "candidate_pages": candidate_pages(pages, args.limit)}, indent=2))
        return 0
    if args.command == "extract":
        # Imported lazily: absent API credentials must never trigger network calls.
        from .llm import extract
        candidates = extract(selected(pages, args.pages), args.model, args.reasoning)
    else:
        candidates = json_load(args.input)
    accepted, rejected = validate_predictions(candidates, pages, args.report.name)
    result = {"document_id": args.report.name, "pdf_page_count": len(pages),
              "records": accepted, "rejected": rejected,
              "status": "provisional; verbatim source matching only, NOT auditor verification"}
    json_write(args.output, result)
    print(f"{len(accepted)} provisional records, {len(rejected)} rejected; saved {args.output}")
    return 0 if not rejected else 2


if __name__ == "__main__":
    raise SystemExit(main())
