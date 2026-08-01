# Technology Stack

## Runtime
- **Python 3.12** — target runtime version (see `.python-version`)
- **UV** — package manager (use `uv sync` for installs, `uv add` for new deps)

## Web Framework
- **FastAPI** — async web framework (Monitor service)
- **Uvicorn** — ASGI server for running the app
- **Pydantic v2** — data validation and settings management

## HTTP Client
- **httpx** — `AsyncClient` for all external HTTP requests (RSS feed polling, external API calls)

## Code Quality
- **ruff** — both formatter and linter (single tool)
- **pytest** — test runner
- **pytest-asyncio** — async test support

## Task Scheduling
- **asyncio** — built-in async task scheduling for periodic RSS polling (every 5 minutes)

## YAML Configuration
- **PyYAML** — parsing `newsfeeds.yaml` configuration file

## Messages Framework
- **RabbitMQ** in **Docker** — message broker (transport between Monitor and Worker)
- **aio-pika** — async RabbitMQ client for publishing messages
- **FastStream** — consumer framework for subscribing to the queue

## Natural Language Processing
- **SpaCy** — NER (Named Entity Recognition) with Russian-language models (`ru_core_news_sm`, `ru_core_news_md`, etc.)

## Database
- **PostgreSQL** version 17 in **Docker**
- **SQLAlchemy** — ORM for database models
- **Alembic** — migrations (generate only, never auto-apply)

## Infrastructure
- **Docker Compose** — orchestration for all services (Queue, Database, Monitor, Worker)
- **Queue** and **PostgreSQL** — only via **docker-compose**, no "manual" local installations in the code