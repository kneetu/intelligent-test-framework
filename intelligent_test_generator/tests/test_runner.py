"""Generator runner with fake LLM for deterministic output."""

import pytest

from generator_core.runner import generate_one_case
from generator_core.schema import TestCaseRow


@pytest.mark.asyncio
async def test_generate_one_case_with_fake_llm(fake_llm) -> None:
    """generate_one_case returns a TestCaseRow when LLM returns valid JSON."""
    result = await generate_one_case(
        requirement_text="User can log in with email.",
        requirement_id="PRD-1",
        component="Auth",
        llm=fake_llm,
    )
    assert isinstance(result, TestCaseRow)
    assert result.ID == "TC-REQ-001"
    assert result.Name == "Sample test"
