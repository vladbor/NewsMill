"""Feed polling and deduplication logic for the Monitor service."""

from __future__ import annotations

import logging
from collections.abc import Mapping

import httpx

from newsmill.monitor.rss import fetch_feed

logger = logging.getLogger(__name__)


async def poll_all_feeds(
    client: httpx.AsyncClient,
    feeds: Mapping[str, str],
    publisher,
    seen_guids: set[str],
) -> int:
    """Poll all RSS feeds and publish new items to the queue.

    Each feed is fetched and parsed; errors on individual feeds are logged and
    do not stop the remaining feeds. Items whose GUID is already in
    ``seen_guids`` are skipped (deduplication).

    Args:
        client: Shared httpx async client.
        feeds: Mapping of agency name to RSS feed URL.
        publisher: Object with an async ``publish(item)`` method.
        seen_guids: Set of already-processed GUIDs (mutated in place).

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
            if item.guid in seen_guids:
                continue
            seen_guids.add(item.guid)
            await publisher.publish(item)
            published_count += 1

    return published_count
