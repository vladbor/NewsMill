# Конвенции кода и проверки (coding standards)

Свод стиля и обязательных проверок. Это «территория» норм разработки:

## Python

- Python 3.12, `uv` (установка зависимостей — `uv sync`, новых — `uv add`).
- PEP 8; строка до 88 символов (ruff default); 4 пробела; snake_case для
  файлов/функций/переменных, PascalCase для классов, UPPER_SNAKE_CASE для констант.
- Async везде: `async def` для всех I/O-функций и хендлеров, `await` при вызовах
  внешних API/БД; не смешивать sync/async в горячем пути.
- Тип-хинты в сигнатурах; `from __future__ import annotations`; `X | None`
  вместо `Optional[X]`.
- Pydantic v2: `model_validate()` / `model_dump()`.
- Обработка ошибок: ловить конкретные исключения (`httpx.TimeoutException`,
  `httpx.HTTPStatusError`, `httpx.RequestError`), не голый `except:`.
- Импорты: стандартная библиотека → сторонние → локальные; абсолютные импорты.
- Docstrings для публичных модулей/классов/функций.

## FastAPI (Monitor)

- Хендлеры — только `async def`; группы эндпоинтов — через `APIRouter`.
- Валидация входа — Pydantic-моделями на границе эндпоинта.
- Жизненный цикл — через lifespan: старт/стоп периодической задачи, закрытие
  HTTP-клиента и соединения RabbitMQ.
- Периодический опрос — `asyncio.create_task` + `while True`; интервал из
  `Settings.poll_interval_seconds`.
- Внешние ошибки: 502 — лента/API недоступен, 504 — таймаут; внутренние детали
  клиенту не показывать.

## FastStream / Worker

- `RabbitBroker` + `@broker.subscriber(queue)`; хендлер — `async def`.
- Ошибки десериализации/БД/NER логируются, сообщение ack: malformed-запись не
  роняет воркер.
- Транзакция: новость + сущности коммитятся одним блоком; при ошибке — rollback.

## Тестирование

- pytest + pytest-asyncio; тесты в `tests/`, файлы и функции с префиксом `test_`.
- Мок внешних зависимостей: `httpx.MockTransport`/`respx` для HTTP, мок RabbitMQ
  и БД — без реальных сетевых вызовов в тестах.
- Тестировать и успех, и ошибки (timeout, не-2xx, битый ответ).
- В разработке — фокусные тесты (`pytest tests/... -v`), перед коммитом — `pytest -v`.

## Docker / Compose

- Сервисы `queue`, `db`, `monitor`, `worker` в `docker-compose.yml`; сеть
  `newsmill-network`, named volumes, `restart: unless-stopped`.
- RabbitMQ: `rabbitmq:4-management` (порты 5672/15672).
- PostgreSQL: `postgres:18`.
- Хосты внутри compose переопределяются на имена контейнеров (`queue`, `db`).
- Секреты — только через `.env` / `env_file`, никогда в коде или compose-файле.

## Безопасность

- Секреты, ключи, токены — только в `.env` (в `.gitignore`), не логировать.
- Не передавать клиенту сырые сообщения об ошибках и stack traces.
- Таймауты HTTP-клиента: connect 10s, общий 30s.
