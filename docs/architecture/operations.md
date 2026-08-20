# Операции: запуск и обслуживание (prod)

Базовый runbook по продакшен-запуску NewsMill. Локальная разработка — в
`README.md`; здесь только то, что относится к эксплуатации.

## Запуск стека

Prod-стек поднимается docker-compose'ом (RabbitMQ, PostgreSQL, Monitor,
Worker — с учётом профиля `tools` сервис `maintenance` в `up` не входит):

```bash
cd /path/to/project
docker compose up -d
```

Проверка: `docker compose ps`, `GET http://localhost:8000/health` → `{"status": "ok"}`.

## Retention: purge записей старше DELETE_AFTER

Purge — **однократная batch-задача**, а не демон. Контейнер выполняет
`python -m newsmill.maintenance.purge` и завершается. Взаимодействие:

- **Вручную**: `docker compose run --rm maintenance`.
- **Автоматически (prod)**: systemd-таймер `deploy/systemd/newsmill-purge.timer`
  ежедневно в 03:00 вызывает `newsmill-purge.service`
  (`docker compose run --rm --no-deps maintenance`).

Установка юнитов и диагностика описаны в `deploy/systemd/README.md`.

## Диагностика purge

- Логи: `journalctl -u newsmill-purge` (последний запуск), `sudo systemctl start
  newsmill-purge` для ручного прогона.
- Ошибка подключения к БД → стек не поднят: `docker compose up -d db`, повторить
  ручной запуск.
- Пустой прогон (`Purged 0 processed_items and 0 news`) — норма: все записи
  моложе `DELETE_AFTER` (значение из `.env`).

## Правила эксплуатации

- Миграции не автоприменяются — `alembic upgrade head` вручную, после отказавших
  часов (см. `data-model.md` §6).
- `DELETE_AFTER` и другие настройки — только в `.env`, не в юнитах и не в коде.
- Схема не меняется purge'ом, миграции для него не нужны.