"""Data retention helpers for purging outdated database records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from newsmill.common.db.models import News, ProcessedItem


@dataclass(frozen=True)
class PurgeResult:
    """Report of records removed by a purge run.

    Attributes:
        processed_items: Number of ``processed_items`` rows deleted.
        news: Number of ``news`` rows deleted (entities are removed by cascade).
    """

    processed_items: int
    news: int


async def purge_old_records(session: AsyncSession, days: int) -> PurgeResult:
    """Delete records older than ``days`` in a single transaction.

    ``processed_items`` is purged first so the dedup registry does not grow
    while ``news`` rows are being removed; ``entities`` are removed by the
    ``ON DELETE CASCADE`` foreign key.

    Args:
        session: An open async database session.
        days: Age threshold in days; records older than this are removed.

    Returns:
        A :class:`PurgeResult` with the number of deleted rows per table.

    Raises:
        Exception: Any database error rolls the whole transaction back, so no
            partial purge is committed.
    """
    cutoff = datetime.now(UTC) - timedelta(days=days)
    async with session.begin():
        processed_result = await session.execute(
            delete(ProcessedItem.__table__).where(
                ProcessedItem.__table__.c.created_at < cutoff
            )
        )
        news_result = await session.execute(
            delete(News.__table__).where(News.__table__.c.created_at < cutoff)
        )
    return PurgeResult(
        processed_items=processed_result.rowcount, news=news_result.rowcount
    )
