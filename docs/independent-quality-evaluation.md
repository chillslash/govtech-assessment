# Source-first evaluation of the five-report ANAO MVP

**11 October 2026 — independent AI-assisted source review (not professional auditor adjudication)**

## Executive findings

The end-to-end prototype ran on five published audit reports. This evaluation reviews the **14 selected physical PDF pages**, using source-first reading and a separate 10-page audit of material **excluded by discovery**. The earlier model outputs and prompts were not changed.

| Assessment | Result | Interpretation |
| --- | ---: | --- |
| Model findings passing deterministic quotation/locator checks | 50 | All had source-grounded quotations, **not** guaranteed correct interpretations |
| Clearly supported, appropriately atomic extracted records | **40/50 (80%)** | Exploratory AI review of attribution, interpretation and distinctness |
| Correctly source-supported but *merged* multiple deficiencies | **2/50 (4%)** | Content broadly supported; atomic record requirement violated |
| Agency attribution **uncertain** | **7/50 (14%)** | A real weakness appeared in the passage, but the named entity was not clearly established by the source |
| Source **does not establish the claim as written** | **1/50 (2%)** | Important failure despite real source quote |
| Source-first reference weaknesses noted on selected pages | **58** | AI-derived provisional reference catalogue; some labels are agency-specific, others collective |
| Clear/merged weakness concepts covered | **44/58 (75.9%)** | Exploratory reference-concept coverage, **not independently certified recall** |
| Coverage counting source-grounded but attribution-uncertain matches | **46/58 (79.3%)** | Permissive alternative; not the preferred main result |
| Discovered candidate-page audit | **7 clearly relevant misses among 10 intentionally unranked pages** | Not a representative recall percentage; demonstrates shortlist omissions |

**Limits:** The assessor is another AI which has previously seen broad model result summaries, so this is **source-first but not strictly blinded**. It is not a professional auditor review and not an exhaustive annotated gold standard. A source quote can still support the wrong agency or an overbroad interpretation. Counts should never be presented as definitive real-world precision/recall.

## Protocol

1. Identify the 14 physical PDF pages the system actually extracted from: 2018 (25, 45, 46), 2019 (24, 26, 31), 2021 (44, 54), 2024 (30, 38, 56), 2026 (25, 26, 45). Independently read those passages and record individually remediable, explicitly observed deficiencies with direct source snippets; exclude bare recommendations and generic control standards. A source-first catalogue of **58 observations** was saved before mapping to model records.
2. Compare the **unchanged, saved 50** verified predictions against the references, one by one. Classify each as `clear_atomic`, `merged`, `attribution_uncertain`, or `unsupported`. A composite model record can cover multiple reference concepts, but is not credited as an atomic extraction.
3. Calculate both clear-or-merged and permissive concept coverage. Some collective findings share a single reference even when multiple distinct agencies are separately proposed, so this is **not** a one-to-one mathematical precision/recall benchmark.
4. Separately select two deterministic positions (one-third and two-thirds) among **non-shortlisted** findings pages per report. Read these 10 pages from the originals. They were not presented to the discovery model; do not estimate population recall from this deliberately excluded-page sample.

All 58 reference snippets match their PDF source pages after whitespace normalisation, and all sampled holdout evidence snippets were checked against their cited physical pages. Detailed records are in `data/evaluations/independent-reference-selected-pages.json`, `independent-evaluation-selected-pages.json`, and `independent-discovery-holdout.json`.

## Per-report reference comparison

| ANAO audit | Reference concepts | Strictly supported concepts detected | More permissive | Extracted records |
| --- | ---: | ---: | ---: | ---: |
| 2018 Cyber Resilience | 9 | 5 | 7 | 14 |
| 2019 Corporate Entities Cyber Resilience | 15 | 10 | 10 | 8 |
| 2021 Cyber Security Strategies | 6 | 5 | 5 | 5 |
| 2024 Cyber Security Incidents | 17 | 16 | 16 | 16 |
| 2026 Census Cyber Readiness | 11 | 8 | 8 | 7 |
| **Total** | **58** | **44** | **46** | **50** |

### Concrete weaknesses and missed findings

**2018 — attribution is a material weakness.** Paragraph 4.15 says **two entities** had inaccurate/outdated enterprise architecture, then identifies supporting-documentation and storage-strategy omissions without clearly allocating each to every named agency. The model nevertheless emitted Treasury, National Archives, and Geoscience-specific records for both general omissions. We classified six as `attribution_uncertain`; the source quotation is real, but agency-specific responsibility is not established. Paragraph 4.19 notes that Treasury had recently appointed a CIO to assume CISO responsibility; the model asserted the **CISO position was vacant**, which is not established by the passage (`unsupported`). Similarly a Geoscience CISO vacancy was not demonstrated. The system omitted audit/risk committees' failure to review cyber threats (paragraph 4.18) and the lack of forward-documented cyber initiatives (p. 45).

**2019 — notable missed IT controls.** The model extracted none of two high-confidence gaps on its selected p. 26: Australia Post had only five of ten sampled framework controls fully implemented, and lacked documented approvals/risk assessments for deviations (paragraph 2.25). It also missed ASC's security strategy not being updated since 2016 (p. 24, paragraph 2.17), and **both ASC and Australia Post's absent regular network password assessments** (p. 31, paragraph 3.18). It merged three distinct entities' patch-delay failures into one record (p. 31, paragraph 3.13).

**2021 — one distinct omission.** The five extracted entries are well supported, but p. 54 paragraph 2.80 reports both **no timeframe** and **no clear strategy** for reaching PSPF maturity. The system recorded only the strategy gap.

**2024 — near-complete on selected pages, not the report.** Sixteen records match source observations on the selected pages. The substantive missed item is AUSTRAC's **failure to use post-incident lessons to improve monitoring/procedures or share learnings**, paragraph 2.90 on physical p. 56. The audit's high score here should not be generalised: the input included a **chapter conclusion on p. 30** which conveniently lists multiple problems.

**2026 — missing distinct governance problems.** Its first record merges unsynchronised strategic/program risk assessments and missing risk-register data (paragraph 2.9), which should be separate atomic findings. It missed the lack of criteria for assigning appropriately qualified risk owners (paragraph 2.10), the relatively infrequent review of programme risk PR3 (paragraph 2.14), and inadequate consideration of **broader ABS systems** in the 2026 Census security planning (physical p. 45).

## Discovery recall stress check

Heuristic top-eight shortlisting is **a major unmeasured risk**. The LLM only reviews pages shortlisted by the deterministic ranker; only up to three approved pages are extracted. Two predetermined unshortlisted pages per report (10 total) were examined.

- **7 pages contained clear, relevant deficiencies** not available to the discovery model. Examples: Australia Post desktops missing log configuration (2019 p. 32); Future Fund's progress monitoring limitation (2021 p. 56); AUSTRAC's undocumented escalation/timeframes and archived event-data retrieval limitations (2024 p. 49); ABS's skipped quality-gate workshops and missing sign-off/evidence (2026 p. 39).
- **2 pages were scope-uncertain**: cross-government self-assessment guidance rather than specific entity implementation (2018 p. 35); aggregate control implementation grades without individual details (2024 p. 72).
- **1 page showed no clear observed deficiency** under the defined eligibility rules (2026 p. 33).

This **does not mean 70% of all relevant pages were missed**. The sample was intentionally drawn from pages the ranker excluded, so it is biased toward testing blind spots. The result does prove the current discovery budget is insufficient for any **completeness claim**. The system also selected two observed-deficiency pages (2018 p. 45, 2019 p. 26) but produced **zero extracted records** on them.

## Cross-report synthesis

The system generated traceable candidate topic groups spanning multiple reports, but its **final strict LLM thematic synthesis abstained** rather than validating an end-to-end set of recurring weakness themes. An earlier thematic proposal cited three reports but erroneously described support as coming from two; a validation guard was subsequently added. Candidate topic group counts are not independently validated semantic recurrences.

## Assessment and presentation guidance

**Supported claim:** a five-report end-to-end *prototype* with bounded LLM discovery, machine-readable observations, strict source/locator checks, and traceable thematic candidate groups. The source-first audit detected genuine errors that deterministic quote validation missed, which justifies human review.

**Unsupported claim:** 100% accurate extraction; high-coverage automated discovery; reliable agency-by-agency attribution; independently auditor-validated precision/recall; proven reliable semantic cross-report synthesis.

**Highest-value next improvements:** (1) establish and measure an appropriately broad discovery reference set, with more candidate coverage; (2) require an explicit quote supporting **each named agency**, especially for collective findings; (3) enforce one remediable problem per structured record; (4) improve cross-report grouping and deterministic claim checks; (5) make auditor adjudication part of the workflow rather than an optional afterthought.

These findings were obtained without changing, rerunning or tuning the five original model outputs.
