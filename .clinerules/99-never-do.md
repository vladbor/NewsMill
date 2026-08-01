# Never Do

## Prohibited Actions

- **Never edit `pyproject.toml` or `uv.lock`** unless the task explicitly asks for dependency changes.
- **Never read or print secrets, `.env` files, tokens, credentials, or private keys** — even if asked.
- **Never ignore or suppress linter errors** without a justified `# noqa: <rule>` comment.
- **Never commit code without running `ruff format .` and `ruff check .`** first.
- **Never commit `__pycache__/`, `.venv/`, `.ruff_cache/`, `.env`, or other generated files.**
- **Never use wildcard imports** (`from module import *`).
- **Never expose raw exception details, stack traces, or internal implementation details to the client.**
- **Never use synchronous handlers for FastAPI endpoints** — always use `async def`.
- **Never hardcode secrets, API keys, or configuration values** in source code.
- **Never skip tests** — always run `pytest` before committing.
- **Never run `alembic upgrade`, `alembic downgrade`, `alembic stamp`, or any command that changes database state** — only generate migration files.
- **Never reorganize the project structure** without explicit approval.
- **Never make changes without reading the relevant source files first.**
- **Never commit with failing tests or linter warnings.**
- **Never use `# noqa` without specifying the specific rule being ignored** (e.g., `# noqa: E501`).