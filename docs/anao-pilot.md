# ANAO standalone audit-report pilot

## Why the dataset changes

The GovTech proposal concerns identifying themes across individual audits. The Singapore AGO annual reports remain useful development examples, but they already aggregate selected findings. For a better approximation of the intended inputs, use public **standalone performance-audit reports** from the Australian National Audit Office (ANAO).

Two official source documents have been verified:

| Source | Source PDF | Coverage | Local filename |
| --- | --- | --- | --- |
| [ANAO Report 38, 2023-24: Management of Cyber Security Incidents](https://www.anao.gov.au/work/performance-audit/management-cyber-security-incidents) | [Official PDF](https://www.anao.gov.au/sites/default/files/2024-06/Auditor-General_Report_2023-24_38.pdf) | AUSTRAC and Services Australia | `data/raw/anao-2024-incidents.pdf` |
| [ANAO Report 32, 2020-21: Cyber Security Strategies of Non-Corporate Commonwealth Entities](https://www.anao.gov.au/work/performance-audit/cyber-security-strategies-non-corporate-commonwealth-entities) | [Official PDF](https://www.anao.gov.au/sites/default/files/Auditor-General_Report_2020-21_32.pdf) | Multiple government entities | `data/raw/anao-2021-strategies.pdf` |

The ANAO documents are **published audits** and provide much richer individual findings than AGO annual-report overviews. They are not the auditors' confidential working papers. Australian standards and agencies also differ from Singapore's.

### Local retrieval status

On 10 October 2026, the official links were readable through the web browser, but direct downloads to the restricted Gateway account failed with a reset connection. **Do not claim that the PDFs have been downloaded or that the ANAO pilot has produced model results until files are present and the run is completed.** The files are intentionally git-ignored.

Use an ordinary browser to download both official PDFs, and save them under the exact filenames shown above in the repository's `data/raw/` directory. Do not grant Gateway broader Windows profile permissions.

## Small, defensible experiment

1. Inspect downloaded PDFs with `python -m audit_assurance inspect --report data/raw/anao-2024-incidents.pdf`, plus the analogous 2021 command. Use **physical, 1-based PDF pages**, not a paragraph number or assumed printed-page offset.
2. Identify 2-4 detailed findings pages from each report. The published 2024 table of contents places AUSTRAC analysis around printed pages 30-57; the 2021 report puts implementation findings around printed pages 35-56. Choose actual physical pages after inspecting the PDFs.
3. Withhold the executive summary and recommendations pages (around printed 7-17) **from the extraction model**. The runner enforces disjoint page sets and does not put withheld content in the prompt.
4. Run GPT-6 Luna with Medium reasoning in an **ephemeral, read-only** Codex session. Strictly validate each verbatim quote against its cited PDF page. No bypass of the Windows sandbox is required.
5. Independently assess the extracted findings against the detailed source pages, then compare the resulting themes against the withheld summaries/recommendations. These published summaries are an **incomplete thematic reference** and cannot by themselves yield exhaustive recall or precision.
6. If the first two runs work, group source-verified weaknesses across reports by control area. Multiple records in a category indicate a possible shared theme, **not** proof of repeated breaches by the same agency.

### Example commands (after downloading PDFs)

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m audit_assurance inspect --report data/raw/anao-2024-incidents.pdf --limit 20
python -m audit_assurance inspect --report data/raw/anao-2021-strategies.pdf --limit 20
python scripts/run_anao_pilot.py --report data/raw/anao-2024-incidents.pdf --detail-pages 45,46 --summary-pages 9,10 --codex "C:\Users\ryano\.codex\packages\standalone\current\bin\codex.exe" --output outputs/anao-2024-pilot.json
python scripts/run_anao_pilot.py --report data/raw/anao-2021-strategies.pdf --detail-pages 38,39 --summary-pages 9,10 --codex "C:\Users\ryano\.codex\packages\standalone\current\bin\codex.exe" --output outputs/anao-2021-pilot.json
```

**Recheck the example page selections after inspection**: printed and physical PDF page numbers must not be confused. The runner records exact detail and withheld page sets for auditability.

### Limits and stop rule

The experiment measures extraction from **published findings**, not discovery from confidential audit evidence. Source-quote checks establish provenance but not the truth of the inference. Summary/recommendation alignment is a *secondary qualitative check* rather than automatic gold labels; a separate reviewer or manually adjudicated exhaustive labels are still needed for formal precision and recall.

Do not over-invest in changing the pipeline before the files arrive. If the direct PDF download remains blocked, a user-assisted browser download is preferable to unsafe permission or sandbox changes. The principal submission remains the assessment proposal.
