# Intelligent Test Framework

Multi-module framework for PRD-driven test case generation and review. Three modules share a common agent stack (LLM, tools, memory, judge) and produce CSV test cases plus structured review feedback.

## Modules

| Module | Purpose |
|--------|--------|
| **intelligent_common_utils** | Shared agent core: LLM (OpenAI gpt-4o-mini), agent loop, tools, memory, judge, config, Postgres helpers, LangSmith tracing, FastAPI for Jenkins |
| **intelligent_test_generator** | Reads PRD + config → generates test cases as **CSV** (IDs `TC-{Component}-{NNN}`, **Test Group** column Smoke/Full/Comprehensive; see testCase_template) |
| **intelligent_test_reviewer** | Reads PRD + generator CSV → outputs **structured review** (JSON, Pydantic) |

## Run each module in isolation

**Common utils (API):**
```bash
cd intelligent_common_utils
PYTHONPATH=src python -m agent_core.main serve
# Health: GET http://localhost:8000/health
```

**Generator (CLI):**
```bash
PYTHONPATH=intelligent_common_utils/src:intelligent_test_generator/src \
  python -m generator_core.main --prd resources/PRD.txt --output generated_testcases/out.csv
```

**Reviewer (CLI):**
```bash
PYTHONPATH=intelligent_common_utils/src:intelligent_test_reviewer/src \
  python -m reviewer_core.main --prd resources/PRD.txt --csv generated_testcases/out.csv --output review/review.json
```

## Run end-to-end (generate then review)

```bash
# 1. Generate CSV
PYTHONPATH=intelligent_common_utils/src:intelligent_test_generator/src \
  python -m generator_core.main --prd resources/PRD.txt --output generated_testcases/out.csv

# 2. Review CSV
PYTHONPATH=intelligent_common_utils/src:intelligent_test_reviewer/src \
  python -m reviewer_core.main --prd resources/PRD.txt --csv generated_testcases/out.csv --output review/review.json
```

Or use the optional e2e script (see `scripts/run_e2e.sh`).

## Tech stack and versions

See [.cursor/rules/TECH_STACK_VERSIONS.mdc](.cursor/rules/TECH_STACK_VERSIONS.mdc): Python 3.10, LangChain 1.2.11, LangGraph 1.1.0, Pydantic 2.12.5, FastAPI 0.135.1, OpenAI gpt-4o-mini, Postgres 16.

## Style and tests

- Format/lint: `black .` and `ruff check .` (line length 100).
- Tests: `pytest` in each module (use fake LLM for deterministic tests).

## Project rules

- [code_style_guide](.cursor/rules/code_style_guide.mdc)
- [modular_agentic_rules](.cursor/rules/modular_agentic_rules.mdc)
- [project_structure](.cursor/rules/project_structure.mdc)
- [testCase_template](.cursor/rules/testCase_template.mdc)
