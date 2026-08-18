# AGENTS.md — Monitor

FastAPI-сервис опроса RSS-лент. Общие правила — в корневом AGENTS.md, здесь
только то, что важно именно для монитора.

## Ответственность

- `app.py` — приложение FastAPI; lifespan (старт/стоп периодической задачи,
  engine + registry), эндпоинты `/health`, `/refresh`.
- `rss.py` — `fetch_feed()`: HTTP через `httpx.AsyncClient` + парсинг RSS.
- `polling.py` — `poll_all_feeds()`: проход по лентам, claim GUID, публикация.
- `dedup.py` — `GuidRegistry`: атомарный claim GUID в `processed_items`.
- `publisher.py` — `NewsPublisher`: durable-очередь, JSON, delivery PERSISTENT.

## Правила именно здесь

- Эндпоинты: `GET /health` → `{"status": "ok"}`; `POST /refresh` → `{"published": <count>}`.
- Дедупликация — атомарный claim по `guid` в таблицу `processed_items` (переживает
  рестарт); при недоступности БД публикуем всё равно (финальный гейт —
  `UNIQUE` на `news.link` у воркера).
- Ошибка отдельной ленты или публикации логируется и не роняет опрос остальных лент.
- Интервал опроса — из `Settings.poll_interval_seconds`, не хардкодить 300.
- Контракт сообщения — `docs/architecture/message-contract.md`; правки согласовывать.