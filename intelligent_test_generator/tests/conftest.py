"""Fake LLM for deterministic generator tests."""

import sys
from pathlib import Path

gen_src = Path(__file__).resolve().parents[1] / "src"
common_src = Path(__file__).resolve().parents[2] / "intelligent_common_utils" / "src"
for p in (common_src, gen_src):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class FakeListChatModel(BaseChatModel):
    """Returns predefined text (e.g. JSON for PydanticOutputParser)."""

    responses: list

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        text = self.responses.pop(0) if self.responses else "{}"
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=text))]
        )

    @property
    def _llm_type(self) -> str:
        return "fake_list"


@pytest.fixture
def fake_llm() -> BaseChatModel:
    """Fake LLM returning a minimal valid test case JSON."""
    minimal = (
        '{"ID": "TC-REQ-001", "Name": "Sample test", "Requirement ID": "PRD-1", '
        '"Component/Module": "Auth", "Test Group": "Full", '
        '"Test Type": "Functional", "Priority": "P1"}'
    )
    return FakeListChatModel(responses=[minimal])
