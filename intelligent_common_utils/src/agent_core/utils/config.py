"""Load configuration from resources or given path (YAML/JSON). No hardcoded globals."""

import json
import logging
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    """Application config: PRD path, model id, and optional paths."""

    prd_path: str = Field(default="", description="Path to PRD file")
    config_dir: str = Field(default="config", description="Config directory")
    model_id: str = Field(default="gpt-4o-mini", description="LLM model id")
    output_dir: str = Field(default="generated_testcases", description="Output directory")


def load_config(
    config_path: Optional[Union[str, Path]] = None,
) -> AppConfig:
    """
    Load config from a JSON or YAML file, or return defaults.

    Prefer config from resources/ or config/; path can be overridden.
    """
    if config_path is None:
        return AppConfig()
    path = Path(config_path)
    if not path.exists():
        logger.warning("Config path %s does not exist; using defaults.", path)
        return AppConfig()
    try:
        raw = path.read_text(encoding="utf-8")
        if path.suffix.lower() in (".json",):
            data = json.loads(raw)
        elif path.suffix.lower() in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(raw) or {}
            except ImportError:
                logger.warning("PyYAML not installed; treating as empty config.")
                data = {}
        else:
            data = {}
        return AppConfig.model_validate(data)
    except Exception as e:
        logger.exception("Failed to load config from %s: %s", path, e)
        return AppConfig()
