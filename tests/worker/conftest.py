"""Shared fixtures for Worker tests."""

from __future__ import annotations

import pytest

from newsmill.common.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Return a Settings instance for tests.

    Returns:
        A :class:`Settings` object with test-friendly values.
    """
    return Settings(
        rabbitmq_host="rabbitmq-test",
        rabbitmq_port=5672,
        rabbitmq_user="user",
        rabbitmq_pass="pass",
        rabbitmq_queue="news",
        poll_interval_seconds=1,
        newsfeeds_path="newsfeeds.yaml",
        db_host="db-test",
        db_port=5432,
        db_user="dbuser",
        db_pass="dbpass",
        db_name="newsfeeds",
    )


class FakeEntity:
    """A minimal stand-in for a SpaCy span.

    Attributes:
        text: Entity text.
        label_: Entity label.
    """

    def __init__(self, text: str, label_: str) -> None:
        """Initialize the fake entity.

        Args:
            text: Entity text.
            label_: Entity label.
        """
        self.text = text
        self.label_ = label_


class FakeDoc:
    """A minimal stand-in for a SpaCy document.

    Attributes:
        ents: List of fake entities.
    """

    def __init__(self, ents: list[FakeEntity]) -> None:
        """Initialize the fake document.

        Args:
            ents: Entities contained in the document.
        """
        self.ents = ents


class FakeNlp:
    """A stub SpaCy pipeline returning predefined documents."""

    def __init__(self, docs: list[FakeDoc]) -> None:
        """Initialize the stub pipeline.

        Args:
            docs: Documents to return from ``pipe``.
        """
        self._docs = docs

    def pipe(self, texts: list[str]):
        """Return the predefined documents in order.

        Args:
            texts: The input texts (positionally matched to docs count).

        Returns:
            An iterator over the predefined documents.
        """
        return iter(self._docs)


@pytest.fixture
def fake_entities() -> list[FakeEntity]:
    """Return a list of fake named entities.

    Returns:
        A list of :class:`FakeEntity` instances.
    """
    return [
        FakeEntity("Иванов", "PER"),
        FakeEntity("Москва", "LOC"),
        FakeEntity("Россия", "LOC"),
        FakeEntity("Россия", "LOC"),
        FakeEntity("Неважно", "MISC"),
    ]
