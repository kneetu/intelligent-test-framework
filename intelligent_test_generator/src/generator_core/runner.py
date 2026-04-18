"""
Run generator: load PRD, run LCEL (prompt | llm | parser), validate, write CSV.
Uses agent_core from intelligent_common_utils (path must be set).
"""

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Literal

from pydantic import PydanticUndefined

# Ensure intelligent_common_utils is on path when running from generator
_common_src = Path(__file__).resolve().parents[2] / "intelligent_common_utils" / "src"
if _common_src.exists() and str(_common_src) not in sys.path:
    sys.path.insert(0, str(_common_src))

from generator_core.id_utils import (
    assign_sequential_id,
    next_sequence_number,
    resolve_component_segment,
)
from generator_core.prompts import GENERATE_ONE_TEST
from generator_core.schema import TestCaseRow

logger = logging.getLogger(__name__)


def _load_config(config_path: str | None) -> dict[str, Any]:
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


# (TestCaseRow attribute, chain.ainvoke key). Config JSON may override any key.
_PROMPT_DEFAULT_KEYS: tuple[tuple[str, str], ...] = (
    ("Description", "default_description"),
    ("Test_Group", "default_test_group"),
    ("Test_Type", "default_test_type"),
    ("Priority", "default_priority"),
    ("Severity", "default_severity"),
    ("Pre_requisite", "default_pre_requisite"),
    ("Test_Data", "default_test_data"),
    ("Environment", "default_environment"),
    ("Actual_Value", "default_actual_value"),
    ("Additional_Notes", "default_additional_notes"),
    ("Automation_Priority", "default_automation_priority"),
    ("Automation_Status", "default_automation_status"),
    ("Owner", "default_owner"),
    ("Estimated_Time_mins", "default_estimated_time_mins"),
    ("Tags", "default_tags"),
    ("Defect", "default_defect"),
    ("Status", "default_status"),
    ("Version", "default_version"),
)


def _test_case_row_field_default(attr: str) -> Any:
    """Default value for a TestCaseRow field without building a full instance."""
    info = TestCaseRow.model_fields[attr]
    if info.default is not PydanticUndefined:
        return info.default
    if info.default_factory is not None:
        return info.default_factory()
    return None


def _prompt_value_for_key(
    invoke_key: str,
    config: dict[str, Any],
    model_default: Any,
) -> str:
    """Use config override when present; otherwise TestCaseRow field default."""
    if invoke_key in config:
        val = config[invoke_key]
        return "" if val is None else str(val)
    return "" if model_default is None else str(model_default)


def build_chain_invoke_inputs(
    requirement_text: str,
    requirement_id: str,
    component: str,
    format_instructions: str,
    config: dict[str, Any] | None = None,
) -> dict[str, str]:
    """
    Build the full input dict for GENERATE_ONE_TEST | llm | parser.

    Matches all template variables; optional CSV defaults come from TestCaseRow
    defaults unless overridden in config (e.g. default_test_group, default_priority).
    """
    cfg = config if config is not None else {}
    out: dict[str, str] = {
        "requirement_text": requirement_text,
        "requirement_id": requirement_id,
        "component": component,
        "format_instructions": format_instructions,
    }
    for attr, invoke_key in _PROMPT_DEFAULT_KEYS:
        fallback = _test_case_row_field_default(attr)
        out[invoke_key] = _prompt_value_for_key(invoke_key, cfg, fallback)
    return out


async def generate_one_case(
    requirement_text: str,
    requirement_id: str,
    component: str,
    llm=None,
    config: dict[str, Any] | None = None,
) -> TestCaseRow:
    """
    Generate one test case from a requirement using LCEL: prompt | llm | parser.
    """
    from langchain_core.output_parsers import PydanticOutputParser

    if llm is None:
        llm = _get_llm()
    cfg = config if config is not None else {}
    parser = PydanticOutputParser(pydantic_object=TestCaseRow)
    chain = GENERATE_ONE_TEST | llm | parser
    try:
        invoke_payload = build_chain_invoke_inputs(
            requirement_text=requirement_text,
            requirement_id=requirement_id,
            component=component,
            format_instructions=parser.get_format_instructions(),
            config=cfg,
        )
        result = await chain.ainvoke(invoke_payload)
        if isinstance(result, TestCaseRow):
            return result
        return TestCaseRow.model_validate(result)
    except Exception as e:
        logger.exception("generate_one_case failed: %s", e)
        raise


async def run_generator(
    prd_path: str,
    output_csv_path: str,
    config_path: str | None = None,
    max_cases: int | None = None,
) -> str:
    """
    Load PRD, generate test cases via LCEL, write CSV. Returns path to CSV.
    """
    from agent_core.tools.prd_loader import load_prd_content
    from agent_core.utils.tracing import setup_tracing

    setup_tracing()

    # Load optional configuration (e.g. default max_cases) from config_path.
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
    rows: list[TestCaseRow] = []

    seq_mode: Literal["global", "per_component"] = "per_component"
    mode_raw = config.get("id_sequence_mode", "per_component")
    if mode_raw in ("global", "per_component"):
        seq_mode = mode_raw  # type: ignore[assignment]
    width = 3
    wcfg = config.get("id_numeric_width")
    if isinstance(wcfg, int) and wcfg > 0:
        width = min(wcfg, 10)

    global_counter = 0
    per_component: defaultdict[str, int] = defaultdict(int)

    for req_id, text, section_component in sections:
        try:
            row = await generate_one_case(
                requirement_text=text,
                requirement_id=req_id,
                component=section_component,
                llm=llm,
                config=config,
            )
            effective_cm = (row.Component or "").strip() or section_component
            segment = resolve_component_segment(effective_cm, req_id, config)
            seq, global_counter, per_component = next_sequence_number(
                seq_mode,
                segment,
                global_counter,
                per_component,
            )
            row = assign_sequential_id(row, segment, seq, width=width)
            rows.append(row)
        except Exception as e:
            logger.warning("Skipping section %s: %s", req_id, e)
    out_path = Path(output_csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(out_path, rows)
    return str(out_path)


def _split_prd_into_requirements(prd_content: str) -> list[tuple]:
    """Split PRD text into (requirement_id, text, component) for each section."""
    lines = prd_content.strip().split("\n")
    sections: list[tuple] = []
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


def _write_csv(path: Path, rows: list[TestCaseRow]) -> None:
    """Write rows to CSV with exact header from testCase_template."""
    with path.open("w", newline="", encoding="utf-8") as f:
        header = (
            rows[0].to_csv_header()
            if rows
            else (
                "ID,Name,Description,Requirement ID,Component/Module,Test Group,"
                "Test Type,Priority,Severity,Pre-requisite,Test Data,Environment,"
                "Steps,Expected,Actual Value,Additional Notes,Automation Priority,"
                "Automation Status,Owner,Estimated Time (mins),Tags,Defect,"
                "Status,Version"
            )
        )
        f.write(header + "\n")
        for row in rows:
            f.write(row.to_csv_row() + "\n")
    logger.info("Wrote %s rows to %s", len(rows), path)
