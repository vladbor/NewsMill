"""SQLAlchemy ORM models for the NewsMill database."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class News(Base):
    """A single news item stored in the database.

    Attributes:
        id: Primary key.
        source: News agency name.
        title: News headline.
        link: URL to the full article (unique).
        published_at: Publication datetime (timezone-aware).
        text: Description or content of the news item.
        created_at: Creation timestamp in the database.
        entities: Related extracted entities.
    """

    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    link: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    entities: Mapped[list[Entity]] = relationship(
        back_populates="news",
        cascade="all, delete-orphan",
    )


class Entity(Base):
    """A named entity extracted from a news item.

    Attributes:
        id: Primary key.
        news_id: Foreign key referencing the ``news`` table.
        text: Extracted entity text.
        label: Entity type (PER, ORG, LOC, MISC, etc.).
        count: Number of occurrences in the news item.
    """

    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(
        ForeignKey("news.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    news: Mapped[News] = relationship(back_populates="entities")


class ProcessedItem(Base):
    """A GUID already published to the queue by the Monitor.

    Used for cross-restart deduplication: the Monitor claims a GUID atomically
    (``INSERT ... ON CONFLICT DO NOTHING``) before publishing, so a restarted
    Monitor does not republish already-processed items.

    Attributes:
        guid: Unique identifier of the news item (primary key).
        created_at: Timestamp when the GUID was first claimed.
    """

    __tablename__ = "processed_items"

    guid: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
