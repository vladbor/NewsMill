"""FastAPI dependencies for the Monitor service."""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from newsmill.common.config import Settings


def get_settings() -> Settings:
    """Return the application settings instance.

    Returns:
        The global :class:`Settings` object loaded from environment variables.
    """
    return Settings()


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """Provide a shared httpx async client with sensible timeouts.

    The client is created per-request and closed when the request completes.

    Yields:
        A configured :class:`httpx.AsyncClient` instance.
    """
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        yield client
