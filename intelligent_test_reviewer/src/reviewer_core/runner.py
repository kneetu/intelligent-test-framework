"""
Run reviewer: load PRD + CSV, run LCEL per row (or batch), write structured JSON.
"""

import csv
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

_common_src = Path(__file__).resolve().parents[2] / "intelligent_common_utils" / "src"
if _common_src.exists() and str(_common_src) not in sys.path:
    sys.path.insert(0, str(_common_src))

from reviewer_core.prompts import REVIEW_ONE_CASE
from reviewer_core.schema import ReviewResult, SingleCaseReview

logger = logging.getLogger(__name__)


def _get_llm():
    from agent_core.llm import get_llm
    return get_llm()


async def review_one_case(
    prd_excerpt: str,
    test_case_text: str,
    llm=None,
) -> SingleCaseReview:
    """Review one test case using LCEL: prompt | llm | parser."""
    from langchain_core.output_parsers import PydanticOutputParser

    if llm is None:
        llm = _get_llm()
    parser = PydanticOutputParser(pydantic_object=SingleCaseReview)
    chain = REVIEW_ONE_CASE | llm | parser
    try:
        result = await chain.ainvoke(
            {
                "prd_excerpt": prd_excerpt[:3000],
                "test_case_text": test_case_text[:2000],
                "format_instructions": parser.get_format_instructions(),
            }
        )
        if isinstance(result, SingleCaseReview):
            return result
        return SingleCaseReview.model_validate(result)
    except Exception as e:
        logger.exception("review_one_case failed: %s", e)
        raise


async def run_reviewer(
    prd_path: str,
    csv_path: str,
    output_json_path: str,
    config_path: Optional[str] = None,
    max_reviews: Optional[int] = None,
) -> str:
    """Load PRD and CSV, run review for each row, write ReviewResult JSON."""
    from agent_core.tools.prd_loader import load_prd_content
    from agent_core.utils.tracing import setup_tracing

    setup_tracing()
    prd_content = await load_prd_content(prd_path)
    rows = _read_csv_rows(csv_path)
    if max_reviews is not None:
        rows = rows[:max_reviews]
    llm = _get_llm()
    case_reviews: List[SingleCaseReview] = []
    for row in rows:
        try:
            review = await review_one_case(
                prd_excerpt=prd_content[:3000],
                test_case_text=row,
                llm=llm,
            )
            case_reviews.append(review)
        except Exception as e:
            logger.warning("Skipping row: %s", e)
    accepted = sum(1 for r in case_reviews if "accept" in r.verdict.lower())
    rejected = sum(1 for r in case_reviews if "reject" in r.verdict.lower())
    result = ReviewResult(
        case_reviews=case_reviews,
        summary=f"Reviewed {len(case_reviews)} cases.",
        total_accepted=accepted,
        total_rejected=rejected,
    )
    out_path = Path(output_json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Wrote review to %s", out_path)
    return str(out_path)


def _read_csv_rows(csv_path: str) -> List[str]:
    """Read CSV and return list of row strings (for context to LLM)."""
    path = Path(csv_path)
    if not path.exists():
        return []
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(json.dumps(row))
    return rows
