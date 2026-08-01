"""Tests for the health endpoint."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from newsmill.monitor.app import app


def _patch_lifespan() -> list:
    """Patch RabbitMQ and background polling to avoid real I/O in tests.

    Returns:
        A list of active patch objects for cleanup.
    """
    patches = [
        patch("newsmill.monitor.app.NewsPublisher.connect", new=AsyncMock()),
        patch("newsmill.monitor.app.NewsPublisher.close", new=AsyncMock()),
        patch("newsmill.monitor.app._periodic_poll", new=AsyncMock()),
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
