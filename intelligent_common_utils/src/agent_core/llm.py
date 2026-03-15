"""Pluggable LLM interface and OpenAI implementation (gpt-4o-mini default)."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Default model per TECH_STACK_VERSIONS: cost-optimal.
DEFAULT_LLM_MODEL_ID = "gpt-4o-mini"


class LLMConfig(BaseModel):
    """Configuration for the chat LLM (model id and API key source)."""

    model_id: str = Field(default=DEFAULT_LLM_MODEL_ID, description="OpenAI model id")
    api_key_env: str = Field(default="OPENAI_API_KEY", description="Env var for API key")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, description="Max output tokens")


class BaseLLMProvider(ABC):
    """Abstract interface for a chat LLM used by the agent."""

    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        """Return a LangChain chat model instance."""
        ...


def get_llm(
    model_id: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
) -> BaseChatModel:
    """
    Build a LangChain ChatOpenAI model with project default (gpt-4o-mini).

    Override via model_id/temperature/max_tokens or via config/env.
    """
    import os

    from langchain_openai import ChatOpenAI

    resolved_model = model_id or DEFAULT_LLM_MODEL_ID
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set; LLM calls may fail.")
    llm = ChatOpenAI(
        model=resolved_model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key or "",
    )
    return llm
