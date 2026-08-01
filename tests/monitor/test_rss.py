"""Tests for the RSS feed parser."""

from __future__ import annotations

import httpx
import pytest

from newsmill.monitor.rss import fetch_feed


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


@pytest.mark.asyncio
async def test_fetch_feed_parses_items(rss_payload: bytes) -> None:
    """Test that a valid RSS feed is parsed into news items."""
    client = _client_with_content(rss_payload)
    items = await fetch_feed(client, "https://example.com/feed.xml")
    await client.aclose()

    assert len(items) == 2
    assert items[0].link == "https://example.com/1"
    assert items[0].guid == "https://example.com/1"
    assert items[0].text == "First description"


@pytest.mark.asyncio
async def test_fetch_feed_skips_item_without_date(rss_payload: bytes) -> None:
    """Test that items with an unparseable date are skipped."""
    broken = rss_payload.replace(
        b"<pubDate>Sat, 01 Aug 2026 10:00:00 +0500</pubDate>", b""
    )
    client = _client_with_content(broken)
    items = await fetch_feed(client, "https://example.com/feed.xml")
    await client.aclose()

    assert len(items) == 1


@pytest.mark.asyncio
async def test_fetch_feed_raises_on_http_error() -> None:
    """Test that a non-2xx response raises an HTTP error."""
    client = _client_with_content(b"error", status_code=500)
    with pytest.raises(httpx.HTTPStatusError):
        await fetch_feed(client, "https://example.com/feed.xml")
    await client.aclose()


@pytest.mark.asyncio
async def test_fetch_feed_raises_on_malformed_xml() -> None:
    """Test that invalid XML raises a ValueError."""
    client = _client_with_content(b"<rss><channel>")
    with pytest.raises(ValueError):
        await fetch_feed(client, "https://example.com/feed.xml")
    await client.aclose()
