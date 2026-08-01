# NewsMill

Система мониторинга RSS-лент российских новостных агентств с извлечением именованных сущностей (NER).

## Общая информация

NewsMill — это распределённая система, состоящая из двух сервисов:

- **Monitor** — FastAPI-сервис, который периодически (каждые 5 минут) опрашивает RSS-ленты новостных агентств, дедуплицирует записи по `guid` и публикует новые сообщения в очередь RabbitMQ.
- **Worker** — FastStream-сервис, который потребляет сообщения из очереди RabbitMQ, извлекает именованные сущности (PER, ORG, LOC, MISC) с помощью SpaCy и сохраняет результаты в PostgreSQL.

Сервисы общаются через RabbitMQ. Общий код (модели, конфигурация, утилиты) вынесен в пакет `common`.

## Архитектура

```
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
- **PostgreSQL 17** — база данных (в Docker)
- **SQLAlchemy** + **Alembic** — ORM и миграции
- **SpaCy** — NER с русскоязычными моделями
- **httpx** — асинхронный HTTP-клиент
- **PyYAML** — парсинг `newsfeeds.yaml`
- **pydantic-settings** — конфигурация из `.env`
- **ruff** — форматирование и линтинг
- **pytest** + **pytest-asyncio** — тестирование

## Структура каталогов

```
src/
  newsmill/
    __init__.py
    common/          # Общий код (модели, конфигурация, утилиты)
    monitor/         # Monitor-сервис (FastAPI)
    worker/          # Worker-сервис (FastStream)
tests/
  common/            # Тесты общего кода
  monitor/           # Тесты Monitor-сервиса
  worker/            # Тесты Worker-сервиса
pyproject.toml       # Конфигурация проекта и зависимостей
newsfeeds.yaml       # Список RSS-лент
docker-compose.yml   # Оркестрация сервисов (планируется)
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
| `DB_HOST`                | Хост PostgreSQL                                  |
| `DB_PORT`                | Порт PostgreSQL                                  |
| `DB_USER`                | Пользователь PostgreSQL                          |
| `DB_PASS`                | Пароль PostgreSQL                                |
| `DB_NAME`                | Имя базы данных PostgreSQL (`newsfeeds`)         |

## База данных

Схема базы данных `newsfeeds` содержит две таблицы:

### Таблица `news`

| Колонка        | Тип      | Ограничения                  | Описание                          |
|----------------|----------|------------------------------|-----------------------------------|
| `id`           | integer  | PK, autoincrement, NOT NULL  | Первичный ключ                    |
| `source`       | string   | NOT NULL                     | Название агентства                |
| `title`        | string   | NOT NULL                     | Заголовок новости                 |
| `link`         | string   | UNIQUE, NOT NULL             | Ссылка на статью                  |
| `published_at` | datetime | NOT NULL                     | Дата публикации                   |
| `text`         | text     | nullable                     | Описание/содержимое новости       |
| `created_at`   | datetime | NOT NULL, default now        | Время создания записи в БД        |

### Таблица `entities`

| Колонка   | Тип      | Ограничения                          | Описание                          |
|-----------|----------|--------------------------------------|-----------------------------------|
| `id`      | integer  | PK, autoincrement, NOT NULL          | Первичный ключ                    |
| `news_id` | integer  | FK → `news.id`, ON DELETE CASCADE    | Ссылка на новость                 |
| `text`    | string   | NOT NULL                             | Текст сущности                    |
| `label`   | string   | NOT NULL                             | Тип сущности (PER, ORG, LOC, MISC)|
| `count`   | integer  | NOT NULL, default 1                  | Количество вхождений              |

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
- Docker (для RabbitMQ и PostgreSQL)

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

## Статус

- [x] Структура каталогов по сервисам
- [x] `pyproject.toml` с зависимостями
- [x] Реализация Monitor-сервиса
- [x] Реализация Worker-сервиса
- [x] Модели базы данных
- [x] Миграции (Alembic)
- [ ] Docker Compose
