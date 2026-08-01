# Testing Rules

## Test Framework
- Use **pytest** as the test runner.
- Use **pytest-asyncio** for testing async endpoints (`@pytest.mark.asyncio`).
- Run tests with `pytest` (discovers all `test_*.py` files in `tests/`).

## Test Structure
- Place all tests in the `tests/` directory.
- Name test files with `test_` prefix (e.g., `test_health.py`, `test_monitor.py`).
- Name test functions with `test_` prefix and describe the scenario (e.g., `test_health_returns_ok`).
- Group related tests in the same file.

## Fixtures
- Use `pytest.fixture` for reusable test dependencies.
- Define an `async_client` fixture that provides a `TestClient` or `AsyncClient` instance.
- Use `conftest.py` for shared fixtures across multiple test files.
- Clean up resources (e.g., close clients) in fixture teardown.

## Mocking External APIs
- Use `httpx.AsyncClient` mocking to avoid real network calls in tests.
- Use `respx` or `httpx.MockTransport` to intercept and mock HTTP requests.
- Mock RSS feed responses to test polling and parsing logic.
- Mock RabbitMQ connections to test message publishing without a real broker.
- Mock database sessions to test NER and persistence without a real database.
- Test both success and error scenarios (timeout, non-2xx, malformed response).

## What to Test
- **Health endpoint**: returns `{"status": "ok"}` with 200 status.
- **Monitor polling**: RSS feed parsing, deduplication by GUID, error handling for unavailable feeds.
- **Refresh endpoint**: triggers unscheduled poll, returns count of new items.
- **Worker processing**: message deserialization, NER entity extraction, database write.
- **Database models**: news and entities table schema, relationships, constraints.
- **Error handling**: external API timeout returns 504; external API error returns 502; malformed response returns 502.
- **Parameter validation**: valid and invalid parameters.

## Running Tests
- Run focused tests first during development: `pytest tests/test_health.py -v`
- Run the full suite before committing: `pytest -v`
- Use `-x` to stop on first failure for faster debugging.
- Use `-k` to filter tests by name: `pytest -k "health"`