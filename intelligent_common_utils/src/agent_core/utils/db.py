"""Postgres connection helper (async). Use postgres:16 in Docker/k8s per TECH_STACK."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def get_connection(dsn: str) -> Any:
    """
    Return an async Postgres connection (e.g. psycopg.AsyncConnection).

    Caller must close when done. DSN from config/env; infra uses Postgres 16.
    """
    try:
        import psycopg
        conn = await psycopg.AsyncConnection.connect(dsn)
        return conn
    except Exception as e:
        logger.exception("Failed to connect to Postgres: %s", e)
        raise
