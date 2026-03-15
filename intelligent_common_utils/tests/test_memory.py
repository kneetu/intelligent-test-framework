"""Unit tests for memory load/save."""

import json
import tempfile
from pathlib import Path

import pytest

from agent_core.memory import load_memory, save_memory


def test_load_memory_missing_file_returns_empty() -> None:
    """load_memory on non-existent path returns []."""
    assert load_memory("/nonexistent/path/memory.json") == []


def test_save_and_load_memory_roundtrip() -> None:
    """save_memory then load_memory returns same list."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "mem.json"
        messages = [{"role": "human", "content": "Hi"}, {"role": "ai", "content": "Hello"}]
        save_memory(path, messages)
        loaded = load_memory(path)
        assert loaded == messages
