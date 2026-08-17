# active-context — над чем работаем прямо сейчас

## Текущая задача

Реорганизация документации (ДЗ №3, Части 1–4) — **завершена**:
1. Корневой `AGENTS.md` — карта с условиями-указателями (71 строка).
2. Вложенные `AGENTS.md` в `src/newsmill/{monitor,worker,common}/`.
3. `docs/`: план 001 (дедупликация GUID в PostgreSQL), known-issues (добавлен
   пункт про retry лент), agent-workflow (цикл с memory/), coding-standards.
4. `memory/`: active-context, progress, decisions (ADR-001…005).
5. `.clinerules/` удалён, контент разнесён по docs/ и вложенным AGENTS.md.

## Следующий шаг

Выполнять `docs/execution-plans/001-dedup-postgres.md` — перенос `seen_guids`
из памяти Monitor в PostgreSQL (снять известную проблему #1).

## Открытые вопросы

- Нет.
