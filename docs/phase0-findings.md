# Phase 0 — AGO report reconnaissance and initial labels

## Scope and source

Two **real public AGO annual reports** were inspected from `data/raw/`: FY2022/23 (113 PDF pages) and FY2023/24 (122 PDF pages). The local page numbers below are **1-indexed physical PDF pages**, not the printed numbers in the body. Only IT-control sections were sampled; this is *not* a complete audit of either report.

| Source | PDF page / printed page | What we observed |
| --- | --- | --- |
| FY2022/23 | 31–36 / 21–26 | PSD's HRP: privilege configuration, account reviews, activity reviews, and excessive access to files and encryption keys |
| FY2022/23 | 49 / 38 | PA account deprovisioning in VMS, GEMS II and G-FAST; one passage discusses several systems |
| FY2022/23 | 96–99 / 84–87 | STB: approval/review of whitelists; shared DB administration accounts; overly broad rights; root access; incomplete administrator activity reviews |
| FY2023/24 | 84–85 / 72–73 | MSF: GPLS sudo/root privileges, shared accounts and incomplete review logs; separate BBO application findings |
| FY2023/24 | 105 / 93 | ECDA's CMS: missing privileged-activity reviews, inadequate review follow-up, delayed account removal |

**Findings about the format:**

- Body PDFs have page numbers **offset** from printed pagination; never cite a printed-page number as the PDF index.
- Similar security weaknesses are described in differing language (e.g. overly broad root privileges or late deactivation); a fixed taxonomy helps comparison.
- A numbered observation can yield **more than one atomic issue**, but the summary and detailed account may duplicate each other. These two count units must remain separate.
- The actual finding is commonly followed by the organisation's **remediation response** in another numbered paragraph. We should not convert the response into a new negative finding.
- The paragraph about potential risk (e.g. a possibility of unauthorised activities) is **not proof** that that activity occurred.
- IT-related evidence appears under multiple headings, including those not literally titled “IT Controls.” A keyword-only page shortlist is only a reconnaissance aid, not exhaustive extraction.
- The PDF parser for FY2022/23 issued recoverable warnings about malformed PDF objects, yet extracted body text. Text includes line breaks within sentences and replacement glyphs for some punctuation; provenance checks normalise whitespace **but do not perform fuzzy quote matching**.
- One preliminary attempt with `pypdf` to read FY2025/26 failed during PDF initialisation (likely due to its PDF security/structure). That year is not needed for this development slice; do not claim all four PDFs are parseable yet. Later try an alternative parser and document the result.

## Researcher-labelled development examples

`data/labels-dev.json` contains **17 provisional researcher labels**, each connected to an actual source PDF, PDF page, entity, named system, observation number and **verbatim short evidence anchor**. These labels are intentionally *not* presented as an independently adjudicated audit gold standard. They cover four entities across two fiscal years.

For example:
- PSD / HRP / observation 30: a misconfiguration of OS privileges (FY2022/23 PDF p. 32; printed p. 22).
- STB / STAN / observation 133: shared most-privileged DB account (FY2022/23 PDF p. 97; printed p. 85).
- MSF / GPLS / observation 80: shared privileged application account (FY2023/24 PDF p. 84; printed p. 72).
- ECDA / CMS / observation 145: delayed account removal (FY2023/24 PDF p. 105; printed p. 93).

**Important:** Different annotators may select a different number of atomic issues from the same paragraph, and the taxonomy is intentionally small. Before using precision/recall numbers in assessment slides, refine annotation rules, have another reviewer adjudicate discrepancies if possible, and freeze a separate held-out sample.

## Negative and edge cases for the next milestone

1. FY2022/23 PSD paragraph 31 is an agency **response** about remediation, not a fresh finding.
2. FY2023/24 MSF paragraphs 79, 82 and 83 are agency **responses**, not negative observations.
3. FY2023/24 ECDA paragraph 146 describes proposed or completed changes, not an additional weakness.
4. FY2022/23 paragraph 36 includes (a), (b), (c), each needing a distinct annotation decision.
5. FY2022/23 STB paragraph 132 summarises weaknesses expanded in paragraphs 133–139, a **deduplication** trap.
6. PDF page 35/printed 25 PSD paragraph 40b continues a finding from the prior page; handle cross-page source spans without creating a second parent observation.

## Next checkpoint

Use these actual pages to validate deterministic parsing, quote grounding and the initial schema. Then run **one real model extraction** on a bounded set of sections when an authorised inference route is available. Do not report precision, recall, cost or model consistency until that model run actually happens.
