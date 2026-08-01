"""RSS feed fetching and parsing for the Monitor service."""

from __future__ import annotations

import logging
from datetime import datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import httpx

from newsmill.common.models import NewsItem

logger = logging.getLogger(__name__)

_RSS_NS = "{http://purl.org/rss/1.0/}"


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an RSS date string into a datetime.

    Args:
        value: Raw date string from the feed.

    Returns:
        Parsed datetime, or None if the value is missing or unparseable.
    """
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        logger.warning("Could not parse date: %r", value)
        return None


def _extract_items(root: ElementTree.Element) -> list[ElementTree.Element]:
    """Extract item elements from an RSS root element.

    Supports RSS 2.0 (``<item>``) and RSS 1.0 (namespaced ``<item>``) feeds.

    Args:
        root: Parsed root XML element of the feed.

    Returns:
        A list of item elements.
    """
    items = root.findall("channel/item")
    if items:
        return items
    return root.findall(f"{_RSS_NS}item")


def _get_text(item: ElementTree.Element, tag: str) -> str:
    """Fetch the text content of a child element, or an empty string.

    Args:
        item: RSS item element.
        tag: Child tag name to look up.

    Returns:
        Text content of the matching child element, or an empty string.
    """
    child = item.find(tag)
    if child is not None and child.text:
        return child.text
    return ""


async def fetch_feed(client: httpx.AsyncClient, url: str) -> list[NewsItem]:
    """Fetch and parse an RSS feed into a list of news items.

    Items missing a GUID fall back to their link. Items without a parseable
    publication date are skipped.

    Args:
        client: Shared httpx async client used for the request.
        url: Feed URL to fetch.

    Returns:
        A list of :class:`NewsItem` objects extracted from the feed.

    Raises:
        httpx.HTTPStatusError: If the feed returns a non-2xx status.
        httpx.TimeoutException: If the request times out.
        httpx.RequestError: For connection-level failures.
        ValueError: If the response body is not valid XML.
    """
    response = await client.get(url)
    response.raise_for_status()
    try:
        root = ElementTree.fromstring(response.content)
    except ParseError as exc:
        logger.warning("Malformed XML from %s: %s", url, exc)
        raise ValueError(f"Invalid XML from feed {url}") from exc

    items: list[NewsItem] = []
    for item in _extract_items(root):
        guid = _get_text(item, "guid") or _get_text(item, "link")
        if not guid:
            logger.warning("Skipping item with no guid/link in %s", url)
            continue
        published_at = _parse_datetime(_get_text(item, "pubDate"))
        if published_at is None:
            logger.warning("Skipping item with unparseable date in %s", url)
            continue
        items.append(
            NewsItem(
                source="",
                title=_get_text(item, "title"),
                link=_get_text(item, "link"),
                guid=guid,
                published_at=published_at,
                text=_get_text(item, "description"),
            )
        )

    return items
