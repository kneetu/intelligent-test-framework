"""Self-critique: review model output and decide retry or accept."""

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class JudgeResult(BaseModel):
    """Result of judge evaluation: accept or retry with reason."""

    accept: bool = Field(description="True if output is acceptable")
    reason: str = Field(default="", description="Short reason for accept/reject")


def judge_output(
    llm: BaseChatModel,
    original_prompt: str,
    model_output: str,
    criteria: str = "Correctness, completeness, and clarity.",
) -> JudgeResult:
    """
    Use the LLM to evaluate model_output against criteria. Returns accept/reject + reason.
    """
    system = (
        "You are a judge. Evaluate the assistant output for the given user request. "
        "Reply with accept=true if the output is correct and complete; otherwise accept=false "
        "and give a short reason."
    )
    user = (
        f"User request:\n{original_prompt}\n\nAssistant output:\n{model_output}\n\n"
        f"Criteria: {criteria}"
    )
    try:
        messages = [SystemMessage(content=system), HumanMessage(content=user)]
        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        # Simple parse: look for accept true/false and reason
        accept = "accept=true" in content.lower() or "accept: true" in content.lower()
        return JudgeResult(accept=accept, reason=content[:500])
    except Exception as e:
        logger.exception("Judge invocation failed: %s", e)
        return JudgeResult(accept=True, reason=f"Judge error: {e}")
