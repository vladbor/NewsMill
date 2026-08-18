# Модель данных: таблицы news/entities, ключи, дедупликация


## 1. Таблица `news` — новость

| Колонка | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | integer | PK, autoincrement, NOT NULL | Первичный ключ |
| `source` | string | NOT NULL | Название агентства (из `newsfeeds.yaml`) |
| `title` | string | NOT NULL | Заголовок новости |
| `link` | string | UNIQUE, NOT NULL | Ссылка на статью |
| `published_at` | datetime (tz) | NOT NULL | Дата публикации |
| `text` | text | nullable | Описание/содержимое новости |
| `created_at` | datetime (tz) | NOT NULL, default `now()` | Время создания записи |

## 2. Таблица `entities` — именованная сущность

| Колонка | Тип | Ограничения | Описание |
|---|---|---|---|
| `id` | integer | PK, autoincrement, NOT NULL | Первичный ключ |
| `news_id` | integer | FK → `news.id`, ON DELETE CASCADE, NOT NULL | Ссылка на новость |
| `text` | string | NOT NULL | Текст сущности (title case) |
| `label` | string | NOT NULL | Тип: PER, ORG, LOC, MISC |
| `count` | integer | NOT NULL, default 1 | Число вхождений в новости |

## 3. Связи

- `news` 1 — N `entities` (одна новость, много сущностей).
- Каскад удаления: удаление новости удаляет её сущности (`ondelete="CASCADE"` +
  `cascade="all, delete-orphan"` в ORM-relationship).

## 4. Таблица `processed_items` — реестр обработанных GUID (Monitor)

Ключ дедупликации Monitor: guid помечается ДО публикации и переживает рестарт.

| Колонка | Тип | Ограничения | Описание |
|---|---|---|---|
| `guid` | string | PK | Уникальный идентификатор новости (из RSS, fallback — link) |
| `created_at` | datetime (tz) | NOT NULL, default `now()` | Момент первого claim |

Запись добавляется атомарно: `INSERT ... ON CONFLICT (guid) DO NOTHING
RETURNING` (`monitor/dedup.py`), поэтому гонок «проверил-вставил» нет. Строка
создаётся только если GUID ещё не обработан.

## 5. Дедупликация

Два эшелона защиты от дублей:

1. **Monitor — до брокера**: таблица `processed_items`. Перед публикацией GUID
   атомарно claim-ится (`GuidRegistry.claim`); уже обработанный GUID не
   публикуется повторно. При недоступности БД claim падает — запись всё равно
   публикуется (at-least-once; единственный финальный гейт — `UNIQUE` на `link`).
2. **Worker — у БД**: перед вставкой выполняется `SELECT news WHERE link = …`;
   при наличии записи новость пропускается. Страховка через `UNIQUE` на `link`.

## 6. Миграции (Alembic)

- Миграции объявлены в `migrations/versions/`, применяются **только вручную**
  (`alembic upgrade head`), никогда не автоприменяются.
- Генерация из ORM: `uv run alembic revision --autogenerate -m "описание"`.
- Строка подключения собирается в `migrations/env.py` из `DB_*` (asyncpg).