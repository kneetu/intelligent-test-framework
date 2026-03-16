"""Review runner with fake LLM."""

import pytest

from reviewer_core.runner import review_one_case
from reviewer_core.schema import SingleCaseReview


@pytest.mark.asyncio
async def test_review_one_case_fake_llm(fake_llm) -> None:
    result = await review_one_case(
        prd_excerpt="User can log in.",
        test_case_text='{"ID": "TC-001", "Name": "Login test"}',
        llm=fake_llm,
    )
    assert isinstance(result, SingleCaseReview)
    assert result.test_case_id == "TC-001"
    assert result.verdict == "Accept"
