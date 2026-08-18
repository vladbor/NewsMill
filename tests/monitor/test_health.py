"""Tests for the health endpoint."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from newsmill.monitor.app import app


def _patch_lifespan() -> list:
    """Patch RabbitMQ, background polling and the DB to avoid real I/O.

    Returns:
        A list of active patch objects for cleanup.
    """
    seen: set[str] = set()

    async def _claim(guid: str) -> bool:
        if guid in seen:
            return False
        seen.add(guid)
        return True

    patches = [
        patch("newsmill.monitor.app.NewsPublisher.connect", new=AsyncMock()),
        patch("newsmill.monitor.app.NewsPublisher.close", new=AsyncMock()),
        patch("newsmill.monitor.app._periodic_poll", new=AsyncMock()),
        patch("newsmill.monitor.app.get_engine", return_value=object()),
        patch("newsmill.monitor.app.close_engine", new=AsyncMock()),
        patch(
            "newsmill.monitor.dedup.GuidRegistry.claim",
            new=AsyncMock(side_effect=_claim),
        ),
    ]
    for p in patches:
        p.start()
    return patches


def test_health_returns_ok() -> None:
    """Test that GET /health returns a 200 status with a healthy payload."""
    patches = _patch_lifespan()
    try:
        with TestClient(app) as client:
            response = client.get("/health")
    finally:
        for p in patches:
            p.stop()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
