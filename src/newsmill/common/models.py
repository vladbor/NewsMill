"""Pydantic models shared between services."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NewsItem(BaseModel):
    """A single news item extracted from an RSS feed.

    Attributes:
        source: News agency name (e.g., "RIA Novosti").
        title: News headline.
        link: URL to the full article.
        guid: Unique identifier for deduplication.
        published_at: Publication datetime.
        text: Description or content of the news item.
    """

    source: str
    title: str
    link: str
    guid: str
    published_at: datetime
    text: str
