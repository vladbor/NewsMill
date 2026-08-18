"""Feed polling and deduplication logic for the Monitor service."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Mapping

import httpx

from newsmill.monitor.rss import fetch_feed

logger = logging.getLogger(__name__)


async def poll_all_feeds(
    client: httpx.AsyncClient,
    feeds: Mapping[str, str],
    publisher,
    claim: Callable[[str], Awaitable[bool]],
) -> int:
    """Poll all RSS feeds and publish new items to the queue.

    Each feed is fetched and parsed; errors on individual feeds are logged and
    do not stop the remaining feeds. A GUID is claimed via ``claim`` before
    publishing: already processed GUIDs are skipped. If the claim fails (for
    example a database outage) the item is still published, because the final
    duplicate guard is the ``news.link`` unique constraint in the Worker.

    Args:
        client: Shared httpx async client.
        feeds: Mapping of agency name to RSS feed URL.
        publisher: Object with an async ``publish(item)`` method.
        claim: Async predicate that atomically claims a GUID and returns
            ``True`` if the item should be published.

    Returns:
        The number of new items published to the queue.
    """
    published_count = 0
    for source, url in feeds.items():
        try:
            items = await fetch_feed(client, url)
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError):
            logger.exception("Failed to fetch feed %s (%s)", source, url)
            continue
        except ValueError:
            logger.exception("Failed to parse feed %s (%s)", source, url)
            continue

        for item in items:
            item = item.model_copy(update={"source": source})
            try:
                claimed = await claim(item.guid)
            except Exception:
                logger.exception(
                    "Failed to claim guid %s; publishing anyway", item.guid
                )
                claimed = True
            if not claimed:
                continue
            await publisher.publish(item)
            published_count += 1

    return published_count
