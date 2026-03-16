"""Entry point: CLI to run reviewer (PRD + CSV -> JSON)."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

_common = Path(__file__).resolve().parents[2] / "intelligent_common_utils" / "src"
if _common.exists() and str(_common) not in sys.path:
    sys.path.insert(0, str(_common))

from reviewer_core.runner import run_reviewer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review test cases CSV against PRD; output structured JSON"
    )
    parser.add_argument("--prd", required=True, help="Path to PRD file")
    parser.add_argument("--csv", required=True, help="Path to test cases CSV")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    parser.add_argument("--config", default=None)
    parser.add_argument("--max-reviews", type=int, default=None)
    args = parser.parse_args()
    try:
        out = asyncio.run(
            run_reviewer(
                prd_path=args.prd,
                csv_path=args.csv,
                output_json_path=args.output,
                config_path=args.config,
                max_reviews=args.max_reviews,
            )
        )
        print(f"Wrote review to {out}")
    except Exception as e:
        logger.exception("Reviewer failed: %s", e)
        raise


if __name__ == "__main__":
    main()
