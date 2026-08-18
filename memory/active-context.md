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

Пользователь вручную: `alembic upgrade head` (применить миграцию) и
`docker compose up --build` (пересобрать сервисы), затем проверить, что после
рестарта Monitor дубли не публикуются.

## Открытые вопросы

- Нет.