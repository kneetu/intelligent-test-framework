"""
Entry point: parse CLI/config, load PRD, run generator, write CSV.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add intelligent_common_utils to path
_common = Path(__file__).resolve().parents[2] / "intelligent_common_utils" / "src"
if _common.exists() and str(_common) not in sys.path:
    sys.path.insert(0, str(_common))

from generator_core.runner import run_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """CLI: --prd, --output, optional --config, --max-cases."""
    parser = argparse.ArgumentParser(description="Generate test cases CSV from PRD")
    parser.add_argument("--prd", required=True, help="Path to PRD file")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--config", default=None, help="Path to config file")
    parser.add_argument("--max-cases", type=int, default=None, help="Max cases to generate")
    args = parser.parse_args()
    try:
        out = asyncio.run(
            run_generator(
                prd_path=args.prd,
                output_csv_path=args.output,
                config_path=args.config,
                max_cases=args.max_cases,
            )
        )
        logger.info("Wrote CSV to %s", out)
    except Exception as e:
        logger.exception("Generator failed: %s", e)
        raise


if __name__ == "__main__":
    main()
