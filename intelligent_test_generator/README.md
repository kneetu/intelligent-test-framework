# intelligent_test_generator

Generates test cases as CSV from a PRD. Uses intelligent_common_utils for LLM, config, and tracing. Output conforms to testCase_template: columns include **Test Group** (after Component/Module); **ID** format is `TC-{Component}-{NNN}` where the pipeline assigns a deterministic **NNN** (global or per-component via config `id_sequence_mode`).

## Run

From repo root:
  PYTHONPATH=intelligent_common_utils/src:intelligent_test_generator/src \\
  python -m generator_core.main --prd resources/PRD.txt --output generated_testcases/out.csv

Optional: `--config`, `--max-cases`. Config JSON may include `id_sequence_mode` (`global` or `per_component`), `id_numeric_width`, `id_component_fallback` (`NULL` or a slug), `id_area_prefix` (override middle segment for all rows).
