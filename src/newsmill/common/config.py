"""Configuration settings loaded from environment variables."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables in the .env file.

    All RabbitMQ connection parameters and polling settings are taken from
    environment variables defined in ``.env``.

    Attributes:
        rabbitmq_host: RabbitMQ broker host (``RABBITMQ_HOST``).
        rabbitmq_port: RabbitMQ broker port (``RABBITMQ_PORT``).
        rabbitmq_user: RabbitMQ username (``RABBITMQ_USER``).
        rabbitmq_pass: RabbitMQ password (``RABBITMQ_PASS``).
        rabbitmq_queue: Durable queue name for news messages (``RABBITMQ_QUEUE``).
        poll_interval_seconds: Interval between periodic RSS polls
            (``POLL_INTERVAL_SECONDS``).
        newsfeeds_path: Path to the newsfeeds.yaml file (``NEWSFEEDS_PATH``).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    rabbitmq_host: str = Field(validation_alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(validation_alias="RABBITMQ_PORT")
    rabbitmq_user: str = Field(validation_alias="RABBITMQ_USER")
    rabbitmq_pass: str = Field(validation_alias="RABBITMQ_PASS")
    rabbitmq_queue: str = Field(validation_alias="RABBITMQ_QUEUE")
    poll_interval_seconds: int = Field(validation_alias="POLL_INTERVAL_SECONDS")
    newsfeeds_path: str = Field(
        default="newsfeeds.yaml", validation_alias="NEWSFEEDS_PATH"
    )
