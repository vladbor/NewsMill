"""Shared fixtures for retention tests using an in-memory SQLite database."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from newsmill.common.db.models import Base


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    """Create an in-memory SQLite engine with foreign keys enabled.

    Yields:
        An async SQLAlchemy engine backed by ``sqlite+aiosqlite`` in memory.
    """
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine.sync_engine, "connect")
    def _set_foreign_keys(dbapi_connection, _record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def session_factory(
    engine: AsyncEngine,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Return a session factory bound to the in-memory engine.

    Yields:
        A session factory producing sessions for the test database.
    """
    yield async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Yield a single session for direct row insertion in tests.

    Yields:
        An open :class:`AsyncSession`; commits are left to each test.
    """
    async with session_factory() as session:
        yield session
