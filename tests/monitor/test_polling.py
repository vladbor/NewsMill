"""Tests for the feed polling and deduplication logic."""

from __future__ import annotations

import httpx
import pytest

from newsmill.monitor.polling import poll_all_feeds


def _client_with_content(content: bytes, status_code: int = 200) -> httpx.AsyncClient:
    """Build an async client that returns a fixed response.

    Args:
        content: Response body bytes.
        status_code: HTTP status code to return.

    Returns:
        A configured :class:`httpx.AsyncClient` instance.
    """
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status_code, content=content)
    )
    return httpx.AsyncClient(transport=transport)


def _claim_always_new(seen: set[str]):
    """Return an async claim predicate that accepts each GUID only once.

    Args:
        seen: Mutable set of already-claimed GUIDs.

    Returns:
        An async ``claim(guid) -> bool`` callable.
    """

    async def claim(guid: str) -> bool:
        if guid in seen:
            return False
        seen.add(guid)
        return True

    return claim


@pytest.mark.asyncio
async def test_poll_deduplicates_by_guid(rss_payload: bytes, fake_publisher) -> None:
    """Test that items with already-seen GUIDs are not published twice."""
    client = _client_with_content(rss_payload)
    feeds = {"Test Agency": "https://example.com/feed.xml"}
    claim = _claim_always_new(set())

    count1 = await poll_all_feeds(client, feeds, fake_publisher, claim)
    count2 = await poll_all_feeds(client, feeds, fake_publisher, claim)
    await client.aclose()

    assert count1 == 2
    assert count2 == 0
    assert len(fake_publisher.published) == 2
    assert fake_publisher.published[0].source == "Test Agency"


@pytest.mark.asyncio
async def test_poll_continues_on_feed_error(rss_payload: bytes, fake_publisher) -> None:
    """Test that a failing feed does not stop the remaining feeds."""
    transport = httpx.MockTransport(
        lambda request: (
            httpx.Response(500)
            if request.url.host == "broken.example.com"
            else httpx.Response(200, content=rss_payload)
        )
    )
    async with httpx.AsyncClient(transport=transport) as client:
        feeds = {
            "Broken Agency": "https://broken.example.com/feed.xml",
            "Good Agency": "https://good.example.com/feed.xml",
        }
        count = await poll_all_feeds(
            client, feeds, fake_publisher, _claim_always_new(set())
        )

    assert count == 2


@pytest.mark.asyncio
async def test_poll_publishes_when_claim_fails(
    rss_payload: bytes, fake_publisher
) -> None:
    """Test that a failing claim does not lose the item (at-least-once)."""

    async def claim(guid: str) -> bool:
        raise RuntimeError("database is down")

    client = _client_with_content(rss_payload)
    feeds = {"Test Agency": "https://example.com/feed.xml"}

    count = await poll_all_feeds(client, feeds, fake_publisher, claim)
    await client.aclose()

    assert count == 2
    assert len(fake_publisher.published) == 2
