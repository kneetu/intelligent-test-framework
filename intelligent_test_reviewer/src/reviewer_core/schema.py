"""Pydantic models for structured review feedback (no free-text primary output)."""

from typing import List

from pydantic import BaseModel, Field


class SingleCaseReview(BaseModel):
    """Review result for one test case row."""

    test_case_id: str = Field(description="ID of the test case (e.g. TC-LOGIN-001)")
    verdict: str = Field(description="Accept / Reject / Needs revision")
    issues: List[str] = Field(default_factory=list, description="List of issues found")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    severity: str = Field(default="Medium", description="Overall severity of issues")


class ReviewResult(BaseModel):
    """Structured feedback for a set of test cases (file or batch)."""

    case_reviews: List[SingleCaseReview] = Field(default_factory=list)
    summary: str = Field(default="", description="Brief overall summary")
    total_accepted: int = Field(default=0)
    total_rejected: int = Field(default=0)
