"""Configuration settings loaded from environment variables."""

from __future__ import annotations

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables in the .env file.

    All RabbitMQ connection parameters, polling settings and database
    connection parameters are taken from environment variables defined in
    ``.env``. The async PostgreSQL URL is assembled from the individual
    ``DB_*`` variables via the ``database_url`` computed field.

    Attributes:
        rabbitmq_host: RabbitMQ broker host (``RABBITMQ_HOST``).
        rabbitmq_port: RabbitMQ broker port (``RABBITMQ_PORT``).
        rabbitmq_user: RabbitMQ username (``RABBITMQ_USER``).
        rabbitmq_pass: RabbitMQ password (``RABBITMQ_PASS``).
        rabbitmq_queue: Durable queue name for news messages (``RABBITMQ_QUEUE``).
        poll_interval_seconds: Interval between periodic RSS polls
            (``POLL_INTERVAL_SECONDS``).
        newsfeeds_path: Path to the newsfeeds.yaml file (``NEWSFEEDS_PATH``).
        db_host: PostgreSQL host (``DB_HOST``).
        db_port: PostgreSQL port (``DB_PORT``).
        db_user: PostgreSQL username (``DB_USER``).
        db_pass: PostgreSQL password (``DB_PASS``).
        db_name: PostgreSQL database name (``DB_NAME``).
        delete_after_days: Age in days after which records are purged
            (``DELETE_AFTER``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

    rabbitmq_host: str = Field(validation_alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(validation_alias="RABBITMQ_PORT")
    rabbitmq_user: str = Field(validation_alias="RABBITMQ_USER")
    rabbitmq_pass: str = Field(validation_alias="RABBITMQ_PASS")
    rabbitmq_queue: str = Field(validation_alias="RABBITMQ_QUEUE")
    poll_interval_seconds: int = Field(validation_alias="POLL_INTERVAL_SECONDS")
    newsfeeds_path: str = Field(
        default="newsfeeds.yaml", validation_alias="NEWSFEEDS_PATH"
    )
    db_host: str = Field(default="localhost", validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")
    db_user: str = Field(default="postgres", validation_alias="DB_USER")
    db_pass: str = Field(default="postgres", validation_alias="DB_PASS")
    db_name: str = Field(default="newsfeeds", validation_alias="DB_NAME")
    delete_after_days: int = Field(default=30, validation_alias="DELETE_AFTER")

    @computed_field
    @property
    def database_url(self) -> str:
        """Assemble the async PostgreSQL connection URL from DB_* settings.

        Returns:
            An SQLAlchemy async DSN string using the ``asyncpg`` driver.
        """
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
