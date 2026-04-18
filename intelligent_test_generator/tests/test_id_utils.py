"""Tests for TC-{Component}-{NNN} helpers."""

from collections import defaultdict

from generator_core.id_utils import (
    assign_sequential_id,
    format_test_case_id,
    next_sequence_number,
    resolve_component_segment,
    sanitize_component_segment,
)
from generator_core.schema import TestCaseRow


def test_sanitize_component_segment() -> None:
    assert sanitize_component_segment("User Login") == "USER_LOGIN"
    assert sanitize_component_segment("") == ""


def test_format_test_case_id() -> None:
    assert format_test_case_id("LOGIN", 1, width=3) == "TC-LOGIN-001"
    assert format_test_case_id("NULL", 2, width=3) == "TC-NULL-002"


def test_resolve_component_segment_uses_module() -> None:
    assert resolve_component_segment("Shopping Cart", "PRD-1", {}) == "SHOPPING_CART"


def test_resolve_component_segment_null_fallback() -> None:
    cfg = {"id_component_fallback": "NULL"}
    assert resolve_component_segment("", "PRD-1", cfg) == "NULL"


def test_next_sequence_per_component() -> None:
    per: defaultdict[str, int] = defaultdict(int)
    s1, g1, per = next_sequence_number("per_component", "LOGIN", 0, per)
    s2, g2, per = next_sequence_number("per_component", "LOGIN", g1, per)
    s3, _, _ = next_sequence_number("per_component", "CART", g2, per)
    assert (s1, s2, s3) == (1, 2, 1)


def test_next_sequence_global() -> None:
    per: defaultdict[str, int] = defaultdict(int)
    a, g, per = next_sequence_number("global", "LOGIN", 0, per)
    b, g2, per = next_sequence_number("global", "CART", g, per)
    assert (a, b) == (1, 2)
    assert g2 == 2


def test_assign_sequential_id() -> None:
    row = TestCaseRow(
        ID="TC-X-999",
        Name="N",
        Requirement_ID="PRD-1",
        Component="Auth",
    )
    out = assign_sequential_id(row, "LOGIN", 5, width=3)
    assert out.ID == "TC-LOGIN-005"
