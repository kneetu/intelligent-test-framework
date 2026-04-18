"""
Deterministic IDs: TC-{Component}-{NNN} per testCase_template.

Middle segment comes from Component/Module (sanitized); fallback NULL or config.
NNN is assigned by the runner (global or per-component sequence).
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Literal

from generator_core.schema import TestCaseRow

SequenceMode = Literal["global", "per_component"]


def sanitize_component_segment(raw: str) -> str:
    """
    Convert Component/Module text to UPPER_SNAKE for the ID middle segment.
    """
    if not raw or not str(raw).strip():
        return ""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", str(raw).strip()).strip("_").upper()
    return slug[:40] if slug else ""


def resolve_component_segment(
    component_module: str,
    requirement_id: str,
    config: dict[str, Any],
) -> str:
    """
    Middle segment for TC-{Component}-{NNN}: prefer Component/Module, else fallback.

    Uses id_component_fallback (default 'NULL') or id_area_prefix when set.
    """
    override = config.get("id_area_prefix")
    if isinstance(override, str) and override.strip():
        seg = sanitize_component_segment(override)
        if seg:
            return seg
    merged = (component_module or "").strip()
    seg = sanitize_component_segment(merged)
    if seg and seg != "GENERAL":
        return seg
    fallback = config.get("id_component_fallback", "NULL")
    if isinstance(fallback, str) and fallback.strip():
        fb = fallback.strip().upper()
        if fb == "NULL":
            return "NULL"
        seg2 = sanitize_component_segment(fallback)
        if seg2:
            return seg2
    rid = (requirement_id or "").strip()
    match = re.match(r"PRD[-_]?([\d.]+)", rid, re.IGNORECASE)
    if match:
        part = match.group(1).replace(".", "_")
        return f"PRD_{part}"[:40]
    return "NULL"


def format_test_case_id(component_segment: str, sequence: int, width: int = 3) -> str:
    """
    Build TC-{Component}-{NNN} with zero-padded NNN.
    """
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", component_segment).strip("_") or "NULL"
    suffix = str(max(0, int(sequence))).zfill(width)
    return f"TC-{safe}-{suffix}"


def assign_sequential_id(
    row: TestCaseRow,
    component_segment: str,
    sequence: int,
    width: int = 3,
) -> TestCaseRow:
    """Return a copy of row with ID set to TC-{Component}-{NNN}."""
    new_id = format_test_case_id(component_segment, sequence, width=width)
    return row.model_copy(update={"ID": new_id})


def next_sequence_number(
    mode: SequenceMode,
    component_segment: str,
    global_counter: int,
    per_component: defaultdict[str, int],
) -> tuple[int, int, defaultdict[str, int]]:
    """
    Advance counters and return the sequence number for this row.

    Returns (sequence_for_id, new_global_counter, per_component_map).
    """
    if mode == "global":
        next_g = global_counter + 1
        return next_g, next_g, per_component
    per_component[component_segment] += 1
    seq = per_component[component_segment]
    return seq, global_counter, per_component
