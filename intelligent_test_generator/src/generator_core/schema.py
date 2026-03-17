"""
Pydantic model for one test case row matching testCase_template CSV columns.
Header order: ID, Name, Description, Requirement ID, Component/Module, ...
"""

from pydantic import BaseModel, ConfigDict, Field


# Allowed enums per testCase_template
TEST_TYPES = ("Functional", "Negative", "Performance", "Accessibility")
PRIORITIES = ("P0", "P1", "P2", "P3")
SEVERITIES = ("S1", "S2", "S3", "S4")
TEST_GROUPS = ("Smoke", "Full", "Comprehensive")


class TestCaseRow(BaseModel):
    """One row of the test case CSV; all columns from testCase_template."""

    ID: str = Field(description="TC-{REQ_OR_AREA}-{NNN}")
    Name: str = Field(description="5-12 words, imperative summary")
    Description: str = Field(default="")
    Requirement_ID: str = Field(alias="Requirement ID", description="PRD section/ID")
    Component_Module: str = Field(alias="Component/Module", default="")
    Test_Type: str = Field(alias="Test Type", default="Functional")
    Priority: str = Field(default="P1")
    Severity: str = Field(default="S2")
    Pre_requisite: str = Field(alias="Pre-requisite", default="None")
    Test_Data: str = Field(alias="Test Data", default="")
    Environment: str = Field(default="")
    Steps: str = Field(default="")
    Expected: str = Field(default="")
    Actual_Value: str = Field(alias="Actual Value", default="")
    Additional_Notes: str = Field(alias="Additional Notes", default="")
    Automation_Priority: str = Field(alias="Automation Priority", default="")
    Automation_Status: str = Field(alias="Automation Status", default="")
    Owner: str = Field(default="")
    Estimated_Time_mins: str = Field(alias="Estimated Time (mins)", default="")
    Tags: str = Field(default="")
    Defect: str = Field(default="")
    Status: str = Field(default="Draft")
    Version: str = Field(default="1.0")

    model_config = ConfigDict(populate_by_name=True)

    def to_csv_header(self) -> str:
        """Exact CSV header per testCase_template."""
        return (
            "ID,Name,Description,Requirement ID,Component/Module,Test Type,Priority,"
            "Severity,Pre-requisite,Test Data,Environment,Steps,Expected,Actual Value,"
            "Additional Notes,Automation Priority,Automation Status,Owner,"
            "Estimated Time (mins),Tags,Defect,Status,Version"
        )

    def to_csv_row(self) -> str:
        """Escape and join fields for one CSV row."""
        import csv
        from io import StringIO

        out = StringIO()
        w = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        d = self.model_dump(by_alias=True)
        keys = [
            "ID", "Name", "Description", "Requirement ID", "Component/Module",
            "Test Type", "Priority", "Severity", "Pre-requisite", "Test Data",
            "Environment", "Steps", "Expected", "Actual Value", "Additional Notes",
            "Automation Priority", "Automation Status", "Owner",
            "Estimated Time (mins)", "Tags", "Defect", "Status", "Version",
        ]
        row = [str(d.get(k, "")) for k in keys]
        w.writerow(row)
        return out.getvalue().rstrip("\r\n")
