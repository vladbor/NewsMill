# Monitor Service Rules

## Purpose
The Monitor service is a FastAPI container that polls RSS feeds from Russian news agencies every 5 minutes, deduplicates entries, and publishes new messages to the RabbitMQ queue.

## RSS Feed Polling
- Poll RSS feeds from `newsfeeds.yaml` configuration file.
- The YAML file contains a list of dictionaries in format: `"Agency Name": "RSS URL"`
- Supported agencies: RIA Novosti, TASS, Kommersant (from `newsfeeds.yaml`).
- Use `httpx.AsyncClient` to fetch RSS feeds.
- Parse RSS XML responses using `xml.etree.ElementTree` or equivalent.
- Extract fields: `title`, `link`, `guid`, `published_at`, `description` (text).

## Periodic Polling
- Implement periodic polling using `asyncio.create_task()` with a `while True` loop.
- Poll interval: **5 minutes** (300 seconds) — use `asyncio.sleep(300)`.
- Start the background task in FastAPI's `lifespan` startup handler.
- Cancel the background task in FastAPI's `lifespan` shutdown handler.
- Store a reference to the background task for cancellation.

## Force Refresh (`POST /refresh`)
- The `/refresh` endpoint must trigger an immediate unscheduled poll of all feeds.
- Use the same polling logic as the periodic task.
- Return a count of new news items that were published to the queue.
- Do not block the response — use `BackgroundTasks` or run the poll in a separate asyncio task.

## Deduplication
- Deduplicate news entries by `guid` field.
- Before publishing a message to the queue, check if the `guid` has already been processed.
- Maintain deduplication state in memory (e.g., a `set` of seen GUIDs) or query the database.
- Do not publish the same news item twice.

## Message Publishing
- Publish messages to RabbitMQ queue for the Worker to consume.
- Each message must contain at minimum: `source`, `title`, `link`, `published_at`, `text`.
- Use `aio-pika` for async RabbitMQ publishing.
- Connect to RabbitMQ in the `lifespan` startup handler.
- Close the RabbitMQ connection in the `lifespan` shutdown handler.

## Error Handling
- Handle RSS feed fetch failures gracefully (log the error, skip the feed, continue polling).
- Handle RabbitMQ connection errors gracefully (log, retry on next cycle).
- Do not crash the Monitor service if a single feed is unavailable.