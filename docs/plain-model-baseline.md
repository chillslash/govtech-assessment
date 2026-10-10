# Plain GPT-6 Luna Medium baseline (no audit framework)

Date: 10 October 2026. This is the **first configuration** of a potential four-way experiment. The other three configurations **were not run**; no new discovery or atomic-extraction changes were made.

## Method

- Model: `gpt-6-luna`, `model_reasoning_effort="medium"`, Codex CLI, read-only and ephemeral execution.
- Direct, zero-shot, natural-language question; no audit taxonomy, JSON schema, examples, forced exact quotes, extraction-level validation or automated discovery. Python only converts the **same selected PDF pages** into text for the input. The instruction not to use tools was necessary for the restricted Windows account and is not an audit-extraction framework.
- Exactly the same selected pages used in the previous framework experiment: 2021 ANAO PDF pages **43, 44, 45** (PM&C/AGD), and 2024 ANAO PDF pages **48, 49** (AUSTRAC).
- Executive summaries (PDF pages 7-11 of each document) were withheld from model input. Audit **recommendations within the detailed source pages were not removed** from either configuration; this is a potential confound.
- Two separate model calls, one per report. Raw outputs and exact question saved in `data/evaluations/anao-baseline-2021-luna-medium.json` and `data/evaluations/anao-baseline-2024-luna-medium.json`. Run script: `scripts/run_simple_anao_baseline.py`.
- The baseline was evaluated *after* generating the responses, using the same original source passages and previous second-model source review. Evaluation is qualitative and non-blind, not an expert-certified benchmark.

The actual user-facing question (identical for both reports):

> Read the following excerpts from a government audit report. Identify the IT or cybersecurity control weaknesses described. For each issue, briefly explain what was wrong and identify the agency and source page. Mention any common themes you notice. Base your answer only on the excerpts.

## What the model produced

| ANAO report | Plain prompt: reported points | Framework: structured records | Observation |
| --- | ---: | ---: | --- |
| 2021, PDF 43-45 | **4** | **2** | Baseline identified both directly described deficiencies (PM&C monitoring, AGD review documentation). Its other two points cite **recommendations** (nos. 3 and 4) as weaknesses; one extends the stated issue into configuration/user-access testing, while one restates AGD's documentation shortfall. Do not treat all four as independent, independently verified audit findings. |
| 2024, PDF 48-49 | **7** | **7** | Baseline identified substantively the same seven groupings and cited physical PDF pages. Both approaches **merged** separate related issues in paragraphs 2.56 and 2.62 into fewer records. |
| **Total** | **11 reported points** | **9 records** | **Counts are not equivalent to true positives or recall.** |

Both baseline runs completed successfully; the saved raw model answers include page references and narrative themes. The earlier framework's **9/9 quote-location verification** demonstrates deterministic evidence checking. It **does not prove** that the framework extracts more weaknesses or interprets them more accurately than the plain prompt. Likewise, we should not call baseline page citations invalid just because they were not passed through our automated quote validator: those are different output requirements.

## Interpretation

**Core result:** On this very small, already-selected excerpt set, a capable zero-shot model performs at least comparably at *identifying and grouping* the observed weaknesses. **No meaningful uplift in discovery or extraction quality has been established for the framework.**

The framework currently contributes machine-readable consistent records and the ability to **reject invented or incorrectly located quotes** when such outputs occur; that is a separate reliability mechanism, not measured extraction-performance uplift here. The baseline also generated a useful within-report thematic summary without bespoke classification.

The framework therefore should not be pitched as demonstrably more accurate or complete based on this comparison. Potential sources of gain remain untested: whole-document *discovery*, more consistent atomic findings, and cross-report analysis. These should be justified and measured later only if appropriate; the user explicitly asked **not to run** the other configurations until this result has been reviewed.

### Important limitations

- Tiny non-random development sample (five PDF pages, two ANAO reports), previously explored.
- Independent review was by a second AI, not an expert auditor, and has no adjudicated exhaustive labels.
- Recommendations remain embedded in the provided pages and can be mistaken for directly observed deficiencies.
- No repeated seeds/runs, no uncertainty estimates, no baseline structural-consistency benchmark and no end-to-end full-report retrieval.
- No inference about all government audit reports, a production performance guarantee, or model-cost advantage.

**Next decision belongs to the user:** whether this result warrants improved discovery, atomicity and a controlled comparison. None has been initiated as part of this baseline.
