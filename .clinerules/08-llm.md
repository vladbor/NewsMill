# LLM / Agent Rules

## Before Making Changes
- Always read `README.md` first to understand the project context and requirements.
- Read the relevant source files before writing or modifying code.
- Summarize the plan and expected diff before making changes to any file.

## Code Changes
- Prefer focused tests before full test runs (e.g., `pytest tests/test_health.py`).
- Do not edit dependency files (`pyproject.toml`, `uv.lock`) unless the task explicitly asks for it.
- Do not read or print secrets, `.env` files, tokens, credentials, or private keys.
- After each code change, run `ruff format .` and `ruff check .` and fix all warnings.

## Communication
- Use English for all responses, comments, and commit messages.
- Be direct and technical — avoid conversational filler.
- When fixing bugs, verify with the project's existing test suite, not just a reproduction script.