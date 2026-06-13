@echo off
REM Run generator then reviewer (e2e). From repo root. Windows cmd.
setlocal
set "ROOT=%~dp0.."

if "%~1"=="" (set "PRD=%ROOT%\resources\PRD.txt") else (set "PRD=%~1")
if "%~2"=="" (set "OUT_CSV=%ROOT%\generated_testcases\out.csv") else (set "OUT_CSV=%~2")
if "%~3"=="" (set "OUT_JSON=%ROOT%\review\review.json") else (set "OUT_JSON=%~3")

set "PYTHONPATH=%ROOT%\intelligent_common_utils\src;%ROOT%\intelligent_test_generator\src;%ROOT%\intelligent_test_reviewer\src"

for %%F in ("%OUT_CSV%") do if not exist "%%~dpF" mkdir "%%~dpF"
for %%F in ("%OUT_JSON%") do if not exist "%%~dpF" mkdir "%%~dpF"

echo Step 1: Generate test cases CSV from PRD...
python -m generator_core.main --prd "%PRD%" --output "%OUT_CSV%"
if errorlevel 1 exit /b 1

echo Step 2: Review CSV and write structured feedback...
python -m reviewer_core.main --prd "%PRD%" --csv "%OUT_CSV%" --output "%OUT_JSON%"
if errorlevel 1 exit /b 1

echo Done. CSV: %OUT_CSV% ^| Review: %OUT_JSON%
endlocal
