"""Versioned, modular chat prompts for test case generation (no hardcoded globals)."""

from langchain_core.prompts import ChatPromptTemplate

# Prompt: take a PRD section and produce one test case (structured).
GENERATE_ONE_TEST = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a test analyst. Given a requirement from a PRD, output exactly one "
            "atomic, executable test case. Use the schema provided. ID format: "
            "TC-{AREA}-{NNN}. Priority: P0-P3. Test Type: Functional, Negative, "
            "Performance, or Accessibility.",
        ),
        (
            "human",
            "Requirement:\n{requirement_text}\n\n"
            "Requirement ID for traceability: {requirement_id}\n\n"
            "Component/Module: {component}\n\n"
            "{format_instructions}\n\n"
            "Generate one test case following the output schema above.",
        ),
    ]
)
