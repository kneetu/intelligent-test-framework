"""
Entry point and FastAPI app for Jenkins integration.
Exposes health and optional triggers; request/response as Pydantic.
"""

import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent_core.agent import Agent
from agent_core.utils.config import load_config
from agent_core.utils.tracing import setup_tracing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Intelligent Common Utils API", version="0.1.0")

# Optional: run generator/reviewer via API can be added here; for now health only.


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="Service status")


class QueryRequest(BaseModel):
    """Request body for a single agent query."""

    query: str = Field(description="User query for the agent")
    use_judge: bool = Field(default=False, description="Whether to use judge and retry")


class QueryResponse(BaseModel):
    """Response body with agent output."""

    response: str = Field(description="Agent response text")


@app.on_event("startup")
def startup() -> None:
    """Enable LangSmith tracing on startup."""
    setup_tracing()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check for Jenkins or load balancers."""
    return HealthResponse(status="ok")


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    """Run one agent query and return the response."""
    config = load_config()
    agent = Agent(config=config)
    try:
        response_text = await agent.ainvoke(req.query, use_judge=req.use_judge)
        return QueryResponse(response=response_text)
    except Exception as e:
        logger.exception("Query failed: %s", e)
        raise


def run_agent_cli() -> None:
    """CLI loop: read config, run agent, accept queries until exit."""
    config_path = Path("config") / "config.json"
    if not config_path.exists():
        config_path = Path("resources") / "config.json"
    config = load_config(config_path)
    setup_tracing()
    agent = Agent(config=config)
    print("Agent ready. Enter queries (or 'exit' to quit).")
    try:
        while True:
            line = input("> ").strip()
            if not line or line.lower() == "exit":
                break
            result = asyncio.run(agent.ainvoke(line, use_judge=False))
            print(result)
    finally:
        pass


if __name__ == "__main__":
    import sys

    if "serve" in sys.argv:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        run_agent_cli()
