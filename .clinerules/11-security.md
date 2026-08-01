# Security Rules

## Secrets & Configuration
- Store all secrets, API keys, and tokens in `.env` file — never hardcode them.
- Never commit `.env` to version control (it is already in `.gitignore`).
- Use `pydantic-settings` (`BaseSettings`) to load configuration from `.env`.
- Never print, log, or expose secrets, tokens, credentials, or private keys.

## Parameter Validation
- Validate all user input at the endpoint boundary using Pydantic models.
- Enforce strict range constraints on numeric parameters (latitude, longitude, days).
- Never trust or forward raw user input to external APIs without validation.

## HTTP Client Security
- Set reasonable timeouts on `httpx.AsyncClient` (10s connect, 30s total).
- Validate and sanitize responses from external APIs before returning to the client.
- Do not forward raw error messages or stack traces from external APIs to the user.

## Error Handling
- Never expose internal implementation details in error responses.
- Return generic, user-friendly error messages for 4xx and 5xx responses.
- Log errors internally for debugging, but do not leak them to the client.

## Dependencies
- Keep dependencies up-to-date to avoid known vulnerabilities.
- Use `uv` for deterministic dependency resolution via `uv.lock`.
- Run `uv sync` to ensure the lock file is in sync with `pyproject.toml`.