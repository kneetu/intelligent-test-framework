"""Modular chat prompts for test case review."""

from langchain_core.prompts import ChatPromptTemplate

REVIEW_ONE_CASE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a test review expert. Given a PRD requirement and a test case, "
            "output a structured review: verdict (Accept/Reject/Needs revision), "
            "issues, suggestions, and severity. Use the output schema provided.",
        ),
        (
            "human",
            "PRD requirement (excerpt):\n{prd_excerpt}\n\n"
            "Test case to review:\n{test_case_text}\n\n"
            "{format_instructions}\n\n"
            "Produce the structured review.",
        ),
    ]
)
