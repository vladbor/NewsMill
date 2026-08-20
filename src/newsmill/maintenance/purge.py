"""Data retention entry point: purge records older than DELETE_AFTER days."""

from __future__ import annotations

import asyncio
import logging

from newsmill.common.config import Settings
from newsmill.common.db.retention import purge_old_records
from newsmill.common.db.session import close_engine, get_session_factory


def main() -> None:
    """Run the purge against the configured database and log the result.

    The ``DELETE_AFTER`` setting controls how many days of history are kept.
    Records older than that are removed in a single transaction (``news`` rows
    together with their ``entities`` by cascade and dedup ``processed_items``).
    """
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    asyncio.run(_run(settings))


async def _run(settings: Settings) -> None:
    factory = get_session_factory(settings)
    try:
        async with factory() as session:
            result = await purge_old_records(session, settings.delete_after_days)
        logging.getLogger(__name__).info(
            "Purged %d processed_items and %d news older than %d days",
            result.processed_items,
            result.news,
            settings.delete_after_days,
        )
    finally:
        await close_engine()


if __name__ == "__main__":
    main()
