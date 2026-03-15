"""Conversation history persistence (JSON file) for agent context."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


def load_memory(path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Load conversation history from a JSON file. Returns list of message dicts.
    """
    p = Path(path)
    if not p.exists():
        return []
    try:
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.exception("Failed to load memory from %s: %s", path, e)
        return []


def save_memory(
    path: Union[str, Path],
    messages: List[Dict[str, Any]],
) -> None:
    """
    Persist conversation history to a JSON file.
    """
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(messages, indent=2), encoding="utf-8")
    except Exception as e:
        logger.exception("Failed to save memory to %s: %s", path, e)
        raise
