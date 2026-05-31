#!/usr/bin/env bash
# Run generator then reviewer (e2e). From repo root.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRD="${1:-$ROOT/resources/PRD.txt}"
OUT_CSV="${2:-$ROOT/generated_testcases/out.csv}"
OUT_JSON="${3:-$ROOT/review/review.json}"
export PYTHONPATH="$ROOT/intelligent_common_utils/src:$ROOT/intelligent_test_generator/src:$ROOT/intelligent_test_reviewer/src"
mkdir -p "$(dirname "$OUT_CSV")" "$(dirname "$OUT_JSON")"
echo "Step 1: Generate test cases CSV from PRD..."
python -m generator_core.main --prd "$PRD" --output "$OUT_CSV"
echo "Step 2: Review CSV and write structured feedback..."
python -m reviewer_core.main --prd "$PRD" --csv "$OUT_CSV" --output "$OUT_JSON"
echo "Done. CSV: $OUT_CSV | Review: $OUT_JSON"
