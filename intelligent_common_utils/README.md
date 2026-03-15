# intelligent_common_utils

Shared agent core for the intelligent-test-framework: LLM (OpenAI gpt-4o-mini default), agent loop, tools, memory, judge, config, Postgres helpers, and LangSmith tracing. Other modules (intelligent_test_generator, intelligent_test_reviewer) depend on this package.

## Layout

- `src/agent_core/`: main, agent, llm, memory, judge, tools/, utils/
- `config/`: configuration files
- `resources/`: optional default configs
- `k8s/`: deployment and service (Postgres 16 when needed)
- `Dockerfile`: multi-stage Python 3.10 build

## Run

- **CLI agent:** From repo root, `PYTHONPATH=intelligent_common_utils/src python -m agent_core.main`
- **API:** `PYTHONPATH=intelligent_common_utils/src python -m agent_core.main serve` (port 8000)
- **Docker:** Build from `intelligent_common_utils/` and run; set `OPENAI_API_KEY` and optionally `LANGSMITH_API_KEY`

## Versions

See workspace [TECH_STACK_VERSIONS](.cursor/rules/TECH_STACK_VERSIONS.mdc): Python 3.10, LangChain 1.2.11, LangGraph 1.1.0, Pydantic 2.12.5, FastAPI 0.135.1, Postgres 16.
