"""Shared fixtures for Monitor tests."""

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
    )


@pytest.fixture
def rss_payload() -> bytes:
    """Return a sample RSS 2.0 feed body.

    Returns:
        A bytes representation of a valid RSS feed.
    """
    return b"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Test Feed</title>
        <item>
          <title>First headline</title>
          <link>https://example.com/1</link>
          <guid>https://example.com/1</guid>
          <pubDate>Sat, 01 Aug 2026 10:00:00 +0500</pubDate>
          <description>First description</description>
        </item>
        <item>
          <title>Second headline</title>
          <link>https://example.com/2</link>
          <guid>https://example.com/2</guid>
          <pubDate>Sun, 02 Aug 2026 10:00:00 +0500</pubDate>
          <description>Second description</description>
        </item>
      </channel>
    </rss>
    """


class FakePublisher:
    """A stub publisher that records published news items."""

    def __init__(self) -> None:
        """Initialize the stub with an empty list of published items."""
        self.published: list = []

    async def publish(self, item) -> None:
        """Record a published news item.

        Args:
            item: The news item being published.
        """
        self.published.append(item)


@pytest.fixture
def fake_publisher() -> FakePublisher:
    """Return a FakePublisher instance.

    Returns:
        A :class:`FakePublisher` stub.
    """
    return FakePublisher()
