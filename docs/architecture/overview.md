# Архитектура NewsMill: поток данных и карта пакетов

## 1. Общая схема

```
RSS-ленты ─▶ Monitor ─▶ RabbitMQ ─▶ Worker ─▶ PostgreSQL
(FastAPI)     (aio-pika)  (durable)  (FastStream)  (newsfeeds)
```

- **Monitor** (FastAPI) — источник входа: опрашивает RSS-ленты из
  `newsfeeds.yaml`, дедуплицирует по `guid`, публикует новые записи в очередь.
- **RabbitMQ** — durable-очередь (`RABBITMQ_QUEUE`, по умолчанию `news`):
  единственный мост между Monitor и Worker, развязывает их жизненные циклы.
- **Worker** (FastStream) — консюмер очереди: извлекает сущности SpaCy и
  сохраняет новость с сущностями в PostgreSQL.
- **PostgreSQL** — БД `newsfeeds`, таблицы `news`/`entities`.

## 2. Карта пакетов `src/newsmill/`

### common/ — общий код (импортируют оба сервиса)

| Модуль | Ответственность |
|---|---|
| `common/models.py` | `NewsItem` — Pydantic-модель записи: `source, title, link, guid, published_at, text` |
| `common/config.py` | `Settings` (`pydantic-settings`, загрузка из `.env`), сборка `database_url` из `DB_*` |
| `common/feeds.py` | `load_newsfeeds()` — парсинг и валидация `newsfeeds.yaml` |
| `common/db/models.py` | ORM-модели `News`, `Entity` (SQLAlchemy 2.0, `Mapped`) |

### monitor/ — FastAPI-сервис

| Модуль | Ответственность |
|---|---|
| `monitor/app.py` | Приложение FastAPI; lifespan (старт/стоп периодической задачи), эндпоинты `/health`, `/refresh` |
| `monitor/rss.py` | `fetch_feed()` — HTML-запрос через `httpx.AsyncClient`, парсинг RSS 2.0/1.0 через `ElementTree` |
| `monitor/polling.py` | `poll_all_feeds()` — проход по всем лентам, дедупликация по `guid`, публикация, счётчик |
| `monitor/publisher.py` | `NewsPublisher` — подключение к RabbitMQ (`aio-pika`), durable-очередь, публикация JSON |
| `monitor/dependencies.py` | `get_settings`, `get_http_client` — зависимости для эндпоинтов |

### worker/ — FastStream-сервис

| Модуль | Ответственность |
|---|---|
| `worker/main.py` | Точка входа `python -m newsmill.worker.main` |
| `worker/app.py` | `create_app()` — FastStream + `RabbitBroker`, подписка на очередь, `_deserialize_item`, `_persist` |
| `worker/ner.py` | SpaCy NER: загрузка модели `ru_core_news_md`, `extract_entities()`, агрегация счетчиков |
| `worker/database.py` | Async-движок/сессии SQLAlchemy (`asyncpg`), общие `get_engine`/`get_session_factory` |

## 3. Эндпоинты Monitor (FastAPI)

| Метод | Путь | Описание | Ответ |
|---|---|---|---|
| GET | `/health` | Проверка работоспособности | `{"status": "ok"}` (200) |
| POST | `/refresh` | Внеплановый опрос всех лент с публикацией | `{"published": <count>}` (200) |

## 4. Межсервисные контракты

- **Monitor → очередь**: JSON-сериализация `NewsItem` (`model_dump(mode="json")`),
  delivery_mode PERSISTENT. Детали — `architecture/message-contract.md`.
- **очередь → Worker**: FastStream десериализует тело в `NewsItem` (`model_validate`).
- **Worker → PostgreSQL**: вставка `News` + связанных `Entity` одной транзакцией.
  Модель — `architecture/data-model.md`.

## 5. Инфраструктура

- Docker Compose: `queue` (rabbitmq:4-management), `db` (postgres:18),
  `monitor`, `worker` — в сети `newsmill-network`, с healthcheck и томами.
- Хосты переопределяются на имена контейнеров: `RABBITMQ_HOST=queue`, `DB_HOST=db`.
- Конфигурация — из `.env` (`common/config.py`).