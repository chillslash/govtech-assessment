# ANAO standalone-report pilot — first results (10 October 2026)

## Exact experiment

Two **published, standalone ANAO performance audits** were used as inputs (official PDF files, locally downloaded). The model was **GPT-6 Luna, Medium** through Codex CLI in ephemeral read-only mode. Its prompts contained *only* the selected detailed findings pages, never executive summaries.

| Audit | Detailed physical PDF pages passed to model | Withheld summary pages | Model records | Quotes on cited pages |
| --- | --- | --- | ---: | ---: |
| 2021 — Cyber Security Strategies of Non-Corporate Commonwealth Entities | 43–45 (PM&C and AGD) | 7–11 | 2 | 2/2 |
| 2024 — Management of Cyber Security Incidents | 48–49 (AUSTRAC) | 7–11 | 7 | 7/7 |
| **Total** | **5 pages** | | **9** | **9/9** |

Raw model outputs, page references and validation results are saved in `data/evaluations/anao-2021-pilot.json` and `data/evaluations/anao-2024-pilot.json`. The original 2024 attempt with pages 47–49 stalled and was cancelled; it **did not** yield output or a model score. A new 48–49 run completed.

## Second-model source review (provisional, not auditor ground truth)

Before reading the extraction results, a different AI assistant inspected the selected detailed source pages and identified **2 issue concepts in 2021 and 10 in 2024**. This is a subjective working reference, not an independently adjudicated or exhaustive expert label set.

| Source paragraphs | Source-backed issue concepts identified by the reviewer | What the model did |
| --- | --- | --- |
| 2021 §§2.27, 2.33 | Incomplete event-monitoring assurance (PM&C); undocumented/unapproved security-event reviews (AGD) | Extracted both as separate records |
| 2024 §2.55 | Decentralised logging not implemented in the recommended manner | Extracted |
| 2024 §2.56 | Insufficient SIEM coverage; missing monitoring-resource prioritisation strategy | **Merged two distinct deficiencies into one record** |
| 2024 §2.59 | Automatic alert prioritisation unused; analyst escalations undocumented | Extracted both |
| 2024 §2.61 | Non-significant event investigations not formally recorded | Extracted |
| 2024 §2.62 | Undefined event-analysis timeframes; absent timeliness/completeness reviews; historical SIEM archive unavailable; missing event retrieval processes | **Merged four distinct deficiencies into two records** |

On a meaning-based second-model review, all nine reported findings are supported by the detailed passages; however the **seven 2024 records consolidate ten provisionally identified issues**. This is a substantive extraction granularity error, even though every quote is verifiable. Category assignment also needs adjudication; e.g., alert-prioritisation weaknesses could reasonably fall under logging/monitoring or incident response.

Do **not** present the 12/12 concept-level correspondence as a formally measured recall score, or 9/9 semantic support as expert-certified precision. This was a deliberately chosen tiny development pilot with AI-assisted reference review, and atomicity decisions affect the denominator.

## Withheld-summary thematic cross-check

Only after inference, the evaluator read the report's withheld summary pages.

- **2024, summary PDF p. 9:** ANAO independently highlights inadequate AUSTRAC logging coverage and undocumented analysis of security events. This **agrees with the extracted monitoring-related theme**, but the summary also covers business continuity, recovery and broader controls outside the pages supplied to the model.
- **2021, summary PDF p. 10:** ANAO describes broader maturity and mitigation-strategy weaknesses at PM&C and AGD. The narrow selected input pages establish specific monitoring issues, **not** the report's broader cyber-resilience conclusion. The model must not infer that conclusion from this pilot.

Across the two audit documents, **incomplete security-event coverage/review and weak documentation of monitoring or escalation** form a plausible common theme. Code can count source-backed records, but two targeted reports are not evidence of overall prevalence or government-wide risk.

## Assessment implication and next step

The proposed workflow is workable on actual **individual public audit reports**, with traceable source evidence and recurring themes. It still needs an explicit atomic-issue definition, semantic review and a frozen evaluation set. A larger test should sample independent agencies, unrelated topics and negative passages, include the unobserved Services Australia findings and compare an unstructured baseline. The assessment asks primarily for a **solution proposal**, so this pilot supports feasibility rather than production-ready accuracy.

No confidential audit letters were used. All reported model findings remain provisional.
