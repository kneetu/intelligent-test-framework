"""LangSmith tracing setup for LangChain/LangGraph runs."""

import logging
import os

logger = logging.getLogger(__name__)


def setup_tracing(
    project_name: str = "intelligent-test-framework",
    api_key_env: str = "LANGSMITH_API_KEY",
) -> None:
    """
    Enable LangSmith tracing via environment variables.

    Set LANGSMITH_TRACING=true and LANGSMITH_API_KEY (or api_key_env).
    """
    api_key = os.environ.get(api_key_env)
    if api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_PROJECT", project_name)
        os.environ.setdefault("LANGCHAIN_API_KEY", api_key)
    else:
        logger.debug("LangSmith API key not set; tracing disabled.")
