# GovTech Assessment — LLM-Powered Audit Assurance — Assessment and Prototype Plan

**Assessment:** Internship Take-Home Technical Assessment — *LLM-Powered Audit Assurance Solution Proposal*.  
**State:** Proposal and prototype roadmap only; no LLM solution built or evaluated yet.  
**Expected submission:** 6–8 slides **or** a written plan of up to five pages (excluding optional appendices). AI assistant use must be disclosed.

## 1. What the assignment asks

The assessment evaluates our ability to understand an audit-review workflow, propose an appropriate LLM approach, explain source grounding, identify development steps and dependencies, evaluate reliability, and address risks, security and human oversight. **It does not require a working implementation**. AGO annual reports are suggested as public reference material; we do not have to process every report.

**Core task:** Help auditors review **multiple audit reports** and identify IT control/technology-related observations, common risks, control weaknesses and cross-report patterns. **Not** automatically draft AGO's own annual report. The public annual reports are sample inputs for a prototype.

**Intended users:** Audit-team members and reviewers compiling findings and preparing thematic analyses across reports.  
**Desired outcome:** A source-backed finding register and defensible cross-report summaries, with page-level evidence and human review.  
**Not in scope:** Automated audit opinions, formal severity ratings without approved criteria, compliance certification, autonomous remediation or replacing auditors' judgement.

## 2. The design reasoning, not just the end state

1. **Start from a generic chatbot baseline.** Uploading PDFs and asking for a summary is easy and might perform well on a small sample. The weaknesses are completeness, inconsistent classification, unverifiable counts and possible duplicate mentions. A baseline will help establish whether the framework actually adds value.
2. **Distinguish parsing from understanding.** Extracting PDF page text and metadata is generally a deterministic software task. Determining which statements constitute audit observations, which weaknesses they describe, and how to classify differently worded findings benefits from LLM inference.
3. **Separate interpretation from calculation.** A report's overview and detailed sections may repeat the same issue; a single paragraph may list several distinct issues. First build a reviewable structured register; then count, group and compare with conventional code. An LLM can optionally explain those code-derived results.
4. **Keep the MVP lean.** Python PDF parser + an extraction prompt + validated structured output + simple CSV/JSON/Markdown outputs. Avoid a complex agent framework, vector DB, web UI or fine-tuning unless evaluation later justifies one.

**High-level flow:** PDFs → page-anchored text/sections → LLM extraction/classification → schema/evidence validation + deduplication → provisional findings register → auditor verification → deterministic cross-report analysis → source-backed report/optional grounded LLM narrative.

## 3. Three key design decisions

### A. Extraction coverage: how will we find relevant observations reliably?

- Preserve PDF page numbers, section headings and numbered paragraphs. Distinguish **PDF page index** from **printed report page**.
- Segment around semantic sections rather than rigid fixed-token blocks, with some overlap where sentences span page boundaries.
- Do not search only for the heading “Weaknesses in IT Controls”: findings can instead be under descriptions such as **management of privileged OS accounts**.
- Extract **atomic control weaknesses** under a **parent observation**. For example, incomplete logging and delayed patching are different weaknesses within one audit observation.
- Distinguish the auditor's observation, stated impact and the audited entity's response/remediation. Responses are not new failures.
- Match overview summaries to their detailed source passages to prevent double-counting. If unclear, mark for reviewer attention instead of inventing a link.

**Trade-off:** Narrow heading filters are cheap but can miss valid findings; unrestricted long-context extraction costs more and may still omit items. Test section-based extraction plus a broad coverage check.

### B. Grounding: what makes the output auditable?

- Each weakness must retain the original report, year, entity, system (if named), original excerpt, **PDF page**, optional printed page, and section/paragraph.
- Use a **fixed versioned JSON schema** and schema validation. Programmatically check whether cited text actually appears on the claimed source page. An existing quote is necessary, but not sufficient, evidence that the classification is correct.
- Start with a small IT-control taxonomy: account lifecycle; privileged access; authentication/password; audit logging/monitoring; change management/segregation of duties; patch/configuration; data integrity; other/uncertain. Allow multiple tags where warranted.
- Store human review status (proposed/verified/rejected) and reviewer notes. Never imply that unreviewed LLM results are authoritative audit conclusions.
- All counts, grouping and filtering are performed with code. Source-linked records support every user-facing aggregate.

**Trade-off:** This may force more abstentions and reviewer work, but makes a defensible audit tool rather than a fluent summariser.

### C. Evaluation: how can we tell if it works?

- **Gold standard:** Manually label a small set of real report passages with atomic weaknesses, categories, source spans/pages, entities, remediation vs finding, and duplicate links.
- **Core metrics:** Precision, recall (critical for missing findings), classification agreement, citation/source correctness, unsupported statement rate, duplicate rate, and consistency across repeat runs.
- Define weakness-matching and adjudication rules before comparing results. Precision/recall calculations are deterministic for fixed labels/matching rules, despite LLM inference varying.
- **Baseline:** Give a generic chatbot the same sources and a fixed task prompt; compare missed findings, false positives, traceability and time/cost, not just writing quality.
- Keep distinct development and held-out reports. Record thresholds before the held-out test, including a particularly strict standard for source correctness. Report measured results honestly and include examples of failure.
- If time permits, track manual-review time saved, run duration and per-report inference cost.

**Trade-off:** Labelling costs time, but a small reliable test is more convincing than unmeasured claims.

## 4. Proposed data schema and component ownership

Suggested per-weakness record:

| Field | Purpose |
|---|---|
| document_id, fiscal_year, source_url | Source identity and provenance |
| entity, system (optional) | Where the issue occurred |
| parent_observation_id, weakness_id | Prevent conflating observations with individual weaknesses |
| weakness_summary, control_categories | Structured, comparable interpretation |
| evidence_quote, pdf_page, printed_page (optional), paragraph | Direct source tracing |
| risk_statement, management_response (optional) | Preserve distinctions between finding, implication and response |
| review_status, review_notes | Auditor verification |

**Deterministic code:** PDF parsing, preservation of source anchors, JSON validation, evidence string checks, dedup keys, grouping/counts and metric calculation.  
**LLM:** Semantic finding extraction, issue classification, and optional prose over already-validated records.  
**Auditors:** Gold labels, disputed cases, significance, final review and decisions.

**Counting rule:** Count **unique observations** and **atomic weaknesses** separately. One AGO observation can contain several weaknesses. Do not equate our extracted weakness counts with AGO's overview category tallies.

## 5. Implementation sequence

**Phase 0 — Understand documents.** Examine selected sections in 2–4 AGO years. Inspect different layouts, audit periods, heading conventions, paragraph numbering, overview/detail repetition and response paragraphs. Agree on an extraction unit and taxonomy.

**Phase 1 — Vertical slice.** Use a Python PDF library on selected pages; one LLM structured extraction request; validate and save JSONL/CSV plus source page references. Manually review approximately 5–10 observations. Avoid production infrastructure.

**Phase 2 — Multiple reports.** Add section discovery beyond explicit IT headings, deduplication and exact cross-report aggregation. Produce a short report of common control categories with drill-down excerpts.

**Phase 3 — Measure and improve.** Label enough source passages for a useful benchmark, score extraction and source support, compare the generic-chatbot baseline, inspect errors and run one sensible iteration. Test on held-out report material without secretly tuning on it.

**Phase 4 — Assessment slides.** Use a real input→extracted-record example, architecture, key decisions/trade-offs, development steps, evaluation protocol and **actual measured** results (if available), risks and human sign-off.

**Stop rule:** A rigorous 6–8 slide proposal meets the brief even if the optional prototype is incomplete. No claim of production-readiness or invented benchmark scores.

## 6. Real public sample documents

Official AGO index: https://www.ago.gov.sg/publications/annual-reports/

| Public report | Official PDF | Good initial cases | Suggested role |
|---|---|---|---|
| **FY2022/23** | [PDF](https://isomer-user-content.by.gov.sg/357/1bc6d111-c831-4c73-a519-90df522831af/ar_fy2022_23.pdf) | PSD, PA and STB; privileged OS/DB accounts and access controls | Development |
| **FY2023/24** | [PDF](https://isomer-user-content.by.gov.sg/357/baf0b405-c14b-4621-a70e-f370d71bbd76/ar_fy2023_24.pdf) | MSF and ECDA; sudo review, shared privileged accounts, user access; multiple issues within one thematic audit | Development |
| **FY2024/25** | [PDF](https://isomer-user-content.by.gov.sg/357/23cd5ad4-3405-4c67-9787-af1d6e389ed5/ar_fy2024_25.pdf) | MOM root-account management; **printed page 23** | Potential evaluation set |
| **FY2025/26** | [PDF](https://isomer-user-content.by.gov.sg/357/4f8ec87d-3c06-4ada-bc7c-80214c49cfd9/Report%20of%20the%20Auditor-General%20for%20FY2025-26.pdf) | SSG, WSG and GIC; **printed pages 58, 69 and 72** (overview 8) | Demo / later evaluation |

**Caveats:** These are published **annual reports**, not all underlying audit documents. AGO states that the annual report covers selected significant observations; management letters include further detail (https://www.ago.gov.sg/faq-reports/). Our tool can study *patterns in published findings*, not infer total agency risk or prevalence. Also, FY2025/26 has already been inspected while planning; do not call a test on this year fully blind.

**Concrete test scenarios:** A clean IT-labelled finding; one IT finding under a less obvious heading; multiple atomic weaknesses in one narrative; same observation repeated in overview and detail; remedial action that must **not** become a finding; similar weakness across different entities without wrongly declaring a repeat breach; missing/ambiguous fields; cross-page passages; clearly non-IT negative examples.

Optionally create **synthetic rewrites** to test phrasing/layout robustness, but label these separately and never present them as original AGO evidence.

## 7. Operational risks, security and human oversight

- **Confidentiality:** Start with public PDFs only. Confidential reports would require approved hosting/vendors, access controls, retention/data-residency decisions and security review before being sent to an LLM API.
- **Hallucination and omission:** Schema/quotation checks catch some errors, not all; use gold recall/precision tests and a reviewer queue.
- **Prompt injection:** Treat document text strictly as untrusted *source data*; it must not provide operative instructions or authorize network/filesystem actions.
- **PDF complexity:** Handle born-digital PDFs first; scanned pages, charts, tables, two-column layouts and footnotes require detection and perhaps a later OCR strategy.
- **Bias and ambiguity:** Published case selection is not representative of all audits. Risk ratings and categories require explicit rules and human review.
- **Human control:** Auditors inspect, accept or reject findings and retain responsibility for professional judgements and official outputs.

## 8. Proposed 7-slide storyline

1. Audit problem, target users and workflow.
2. One real report excerpt and the target structured record.
3. Proposed architecture, responsibilities of code vs LLM.
4. Three consequential design decisions: coverage, grounding and evaluation.
5. MVP development milestones and constraints.
6. Evaluation plan and actual prototype results/baseline if completed.
7. Security, limitations, auditor oversight, next iteration.

**Disclosure requirement:** The assessment permits AI assistance only if disclosed; state how it assisted the proposal and prototype where applicable.

## 9. Next actions

1. Obtain and validate 2–4 official PDFs, including text extraction and page mapping.
2. Create 5–10 carefully labelled example weaknesses and a small negative test set.
3. Implement the minimal Python parser → LLM structured extraction → validated register path.
4. Evaluate errors and compare to the generic-chatbot baseline.
5. Use only reproduced, traceable measurements and findings in the slides.

---

**Decision record:** Prioritise a lean, repeatable, evidence-linked extraction workflow over an attractive but unmeasured chatbot. Building the optional prototype is to strengthen the assessment, not to replace the required proposal.