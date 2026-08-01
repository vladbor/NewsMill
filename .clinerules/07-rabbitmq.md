# RabbitMQ Rules

## Purpose
RabbitMQ is the message broker that transports news items from the Monitor service to the Worker service.

## Docker Setup
- RabbitMQ must run in Docker as part of `docker-compose.yml`.
- Use the official `rabbitmq:4-management` image (includes management UI).
- Expose ports: `5672` for AMQP protocol, `15672` for management UI.
- Set default user/password via environment variables: `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`.

## Connection
- Store RabbitMQ connection parameters in `.env` (host, port, user, password).
- Use `pydantic-settings` (`BaseSettings`) to load connection parameters.
- Monitor connects to RabbitMQ using `aio-pika` for publishing messages.
- Worker connects to RabbitMQ using FastStream for consuming messages.

## Message Format
- Each message published to the queue must contain at minimum:
  - `source` — agency name (e.g., "RIA Novosti")
  - `title` — news headline
  - `link` — URL to the full article
  - `published_at` — publication datetime
  - `text` — description/content of the news item
- Use JSON serialization for message payloads.
- Use a durable queue to prevent message loss on broker restart.

## Queue Configuration
- Define a single queue named `news` (or `news_items`) for all news messages.
- Configure the queue as durable (`durable=True`).
- Do not use exclusive queues — both Monitor and Worker need access.
- Use direct exchange or default exchange for simplicity.

## Error Handling
- Handle connection failures gracefully (log, retry on next cycle).
- Handle publishing failures gracefully (log, do not crash the Monitor).
- Use `try/except` around all `aio-pika` operations.
- Set reasonable connection timeouts.