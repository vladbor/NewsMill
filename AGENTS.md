# AGENTS.md

NewsMill — распределённая система мониторинга RSS-лент российских
новостных агентств (RIA, TASS, Kommersant — список в `newsfeeds.yaml`)
с извлечением именованных сущностей (NER) на русском языке.

Поток данных:

```
RSS-ленты → Monitor → RabbitMQ → Worker → PostgreSQL
```

## Сервисы

- **Monitor** — `src/newsmill/monitor/`, FastAPI. Каждые `POLL_INTERVAL_SECONDS`
  опрашивает RSS-ленты (`asyncio` + `httpx`), дедуплицирует по `guid` и
  публикует новые записи в RabbitMQ (`aio-pika`). Эндпоинты: `GET /health`,
  `POST /refresh`.
- **Worker** — `src/newsmill/worker/`, FastStream. Консюмер очереди: SpaCy NER
  (PER, ORG, LOC, MISC), сохранение новости с сущностями в PostgreSQL.
- **RabbitMQ / PostgreSQL** — брокер и БД `newsfeeds` (таблицы `news`/`entities`),
  поднимаются в Docker.
- **common** — `src/newsmill/common/`: разделяемые Pydantic/SQLAlchemy-модели,
  конфигурация (`pydantic-settings`), загрузка лент.

## Как запустить

```bash
uv sync                                # зависимости (Python 3.12)
cp .env.EXAMPLE .env                   # конфигурация; .env не коммитить
alembic upgrade head                   # миграции — ТОЛЬКО вручную
docker compose up --build              # 4 контейнера: queue, db, monitor, worker
```

- Monitor (локально): `uvicorn src.newsmill.monitor.app:app --port 8000`
  — проверка: `GET http://localhost:8000/health`.
- Worker (локально): `python -m src.newsmill.worker.main`.
- Перед коммитом: `ruff format .`, `ruff check .`, `pytest -v`.

## Куда смотреть дальше (указатели с условием срабатывания)

Читай документ ДО начала работы соответствующего типа — указатель без условия
агент пролистывает.

- **Перед началом любой работы** — прочитай `memory/active-context.md`; после
  завершения задачи обнови `memory/progress.md` и `memory/active-context.md`.
- **Перед правкой API или контракта сообщения** —
  `docs/architecture/message-contract.md` + `docs/design-docs/core-beliefs.md`.
- **Перед изменением схемы БД / ORM-моделей / миграций** —
  `docs/architecture/data-model.md`.
- **Перед доработкой функциональности** — файлы в папке `docs/execution-plans/001`
  (текущий план ближайшей работы).
- **Перед работой в конкретном сервисе** — его вложенный AGENTS.md:
  `src/newsmill/monitor/AGENTS.md`, `src/newsmill/worker/AGENTS.md`,
  `src/newsmill/common/AGENTS.md`.
- **Перед выбором технологии / инфраструктуры** —
  `docs/design-docs/broker-choice.md`.
- **Перед тем как пометить проблему «сознательно не чиним»** —
  `docs/technical-debt/known-issues.md`.
- **После закрытия задачи** — обнови статус плана в `execution-plans` и
  `docs/technical-debt/known-issues.md`, актуализируй `memory/active-context.md`.
- **Как агент работает здесь** — `docs/principles/agent-workflow.md` и
  `docs/principles/coding-standards.md`.

## Порядок знакомства агента с репозиторием

1. `README.md` — общий контекст, эндпоинты, конфигурация, запуск.
2. `docs/architecture/overview.md` — поток данных и карта пакетов.
3. `docs/principles/agent-workflow.md` — рабочий цикл агента.
4. `memory/` — текущее состояние работы. Обновляй самостоятельно.

Схема БД, конвенции кода и история решений вынесены в `docs/` — не дублируй
их здесь.
