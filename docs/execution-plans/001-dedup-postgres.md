# План 001: дедупликация GUID в PostgreSQL

> Ближайшая доработка. Выполняется по циклу `docs/principles/agent-workflow.md`.

## Метаданные

- **Номер**: 001
- **Версия плана**: 1.0
- **Статус**: реализовано (ждёт применения миграции вручную)
- **Приоритет**: средний

## Цель

Убрать повторную публикацию дублей после рестарта Monitor. Раньше `seen_guids`
хранился в памяти процесса (`monitor/app.py`, `MonitorState`) и сбрасывался при
перезапуске: GUID, накопленные за время простоя, считались «новыми» и снова
публиковались в очередь.

## Решение

Признак обработки хранится в отдельной таблице `processed_items` (PK по `guid`),
а не в подзапросе к `news.link`: метка создаётся ДО публикации и не путает
«опубликовано» с «сохранено воркером». Claim — атомарный
`INSERT ... ON CONFLICT (guid) DO NOTHING RETURNING` (`monitor/dedup.py`).
При недоступности БД запись публикуется (at-least-once; финальный гейт —
`UNIQUE` на `news.link` у воркера). Обоснование — `memory/decisions.md` ADR-006.

## Шаги

- [x] 1. Изучить текущее поведение: `monitor/polling.py`, `MonitorState`, миграции.
- [x] 2. Выбрать хранилище: таблица `processed_items` (PK по `guid`). ADR-006.
- [x] 3. Проверить: контракт сообщения (`common/models.py`) не менялся;
      изменения в `common/` — только инфраструктура (модель, сессии).
- [x] 4. Реализация: `GuidRegistry.claim` вместо `seen_guids`; lifespan создаёт
      engine + registry (`monitor/app.py`, `monitor/polling.py`).
- [x] 5. Миграция сгенерирована: `18ff3d1326cf_add_processed_items_table.py`.
      НЕ применялась (`alembic upgrade` — вручную пользователем).
- [x] 6. Тесты: dedup через claim; сбой claim → публикация (at-least-once).
- [x] 7. Проверка: `ruff format .`, `ruff check .`, `pytest -v` — зелёные.
- [x] 8. Обновлены `docs/` (`data-model.md`, `overview.md`, `known-issues.md`,
      `README.md`, `monitor/AGENTS.md`) и `memory/` (ADR-006, ADR-007).

## Прогресс

| Дата | Что сделано | Что осталось |
|---|---|---|
| 2026-08-17 | План оформлен, задача зафиксирована | Шаги 1–8 |
| 2026-08-18 | Реализовано: модель, session-модуль, GuidRegistry, polling, app, tests, миграция, docs, memory | Применить миграцию пользователем (`alembic upgrade head`) и пересобрать docker |

## Решение по завершении

- [x] План 001 реализован; известная проблема #1 выведена из `known-issues.md`
      (отмечена решённой), состояние зафиксировано в `memory/`.
- [ ] Применить миграцию (`alembic upgrade head`) и пересобрать docker
      (`docker compose up --build`) — ручная операция пользователя.
