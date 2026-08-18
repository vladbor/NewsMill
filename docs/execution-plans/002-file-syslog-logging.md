# План 002: логирование на диск и в syslog

> Ближайшая доработка. Выполняется по циклу `docs/principles/agent-workflow.md`.

## Метаданные

- **Номер**: 002
- **Версия плана**: 0.1
- **Статус**: запланировано
- **Приоритет**: низкий

## Цель

Ввести единый механизм логирования для Monitor и Worker: запись на диск (файл
с ротацией) и в syslog. Путь к каталогу логов задаётся переменной окружения
`LOGGING_PATH` (в `.env`); каждый сервис пишет в отдельный подкаталог внутри
`LOGGING_PATH` (`<LOG>ING_PATH/monitor`, `.../worker`). Сейчас сервисы используют
только `logging.getLogger(__name__)` без корневой конфигурации: Monitor
(uvicorn) выводит лишь собственные логгеры `uvicorn.*`, INFO `newsmill.monitor.*`
пропадает, Worker (FastStream) пишет только в stdout (см. `known-issues.md`, #8).

## Решение

Общий модуль `common/logging.py` — `configure_logging(service, settings)`,
который навешивает на root-логгер три хендлера:

- **Файл**: `RotatingFileHandler` на `{LOGGING_PATH}/{service}/app.log`
  (5 МБ × 3), каталог создаётся `mkdir(parents=True, exist_ok=True)`.
  В контейнерах `LOGGING_PATH=/logs`, каталог монтируется bind-volume
  `${LOGGING_PATH:-./logs}:/logs` — файлы остаются на хосте.
- **stdout**: `StreamHandler` — `docker compose logs` продолжает работать.
- **syslog**: `logging.handlers.SysLogHandler(address="/dev/log")` с graceful
  fallback: если `/dev/log` отсутствует (macOS, контейнер без демона) — warning
  в консоль, без падения сервиса.

Хендлеры вешаем на root; для `uvicorn`, `uvicorn.error`, `uvicorn.access` и
`faststream` очищаем собственные хендлеры и полагаемся на `propagate` — каждая
запись попадает в stdout, файл и syslog один раз. У uvicorn `log_config=None`,
чтобы он не навешивал свою конфигурацию.

`Settings.logging_path` (`LOGGING_PATH`, по умолчанию `logs`) — в
`common/config.py`. Точки входа: новый `monitor/main.py` (вызов
`configure_logging("monitor")` перед `uvicorn.run`), вызов в
`worker/main.py`. В runtime-образ Docker добавляется `busybox` и
`docker/entrypoint.sh`, запускающий `busybox syslogd` (создаёт `/dev/log`) перед
`exec "$@"`. В `.env.EXAMPLE` строка `LOGGING_PATH=logs` (сейчас там битая
` LOGGING_PAT=logs` с пробелом — исправить).

## Шаги

- [ ] 1. Изучить текущий вывод: uvicorn-логгеры Monitor, FastStream-лого Worker,
      куда пропадают INFO-записи `newsmill.*`.
- [ ] 2. Настроить `Settings`: поле `logging_path` из `LOGGING_PATH` (`common/config.py`).
- [ ] 3. Реализовать `common/logging.py`: файл + stdout + syslog, graceful fallback,
      идемпотентность, чистка хендлеров `uvicorn*`/`faststream`.
- [ ] 4. Точки входа: `monitor/main.py` (uvicorn с `log_config=None`),
      вызов `configure_logging` в `worker/main.py`.
- [ ] 5. Docker: `busybox` + `docker/entrypoint.sh` в runtime-образе; compose —
      `LOGGING_PATH: /logs` + `${LOGGING_PATH:-./logs}:/logs` для monitor и worker;
      `.env.EXAMPLE` → `LOGGING_PATH=logs`; `.gitignore` → `logs/`.
- [ ] 6. Тест `tests/common/test_logging.py`: файл `tmp/monitor/app.log` создаётся,
      код не падает без `/dev/log`.
- [ ] 7. Проверка: `ruff format .`, `ruff check .`, `pytest -v` — зелёные.
- [ ] 8. Обновлены `docs/` (`README.md`, `overview.md`, `known-issues.md` — #8
      отмечается решённой) и `memory/` (ADR-008); пересбор docker — вручную
      пользователем.

## Прогресс

| Дата | Что сделано | Что осталось |
|---|---|---|
| 2026-08-18 | План оформлен, известная проблема #8 зафиксирована | Шаги 1–8 |

## Решение по завершении

- [ ] План 002 реализован; известная проблема #8 из `known-issues.md`
      выводится (отмечается решённой), состояние фиксируется в `memory/`.
- [ ] Пересбор docker (`docker compose up --build`) — ручная операция
      пользователя; проверка файлов `./logs/monitor/app.log` и
      `./logs/worker/app.log`.