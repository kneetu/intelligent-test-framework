"""Async tool to load PRD file content from path."""

import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


async def load_prd_content(prd_path: Union[str, Path]) -> str:
    """
    Read PRD file and return its text. Used by generator/reviewer.
    """
    path = Path(prd_path)
    if not path.exists():
        logger.warning("PRD path does not exist: %s", path)
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.exception("Failed to read PRD %s: %s", path, e)
        raise
