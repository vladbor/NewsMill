# NewsMill

Система мониторинга RSS-лент российских новостных агентств с извлечением именованных сущностей (NER).

## Общая информация

NewsMill — это распределённая система, состоящая из двух сервисов:

- **Monitor** — FastAPI-сервис, который периодически (каждые 5 минут) опрашивает RSS-ленты новостных агентств, дедуплицирует записи по `guid` и публикует новые сообщения в очередь RabbitMQ.
- **Worker** — FastStream-сервис, который потребляет сообщения из очереди RabbitMQ, извлекает именованные сущности (PER, ORG, LOC, MISC) с помощью SpaCy и сохраняет результаты в PostgreSQL.

Сервисы общаются через RabbitMQ. Общий код (модели, конфигурация, утилиты) вынесен в пакет `common`.

## Архитектура

```text
┌────────────┐     ┌──────────────┐     ┌────────────┐     ┌──────────────┐
│  RSS-ленты │ ──▶ │   Monitor    │ ──▶ │  RabbitMQ  │ ──▶ │    Worker    │
│ (агентства)│     │  (FastAPI)   │     │  (очередь) │     │  (FastStream)│
└────────────┘     └──────────────┘     └────────────┘     └──────┬───────┘
                                                                  │
                                                                  ▼
                                                          ┌──────────────┐
                                                          │  PostgreSQL  │
                                                          │  (newsfeeds) │
                                                          └──────────────┘
```

## Технологический стек

- **Python 3.12** — целевая версия рантайма
- **UV** — менеджер пакетов
- **FastAPI** + **Uvicorn** — веб-фреймворк (Monitor)
- **FastStream** + **aio-pika** — потребление сообщений из RabbitMQ (Worker)
- **RabbitMQ** — брокер сообщений (в Docker)
- **PostgreSQL 18** — база данных (в Docker)
- **SQLAlchemy** + **Alembic** — ORM и миграции
- **SpaCy** — NER с русскоязычными моделями
- **httpx** — асинхронный HTTP-клиент
- **PyYAML** — парсинг `newsfeeds.yaml`
- **pydantic-settings** — конфигурация из `.env`
- **ruff** — форматирование и линтинг
- **pytest** + **pytest-asyncio** — тестирование

## Структура каталогов

```text
src/
  newsmill/
    __init__.py
    common/          # Общий код (модели, конфигурация, утилиты)
    monitor/         # Monitor-сервис (FastAPI)
    worker/          # Worker-сервис (FastStream)
    maintenance/     # Обслуживание: purge устаревших записей (retention)
tests/
  common/            # Тесты общего кода
  monitor/           # Тесты Monitor-сервиса
  worker/            # Тесты Worker-сервиса
pyproject.toml       # Конфигурация проекта и зависимостей
newsfeeds.yaml       # Список RSS-лент
Dockerfile           # Многоступенчатый Docker-образ приложения
docker-compose.yml   # Оркестрация сервисов (Docker Compose)
.dockerignore        # Исключения из контекста сборки Docker
AGENTS.md            # Инструкции для агента: карта с указателями на docs/ и memory/
docs/                # Стабильное знание о системе (архитектура, планы, техдолг)
memory/              # Изменчивое состояние работы агента (активный контекст, прогресс, ADR)
REPORT.md            # Отчёт по harness'у (ДЗ №3)
migrations/          # Миграции Alembic
```

## Эндпоинты сервисов

### Monitor (FastAPI)

| Метод | Путь      | Описание                                                                  | Формат ответа                  |
|-------|-----------|---------------------------------------------------------------------------|--------------------------------|
| GET   | `/health` | Проверка работоспособности сервиса                                        | `{"status": "ok"}` (200)       |
| POST  | `/refresh`| Немедленный внеплановый опрос всех RSS-лент с публикацией новых записей   | `{"published": <count>}` (200) |

## Конфигурация (.env)

Конфигурация загружается из файла `.env` с помощью `pydantic-settings`:

| Переменная               | Описание                                        |
|--------------------------|-------------------------------------------------|
| `RABBITMQ_HOST`          | Хост RabbitMQ                                   |
| `RABBITMQ_PORT`          | Порт RabbitMQ (AMQP)                            |
| `RABBITMQ_USER`          | Пользователь RabbitMQ                           |
| `RABBITMQ_PASS`          | Пароль RabbitMQ                                 |
| `RABBITMQ_QUEUE`         | Имя durable-очереди для сообщений новостей      |
| `POLL_INTERVAL_SECONDS`  | Интервал периодического опроса RSS-лент (сек.)  |
| `NEWSFEEDS_PATH`         | Путь к файлу `newsfeeds.yaml` (по умолчанию)    |
| `LOGGING_PATH`           | Каталог логов сервисов (по умолчанию `logs`)    |
| `DB_HOST`                | Хост PostgreSQL                                  |
| `DB_PORT`                | Порт PostgreSQL                                  |
| `DB_USER`                | Пользователь PostgreSQL                          |
| `DB_PASS`                | Пароль PostgreSQL                                |
| `DB_NAME`                | Имя базы данных PostgreSQL (`newsfeeds`)         |
| `DELETE_AFTER`           | Возраст записей (дней), старше которых purge удаляет (по умолчанию `30`) |

## База данных

Схема базы данных `newsfeeds` содержит три таблицы:

### Таблица `news`

| Колонка        | Тип      | Ограничения                  | Описание                          |
|----------------|----------|------------------------------|-----------------------------------|
| `id`           | integer  | PK, autoincrement, NOT NULL  | Первичный ключ                    |
| `source`       | string   | NOT NULL                     | Название агентства                |
| `title`        | string   | NOT NULL                     | Заголовок новости                 |
| `link`         | string   | UNIQUE, NOT NULL             | Ссылка на статью                  |
| `published_at` | datetime with time zone | NOT NULL        | Дата публикации                   |
| `text`         | text     | nullable                     | Описание/содержимое новости       |
| `created_at`   | datetime with time zone | NOT NULL, default now | Время создания записи в БД  |

### Таблица `entities`

| Колонка   | Тип      | Ограничения                          | Описание                          |
|-----------|----------|--------------------------------------|-----------------------------------|
| `id`      | integer  | PK, autoincrement, NOT NULL          | Первичный ключ                    |
| `news_id` | integer  | FK → `news.id`, ON DELETE CASCADE    | Ссылка на новость                 |
| `text`    | string   | NOT NULL                             | Текст сущности                    |
| `label`   | string   | NOT NULL                             | Тип сущности (PER, ORG, LOC, MISC)|
| `count`   | integer  | NOT NULL, default 1                  | Количество вхождений              |

### Таблица `processed_items`

Реестр GUID, уже опубликованных Monitor'ом в очередь (дедупликация, переживает
рестарт Monitor). Запись создаётся атомарно перед публикацией
(`INSERT ... ON CONFLICT (guid) DO NOTHING`).

| Колонка      | Тип      | Ограничения                     | Описание                     |
|--------------|----------|---------------------------------|------------------------------|
| `guid`       | string   | PK, NOT NULL                    | Уникальный идентификатор новости |
| `created_at` | datetime with time zone | NOT NULL, default now | Момент первого claim      |

## Миграции (Alembic)

Миграции управляются через [Alembic](https://alembic.sqlalchemy.org/) и находятся в каталоге `migrations/`.

Строка подключения к базе данных собирается в `migrations/env.py` из переменных `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, `DB_NAME` (дефолты совпадают с `src/newsmill/common/config.py`). Для соединения используется асинхронный драйвер `asyncpg`.

### Генерация новой миграции

Создать файл миграции на основе изменений ORM-моделей:

```bash
uv run alembic revision --autogenerate -m "описание изменения"
```

### Применение миграций

Миграции **не применяются автоматически** — это ручная операция. Для применения используйте:

```bash
uv run alembic upgrade head
```

После применения миграции зафиксируйте новый файл в каталоге `migrations/versions/` в git.

## Установка

### Предварительные требования

- Python 3.12
- UV (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker и Docker Compose (для запуска всех сервисов — RabbitMQ, PostgreSQL, Monitor, Worker)

### Установка зависимостей

```bash
uv sync
```

## Тестирование

```bash
pytest -v
```

## Запуск сервисов

### Monitor (локально)

Запуск FastAPI-приложения Monitor с Uvicorn:

```bash
uvicorn src.newsmill.monitor.app:app --host 0.0.0.0 --port 8000
```

Возможные эндпоинты:
- `GET /health` — проверка состояния
- `POST /refresh` — принудительный опрос

### Worker (локально)

Запуск FastStream-консюмера Worker:

```bash
python -m src.newsmill.worker.main
```

Worker подписывается на очередь RabbitMQ (`RABBITMQ_QUEUE`), десериализует сообщения в `NewsItem`, извлекает именованные сущности (PER, ORG, LOC, MISC) с помощью SpaCy (`ru_core_news_md`) и сохраняет новость с сущностями в PostgreSQL.

### Очистка старых записей (retention)

Записи базы данных (новости, сущности каскадом и реестр `processed_items`) старше
`DELETE_AFTER` дней из `.env` удаляются отдельной командой:

```bash
python -m newsmill.maintenance.purge          # локально
docker compose run --rm maintenance            # в Docker
```

Сервис `maintenance` в `docker-compose.yml` объявлен с профилем `tools`, поэтому
он не поднимается командой `docker compose up` и запускается только явно, как
выше. Миграций не требует — схема не меняется.

### Все сервисы (Docker Compose)

Запуск всех компонентов NewsMill — **4 отдельных контейнера** (RabbitMQ, PostgreSQL, Monitor, Worker) — одной командой:

```bash
docker compose up --build
```

Конфигурация оркестрации находится в `docker-compose.yml`:

| Контейнер        | Сервис     | Описание                                        |
|------------------|------------|-------------------------------------------------|
| `newsmill-queue` | RabbitMQ   | Брокер сообщений (порты `5672`, `15672`)        |
| `newsmill-db`    | PostgreSQL | База данных `newsfeeds` (порт `5432`)           |
| `newsmill-monitor` | Monitor  | FastAPI-сервис (порт `8000`)                    |
| `newsmill-worker`  | Worker   | FastStream-консюмер (без внешних портов)        |

Все сервисы размещены в общей сети `newsmill-network`, используют именованные тома для персистентности данных и перезапускаются при сбоях (`restart: unless-stopped`). Конфигурация загружается из `.env`, при этом хосты `RABBITMQ_HOST=queue` и `DB_HOST=db` автоматически переопределяются на имена контейнеров.

Проверка работоспособности:

- Monitor: `GET http://localhost:8000/health` → `{"status": "ok"}`
- RabbitMQ Management UI: `http://localhost:15672` (guest/guest)

Остановка всех сервисов:

```bash
docker compose down
```

## Статус

- [x] Структура каталогов по сервисам
- [x] `pyproject.toml` с зависимостями
- [x] Реализация Monitor-сервиса
- [x] Реализация Worker-сервиса
- [x] Модели базы данных
- [x] Миграции (Alembic)
- [x] Docker Compose
- [x] Дедупликация GUID в PostgreSQL (`processed_items`, план 001)
- [x] Purge устаревших записей по `DELETE_AFTER` (план 003)
- [x] Harness для агента: `AGENTS.md`, `docs/`, `memory/`, `REPORT.md`