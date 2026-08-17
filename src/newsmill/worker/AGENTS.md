# AGENTS.md — Worker

FastStream-консюмер очереди RabbitMQ. Общие правила — в корневом AGENTS.md,
здесь только то, что важно именно для воркера.

## Ответственность

- `main.py` — точка входа; `app.py` — `create_app()`: `RabbitBroker` + подписка.
- `ner.py` — SpaCy NER: модель, извлечение, агрегация счётчиков.
- `database.py` — async-движок/сессии SQLAlchemy (`asyncpg`).

## Правила именно здесь

- Хендлер подписан на `RABBITMQ_QUEUE`, десериализует тело в `NewsItem`.
- Модель SpaCy `ru_core_news_md` загружается ОДИН раз (lazy singleton в `ner.py`),
  не перезагружается на каждое сообщение.
- Сущности — из `title` и `text`; лейблы нормализуются к PER/ORG/LOC/MISC.
- `News` + `entities` пишутся одной транзакцией; дубль страхуется `SELECT` по `link`
  + `UNIQUE` (не полагаться только на память монитора).
- Ошибка сообщения логируется и ack: malformed-запись не роняет воркер.
