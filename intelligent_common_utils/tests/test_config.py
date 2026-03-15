"""Unit tests for config loading."""

import tempfile
from pathlib import Path

import pytest

from agent_core.utils.config import AppConfig, load_config


def test_load_config_none_returns_defaults() -> None:
    """load_config(None) returns default AppConfig."""
    config = load_config(None)
    assert isinstance(config, AppConfig)
    assert config.model_id == "gpt-4o-mini"


def test_load_config_json() -> None:
    """load_config loads JSON and overrides model_id."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(b'{"model_id": "gpt-4o", "prd_path": "/tmp/prd.txt"}')
        f.flush()
        config = load_config(f.name)
    assert config.model_id == "gpt-4o"
    assert config.prd_path == "/tmp/prd.txt"
