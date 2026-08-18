"""Database models shared between services."""

from newsmill.common.db.models import Base, Entity, News, ProcessedItem

__all__ = ["Base", "Entity", "News", "ProcessedItem"]
