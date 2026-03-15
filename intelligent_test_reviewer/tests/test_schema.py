"""Review schema tests."""

from reviewer_core.schema import ReviewResult, SingleCaseReview


def test_single_case_review() -> None:
    r = SingleCaseReview(
        test_case_id="TC-001",
        verdict="Accept",
        issues=[],
        suggestions=[],
        severity="Low",
    )
    assert r.test_case_id == "TC-001"
    assert r.verdict == "Accept"


def test_review_result_json() -> None:
    result = ReviewResult(
        case_reviews=[],
        summary="Done",
        total_accepted=0,
        total_rejected=0,
    )
    assert "Done" in result.model_dump_json()
