# First live extraction evaluation (development set)

**Date:** 10 October 2026. **Model:** `gpt-6-luna`, `medium` reasoning, via authenticated Codex CLI 0.155.0 (`--ephemeral --ignore-user-config --sandbox read-only`). Source content was placed in the prompt; the model did not need filesystem tools. Two separate model calls were made.

## Source scope and observations

- AGO FY2022/23, PDF pages 32-33 (printed 22-23): PSD / HRP, observations 30, 32, 33, 36a and 36b.
- AGO FY2023/24, PDF pages 84-85 and 105 (printed 72-73 and 93): MSF / GPLS and BBO, ECDA / CMS, observations 78, 80, 81, 144 and 145.
- These pages were selected *because* the provisional reference labels cover them. This is **not** a held-out experiment, a random sample or a complete evaluation of either report.

## Results

| Measure | PSD | MSF/ECDA | Combined |
| --- | ---: | ---: | ---: |
| Model-proposed atomic weaknesses | 6 | 11 | 17 |
| Evidence quotes found on cited PDF pages after type normalisation | 6 | 11 | 17 |
| Source-quote rejections after normalisation | 0 | 0 | 0 |
| Selective reference labels on these pages | 5 | 5 | 10 |
| Strict nested-quote and category matches to selective labels | 3 | 5 | 8 |
| Matching observation ID, category, entity and PDF page | 5 | 5 | 10 |
| Numeric observation IDs corrected to strings | 0 | 11 | 11 |

The two PSD strict quote-span mismatches referred to the same observation and category as their labels but used different verifiable evidence spans. The MSF/ECDA response initially failed schema validation because it returned observation IDs as JSON integers. A deterministic correction converts only integers already present in the declared target observation set to strings. All 11 quotes then passed the **same** PDF-source validation. Original model records and correction indices are retained.

**Do not report conventional precision or recall from this sample.** The existing 17 researcher labels were made as illustrative anchors and are not exhaustive even within the target paragraphs. The model extracted extra plausible, source-backed weaknesses (including incomplete privileged-activity logs and access reviews). Calling them false positives would be misleading. Similarly, 10/10 selective anchor coverage does not prove that all actual weaknesses were found.

Source validation verifies *quote location*, not semantic truth, correct taxonomy, completeness, or whether different records should be combined. The model also split PSD's incomplete server-account and database-account reviews under observation 36b into separate records; whether these count as one or two atomic weaknesses requires an explicit annotation rule.

## Reproduce and inspect

The committed [model-output snapshot](../data/evaluations/phase1-dev-gpt6-luna-20261010.json) contains unedited model records, observed type corrections and independently validated results. It is not a mock benchmark.

With the two official PDFs under `data/raw/`, `pypdf` installed and Codex CLI authenticated as the execution account:

```powershell
python scripts/run_codex_eval.py --group psd --codex 'C:\Users\ryano\.codex\packages\standalone\current\bin\codex.exe'
python scripts/run_codex_eval.py --group msf-ecda --codex 'C:\Users\ryano\.codex\packages\standalone\current\bin\codex.exe'
```

Live runs write `outputs/codex-dev-*.json` (ignored by Git) and can vary on repetition. They use no API key or unrestricted Codex execution.

## Next measurement

1. Finish labelling *all* atomic weaknesses in the selected numbered paragraphs and agree on when scope-specific subissues count separately.
2. Manually adjudicate model predictions against that complete reference, including quote-span differences, category decisions, and duplicates.
3. Freeze the extraction prompt and rules before examining FY2024/25 as a held-out set.
4. Compare against an unstructured chatbot baseline using the same input budget; report extraction quality, source support, and qualitative errors separately.
