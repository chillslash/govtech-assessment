# Five-report ANAO MVP evaluation — 11 October 2026

## Scope

Five **individual** ANAO performance audits were read from locally downloaded public PDFs. Physical PDF page numbers are used throughout. The original 2021 and 2024 pilot files were not overwritten; the three added reports are: 2018 *Cyber Resilience*; 2019 *Cyber Resilience of Government Business Enterprises and Corporate Commonwealth Entities*; and 2026 *Cyber Security Readiness for the 2026 Census*.

**Architecture:** deterministic bounded findings-section selection and cheap keyword candidate ranking → GPT-6 Luna Medium page-level **LLM discovery** → structured atomic extraction on selected pages → deterministic source quote and paragraph/table checks → cross-report category statistics and LLM thematic proposals.

### Method and actual limits

- For each report, read the PDF but present only the **top eight heuristic-ranked pages** from the findings section to the discovery LLM, in batches of four pages. Executive-summary pages are outside the findings bounds and never used in model prompts.
- The discovery LLM nominates pages accompanied by verbatim supporting excerpts. Python verifies each quote occurs on the claimed page.
- At most **three LLM-approved pages per report** were selected for detailed extraction. The implementation selects earlier approved physical pages preferentially; this is a deterministic bounded sample, not complete report coverage.
- The extraction LLM produces a fixed JSON record per proposed weakness; Python checks mandatory fields, allowed category, exact evidence quote and physical page, and that the cited paragraph/table contains the quote (or uses a flagged page-only fallback when the finding is unnumbered).
- A final LLM considers topical candidate groups constructed from the source-verified records; its thematic groupings must cite exact finding IDs from **at least two separate reports and at least two agencies**, or are rejected. The cross-report report also includes purely deterministic category and candidate-group counts.
- Original raw outputs are retained. None of the findings or thematic interpretations has been independently adjudicated by a professional auditor. Do **not** interpret source verification as semantic accuracy, precision, recall or deployment readiness.

## Model run — five reports

| Report | LLM-selected physical PDF pages | Source-verified extracted records | Rejected extraction records |
| --- | --- | ---: | ---: |
| 2018 Cyber Resilience | 25, 45, 46 | 14 | 1 |
| 2019 Corporate Entities Cyber Resilience | 24, 26, 31 | 8 | 2 |
| 2021 Cyber Security Strategies | 44, 54 | 5 | 0 |
| 2024 Cyber Security Incidents | 30, 38, 56 | 16 | 0 |
| 2026 Census Cyber Readiness | 25, 26, 45 | 7 | 1 |
| **Total** | **14 selected pages** | **50** | **4** |

The reported rejections are conservative source/locator quality-gate failures, not automatically confirmed model hallucinations. The **50** accepted records passed deterministic quote and source checks. A saved-record replay test rereads each local PDF and confirms the 50 retained citations.

### Qualitative spot checks

The 2018 report yielded multiple observations about risk registers, supporting documentation, security planning and vacant security leadership roles across the named audited entities. Agency attribution requires human review: a paragraph describing a group of agencies may support collective findings without establishing the same failure in every named agency.

The 2019 report yielded vulnerabilities and missing asset-specific risk assessment documentation, plus patch remediation gaps. The 2024 sample included governance and backup testing controls. The 2026 Census audit's sample emphasised risk tracking, ownership and timeliness of updates. Some findings are fairly broad, and separate records can overlap: atomicity is still imperfect. Page-only references require especially careful manual review.

## Cross-report analysis

The software calculated four **candidate recurring control areas** with verified source-record references:
- Risk/asset governance: candidate findings from **five** reports.
- Documentation/oversight: candidate findings from **five** reports.
- Monitoring and incident handling: candidate findings from **two** reports.
- Patching/configuration: candidate findings from **two** reports.

These are **topic-based candidates**, not evidence that the underlying deficiencies are all semantically identical.

The unrestricted initial five-report LLM synthesis returned no cross-report themes. A more focused thematic pass once produced a plausible risk-record management theme, citing three reports and four agencies, but its draft prose incorrectly claimed two reports. We strengthened the report-count consistency rule and model prompt. The latest stringent thematic pass abstained (zero semantically accepted thematic claims); deterministic candidate groups remain available for auditor review. This is a real observed limitation, **not a hidden success**.

## What this validates — and does not

**Demonstrated:** the full pipeline runs on five public audits, discovery and extraction are separate LLM responsibilities, source references are machine-verifiable, findings remain structured, and cross-report evidence groups are traceable to precise audit pages.

**Not established:** discovery recall on unseen full reports; independently adjudicated precision/recall; robust entity attribution or atomicity; stable automated thematic synthesis; prevalence of these issues across Australian government; or security/compliance properties of a production GovTech deployment.

## Reproduce

- Smoke test: `python scripts/run_anao_multi.py --report-id 2024 --smoke`
- Each bounded report run: `python scripts/run_anao_multi.py --report-id 2018` (or `2019`, `2021`, `2024`, `2026`)
- Source-grounded cross-report analysis: `python scripts/run_anao_multi.py --themes`
- Unit and saved-PDF replay tests: `python -m unittest discover -s tests -q` with `PYTHONPATH=src;.deps` on the Windows Gateway.

Outputs: `data/evaluations/anao-multi-2018.json` through `anao-multi-2026.json`, plus `anao-multi-themes.json`. Original and earlier development baselines remain untouched. Local source PDFs remain Git-ignored.

**Recommendation:** freeze the engineering sample rather than tuning prompts repeatedly on these same reports. For submission, show the working MVP and source-checked results, disclose the thematic-abstention failure, and make independent auditor evaluation, improved discovery recall and workflow integration explicit next steps.
