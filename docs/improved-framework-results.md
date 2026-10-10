# Improved-framework pilot — 10 October 2026

Implemented two stages: (1) full-report candidate-page discovery by deterministic negative-control keyword ranking within the audit-findings chapter, and (2) GPT-6 Luna Medium atomic extraction. Both feed source text only (executive summaries PDF 7–11 withheld). Python verifies strict quotes **and** the cited paragraph/table, or flags a page-only reference for unnumbered findings. No weaker-model tests were run.

## Same-page comparison

| ANAO report and physical PDF pages | Original framework | Updated framework | Plain GPT-6 Medium |
| --- | ---: | ---: | ---: |
| 2021: 43–45 | 2 | **2** | 4 points, 2 recommendation-derived/repetitive |
| 2024: 48–49 | 7 | **9** | 7 points |
| Total | 9 | **11** | 11 reported points |

All 11 updated matched-page records passed strict source-quote and locator checks. Qualitatively they reflect published deficiencies. **The improvement is partial:** 2024 paragraph 2.56 still combines insufficient SIEM coverage with a missing prioritisation strategy; paragraph 2.62 still combines timeliness/completeness review into one finding. More records are not proof of higher recall or correctness.

## Automatically discovered pages

| Report | Ranked pages supplied | Records accepted | Rejected |
| --- | --- | ---: | ---: |
| ANAO 2021 | **36** (new) | **1** | **1** |
| ANAO 2024 | **36, 49** (36 new) | **9** | **0** |

On 2021 page 36, the model identified PM&C's administrative-privilege weakness and AGD's patching weakness. One was rejected only because the exact quotation did not match the PDF parser's space before a period. On 2024 page 36, genuine IT audit comments appeared in tables 2.4 and 2.5; the final model correctly cited those tables. Some tightly related items may still be split too finely, such as annual policy review versus documenting plans for it.

The initial discovery test revealed **prompt leakage**: a hard-coded paragraph ID example became an erroneous citation on a table-only page. We removed source-specific IDs from the prompt and added independent verification of the cited paragraph/table; otherwise use an explicitly flagged `PDF page N` for unnumbered findings. A 2021 two-page discovery run stalled; only completed runs are reported.

## Limits and artifacts

This is an exploratory, AI-reviewed small development sample, not auditor-certified precision/recall. Discovery searches the entire findings chapter but only extracts the highest ranked pages, can miss relevant observations and may over-select one agency. A quote's presence does not guarantee a correct interpretation. Human approval of findings remains essential.

Implementation: `src/audit_assurance/discovery.py`, `scripts/run_anao_v2.py`. Tests: `tests/test_improved_pipeline.py`. Final run snapshots: `data/evaluations/anao-v2-final-{matched,discovered}-{2021,2024}.json`. Baseline snapshots remain unchanged. Further tuning should use a fresh, labelled evaluation set rather than these development cases.
