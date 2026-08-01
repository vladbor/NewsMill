# FastAPI Rules

## Endpoints
- Define all endpoints with `async def` — never use synchronous handlers.
- Use explicit HTTP method decorators: `@app.get()`, `@app.post()`, etc.
- Group related endpoints under a common prefix using `APIRouter`.
- Keep endpoint handlers thin — delegate business logic to service functions.

## Monitor Endpoints
- `GET /health` — returns `{"status": "ok"}` with 200 status.
- `POST /refresh` — initiates an unscheduled poll of all RSS feeds, returns a count of new news items.
- Use `BackgroundTasks` or an asyncio task reference for the `/refresh` endpoint to trigger polling without blocking the response.

## Parameter Validation
- Use Pydantic models for request bodies (POST/PUT).
- Use `Query()` with `Field()` constraints for query parameters (e.g., `latitude: float = Field(..., ge=-90, le=90)`).
- Use `Path()` for path parameters with validation.
- Validate all external inputs at the endpoint boundary.

## Dependency Injection
- Use `Depends()` for shared dependencies (e.g., `httpx.AsyncClient`, settings, RabbitMQ channel).
- Define reusable dependencies in a dedicated module (e.g., `src/dependencies.py`).
- Prefer generator-based dependencies for resource cleanup (e.g., client lifecycle).

## Background Tasks & Lifespan
- Use FastAPI's `lifespan` context manager for startup/shutdown logic:
  - **Startup**: create `httpx.AsyncClient`, connect to RabbitMQ, start the asyncio background task for periodic RSS polling.
  - **Shutdown**: cancel the background task, close the HTTP client, close the RabbitMQ connection.
- Implement periodic polling using `asyncio.create_task()` with a `while True` loop and `asyncio.sleep(300)` (5 minutes).
- Store a reference to the background task so it can be cancelled on shutdown.
- The `/refresh` endpoint should call the same polling logic synchronously (or via a separate task) and return the count of new items.

## Error Handling
- Use `HTTPException` with appropriate status codes for user-facing errors:
  - `400` — invalid parameters
  - `404` — resource not found
  - `502` — external API / RSS feed unavailable
  - `504` — external API / RSS feed timeout
- Register a global exception handler with `@app.exception_handler()` for consistent error responses.
- Never expose raw exception details or stack traces to the client.

## Response Models
- Use Pydantic models as `response_model` decorator parameter for automatic validation and serialization.
- Use `response_model_exclude_none=True` to omit `None` fields from responses.
- Use `status_code` parameter to document the expected HTTP status code.

## httpx Client
- Create a single reusable `AsyncClient` instance as a dependency.
- Configure timeout on the client (default: 10s connect, 30s total).
- Set `base_url` from settings (`.env` file) when possible.
- Close the client on application shutdown using a lifespan handler.