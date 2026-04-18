"""Versioned, modular chat prompts for test case generation (no hardcoded globals)."""

from langchain_core.prompts import ChatPromptTemplate

# Prompt: take a PRD section and produce one test case (structured).
# Use {{ and }} for literal braces—LangChain treats single {name} as input variables.
GENERATE_ONE_TEST = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a test analyst. Given a requirement from a PRD, output exactly one "
            "atomic, executable test case. Use the schema provided. ID format is "
            "TC-{{Component}}-{{NNN}} where Component matches Component/Module "
            "(UPPER_SNAKE); the numeric suffix NNN is assigned by the pipeline—any "
            "value you output in ID may be overwritten. Set Test Group to one of: "
            "Smoke, Full, Comprehensive. Test Type: Functional, Negative, "
            "Performance, or Accessibility. Priority: P0-P3. Name is a short "
            "imperative summary (5-12 words).",
        ),
        (
            "human",
            "Requirement:\n{requirement_text}\n\n"
            "Requirement ID for traceability: {requirement_id}\n\n"
            "Component/Module (context): {component}\n\n"
            "Default or suggested values for optional CSV columns (use when "
            "appropriate; you must still produce Name, Steps, and Expected):\n"
            "- Description: {default_description}\n"
            "- Test Group: {default_test_group}\n"
            "- Test Type: {default_test_type}\n"
            "- Priority: {default_priority}\n"
            "- Severity: {default_severity}\n"
            "- Pre-requisite: {default_pre_requisite}\n"
            "- Test Data: {default_test_data}\n"
            "- Environment: {default_environment}\n"
            "- Actual Value: {default_actual_value}\n"
            "- Additional Notes: {default_additional_notes}\n"
            "- Automation Priority: {default_automation_priority}\n"
            "- Automation Status: {default_automation_status}\n"
            "- Owner: {default_owner}\n"
            "- Estimated Time (mins): {default_estimated_time_mins}\n"
            "- Tags: {default_tags}\n"
            "- Defect: {default_defect}\n"
            "- Status: {default_status}\n"
            "- Version: {default_version}\n\n"
            "{format_instructions}\n\n"
            "Generate one test case following the output schema above.",
        ),
    ]
)
