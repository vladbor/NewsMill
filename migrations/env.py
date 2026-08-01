"""Alembic migration environment for the NewsMill database.

This module configures Alembic to work with the async SQLAlchemy engine
(``asyncpg`` driver). The database URL is assembled from the ``DB_*``
environment variables using the same defaults as :class:`Settings` in
``newsmill.common.config``.
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from newsmill.common.db.models import Base

# The alembic Config object, providing access to the values within the .ini
# file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add the target metadata so that ``alembic revision --autogenerate`` can
# detect changes in the ORM models.
target_metadata = Base.metadata


def _build_database_url() -> str | None:
    """Assemble the async database URL from ``DB_*`` environment variables.

    Returns:
        The assembled URL, or ``None`` if a URL was already provided via the
        ``sqlalchemy.url`` ini option.
    """
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "postgres")
    name = os.getenv("DB_NAME", "newsfeeds")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with a URL and not an Engine. Emits SQL for
    the target database dialect without connecting to it.
    """
    url = _build_database_url()
    if url is None:
        raise RuntimeError("Cannot build database URL for offline mode.")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _prepare_sync_engine() -> None:
    """Configure the async engine for offline/other tooling not in offline mode."""
    url = _build_database_url()
    if url is None:
        raise RuntimeError("Cannot build database URL.")
    config.set_main_option("sqlalchemy.url", url)


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations in a transaction on the given connection.

    Args:
        connection: A SQLAlchemy connection to run the migrations on.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using the async engine."""
    _prepare_sync_engine()

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario an async engine is created and connected to the database
    to execute the migration scripts.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
