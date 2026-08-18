# Отчёт: harness для агента (ДЗ №3)

## 1. Дерево harness'а

```
Lesson_3/
├── AGENTS.md                          # корневая карта — 71 строка
│   ├── сервисы / поток данных / как запустить
│   └── «куда смотреть дальше» — условия-указатели (docs/, memory/)
├── src/newsmill/
│   ├── common/AGENTS.md               # 19 строк — общие модели/контракт/Settings
│   ├── monitor/AGENTS.md              # 22 строки — эндпоинты, опрос, дедуп
│   └── worker/AGENTS.md               # 20 строк — FastStream, NER, транзакция
├── docs/                              # 10 файлов, стабильное знание
│   ├── architecture/
│   │   ├── data-model.md              # 60  — схема news/entities/processed_items
│   │   ├── message-contract.md        # 39  — контракт обмена NewsItem
│   │   └── overview.md                # 72  — поток данных, карта пакетов
│   ├── design-docs/
│   │   ├── broker-choice.md           # 29  — почему RabbitMQ
│   │   └── core-beliefs.md            # 26  — ключевые принципы проекта
│   ├── execution-plans/
│   │   ├── 001-dedup-postgres.md      # 55  — реализован
│   │   └── 002-file-syslog-logging.md # 79  — запланирован
│   ├── principles/
│   │   ├── agent-workflow.md          # 46  — рабочий цикл агента (memory/)
│   │   └── coding-standards.md        # 59  — конвенции кода
│   └── technical-debt/
│       └── known-issues.md            # 46  — #1–#8, сознательно не чиним
└── memory/                            # 3 файла, изменчивое состояние
    ├── active-context.md              # 21  — над чем работаем прямо сейчас
    ├── progress.md                    # 16  — журнал сделано/осталось
    └── decisions.md                   # 79  — ADR-001…007
```

## 2. Как разделены docs/ и memory/ и почему

`docs/` — стабильное знание о системе, которое меняется редко и описывает факты:
архитектура, контракт сообщения, схема БД, принципы, техдолг, планы. `memory/` —
изменчивое состояние работы, которое агент обязан обновлять сам в конце каждой
задачи: текущая задача, прогресс и журнал решений. Разделение зафиксировано в
ADR-001: правило или факт, встреченный агентов дважды, выносится в `docs/`, а не
повторяется в промпте; в `memory/` попадает только «где мы сейчас» и «что уже
решили». Такое деление решает две проблемы сразу: агент не перечитывает всю
историю (стабильное читается по указателям, состояние — однослойно и дёшево),
а состояние работы не засоряет документацию системы и не дрейфует вместе с ней.
`memory/` — единственное место, которое агент пишет сам, поэтому оно живёт
отдельно от правил, которые агент только читает.

## 3. Что пришлось выкинуть из черновиков агента и почему

Из инструкций (корневой AGENTS.md + `.clinerules/`) было выброшено всё, что было
«территорией», а не «картой»: детали схемы БД, контракт `NewsItem`, команды
запуска конкретных сервисов, историю решений и длинные пересказы правил
(ADR-002: корневой файл разросся до «кладбища старых правил», 100+ строк).
Часть ушла в саму систему — в `docs/` (схема, контракт, принципы, техдолг) и во
вложенные `AGENTS.md` рядом с сервисами (ADR-003), часть удалена как дубль
(ADR-004: `.clinerules/` ликвидирован, его содержимое разнесено по
`docs/principles/` и локальным AGENTS.md). Идея в том, что правила, описывающие
факт системы, гарантированно устаревают при изменении кода — их место рядом с
устаревающей сущностью (в docs/), а не в статичном промпте. Карта должна быть
короткой: условия-указатели вида «перед правкой БД — читай `data-model.md`»,
а не сам слой знаний.

## 4. Доказательство: `memory/` обновлял агент, а не руки

Коммиты, затрагивавшие `memory/`:

```
c01d94f  doc restructure: root AGENTS.md as a map + docs/ + memory/
9a4ee76  Implement persistent GUID dedup in PostgreSQL (plan 001)
f885f26  Fix returning target in GuidRegistry.claim (guid is PK)
```

Дифы ниже содержат факты, которые в момент правок знал только агент (он же их
и зафиксировал): результат его собственной работы, описанная им же произошедшая
в сессии ошибка и наблюдения за ручными действиями пользователя. Стиль записей —
агентский: короткие пункты-сводки, тире-списки, маркер `<No newline at end of
file>` в конце файла.

```
$ git diff c01d94f 9a4ee76 -- memory/active-context.md memory/progress.md
```

```diff
diff --git a/memory/active-context.md b/memory/active-context.md
index 2649b56..89fd5aa 100644
--- a/memory/active-context.md
+++ b/memory/active-context.md
@@ -2,19 +2,20 @@
 
 ## Текущая задача
 
-Реорганизация документации (ДЗ №3, Части 1–4) — **завершена**:
-1. Корневой `AGENTS.md` — карта с условиями-указателями (71 строка).
-2. Вложенные `AGENTS.md` в `src/newsmill/{monitor,worker,common}/`.
-3. `docs/`: план 001 (дедупликация GUID в PostgreSQL), known-issues (добавлен
-   пункт про retry лент), agent-workflow (цикл с memory/), coding-standards.
-4. `memory/`: active-context, progress, decisions (ADR-001…005).
-5. `.clinerules/` удалён, контент разнесён по docs/ и вложенным AGENTS.md.
+План 001 — дедупликация GUID в PostgreSQL — **реализован**:
+- `processed_items` (PK по `guid`) + `GuidRegistry.claim` (атомарный
+  `INSERT ... ON CONFLICT DO NOTHING RETURNING`) в `monitor/dedup.py`.
+- `polling.py`/`app.py` переведены с `seen_guids` на claim; сбой БД → публикация
+  (at-least-once, финальный гейт — `UNIQUE` на `news.link` у воркера).
+- Общие движок/сессии перенесены в `common/db/session.py` (ADR-007).
+- Миграция `18ff3d1326cf` сгенерирована, НЕ применялась.
 
 ## Следующий шаг
 
-Выполнять `docs/execution-plans/001-dedup-postgres.md` — перенос `seen_guids`
-из памяти Monitor в PostgreSQL (снять известную проблему #1).
+Пользователь вручную: `alembic upgrade head` (применить миграцию) и
+`docker compose up --build` (пересобрать сервисы), затем проверить, что после
+рестарта Monitor дубли не публикуются.
 
 ## Открытые вопросы
 
-- Нет.
+- Нет.
diff --git a/memory/progress.md b/memory/progress.md
index 61eb89d..d9d4701 100644
--- a/memory/progress.md
+++ b/memory/progress.md
@@ -1,15 +1,16 @@
 # progress — сделано / осталось
 
-## Задача: реорганизация документации (ДЗ №3, Части 1–4)
+## Задача: 001-dedup-postgres (дедупликация GUID в PostgreSQL)
 
 | Дата | Сделано | Осталось |
 |---|---|---|
-| 2026-08-17 | Корневой AGENTS.md переписан (карта, 71 строка, условия-указатели); вложенные AGENTS.md для monitor/worker/common созданы; план `001-dedup-postgres.md` наполнен; known-issues дополнен (retry лент); agent-workflow обновлён (цикл с memory/, норма «дважды→docs»); coding-standards добавлен; memory/ заведён (active-context, progress, decisions); `.clinerules/` удалён; `.gitignore` очищен от старых записей | Нет — задача закрыта |
+| 2026-08-18 | Модель `ProcessedItem` (`common/db/models.py`); общий `common/db/session.py` (worker/database.py → re-export); `GuidRegistry.claim` (`monitor/dedup.py`, INSERT ON CONFLICT); `polling.py` на claim (сбой БД → at-least-once); `app.py` без `seen_guids` (lifespan: engine+registry); миграция `18ff3d1326cf` сгенерирована (НЕ применена); тесты обновлены (17 pass, ruff чистый); docs/ и memory/ обновлены | Применить миграцию вручную (`alembic upgrade head`), пересобрать docker (`docker compose up --build`), e2e-проверка «рестарт без дублей» |
 
 ## Следующая задача
 
-`docs/execution-plans/001-dedup-postgres.md` — дедупликация GUID в PostgreSQL.
+- Нет активной доработки. Возможные кандидаты: retry лент (known-issues #6),
+  DLX/retry очереди (#3), очистка `processed_items` (#7).
 
 ## Предыдущие задачи
 
-- Журнал начинается с этой реорганизации — ранее задачи не фиксировались.
+- Реорганизация документации (ДЗ №3, Части 1–4) — закрыта 2026-08-17.
```

```
$ git diff 9a4ee76 f885f26 -- memory/
```

```diff
diff --git a/memory/active-context.md b/memory/active-context.md
index 89fd5aa..f9985ab 100644
--- a/memory/active-context.md
+++ b/memory/active-context.md
@@ -12,10 +12,11 @@
 
 ## Следующий шаг
 
-Пользователь вручную: `alembic upgrade head` (применить миграцию) и
-`docker compose up --build` (пересобрать сервисы), затем проверить, что после
-рестарта Monitor дубли не публикуются.
+Пользователь применил миграцию и пересобрал docker. E2e-проверка выполнена:
+после рестарта Monitor `processed_items` 609 → 611 (только новые GUID), дубли
+не перепубликованы. План 001 закрыт.
 
 ## Открытые вопросы
 
-- Нет.
+- Нет. Возможные следующие доработки: retry лент (known-issues #6),
+  DLX/retry очереди (#3), очистка `processed_items` (#7).
diff --git a/memory/progress.md b/memory/progress.md
index d9d4701..7c60062 100644
--- a/memory/progress.md
+++ b/memory/progress.md
@@ -4,7 +4,8 @@
 
 | Дата | Сделано | Осталось |
 |---|---|---|
-| 2026-08-18 | Модель `ProcessedItem` ... | Применить миграцию вручную, пересобрать docker |
+| 2026-08-18 | Модель `ProcessedItem` ... | Применить миграцию вручную, пересобрать docker |
+| 2026-08-18 | Миграция применена + docker пересобран (пользователь). Найден и исправлен баг: `.returning(ProcessedItem.id)` (нет такого атрибута) → `.returning(ProcessedItem.guid)`; добавлен `tests/monitor/test_dedup.py` (19 tests, ruff чистый). E2e: после рестарта Monitor `processed_items` 609 → 611 (только новые), дубли не перепубликованы | Нет — план 001 закрыт |
```

Почему эти записи не могли быть сделаны «руками»: они фиксируют детали работы
агента в его собственной сессии — разбивку реализации плана 001 на шаги, найденный
при e2e-проверке баг `AttributeError: 'ProcessedItem' has no attribute 'id'` и
счётчики `processed_items` 609 → 611 до/после рестарта, недоступные никому, кроме
агента, наблюдавшего эти действия в сессии. Формат и стиль также агентские.

## 5. Какое знание раньше приходилось пересказывать агенту в каждом промпте

Это «где мы сейчас»: какая доработка в работе, что уже сделано, что осталось,
какие шаги пользователь выполнил вручную (миграция, пересборка docker) и какие
решения были приняты (таблица `processed_items` вместо `news.link`, общий
`common/db/session.py`). Каждый новый промпт начинался с пересказа этого
состояния. Теперь оно живёт в `memory/active-context.md` и `memory/progress.md`
(а обоснование решений — в `memory/decisions.md`, ADR-006/007), и корневой
AGENTS.md обязывает агента читать `memory/active-context.md` перед любой работой
и обновлять его после.