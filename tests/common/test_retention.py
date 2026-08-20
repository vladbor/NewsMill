"""Tests for the purge_old_records retention procedure."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import Delete

from newsmill.common.db.models import Entity, News, ProcessedItem
from newsmill.common.db.retention import purge_old_records

OLD_DAYS = 30
NOW = datetime.now(UTC)


def _dt(**kwargs) -> datetime:
    """Build a timezone-aware datetime relative to ``NOW``."""
    return NOW - timedelta(days=kwargs.pop("days", 0), **kwargs)


async def _add_processed(
    session: AsyncSession, guid: str, created_at: datetime
) -> None:
    await session.execute(
        insert(ProcessedItem.__table__).values(guid=guid, created_at=created_at)
    )
    await session.commit()


async def _add_news(session: AsyncSession, link: str, created_at: datetime) -> int:
    result = await session.execute(
        insert(News.__table__)
        .values(
            source="ria",
            title=f"Title {link}",
            link=link,
            published_at=created_at,
            created_at=created_at,
        )
        .returning(News.id)
    )
    news_id = result.scalar_one()
    await session.commit()
    return news_id


async def test_purge_deletes_old_processed_items(session: AsyncSession) -> None:
    await _add_processed(session, "old-guid", _dt(days=40))
    await _add_processed(session, "fresh-guid", _dt(days=1))

    result = await purge_old_records(session, OLD_DAYS)

    assert result.processed_items == 1
    remaining = (await session.execute(select(ProcessedItem.guid))).scalars().all()
    assert remaining == ["fresh-guid"]


async def test_purge_deletes_old_news(session: AsyncSession) -> None:
    await _add_news(session, "http://old", _dt(days=60))
    await _add_news(session, "http://fresh", _dt(days=2))

    result = await purge_old_records(session, OLD_DAYS)

    assert result.news == 1
    remaining = (await session.execute(select(News.link))).scalars().all()
    assert remaining == ["http://fresh"]


async def test_purge_removes_entities_by_cascade(
    session: AsyncSession,
) -> None:
    news_id = await _add_news(session, "http://old", _dt(days=60))
    await session.execute(
        insert(Entity.__table__).values(
            news_id=news_id, text="Иванов", label="PER", count=1
        )
    )
    await session.commit()

    await purge_old_records(session, OLD_DAYS)

    entity_rows = (await session.execute(select(Entity.id))).scalars().all()
    assert entity_rows == []


async def test_purge_keeps_records_younger_than_threshold(
    session: AsyncSession,
) -> None:
    await _add_processed(session, "guid", _dt(days=1))
    await _add_news(session, "http://recent", _dt(days=1))

    result = await purge_old_records(session, OLD_DAYS)

    assert result.processed_items == 0
    assert result.news == 0


async def test_purge_is_atomic_on_error(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await _add_processed(session, "old-guid", _dt(days=40))
    await _add_news(session, "http://old", _dt(days=40))

    original_execute = AsyncSession.execute

    async def failing_execute(self, statement, *args, **kwargs):
        if isinstance(statement, Delete) and statement.table is News.__table__:
            raise RuntimeError("boom")
        return await original_execute(self, statement, *args, **kwargs)

    monkeypatch.setattr(AsyncSession, "execute", failing_execute)

    with pytest.raises(RuntimeError, match="boom"):
        await purge_old_records(session, OLD_DAYS)

    monkeypatch.setattr(AsyncSession, "execute", original_execute)
    remaining = (await session.execute(select(ProcessedItem.guid))).scalars().all()
    assert remaining == ["old-guid"]


async def test_purge_never_overflows_deadline(session: AsyncSession) -> None:
    await _add_processed(session, "guid", _dt(days=1))
    result = await purge_old_records(session, days=10**4)

    assert result.processed_items == 0
    assert result.news == 0


async def test_purge_is_noop_on_empty_database(session: AsyncSession) -> None:
    result = await purge_old_records(session, OLD_DAYS)

    assert result.processed_items == 0
    assert result.news == 0
