"""Tests for the SQLAlchemy database models."""

from __future__ import annotations

from newsmill.common.db import Entity, News


def test_news_table_columns() -> None:
    """Test that the news table has the expected columns."""
    columns = News.__table__.columns
    assert set(columns.keys()) == {
        "id",
        "source",
        "title",
        "link",
        "published_at",
        "text",
        "created_at",
    }
    assert columns["link"].unique is True
    assert columns["source"].nullable is False
    assert columns["text"].nullable is True


def test_entity_table_columns() -> None:
    """Test that the entities table has the expected columns."""
    columns = Entity.__table__.columns
    assert set(columns.keys()) == {"id", "news_id", "text", "label", "count"}
    assert columns["news_id"].nullable is False
    assert columns["count"].default is not None


def test_news_entities_relationship() -> None:
    """Test that the news-entities relationship is configured."""
    assert "entities" in News.__mapper__.relationships
    assert "news" in Entity.__mapper__.relationships
