# progress — сделано / осталось

## Задача: 001-dedup-postgres (дедупликация GUID в PostgreSQL)

| Дата | Сделано | Осталось |
|---|---|---|
| 2026-08-18 | Модель `ProcessedItem` (`common/db/models.py`); общий `common/db/session.py` (worker/database.py → re-export); `GuidRegistry.claim` (`monitor/dedup.py`, INSERT ON CONFLICT); `polling.py` на claim (сбой БД → at-least-once); `app.py` без `seen_guids` (lifespan: engine+registry); миграция `18ff3d1326cf` сгенерирована (НЕ применена); тесты обновлены (17 pass, ruff чистый); docs/ и memory/ обновлены | Применить миграцию вручную (`alembic upgrade head`), пересобрать docker (`docker compose up --build`), e2e-проверка «рестарт без дублей» |

## Следующая задача

- Нет активной доработки. Возможные кандидаты: retry лент (known-issues #6),
  DLX/retry очереди (#3), очистка `processed_items` (#7).

## Предыдущие задачи

- Реорганизация документации (ДЗ №3, Части 1–4) — закрыта 2026-08-17.