# Full-report audit-assurance evaluation — 11 October 2026

## Protocol
The expanded five-report ANAO prototype was run against **every physical PDF page in each previously inspected substantive findings-section range**: 189 pages in total. Each page was presented to GPT-6 Luna Medium for LLM discovery in batches of four; 102 pages with source-verified discovery nominations underwent atomic extraction in two-page batches, without a top-eight discovery shortlist or a three-page per-report cap. The earlier five-report results and independent reference labels were preserved unchanged.

This is exhaustive **page screening within the chosen findings bounds**, **not exhaustive extraction of all observed weaknesses**. A relevant page can be missed by discovery or produce zero accepted records; report covers, appendices, and pages outside findings bounds were not scanned.

## Full-run numbers

| ANAO report | Pages screened | Nominated | Source-verified records | Rejected extracted records |
|---|---:|---:|---:|---:|
| 2018 Cyber Resilience | 28 | 18 | 45 | 15 |
| 2019 Corporate Entities Cyber Resilience | 28 | 19 | 54 | 1 |
| 2021 Cyber Security Strategies | 48 | 12 | 21 | 3 |
| 2024 Cyber Security Incidents | 59 | 44 | 153 | 15 |
| 2026 Census Cyber Readiness | 26 | 9 | 13 | 0 |
| **Total** | **189** | **102** | **286** | **34** |

There were also 24 invalid or ungrounded discovery nominations rejected before extraction. All five report runs completed successfully; the 34 rejected extraction records failed automated evidence/locator checks. The 286 retained records are **not 286 independently confirmed unique weaknesses**. Quote matching cannot establish correct interpretation, agency attribution, or absence of duplicates.

The original bounded MVP produced 50 source-verified records from 14 detailed pages across these same five reports. The expanded scan materially increases pages seen and provisional findings returned, but the counts do not establish improved accuracy.

## Comparison with the independent source-first audit

The pre-existing catalogue of **58 source-first reference weakness concepts** on the original 14 selected pages was frozen before the expanded model run. A separate AI-assisted semantic assessor then mapped expanded findings against those references; this was **not a blinded, professional-auditor benchmark**.

| Report | Reference concepts | Clear atomic match | Merged match | Attribution uncertain | Absent |
|---|---:|---:|---:|---:|---:|
| 2018 | 9 | 3 | 0 | 2 | 4 |
| 2019 | 15 | 15 | 0 | 0 | 0 |
| 2021 | 6 | 6 | 0 | 0 | 0 |
| 2024 | 17 | 15 | 1 | 0 | 1 |
| 2026 | 11 | 4 | 0 | 0 | 7 |
| **Total** | **58** | **43** | **1** | **2** | **12** |

Under this exploratory matching exercise, **44/58** concepts were matched clearly or within merged records. The earlier source-first review also found **44/58**, but through a different adjudication process; this numerical equality is **not a controlled head-to-head comparison or report-level recall measurement**. The weak 2018 and 2026 reference coverage deserves particular attention. On the 2026 report, discovery rejected or missed the page 25 material despite its previous use in the original MVP; the expanded scan therefore **did not monotonically improve discovery**.

## Missed-page stress test

Ten earlier source-first holdout pages had been intentionally chosen outside the heuristic top-eight shortlist: **seven clearly positive**, **two scope-uncertain**, and **one with no clear observed weakness**. On the expanded run, among the seven positive pages:

- **Four** had matching observations: 2018 p28, 2019 p32 and p40, and 2021 p69.
- **Two** had partial coverage: 2024 p49 and 2026 p39.
- **One** was missed: 2021 p56, nominated by discovery but with no retained extraction for that weakness.

Two original AI judge verdicts were inconsistent with the earlier source-first labels: 2019 p40 was a *positive* holdout with a matching ASC data-ownership record but was called scope-uncertain; 2026 p33 had *no* observed weakness but its absence was called missed. These two corrections are stored transparently as overlays in the summary JSON; original judge responses are unchanged. This intentionally excluded-page sample **cannot be extrapolated to whole-report recall**.

## Cross-report synthesis

The software assembled deterministic candidate control groups, and a cautious LLM thematic pass proposed two source-linked cross-report themes:

- **Application-whitelisting gaps** — 4 model records, 3 reported agencies, across the 2018 and 2019 reports.
- **Patch-management weaknesses** — 6 model records, 5 reported agencies, across the 2018 and 2019 reports.

Each proposed theme passed structural validation of cited finding IDs, distinct reports, and distinct entity names. However, **structural validation does not verify the semantic equivalence of issues**; auditor approval is still required. No sector-wide prevalence or severity ranking is supported.

## Interpretation and next steps

**Demonstrated:** end-to-end five-report functionality, source-anchored extraction with automatically checked citations, screening of all 189 scoped findings pages, an auditable structured register, and traceable cross-report candidate themes.

**Not demonstrated:** fully exhaustive weakness extraction, production precision or recall, correct interpretation and attribution of every source-checked record, auditor-confirmed themes, reliable time savings, or security readiness for confidential audits. The study used Australian ANAO published reports, not a representative sample of Singapore AGO operations.

Next steps should be (1) blind expert reference labelling and discovery-recall measurement on broader pages, (2) more conservative entity attribution and atomicity/dedup checks, (3) source-ID-linked reviewer sign-off and feedback, (4) an authorised security/data-handling review before confidential use. No further model tuning was performed on the five original bounded outputs.

## Reproducibility

Run the full pipeline via scripts/run_anao_full.py, the reference mapping via scripts/evaluate_anao_full.py, and aggregate metrics via scripts/summarise_anao_full.py. Full model responses and checks are saved in data/evaluations/anao-full-YYYY.json, reference matching in anao-full-eval-YYYY.json, thematic proposals in anao-full-themes.json, and corrections/aggregate numbers in anao-full-evaluation-summary.json. The original bounded runs remain untouched.

**AI-use disclosure:** ChatGPT/Codex GPT-6 Luna Medium assisted with architecture, code, inference, evaluation, and draft presentation creation. No professional auditor approved the extracted findings.

