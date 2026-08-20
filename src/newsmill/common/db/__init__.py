"""Database models shared between services."""

from newsmill.common.db.models import Base, Entity, News, ProcessedItem
from newsmill.common.db.retention import PurgeResult, purge_old_records

__all__ = [
    "Base",
    "Entity",
    "News",
    "ProcessedItem",
    "PurgeResult",
    "purge_old_records",
]
