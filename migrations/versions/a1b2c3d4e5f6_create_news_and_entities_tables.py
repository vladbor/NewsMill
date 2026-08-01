"""Create news and entities tables.

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-08-01 20:29:00.000000

Initial schema for the NewsMill database: the ``news`` and ``entities``
tables as defined by the ORM models in ``newsmill.common.db.models``.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the ``news`` and ``entities`` tables."""
    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("link", sa.String(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("link"),
    )

    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("news_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("count", sa.Integer(), server_default="1", nullable=False),
        sa.ForeignKeyConstraint(["news_id"], ["news.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop the ``entities`` and ``news`` tables."""
    op.drop_table("entities")
    op.drop_table("news")
