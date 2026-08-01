# Python Rules

## PEP 8 Compliance
- Follow PEP 8 style guidelines for all Python code.
- Maximum line length: 88 characters (ruff default, slightly wider than PEP 8's 79).
- Use 4 spaces per indentation level (no tabs).
- Two blank lines between top-level definitions (classes, functions).
- One blank line between method definitions inside a class.

## Async/Await
- Use `async def` for all endpoint handlers and any function that performs I/O.
- Use `await` when calling external APIs, database queries, or any async operation.
- Do not mix sync and async code unnecessarily — prefer async throughout.

## Type Hints
- Add type hints to all function signatures (parameters and return types).
- Use `from __future__ import annotations` at the top of files to enable PEP 604 syntax.
- Prefer `|` over `Optional` (e.g., `str | None` instead of `Optional[str]`).
- Use `TypedDict` or Pydantic models for complex return types.

## Error Handling
- Catch specific exceptions, not bare `except:` or `Exception`.
- Handle `httpx.TimeoutException` for external API timeouts.
- Handle `httpx.HTTPStatusError` for non-2xx responses from external APIs.
- Handle `httpx.RequestError` for connection-level failures.
- Use `try/except/finally` for resource cleanup (e.g., closing clients).

## Pydantic
- Use Pydantic v2 models for request/response validation.
- Define models with `BaseModel` and use `Field()` for constraints.
- Use `model_validate()` for dict-to-model conversion (v2 style).
- Use `model_dump()` for model-to-dict conversion (v2 style).

## Configuration
- Use `pydantic-settings` (`BaseSettings`) for `.env` file loading.
- Store external API base URL and other config in `.env`.
- Access config via a global settings object or dependency injection.

## Imports
- Group imports in this order: standard library, third-party, local.
- Use absolute imports for local modules (e.g., `from src.app import ...`).
- Avoid circular imports by structuring code into clear layers.