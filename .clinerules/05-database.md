# Database Rules

## ORM
- Use **SQLAlchemy** as the ORM for all database models.
- Define models as classes inheriting from `DeclarativeBase`.
- Use `Mapped` and `mapped_column` for column definitions (SQLAlchemy 2.0 style).
- Store all models in a dedicated module (e.g., `src/models.py` or `src/models/`).

## Schema

### Table: `news`
- `id` — Primary Key, auto-increment, NOT NULL
- `source` — string, NOT NULL (agency name, e.g., "RIA Novosti")
- `title` — string, NOT NULL
- `link` — string, UNIQUE, NOT NULL
- `published_at` — datetime, NOT NULL
- `text` — text, nullable (description/content of the news item)
- `created_at` — datetime, NOT NULL, default current timestamp

### Table: `entities`
- `id` — Primary Key, auto-increment, NOT NULL
- `news_id` — Foreign Key referencing `news.id`, ON DELETE CASCADE, NOT NULL
- `text` — string, NOT NULL (extracted entity text)
- `label` — string, NOT NULL (entity type: PER, ORG, LOC, etc.)
- `count` — integer, NOT NULL, default 1

## Database Name
- Use `newsfeeds` as the database name (e.g., `newsfeeds` for PostgreSQL database).

## Migrations (Alembic)
- **Generate migration files only** — NEVER apply them.
- Use `alembic revision --autogenerate -m "description"` to create a new migration.
- Migration files are stored in a `versions/` directory inside the migrations folder.
- Do NOT run `alembic upgrade`, `alembic downgrade`, `alembic stamp`, or any command that changes database state.
- After generating a migration, show what file was created and describe what it does.
- This is a strict boundary: applying migrations is a manual human operation.

## Configuration
- Store database connection string in `.env` (e.g., `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/newsfeeds`).
- Use `pydantic-settings` (`BaseSettings`) to load the connection string.
- Use `asyncpg` as the async PostgreSQL driver for SQLAlchemy async sessions.