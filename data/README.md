# Public test corpus

Official source and four candidate AGO PDFs are linked in the repository README.

`raw/` is reserved for downloaded public AGO annual-report PDFs, which are ignored by Git. Keep source links and filenames traceable. Proposed development reports: FY2022/23 and FY2023/24; potential held-out FY2024/25; FY2025/26 already inspected and suitable for demo. Use an actually unseen report for a stronger blind final test.

Start by manually labelling a few **atomic weaknesses** from detailed findings, not just overview paragraphs. Record both physical PDF page number and printed page number, and identify duplicate mentions across overview/detail. Public data only; no confidential audit reports.

To download all four reports on Windows, from the repository root run:

    powershell -ExecutionPolicy Bypass -File .\scripts\download_reports.ps1

This is an optional script and has **not been executed** as part of initial project setup. It downloads source PDFs to the Git-ignored `data/raw/` folder and checks the `%PDF` file header.
