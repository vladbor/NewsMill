"""Tests for the refresh endpoint."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from newsmill.monitor.app import app
from newsmill.monitor.dependencies import get_http_client


@pytest.fixture
def patched_lifespan():
    """Patch RabbitMQ, background polling and the DB to avoid real I/O.

    Yields:
        Nothing; restores patches on teardown.
    """
    seen: set[str] = set()

    async def _claim(guid: str) -> bool:
        if guid in seen:
            return False
        seen.add(guid)
        return True

    with (
        patch("newsmill.monitor.app.NewsPublisher.connect", new=AsyncMock()),
        patch("newsmill.monitor.app.NewsPublisher.close", new=AsyncMock()),
        patch("newsmill.monitor.app._periodic_poll", new=AsyncMock()),
        patch("newsmill.monitor.app.get_engine", return_value=object()),
        patch("newsmill.monitor.app.close_engine", new=AsyncMock()),
        patch(
            "newsmill.monitor.dedup.GuidRegistry.claim",
            new=AsyncMock(side_effect=_claim),
        ),
    ):
        yield


def test_refresh_returns_published_count(
    rss_payload: bytes, fake_publisher, patched_lifespan
) -> None:
    """Test that POST /refresh polls feeds and returns the new item count."""
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=rss_payload)
    )

    async def override_http_client():
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    with patch(
        "newsmill.monitor.publisher.NewsPublisher.publish",
        new=fake_publisher.publish,
    ):
        app.dependency_overrides[get_http_client] = override_http_client
        with TestClient(app) as client:
            response = client.post("/refresh")
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"published": 2}
