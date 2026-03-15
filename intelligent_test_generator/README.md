# intelligent_test_generator

Generates test cases as CSV from a PRD. Uses intelligent_common_utils for LLM, config, and tracing. Output conforms to testCase_template (ID, Name, Description, Requirement ID, etc.).

## Run

From repo root:
  PYTHONPATH=intelligent_common_utils/src:intelligent_test_generator/src \\
  python -m generator_core.main --prd resources/PRD.txt --output generated_testcases/out.csv

Optional: --config, --max-cases.
