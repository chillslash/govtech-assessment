# Download publicly available AGO annual reports for local prototype testing.
# Run from anywhere: powershell -ExecutionPolicy Bypass -File .\scripts\download_reports.ps1
$ErrorActionPreference = 'Stop'
$raw = Join-Path (Split-Path -Parent $PSScriptRoot) 'data\raw'
New-Item -ItemType Directory -Path $raw -Force | Out-Null
$reports = @(
    @{ Name = 'ago-fy2022-23.pdf'; Url = 'https://isomer-user-content.by.gov.sg/357/1bc6d111-c831-4c73-a519-90df522831af/ar_fy2022_23.pdf' },
    @{ Name = 'ago-fy2023-24.pdf'; Url = 'https://isomer-user-content.by.gov.sg/357/baf0b405-c14b-4621-a70e-f370d71bbd76/ar_fy2023_24.pdf' },
    @{ Name = 'ago-fy2024-25.pdf'; Url = 'https://isomer-user-content.by.gov.sg/357/23cd5ad4-3405-4c67-9787-af1d6e389ed5/ar_fy2024_25.pdf' },
    @{ Name = 'ago-fy2025-26.pdf'; Url = 'https://isomer-user-content.by.gov.sg/357/4f8ec87d-3c06-4ada-bc7c-80214c49cfd9/Report%20of%20the%20Auditor-General%20for%20FY2025-26.pdf' }
)
foreach ($report in $reports) {
    $dest = Join-Path $raw $report.Name
    if (Test-Path -LiteralPath $dest) { Write-Output "Already exists: $($report.Name)"; continue }
    Write-Output "Downloading $($report.Name)..."
    Invoke-WebRequest -Uri $report.Url -OutFile $dest -UseBasicParsing -TimeoutSec 90
    $fs = [System.IO.File]::OpenRead($dest)
    try { $header = New-Object byte[] 4; $n = $fs.Read($header, 0, 4) }
    finally { $fs.Dispose() }
    if ($n -ne 4 -or [System.Text.Encoding]::ASCII.GetString($header) -ne '%PDF') {
        Remove-Item -LiteralPath $dest -Force
        throw "Download was not a PDF: $($report.Name)"
    }
    Write-Output "Saved $($report.Name)"
}
