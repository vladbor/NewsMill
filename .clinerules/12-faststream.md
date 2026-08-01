# FastStream Rules

## Purpose
FastStream is the consumer framework used by the Worker service to subscribe to the RabbitMQ queue and process incoming news messages.

## Worker Setup
- The Worker service is a FastStream-based consumer that subscribes to the RabbitMQ queue.
- Define the FastStream application with a `RabbitBroker` instance.
- Use `@broker.subscriber("news")` decorator to register the message handler on the `news` queue.
- The handler function must be `async def`.

## Message Handling
- Each incoming message is a JSON payload containing: `source`, `title`, `link`, `published_at`, `text`.
- Deserialize the message into a Pydantic model for validation.
- Pass the validated data to the NER processing function.
- After processing, write the results to PostgreSQL using SQLAlchemy async sessions.

## NER Integration
- In the message handler, call the SpaCy NLP pipeline to extract named entities.
- Extract entities from both `title` and `text` fields.
- Collect entities with their labels (PER, ORG, LOC, etc.) and count occurrences.
- Write the original news item to the `news` table.
- Write the extracted entities to the `entities` table.

## Database Operations
- Use SQLAlchemy async sessions within the FastStream handler.
- Create a new session for each message (or use a session factory).
- Commit the transaction after successfully writing news + entities.
- Roll back on error to avoid partial writes.

## Error Handling
- Handle deserialization errors gracefully (log, acknowledge message to avoid poison pill).
- Handle database errors gracefully (log, retry or dead-letter as appropriate).
- Handle SpaCy processing errors gracefully (log, skip entity extraction if model fails).
- Do not crash the Worker on a single malformed message.

## Configuration
- Store RabbitMQ connection parameters in `.env` (host, port, user, password).
- Use `pydantic-settings` (`BaseSettings`) to load configuration.
- Store database connection string in `.env` as well.
- Connect to RabbitMQ on Worker startup, close on shutdown.