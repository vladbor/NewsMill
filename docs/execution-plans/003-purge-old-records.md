# План 003: удаление записей БД старше DELETE_AFTER

> Ближайшая доработка. Выполняется по циклу `docs/principles/agent-workflow.md`.

## Метаданные

- **Номер**: 003
- **Версия плана**: 0.1
- **Статус**: запланировано
- **Приоритет**: низкий

## Цель

Ввести процедуру удаления записей базы данных старше `DELETE_AFTER` дней
(значение берётся из `.env`). Удаление касается всех таблиц: `news` и `entities`
(каскадом по FK `ON DELETE CASCADE`) и `processed_items`. Сейчас записи хранятся
бессрочно (см. `known-issues.md`, #9; пункт #7 про рост `processed_items` — этим
планом решается). Запуск — отдельной командой, без усложнения сервисов.

## Решение

- **Конфигурация**: поле `Settings.delete_after: int` из `DELETE_AFTER`
  (по умолчанию `30`, дней); `.env.EXAMPLE` получает строку `DELETE_AFTER=30`.
- **Логика** (`common/db/retention.py`): `purge_old_records(session, days)` —
  в одной транзакции:
  1. `DELETE FROM processed_items WHERE created_at < cutoff`;
  2. `DELETE FROM news WHERE created_at < cutoff` (записи `entities` удаляются
     каскадом по FK).
  Отсечка `cutoff = now() - timedelta(days=days)` по `created_at`. Сначала
  удаляется `processed_items`, чтобы не мешать активному claim-у Monitor'а.
  Сбой БД → исключение, транзакция откатывается, ничего не удаляется
  частично. Функция возвращает количество удалённых строк по каждой таблице.
- **Запуск** — отдельный entrypoint `python -m newsmill.maintenance.purge`:
  `Settings()` → `get_session_factory()` → purge → лог количества удалённых
  строк → `close_engine()`. В Docker — `docker compose run --rm` на том же
  образе (миграции и пересборка не требуются).
- **Миграция не нужна**: схема не меняется.

## Нюансы

- Удаление `processed_items` старше порога может вернуть `guid` «ожившей» после
  долгой паузы ленты в разряд «новых» — он будет повторно опубликован. Дубль
  сохранения всё равно блокируется `UNIQUE` на `news.link` у воркера; для
  учебного проекта приемлемо (отражается в `known-issues.md`/#9).

## Шаги

- [x] 1. Изучить `created_at` в таблицах и каскад `entities.news_id → news.id`.
- [x] 2. Настроить `Settings`: поле `delete_after_days` из `DELETE_AFTER`
      (`common/config.py`); `.env.EXAMPLE` → `DELETE_AFTER=30`.
- [x] 3. Реализовать `common/db/retention.py`: `purge_old_records`, одна
      транзакция, счётчики удалённых строк (`PurgeResult`).
- [x] 4. Entrypoint `newsmill/maintenance/purge.py`; в compose — сервис
      `maintenance` (профиль `tools`): `docker compose run --rm maintenance`.
- [x] 5. Тесты (`tests/common/`) на in-memory SQLite (`aiosqlite`, PRAGMA
      foreign_keys): старые удаляются, свежие остаются, `entities` каскадом,
      сбой БД не удаляет частично, порог и пустая БД.
- [x] 6. Проверка: `ruff format .`, `ruff check .`, `pytest -v` — зелёные.
- [x] 7. Обновлены `docs/` (`README.md` — `DELETE_AFTER` + раздел retention,
      `data-model.md` §7, `known-issues.md` — #7/#9 решены) и `memory/`
      (ADR-008, active-context, progress).
- [x] 8. Ручная проверка пользователем: `docker compose run --rm maintenance` —
      образ собран, контейнер запущен, `INFO:__main__:Purged 0 processed_items
      and 0 news older than 90 days` (DELETE_AFTER=90; все записи младше порога).

## Прогресс

| Дата | Что сделано | Что осталось |
|---|---|---|
| 2026-08-19 | План оформлен, известные проблемы #7/#9 зафиксированы | Шаги 1–8 |
| 2026-08-20 | Шаги 1–7 выполнены: реализация, тесты (7, зелёные), compose, docs, ADR-008 | Шаг 8 — ручная проверка пользователем |
| 2026-08-20 | Ручная проверка: `docker compose run --rm maintenance` → 0/0 (всё моложе 90 дней, DELETE_AFTER=90) | План 003 закрыт |
| 2026-08-20 | Продакшен-запуск оформлен: systemd-юниты `deploy/systemd/`, runbook `docs/architecture/operations.md`, ADR-009 | Открытых пунктов нет |

## Решение по завершении

- [x] План 003 реализован; пункты #7 (решено) и #9 (решено) из
      `known-issues.md` обновлены, состояние фиксируется в `memory/`.
- [x] Ручная проверка purge-команды пользователем на работающей базе
      (0/0 purge при DELETE_AFTER=90 — записи моложе порога).