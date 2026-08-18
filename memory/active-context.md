# active-context — над чем работаем прямо сейчас

## Текущая задача

План 001 — дедупликация GUID в PostgreSQL — **реализован**:
- `processed_items` (PK по `guid`) + `GuidRegistry.claim` (атомарный
  `INSERT ... ON CONFLICT DO NOTHING RETURNING`) в `monitor/dedup.py`.
- `polling.py`/`app.py` переведены с `seen_guids` на claim; сбой БД → публикация
  (at-least-once, финальный гейт — `UNIQUE` на `news.link` у воркера).
- Общие движок/сессии перенесены в `common/db/session.py` (ADR-007).
- Миграция `18ff3d1326cf` сгенерирована, НЕ применялась.

## Следующий шаг

Пользователь применил миграцию и пересобрал docker. E2e-проверка выполнена:
после рестарта Monitor `processed_items` 609 → 611 (только новые GUID), дубли
не перепубликованы. План 001 закрыт.

## Открытые вопросы

- Нет. Возможные следующие доработки: retry лент (known-issues #6),
  DLX/retry очереди (#3), очистка `processed_items` (#7).