"""
Run generator: load PRD, run LCEL (prompt | llm | parser), validate, write CSV.
Uses agent_core from intelligent_common_utils (path must be set).
"""

import csv
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Ensure intelligent_common_utils is on path when running from generator
_common_src = Path(__file__).resolve().parents[2] / "intelligent_common_utils" / "src"
if _common_src.exists() and str(_common_src) not in sys.path:
    sys.path.insert(0, str(_common_src))

from generator_core.prompts import GENERATE_ONE_TEST
from generator_core.schema import TestCaseRow

logger = logging.getLogger(__name__)


def _load_config(config_path: Optional[str]) -> dict:
    """
    Load generator configuration from a JSON file, if provided.

    Returns an empty dict if no path is given, the file does not exist,
    or the file cannot be parsed.
    """
    if not config_path:
        return {}
    path = Path(config_path)
    if not path.is_file():
        logger.warning("Config file not found at %s; ignoring.", config_path)
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        logger.warning("Config file %s did not contain a JSON object; ignoring.", config_path)
        return {}
    except Exception as e:
        logger.warning("Failed to load config from %s: %s", config_path, e)
        return {}


def _get_llm():
    """Get LLM from common_utils (gpt-4o-mini default)."""
    from agent_core.llm import get_llm
    return get_llm()


async def generate_one_case(
    requirement_text: str,
    requirement_id: str,
    component: str,
    llm=None,
) -> TestCaseRow:
    """
    Generate one test case from a requirement using LCEL: prompt | llm | parser.
    """
    from langchain_core.output_parsers import PydanticOutputParser

    if llm is None:
        llm = _get_llm()
    parser = PydanticOutputParser(pydantic_object=TestCaseRow)
    chain = GENERATE_ONE_TEST | llm | parser
    try:
        result = await chain.ainvoke(
            {
                "requirement_text": requirement_text,
                "requirement_id": requirement_id,
                "component": component,
                "format_instructions": parser.get_format_instructions(),
            }
        )
        if isinstance(result, TestCaseRow):
            return result
        return TestCaseRow.model_validate(result)
    except Exception as e:
        logger.exception("generate_one_case failed: %s", e)
        raise


async def run_generator(
    prd_path: str,
    output_csv_path: str,
    config_path: Optional[str] = None,
    max_cases: Optional[int] = None,
) -> str:
    """
    Load PRD, generate test cases via LCEL, write CSV. Returns path to CSV.
    """
    from agent_core.tools.prd_loader import load_prd_content
    from agent_core.utils.tracing import setup_tracing

    setup_tracing()

    # Load optional configuration (e.g., default max_cases) from config_path.
    config = _load_config(config_path)
    if max_cases is None:
        cfg_max_cases = config.get("max_cases")
        if isinstance(cfg_max_cases, int) and cfg_max_cases > 0:
            max_cases = cfg_max_cases

    prd_content = await load_prd_content(prd_path)
    if not prd_content.strip():
        logger.warning("PRD empty or unreadable; writing header-only CSV.")
    # Split PRD into rough sections (by numbered items or paragraphs)
    sections = _split_prd_into_requirements(prd_content)
    if max_cases is not None:
        sections = sections[: max_cases]
    llm = _get_llm()
    rows: List[TestCaseRow] = []
    for i, (req_id, text, component) in enumerate(sections):
        try:
            row = await generate_one_case(
                requirement_text=text,
                requirement_id=req_id,
                component=component,
                llm=llm,
            )
            rows.append(row)
        except Exception as e:
            logger.warning("Skipping section %s: %s", req_id, e)
    out_path = Path(output_csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(out_path, rows)
    return str(out_path)


def _split_prd_into_requirements(prd_content: str) -> List[tuple]:
    """Split PRD text into (requirement_id, text, component) for each section."""
    lines = prd_content.strip().split("\n")
    sections: List[tuple] = []
    current = []
    component = "General"
    req_id = "PRD-1"
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                sections.append((req_id, "\n".join(current), component))
                current = []
            continue
        if stripped[0].isdigit() and "." in stripped[:4]:
            if current:
                sections.append((req_id, "\n".join(current), component))
            parts = stripped.split(".", 1)
            req_id = f"PRD-{parts[0].strip()}"
            current = [parts[1].strip()] if len(parts) > 1 else [stripped]
        else:
            current.append(stripped)
    if current:
        sections.append((req_id, "\n".join(current), component))
    if not sections:
        sections = [("PRD-1", prd_content[:2000] or "No content", "General")]
    return sections


def _write_csv(path: Path, rows: List[TestCaseRow]) -> None:
    """Write rows to CSV with exact header from testCase_template."""
    with path.open("w", newline="", encoding="utf-8") as f:
        header = (
            rows[0].to_csv_header()
            if rows
            else (
                "ID,Name,Description,Requirement ID,Component/Module,Test Type,"
                "Priority,Severity,Pre-requisite,Test Data,Environment,Steps,"
                "Expected,Actual Value,Additional Notes,Automation Priority,"
                "Automation Status,Owner,Estimated Time (mins),Tags,Defect,"
                "Status,Version"
            )
        )
        f.write(header + "\n")
        for row in rows:
            f.write(row.to_csv_row() + "\n")
    logger.info("Wrote %s rows to %s", len(rows), path)
