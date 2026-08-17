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

## 4. Дедупликация

Два эшелона защиты от дублей:

1. **Monitor — до брокера**: `seen_guids` (множество GUID в памяти приложения).
   Запись уже обработанная по `guid` не публикуется в очередь
   (`monitor/polling.py`). Заметка: множество живёт только в рантайме процесса.
2. **Worker — у БД**: перед вставкой выполняется `SELECT news WHERE link = …`;
   при наличии записи новость пропускается. Страховка через `UNIQUE` на `link`.

## 5. Миграции (Alembic)

- Миграции объявлены в `migrations/versions/`, применяются **только вручную**
  (`alembic upgrade head`), никогда не автоприменяются.
- Генерация из ORM: `uv run alembic revision --autogenerate -m "описание"`.
- Строка подключения собирается в `migrations/env.py` из `DB_*` (asyncpg).