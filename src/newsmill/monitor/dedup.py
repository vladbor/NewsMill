"""Persistent GUID deduplication for the Monitor service.

The deduplication state lives in PostgreSQL so it survives Monitor restarts:
each GUID is claimed atomically with ``INSERT ... ON CONFLICT DO NOTHING``
before the news item is published to the queue.
"""

from __future__ import annotations

import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncEngine

from newsmill.common.db.models import ProcessedItem

logger = logging.getLogger(__name__)


class GuidRegistry:
    """Atomic, database-backed registry of already-processed GUIDs.

    Attributes:
        engine: The shared async SQLAlchemy engine.
    """

    def __init__(self, engine: AsyncEngine) -> None:
        """Initialize the registry with the given engine.

        Args:
            engine: The shared async SQLAlchemy engine.
        """
        self._engine = engine

    async def claim(self, guid: str) -> bool:
        """Atomically claim a GUID for publication.

        The GUID is inserted into ``processed_items`` only if it is not
        already present. A claimed GUID (new row) returns ``True``; an already
        processed GUID returns ``False``.

        Args:
            guid: The news item GUID to claim.

        Returns:
            ``True`` if the GUID was new and the item should be published,
            ``False`` if it was already processed.
        """
        stmt = (
            pg_insert(ProcessedItem)
            .values(guid=guid)
            .on_conflict_do_nothing()
            .returning(ProcessedItem.guid)
        )
        async with self._engine.begin() as conn:
            result = await conn.execute(stmt)
        return result.first() is not None
