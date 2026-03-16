"""Test CaseRow schema and CSV serialization."""

import pytest

from generator_core.schema import TestCaseRow


def test_test_case_row_to_csv_header() -> None:
    """Header matches testCase_template order."""
    row = TestCaseRow(
        ID="TC-LOGIN-001",
        Name="Login with valid email",
        Requirement_ID="PRD-3.2.1",
        Component_Module="Auth",
    )
    assert "ID,Name,Description,Requirement ID" in row.to_csv_header()
    assert "Actual Value" in row.to_csv_header()


def test_test_case_row_to_csv_row() -> None:
    """to_csv_row produces a valid CSV line."""
    row = TestCaseRow(
        ID="TC-001",
        Name="Test",
        Requirement_ID="PRD-1",
        Component_Module="M",
    )
    line = row.to_csv_row()
    assert "TC-001" in line
    assert "Test" in line
