# Продакшен-запуск purge через systemd timer

Юниты запускают однократную задачу очистки записей БД старше `DELETE_AFTER`
(см. `docs/architecture/operations.md`). Задача выполняется в контейнере того же
образа, что и сервисы, без поднятия зависимостей (`--no-deps`).

## Установка

1. Скопируйте юниты в системный каталог systemd:

   ```bash
   sudo cp newsmill-purge.service newsmill-purge.timer /etc/systemd/system/
   ```

2. В `/etc/systemd/system/newsmill-purge.service` замените плейсхолдеры:

   - `Documentation=file:///REPLACE/PROJECT/...` — путь к репозиторию;
   - `WorkingDirectory=/REPLACE/PROJECT` — каталог с `docker-compose.yml` и
     `.env` (compose читает `.env` отсюда).

   Убедитесь, что `docker compose` доступен как плагин (`/usr/bin/docker`).

3. Перезагрузите systemd и включите таймер:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now newsmill-purge.timer
   ```

## Проверка

```bash
systemctl list-timers newsmill-purge.timer   # следующая активация
sudo systemctl start newsmill-purge.service  # ручной запуск
sudo journalctl -u newsmill-purge            # логи задачи (journald)
```

Ожидаемый лог успешного запуска:

```
INFO:__main__:Purged N processed_items and M news older than <days> days
```

## Нюансы

- **Стек должен быть поднят**: `--no-deps` не поднимает `db`. Если контейнеры
  не запущены, задача упадёт по подключению к БД. Перед установкой убедитесь,
  что стек работает: `docker compose up -d`.
- **Расписание**: ежедневно в 03:00 (`OnCalendar=*-*-* 03:00:00`).
  `Persistent=true` — после простоя хоста в момент срабатывания задача
  выполнится при ближайшей загрузке. `RandomizedDelaySec=600` размывает старт,
  чтобы все хосты не «топали» одновременно.
- **Идемпотентность**: повторные запуски удаляют 0 строк — безопасно.
- **Значение `DELETE_AFTER`** берётся из `.env` (читается compose'ом из
  `WorkingDirectory`). Менять — в `.env`, не в юнитах.
- **Права**: юнит выполняется от root и читает `.env` (пароль БД). Ограничьте
  права на `.env` (`chmod 600`) и не коммитьте его.
- **Профиль `tools`**: сервис `maintenance` не запускается командой
  `docker compose up`, поэтому не конфликтует с основным стеком.