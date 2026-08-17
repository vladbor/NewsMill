# AGENTS.md — Monitor

FastAPI-сервис опроса RSS-лент. Общие правила — в корневом AGENTS.md, здесь
только то, что важно именно для монитора.

## Ответственность

- `app.py` — приложение FastAPI; lifespan (старт/стоп периодической задачи),
  эндпоинты `/health`, `/refresh`.
- `rss.py` — `fetch_feed()`: HTTP через `httpx.AsyncClient` + парсинг RSS.
- `polling.py` — `poll_all_feeds()`: проход по лентам, дедупликация, публикация.
- `publisher.py` — `NewsPublisher`: durable-очередь, JSON, delivery PERSISTENT.

## Правила именно здесь

- Эндпоинты: `GET /health` → `{"status": "ok"}`; `POST /refresh` → `{"published": <count>}`.
- Дедупликация — по `guid` через `seen_guids` (память процесса; план 001 —
  `docs/execution-plans/001-dedup-postgres.md` — перенесёт её в БД).
- Ошибка отдельной ленты или публикации логируется и не роняет опрос остальных лент.
- Интервал опроса — из `Settings.poll_interval_seconds`, не хардкодить 300.
- Контракт сообщения — `docs/architecture/message-contract.md`; правки согласовывать.
