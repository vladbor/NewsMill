# progress — сделано / осталось

## Задача: 001-dedup-postgres (дедупликация GUID в PostgreSQL)

| Дата | Сделано | Осталось |
|---|---|---|
| 2026-08-18 | Модель `ProcessedItem` (`common/db/models.py`); общий `common/db/session.py` (worker/database.py → re-export); `GuidRegistry.claim` (`monitor/dedup.py`, INSERT ON CONFLICT); `polling.py` на claim (сбой БД → at-least-once); `app.py` без `seen_guids` (lifespan: engine+registry); миграция `18ff3d1326cf` сгенерирована (НЕ применена); тесты обновлены (17 pass, ruff чистый); docs/ и memory/ обновлены | Применить миграцию вручную, пересобрать docker |
| 2026-08-18 | Миграция применена + docker пересобран (пользователь). Найден и исправлен баг: `.returning(ProcessedItem.id)` (нет такого атрибута) → `.returning(ProcessedItem.guid)`; добавлен `tests/monitor/test_dedup.py` (19 tests, ruff чистый). E2e-проверка: после рестарта Monitor `processed_items` 609 → 611 (только новые), дубли не перепубликованы | Нет — план 001 закрыт |

## Задача: 003-purge-old-records (retention — удаление записей старше DELETE_AFTER)

| Дата | Сделано | Осталось |
|---|---|---|
| 2026-08-19 | План оформлен, known-issues #7/#9 зафиксированы (задача была только документной) | — |
| 2026-08-20 | `Settings.delete_after_days` (`DELETE_AFTER`); `common/db/retention.py` (`purge_old_records`, одна транзакция, каскад); entrypoint `newsmill/maintenance/purge.py`; compose-сервис `maintenance` (профиль `tools`); tests на aiosqlite (in-memory SQLite, PRAGMA FKs, 7 тестов); README.md, data-model.md, known-issues #9 → решено, ADR-008, active-context; ruff/pytest зелёные | Ручная проверка пользователем |
| 2026-08-20 | Ручная проверка выполнена: `docker compose run --rm maintenance` → `Purged 0 processed_items and 0 news older than 90 days` (DELETE_AFTER=90, все записи моложе порога) | Нет — план 003 закрыт |

## Следующая задача

- Нет активной доработки. Возможные кандидаты: retry лент (known-issues #6),
  DLX/retry очереди (#3), единый механизм логирования (план 002, #8).

## Предыдущие задачи

- Реорганизация документации (ДЗ №3, Части 1–4) — закрыта 2026-08-17.