# intelligent_test_reviewer

Reviews test cases (CSV from generator) against the PRD and outputs structured feedback (JSON). Uses intelligent_common_utils for LLM and tracing.

## Run

From repo root:
  PYTHONPATH=intelligent_common_utils/src:intelligent_test_reviewer/src \\
  python -m reviewer_core.main --prd resources/PRD.txt --csv generated_testcases/out.csv --output review/review.json

Optional: --config, --max-reviews.
