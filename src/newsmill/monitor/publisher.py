"""RabbitMQ message publishing for the Monitor service."""

from __future__ import annotations

import json
import logging
from typing import Any

import aio_pika

from newsmill.common.models import NewsItem

logger = logging.getLogger(__name__)


def _build_amqp_url(host: str, port: int, user: str, password: str) -> str:
    """Build an AMQP connection URL from individual parts.

    Args:
        host: RabbitMQ broker host.
        port: RabbitMQ broker port.
        user: RabbitMQ username.
        password: RabbitMQ password.

    Returns:
        A fully-formed AMQP connection URL.
    """
    return f"amqp://{user}:{password}@{host}:{port}/"


class NewsPublisher:
    """Publishes news items to a durable RabbitMQ queue.

    The connection and channel are established lazily via ``connect()`` and
    closed via ``close()``. Publishing errors are logged but never propagated,
    so a broker failure does not crash the Monitor service.
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        queue_name: str,
    ) -> None:
        """Initialize the publisher.

        Args:
            host: RabbitMQ broker host.
            port: RabbitMQ broker port.
            user: RabbitMQ username.
            password: RabbitMQ password.
            queue_name: Name of the durable queue to publish to.
        """
        self._amqp_url = _build_amqp_url(host, port, user, password)
        self._queue_name = queue_name
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self) -> None:
        """Establish the RabbitMQ connection and declare the durable queue."""
        if self._connection is not None:
            return
        logger.info("Connecting to RabbitMQ at %s", self._queue_name)
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(self._queue_name, durable=True)

    async def publish(self, item: NewsItem) -> None:
        """Publish a news item to the queue as a JSON message.

        Args:
            item: The news item to publish.
        """
        if self._channel is None:
            logger.warning("Cannot publish: RabbitMQ is not connected")
            return
        payload: dict[str, Any] = item.model_dump(mode="json")
        message = aio_pika.Message(
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        try:
            await self._channel.default_exchange.publish(
                message, routing_key=self._queue_name
            )
            logger.info("Published news item: %s", item.guid)
        except (aio_pika.exceptions.AMQPError, aio_pika.exceptions.AMQPConnectionError):
            logger.exception("Failed to publish news item %s", item.guid)

    async def close(self) -> None:
        """Close the RabbitMQ connection, if open."""
        if self._connection is None:
            return
        await self._connection.close()
        self._connection = None
        self._channel = None
        logger.info("RabbitMQ connection closed")
