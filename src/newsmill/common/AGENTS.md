# AGENTS.md — common

Общий код для Monitor и Worker: правка здесь затрагивает оба сервиса сразу.
Общие правила — в корневом AGENTS.md.

## Ответственность

- `models.py` — `NewsItem` (Pydantic): контракт сообщения очереди.
- `config.py` — `Settings` (`pydantic-settings`), сборка `database_url` из `DB_*`.
- `feeds.py` — `load_newsfeeds()`: парсинг/валидация `newsfeeds.yaml`.
- `db/models.py` — ORM-модели `News` / `Entity`.

## Правила именно здесь

- `NewsItem` — единственный источник контракта
  (`docs/architecture/message-contract.md`). Менять поля — только как
  breaking-change: синхронно оба сервиса + обновить docs.
- Секретов в коде нет — всё через `Settings` из `.env`.
- Не тянуть сюда сервисную логику: здесь граница совместимости сервисов.
