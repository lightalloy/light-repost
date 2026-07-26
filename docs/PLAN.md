# light-repost — план MVP

## Фиксируем scope

**Делаем сейчас**
- Автопостинг: пост в TG-канале → пост в одно VK-сообщество
- Только **текст** (community token)
- Всё в `.env` (токены, `CHANNEL_ID`, `VK_GROUP_ID`)
- Удаление в канале → удаление поста в VK (минимальный sync)
- Docker + VPS — после того как локально заработает

**Не делаем сейчас**
- Фото на стену VK: `photos.getWallUploadServer` / альбом недоступны с community token (error 27); user/VK ID — отдельный гемор; doc как файл — бессмысленно. Отложено.
- Связки канал↔сообщество в БД
- Режим «переслал боту»
- Редактирование, видео, media group, подпись со ссылкой

## Стек для mvp-mvp

| Что | Выбор |
|-----|--------|
| Python | 3.12 |
| Telegram | **aiogram 3** (сразу async — это «нормальный» стиль для ботов) |
| VK | **httpx** + прямые вызовы API (`wall.post`, позже `wall.delete`; фото — TBD) |
| Конфиг | `pydantic-settings` + `.env` |
| Маппинг TG↔VK для удаления | простой **SQLite** (одна таблица) или даже JSON-файл на старте |
| Деплой | Dockerfile + `docker compose` позже |
| Получение апдейтов | **polling** для отладки → **webhook** на VPS |

Почему не `vk_api`: он sync и тянет лишнее. Для обучения полезнее прямые вызовы через httpx.

Почему сразу async: сильный Ruby-бэкграунд — async в Python ближе к «сервисному» коду, чем sync-скрипт. Sync можно разобрать **параллельно как учебный контраст**, не как основу проекта.

### Polling vs webhook

Посты редкие (хоть раз в неделю) — webhook на VPS логичнее по смыслу: Telegram сам стучится, когда есть апдейт.

Но long polling — это не «долби API каждую секунду»: бот ждёт на `getUpdates` до ~30–50 с, нагрузка крошечная. Для локальной отладки polling проще (не нужны HTTPS, домен, nginx/caddy, tunnel).

**Решение:** polling оставляем для разработки; на деплое (Docker + VPS) переключаемся на webhook.

## Минимальная архитектура

```
light-repost/
  app/
    main.py          # запуск polling
    config.py        # Settings из .env
    handlers/
      channel.py     # channel_post, channel_post_deleted (или service message)
    services/
      vk.py              # wall_post (текст); позже delete_post / фото
      mapping.py         # сохранить tg_msg_id → vk_post_id
  .env.example
  requirements.txt
  Dockerfile         # фаза 2
```

Поток:
1. `channel_post` → текст → `wall.post`
2. Сохранить `(channel_id, message_id) → (vk_owner_id, vk_post_id)`
3. Удаление поста в канале → найти mapping → `wall.delete`

Нюанс: Telegram отдаёт удаление через `message` с `deleted` / `Message.is_automatic_forward` — для каналов это `channel_post` с типом service или отдельный апдейт. В Bot API для каналов удаление часто приходит ненадёжно боту-админу. Для mvp честнее: **сначала постинг**, sync удаления — вторым маленьким шагом, когда убедимся, какие апдейты реально приходят.

Практически для удаления: заложить таблицу mapping сразу, а авто-delete включить, когда проверим апдейты. Альтернатива: команда `/delete` reply на пост.

## Учебный трек (Ruby → Python)

На этом проекте естественно пройти:

1. **модули vs классы** — как `module`/`class` в Ruby, но без «всего в объекте»
2. **type hints** — близко к RBS/Sorbet, но встроены
3. **async/await** — аналог идей из Sidekiq/async gem, но на уровне I/O
4. **Pydantic** — как dry-struct / ActiveModel validations для конфига
5. **httpx** — как Faraday, но async-клиент
6. **venv + requirements** — bundler/Gemfile попроще

Контраст sync vs async (для обучения, не для продакшена):
- sync: `requests` + `vk_api`, один скрипт «взял пост → запостил»
- async: aiogram + httpx — то, что оставляем в репо

Можно один раз написать sync-функцию `post_to_vk_sync()` в черновике, потом переписать на async — отличное упражнение.

## Порядок реализации (маленькие шаги)

1. Бот отвечает `/start` в личке (проверка, что токен живой)
2. Логировать `channel_post` (только текст) в консоль
3. `wall.post` текста в VK из хендлера
4. Docker + VPS
5. Переключить получение апдейтов на webhook
6. Ссылки из TG entities → в текст VK (MVP: блок ссылок внизу поста; bold/italic не переносим)
7. Mapping + попытка delete
8. Фото (если появится нормальный путь без user-token ада)


## Что нужно подготовить до кода

- BotFather → токен
- Бот добавлен **админом канала** с правом читать сообщения
- VK: сообщество, токен с `wall` (community token)
- ID канала (обычно `-100...`) и ID группы VK (число, в API `owner_id = -group_id`)

## Следующий шаг

Скелет проекта: `config`, `/start`, хендлер `channel_post` с логом текста, `.env.example`, `requirements.txt`. Без VK ещё — чтобы сначала увидеть апдейты в логах.
