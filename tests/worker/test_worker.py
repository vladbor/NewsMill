"""Tests for the Worker message processing logic."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from newsmill.common.models import NewsItem
from newsmill.worker.app import _deserialize_item, _persist


def _sample_item() -> NewsItem:
    """Return a sample NewsItem for tests.

    Returns:
        A :class:`NewsItem` instance.
    """
    return NewsItem(
        source="RIA Novosti",
        title="Заголовок новости",
        link="https://example.com/1",
        guid="https://example.com/1",
        published_at=datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
        text="Текст новости",
    )


def test_deserialize_item_valid() -> None:
    """Test that a valid JSON body is deserialized into a NewsItem."""
    item = _sample_item()
    body = json.dumps(item.model_dump(mode="json"), ensure_ascii=False).encode("utf-8")

    result = _deserialize_item(body)

    assert result == item


def test_deserialize_item_invalid_json() -> None:
    """Test that invalid JSON raises a JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        _deserialize_item(b"not json")


def test_deserialize_item_missing_fields() -> None:
    """Test that a payload missing required fields raises a ValidationError."""
    body = json.dumps({"source": "RIA"}).encode("utf-8")
    with pytest.raises(ValueError):
        _deserialize_item(body)


class FakeSession:
    """A stub async session that records added objects."""

    def __init__(self) -> None:
        """Initialize the stub with empty records."""
        self.added: list = []
        self.committed = False
        self.flushed = False
        self._existing = None

    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Exit the async context manager."""

    async def scalar(self, statement):
        """Return the preconfigured existing row, if any.

        Args:
            statement: The SQL statement (ignored).

        Returns:
            The preconfigured existing row or ``None``.
        """
        return self._existing

    def add(self, obj) -> None:
        """Record an added object.

        Args:
            obj: The object being added.
        """
        self.added.append(obj)

    async def flush(self) -> None:
        """Mark the session as flushed."""
        self.flushed = True

    async def commit(self) -> None:
        """Mark the session as committed."""
        self.committed = True


class FakeFactory:
    """A stub session factory returning a FakeSession."""

    def __init__(self, session: FakeSession) -> None:
        """Initialize the stub factory.

        Args:
            session: The FakeSession to return.
        """
        self._session = session

    def __call__(self):
        """Return the configured FakeSession.

        Returns:
            The :class:`FakeSession` instance.
        """
        return self._session


@pytest.mark.asyncio
async def test_persist_writes_news_and_entities(monkeypatch, settings) -> None:
    """Test that a news item and its entities are persisted."""
    from newsmill.common.db import Entity, News

    session = FakeSession()
    monkeypatch.setattr(
        "newsmill.worker.app.get_session_factory", lambda settings: FakeFactory(session)
    )

    item = _sample_item()
    extracted = [
        type("R", (), {"text": "Иванов", "label": "PER", "count": 1})(),
        type("R", (), {"text": "Россия", "label": "LOC", "count": 2})(),
    ]

    await _persist(settings, item, extracted)

    assert session.committed is True
    assert session.flushed is True
    assert isinstance(session.added[0], News)
    assert len(session.added) == 3
    assert all(isinstance(e, Entity) for e in session.added[1:])


@pytest.mark.asyncio
async def test_persist_skips_existing(monkeypatch, settings) -> None:
    """Test that an existing news item is not written twice."""
    session = FakeSession()
    session._existing = object()
    monkeypatch.setattr(
        "newsmill.worker.app.get_session_factory", lambda settings: FakeFactory(session)
    )

    await _persist(settings, _sample_item(), [])

    assert session.added == []
    assert session.committed is False
