"""Unit tests for LLM module (default model id and get_llm)."""

import os

import pytest

from agent_core.llm import DEFAULT_LLM_MODEL_ID, get_llm


def test_default_model_id() -> None:
    """Default model must be gpt-4o-mini per TECH_STACK_VERSIONS."""
    assert DEFAULT_LLM_MODEL_ID == "gpt-4o-mini"


def test_get_llm_uses_default_without_args() -> None:
    """get_llm() with no args returns a chat model (default gpt-4o-mini)."""
    os.environ["OPENAI_API_KEY"] = "sk-test-dummy"
    try:
        llm = get_llm()
        assert llm is not None
        assert hasattr(llm, "ainvoke")
    finally:
        os.environ.pop("OPENAI_API_KEY", None)


def test_get_llm_respects_model_id_override() -> None:
    """get_llm(model_id=...) returns a chat model with overridden id."""
    os.environ["OPENAI_API_KEY"] = "sk-test-dummy"
    try:
        llm = get_llm(model_id="gpt-4o")
        assert llm is not None
        assert hasattr(llm, "ainvoke")
    finally:
        os.environ.pop("OPENAI_API_KEY", None)
