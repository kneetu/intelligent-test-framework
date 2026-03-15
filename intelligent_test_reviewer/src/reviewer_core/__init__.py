"""Test case reviewer: PRD + CSV -> structured feedback (Pydantic)."""

from reviewer_core.schema import ReviewResult
from reviewer_core.runner import run_reviewer

__all__ = ["ReviewResult", "run_reviewer"]
