# Coding Rules

## Before Making Changes
- Always read `README.md` first to understand the project context and requirements.
- Follow the existing project structure and conventions — do not reorganize files without explicit approval.
- Review the relevant source files before writing or modifying code.
- Use Context7 MCP as documentation source.

## Formatting & Linting
- Always run `ruff format .` and `ruff check .` before committing changes.
- Fix all warnings reported by `ruff check` before submitting code.
- Never disable linter rules unless absolutely necessary and justified with `# noqa: <rule>`.

## Naming Conventions
- **Files and directories**: lowercase with underscores (`snake_case`).
- **Classes**: PascalCase (e.g., `WeatherResponse`, `ForecastRequest`).
- **Functions and methods**: lowercase with underscores (`snake_case`).
- **Variables**: descriptive, lowercase with underscores.
- **Constants**: uppercase with underscores (`SNAKE_CASE`).

## Code Style
- Use meaningful, self-documenting names. Avoid abbreviations.
- Prefer explicit imports over wildcard imports (`from module import *`).
- Maximum line length: 88 characters (ruff default).
- Use 4 spaces for indentation (no tabs).

## Comments & Documentation
- Write docstrings for all public modules, classes, and functions (Google or NumPy style).
- Include `Args`, `Returns`, and `Raises` sections in docstrings where applicable.
- Use inline comments sparingly — prefer clear code over comments.
- Keep comments up-to-date with the code they describe.

## README.md
- Maintain an up-to-date `README.md` at the project root at all times.
- The `README.md` must contain the following sections:
  - **General information** about the project — purpose, architecture overview, and technology stack.
  - **Service endpoints** — description of all HTTP endpoints (method, path, purpose, response format).
  - **Database fields** — description of all tables and their columns (name, type, constraints, purpose).
  - **Installation preparation** — prerequisites and environment setup steps (e.g., `.env` configuration, Docker).
  - **Installation** — step-by-step instructions for installing dependencies and building the project.
  - **Testing** — instructions for running the test suite.
  - **Service startup** — instructions for starting all services (e.g., via Docker Compose).
- Update `README.md` whenever the project changes in a way that affects any of the documented sections:
  - Adding, removing, or changing an endpoint.
  - Changing the database schema (tables, columns, constraints).
  - Changing the architecture, technology stack, or configuration requirements.
  - Changing installation, testing, or startup procedures.
- Never leave `README.md` outdated relative to the actual state of the codebase.

## Commits
- Write clear, descriptive commit messages in English.
- Keep commits focused on a single logical change.
- Do not commit `__pycache__/`, `.venv/`, `.ruff_cache/`, or `.env`.