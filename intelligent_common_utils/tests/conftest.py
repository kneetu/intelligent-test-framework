"""Pytest fixtures: fake LLM for deterministic tests."""

import sys
from pathlib import Path

# Ensure src is on path so agent_core is importable
src = Path(__file__).resolve().parents[1] / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage


class FakeListChatModel(BaseChatModel):
    """Deterministic fake LLM returning predefined responses."""

    responses: list[str]

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatGeneration, ChatResult

        text = self.responses.pop(0) if self.responses else "ok"
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    @property
    def _llm_type(self) -> str:
        return "fake_list"

    def _generate_async(self, messages, stop=None, run_manager=None, **kwargs):
        return self._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


@pytest.fixture
def fake_llm() -> BaseChatModel:
    """Fake LLM that returns a single deterministic response."""
    return FakeListChatModel(responses=["Test response from fake LLM."])
