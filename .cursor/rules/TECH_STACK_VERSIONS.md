---
Description: Canonical tech stack versions and policies for the intelligent-test-framework multi-module Python project.
glob: "**"
---

### Tech stack overview

This workspace contains three Python modules that MUST share a single dependency baseline:

- `intelligent_test_generator`
- `intelligent_test_reviewer`
- `intelligent_common_utils`

All new services, agents, and utilities in these modules MUST follow the versions and policies defined in this rule, unless a more specific module-level rule explicitly overrides them.

### Language & runtime versions

- **Python baseline**
  - Target: **Python 3.10**
  - Allowed range for all code, tools, Docker images and CI:
    - `python>=3.10,<3.13`
  - Any upgrade outside this range MUST:
    - Be tested across all three modules.
    - Be reflected here, in `requirements.txt`, and in any Docker/K8s manifests.

### Library versions & policies

- **LangChain (Python)**
  - Pinned version for this project:
    - `langchain==1.2.11`
  - Rationale: current stable LangChain v1 release compatible with Python 3.10+ and LangGraph v1, suitable as an LTS-style baseline.
  - Policy:
    - All LangChain usage (chains, agents, tools, retrievers, etc.) SHOULD be implemented in `intelligent_common_utils` and reused by other modules.
    - Minor version upgrades within `1.x` MUST be tested across all three modules before changing this rule.

- **LangGraph**
  - Pinned version:
    - `langgraph==1.1.0`
  - Rationale: stable LangGraph v1 release designed to pair with LangChain v1 and Python 3.10+.
  - Policy:
    - Graph definitions and execution runtimes SHOULD live in `intelligent_common_utils`.
    - Other modules MUST NOT depend on a different `langgraph` major or minor version.

- **LangSmith (Python client)**
  - Pinned version:
    - `langsmith==0.7.4`
  - Rationale: current stable LangSmith Python client with tracing and evaluation support for LangChain/LangGraph applications.
  - Policy:
    - Only `intelligent_common_utils` should declare a direct dependency on `langsmith`.
    - Other modules SHOULD consume shared utilities (e.g. tracing, client helpers) from `intelligent_common_utils` instead of importing `langsmith` directly.

- **Pydantic**
  - Pinned version:
    - `pydantic==2.12.5`
  - Rationale: latest stable Pydantic 2.12 patch release; avoids 2.13 beta while staying on Pydantic v2.
  - Policy:
    - All new models MUST use Pydantic v2 APIs and `BaseModel`.
    - Do NOT introduce new Pydantic v1-style configuration or validators.
    - Structured outputs for agents and all external API responses MUST be represented as Pydantic models.

- **FastAPI**
  - Pinned version:
    - `fastapi==0.135.1`
  - Rationale: current stable FastAPI release compatible with Pydantic v2 and Python 3.10+.
  - Policy:
    - External integration endpoints (including Jenkins-facing APIs) MUST be implemented using FastAPI.
    - Request/response bodies MUST be defined using the Pydantic v2 baseline above.

### Database version policy

- **PostgreSQL**
  - Target database version:
    - **PostgreSQL 16.13**
  - Policy:
    - Docker images and K8s manifests for Postgres MUST use a 16.x tag, e.g.:
      - `postgres:16`
      - `postgres:16.13`
    - Older major versions (`postgres:15`, `postgres:14`, etc.) MUST NOT be used for new infrastructure.
    - If a newer 16.x patch is adopted, update this rule and any manifests together in the same change.

### Typing & schema patterns

- **TypedDict and Annotated**
  - Use `typing.TypedDict` (and `typing_extensions` only where required by Python 3.10) for lightweight schema-like dicts.
  - Use `typing.Annotated` to attach metadata to reducer state, inputs, and outputs where helpful (for example, to describe semantics for LangGraph state or tool parameters).

- **Annotated reducer pattern (high-level policy)**
  - Reducer-like functions that transform agent or graph state SHOULD:
    - Accept and return well-typed objects (Pydantic models or TypedDict-based state).
    - Prefer `Annotated[...]` where additional metadata is needed for tooling or runtime behavior.
  - Further details may be defined in dedicated rules or skills; new reducer-style utilities SHOULD follow the same approach consistently across modules.

### Module-specific notes

- **`intelligent_test_generator`**
  - MAY depend on:
    - `langchain`
    - `langgraph`
    - Pydantic
    - FastAPI (for any future service interfaces)
  - SHOULD obtain shared configuration, database access, LangChain/LangGraph wiring, and LangSmith integration from `intelligent_common_utils`.

- **`intelligent_test_reviewer`**
  - Same version expectations as `intelligent_test_generator`.
  - SHOULD reuse shared utilities and clients from `intelligent_common_utils` instead of configuring LangChain/LangGraph/LangSmith independently.

- **`intelligent_common_utils`**
  - Owns:
    - LangChain and LangGraph configuration.
    - LangSmith client setup.
    - Postgres connections and data access helpers.
  - MUST follow the exact versions and policies defined in this rule and SHOULD be the first place updated when the stack is upgraded.

