# Run generator then reviewer (e2e). From repo root. PowerShell.
param(
    [string]$Prd,
    [string]$OutCsv,
    [string]$OutJson
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Prd)     { $Prd     = Join-Path $Root "resources/PRD.txt" }
if (-not $OutCsv)  { $OutCsv  = Join-Path $Root "generated_testcases/out.csv" }
if (-not $OutJson) { $OutJson = Join-Path $Root "review/review.json" }

$env:PYTHONPATH = (
    "$Root/intelligent_common_utils/src;" +
    "$Root/intelligent_test_generator/src;" +
    "$Root/intelligent_test_reviewer/src"
)
New-Item -ItemType Directory -Force -Path (Split-Path $OutCsv)  | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $OutJson) | Out-Null

Write-Host "Step 1: Generate test cases CSV from PRD..."
python -m generator_core.main --prd $Prd --output $OutCsv
Write-Host "Step 2: Review CSV and write structured feedback..."
python -m reviewer_core.main --prd $Prd --csv $OutCsv --output $OutJson
Write-Host "Done. CSV: $OutCsv | Review: $OutJson"
