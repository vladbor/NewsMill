"""Async database session management for the Worker service."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from newsmill.common.config import Settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(settings: Settings) -> AsyncEngine:
    """Create and return the shared async engine.

    The engine is created once and reused for subsequent calls.

    Args:
        settings: Application settings containing the database URL.

    Returns:
        The SQLAlchemy async engine.
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url)
    return _engine


def get_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    """Create and return the shared async session factory.

    Args:
        settings: Application settings containing the database URL.

    Returns:
        The SQLAlchemy async session factory.
    """
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(settings), expire_on_commit=False
        )
    return _session_factory


async def get_session(settings: Settings) -> AsyncIterator[AsyncSession]:
    """Yield an async session for a single database operation.

    Args:
        settings: Application settings containing the database URL.

    Yields:
        An open :class:`AsyncSession`.
    """
    factory = get_session_factory(settings)
    async with factory() as session:
        yield session


async def close_engine() -> None:
    """Dispose the shared async engine, if it was created."""
    global _engine
    global _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
