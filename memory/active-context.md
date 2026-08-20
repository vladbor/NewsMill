# active-context — над чем работаем прямо сейчас

## Текущая задача

План 003 — retention (удаление записей старше `DELETE_AFTER`) — **реализован**:
- `Settings.delete_after_days` (`DELETE_AFTER`, default 30) + `.env.EXAMPLE`.
- `common/db/retention.py`: `purge_old_records(session, days)` — одна
  транзакция, `processed_items` → `news` (сущности каскадом), `PurgeResult`.
- Entrypoint `python -m newsmill.maintenance.purge`
  (`newsmill/maintenance/purge.py`), в Docker — сервис `maintenance` с
  профилем `tools`: `docker compose run --rm maintenance`.
- Тесты `tests/common/` на in-memory SQLite (`aiosqlite`, PRAGMA FKs):
  каскад, атомарность (rollback при сбое) — 7 тестов.
- docs/ и memory/ обновлены (ADR-008, known-issues #7/#9 → решено).

## Следующий шаг

План 003 закрыт: ручная проверка выполнена (`docker compose run --rm maintenance`
→ `Purged 0 processed_items and 0 news older than 90 days`; `DELETE_AFTER=90` в
`.env`, все записи младше порога). Активной доработки нет.

## Открытые вопросы

- Нет. Возможные следующие доработки: retry лент (known-issues #6),
  DLX/retry очереди (#3), единый механизм логирования (план 002, #8).