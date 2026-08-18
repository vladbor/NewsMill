"""FastAPI application for the Monitor service."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from typing import Any

import httpx
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from newsmill.common.config import Settings
from newsmill.common.db.session import close_engine, get_engine
from newsmill.common.feeds import load_newsfeeds
from newsmill.monitor.dedup import GuidRegistry
from newsmill.monitor.dependencies import get_http_client, get_settings
from newsmill.monitor.polling import poll_all_feeds
from newsmill.monitor.publisher import NewsPublisher

logger = logging.getLogger(__name__)


class MonitorState:
    """Shared state for the Monitor application.

    Attributes:
        settings: Application settings.
        feeds: Mapping of agency name to RSS feed URL.
        publisher: RabbitMQ publisher.
        registry: Database-backed GUID deduplication registry.
        poll_task: Reference to the periodic polling background task.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the state.

        Args:
            settings: Application settings.
        """
        self.settings = settings
        self.feeds: dict[str, str] = {}
        self.publisher = NewsPublisher(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            user=settings.rabbitmq_user,
            password=settings.rabbitmq_pass,
            queue_name=settings.rabbitmq_queue,
        )
        self.engine: AsyncEngine | None = None
        self.registry: GuidRegistry | None = None
        self.poll_task: asyncio.Task[Any] | None = None


async def _periodic_poll(state: MonitorState) -> None:
    """Run periodic RSS polling in a loop.

    Args:
        state: Shared Monitor application state.
    """
    while True:
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0),
                follow_redirects=True,
            ) as client:
                await poll_all_feeds(
                    client, state.feeds, state.publisher, state.registry.claim
                )
        except Exception:
            logger.exception("Periodic poll failed")
        await asyncio.sleep(state.settings.poll_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the Monitor application lifecycle.

    On startup: load feeds, connect to RabbitMQ, and start the periodic
    polling task. On shutdown: cancel the task and close the connection.
    """
    settings = get_settings()
    state = MonitorState(settings)
    app.state.monitor = state

    state.feeds = load_newsfeeds(settings.newsfeeds_path)
    state.engine = get_engine(settings)
    state.registry = GuidRegistry(state.engine)
    await state.publisher.connect()
    state.poll_task = asyncio.create_task(_periodic_poll(state))
    logger.info("Monitor started with %d feeds", len(state.feeds))

    yield

    if state.poll_task is not None:
        state.poll_task.cancel()
        with suppress(asyncio.CancelledError):
            await state.poll_task
    await state.publisher.close()
    await close_engine()
    logger.info("Monitor stopped")


app = FastAPI(title="NewsMill Monitor", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return the service health status.

    Returns:
        A JSON object with a ``status`` of ``"ok"``.
    """
    return {"status": "ok"}


@app.post("/refresh")
async def refresh(
    client: httpx.AsyncClient = Depends(get_http_client),  # noqa: B008
) -> dict[str, int]:
    """Trigger an immediate unscheduled poll of all feeds.

    Args:
        client: Shared httpx async client.

    Returns:
        A JSON object with the count of new news items published.
    """
    state: MonitorState = app.state.monitor
    count = await poll_all_feeds(
        client, state.feeds, state.publisher, state.registry.claim
    )
    return {"published": count}
