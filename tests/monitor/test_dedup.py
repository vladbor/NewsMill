"""Tests for the persistent GUID deduplication registry."""

from __future__ import annotations

import pytest

from newsmill.monitor.dedup import GuidRegistry


class FakeResult:
    """A stub query result exposing :meth:`first`."""

    def __init__(self, row) -> None:
        """Initialize the stub result.

        Args:
            row: The single row returned by ``first()``, or ``None``.
        """
        self._row = row

    def first(self):
        """Return the preconfigured row."""
        return self._row


class FakeConnection:
    """A stub async connection that records the executed statement."""

    def __init__(self, row=None) -> None:
        """Initialize the stub connection.

        Args:
            row: The row the connection should return for any query.
        """
        self._result = FakeResult(row)
        self.executed = None

    async def execute(self, statement):
        """Record and return the stub result for the statement.

        Args:
            statement: The SQL statement executed.

        Returns:
            The preconfigured :class:`FakeResult`.
        """
        self.executed = statement
        return self._result


class FakeEngine:
    """A stub async engine whose transactions yield a FakeConnection."""

    def __init__(self, row=None) -> None:
        """Initialize the stub engine.

        Args:
            row: The row returned for any executed statement.
        """
        self._conn = FakeConnection(row)

    def begin(self):
        """Return an async context manager yielding the fake connection."""

        class _Begin:
            def __init__(self, conn: FakeConnection) -> None:
                self._conn = conn

            async def __aenter__(self) -> FakeConnection:
                return self._conn

            async def __aexit__(self, *args) -> None:
                return None

        return _Begin(self._conn)


@pytest.mark.asyncio
async def test_claim_returns_true_for_new_guid() -> None:
    """Test that a claimed (new row returned) GUID is publishable."""
    engine = FakeEngine(row=("guid-1",))
    registry = GuidRegistry(engine)

    assert await registry.claim("guid-1") is True


@pytest.mark.asyncio
async def test_claim_returns_false_for_existing_guid() -> None:
    """Test that an already-processed GUID is not claimed again."""
    engine = FakeEngine(row=None)
    registry = GuidRegistry(engine)

    assert await registry.claim("guid-1") is False
