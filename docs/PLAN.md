# light-repost — план MVP

## Фиксируем scope

**Делаем сейчас**
- Автопостинг: пост в TG-канале → пост в одно VK-сообщество
- Только **текст** (community token)
- Всё в `.env` (токены, `CHANNEL_ID`, `VK_GROUP_ID`)
- Docker + VPS — после того как локально заработает
- Удаление в канале → удаление поста в VK (минимальный sync)

**Не делаем сейчас**
- Фото на стену VK: `photos.getWallUploadServer` / альбом недоступны с community token (error 27); user/VK ID — отдельный гемор; doc как файл — бессмысленно. Отложено.
- Связки канал↔сообщество в БД
- Режим «переслал боту»
- Редактирование, видео, media group, подпись со ссылкой

## Стек для mvp-mvp

| Что | Выбор |
|-----|--------|
| Python | 3.14 (в Docker; локально ок и 3.12) |
| Telegram | **aiogram 3** (сразу async — это «нормальный» стиль для ботов) |
| VK | **httpx** + прямые вызовы API (`wall.post`, позже `wall.delete`; фото — TBD) |
| Конфиг | `pydantic-settings` + `.env` |
| Маппинг TG↔VK для удаления | простой **SQLite** (одна таблица) или даже JSON-файл на старте |
| Деплой | бот в Docker Compose; на VPS **Caddy на хосте** (TLS), потом другие приложения на ту же машину |
| Получение апдейтов | **polling** локально / пока без домена → **webhook** на VPS |

Почему не `vk_api`: он sync и тянет лишнее. Для обучения полезнее прямые вызовы через httpx.

Почему сразу async: сильный Ruby-бэкграунд — async в Python ближе к «сервисному» коду, чем sync-скрипт. Sync можно разобрать **параллельно как учебный контраст**, не как основу проекта.

### Polling vs webhook

Посты редкие (хоть раз в неделю) — webhook на VPS логичнее по смыслу: Telegram сам стучится, когда есть апдейт.

Но long polling — это не «долби API каждую секунду»: бот ждёт на `getUpdates` до ~30–50 с, нагрузка крошечная. Для локальной отладки polling проще (не нужны HTTPS, домен, tunnel). Локально webhook не обязателен.

**Решение:** polling для разработки; на VPS — webhook за Caddy.

## Минимальная архитектура

```
light-repost/
  app/
    main.py          # запуск polling
    config.py        # Settings из .env
    handlers/
      channel.py     # channel_post, channel_post_deleted (или service message)
    services/
      vk.py              # wall_post; create_comment (ссылки); позже delete_post / фото
      telegram_format.py # extract_links из entities
      mapping.py         # сохранить tg_msg_id → vk_post_id
  .env.example
  requirements.txt
  Dockerfile         # фаза 2
```

Поток:
1. `channel_post` → текст → `wall.post`
2. Если в entities есть `text_link` → `wall.createComment` с URL (голый `url` остаётся в тексте поста; см. `docs/links.md`)
3. Сохранить `(channel_id, message_id) → (vk_owner_id, vk_post_id)`
4. Удаление поста в канале → найти mapping → `wall.delete`

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

1. Бот отвечает `/start` в личке (проверка, что токен живой) ✅
2. Логировать `channel_post` (только текст) в консоль ✅
3. `wall.post` текста в VK из хендлера ✅
4. Docker (+ деплой на VPS)
5. Переключить получение апдейтов на webhook
6. Ссылки: `text_link` → комментарий VK (`wall.createComment`); голый `url` только в тексте поста. Детали: `docs/links.md`
7. Mapping + попытка delete
8. Фото (если появится нормальный путь без user-token ада)

### Docker (уже в репо)

Локально / отладка на VPS с билдом на месте:

```bash
docker compose up -d --build
docker compose logs -f bot
docker compose down
```

Секреты не в образе: `env_file: .env` в `docker-compose.yml`.

### Деплой (план)

Цепочка «как нормально»:

```text
push в main → CI: tests → build → push GHCR     ← автоматом
                         ↓
         Deploy (когда скажешь):
           • кнопка workflow_dispatch в Actions
           • или локально: ./scripts/deploy.sh
                         ↓
              SSH → compose pull && up -d
                         ↓
    (когда готов поддомен) Caddy + webhook
```

#### 1. CI: образ → GHCR (автоматом)

- **Триггер сборки образа:** push в `main` (не руками на ноуте; на PR образ не пушим).
- **Где в Actions:** не отдельный workflow, а **второй job** в текущем `.github/workflows/ci.yml`:
  1. job `test` — как сейчас (и на `pull_request`, и на `push` в `main`);
  2. job `build` — `needs: test`, условие `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`: login в GHCR → build → push.
- Образ: `ghcr.io/lightalloy/light-repost`, теги `latest` + `sha-<short>` (удобно откатить).
- В `docker-compose.yml`: `image: ghcr.io/lightalloy/light-repost:latest` (+ опционально `build:` для локалки).
- Репо **private** → на VPS один раз `docker login ghcr.io` (PAT с `read:packages`); **public** package — login для pull не обязателен.
- Секреты по-прежнему только в `.env` на сервере, не в образе.
- `permissions: packages: write` у job `build`; пуш через `GITHUB_TOKEN`.

Отдельный workflow — только для **Deploy** (`workflow_dispatch`), чтобы кнопка деплоя не смешивалась с CI.

#### 2. Поддомен

+ ns-серверы у регистратора записала
- DNS: `A` запись, например `repost.example.com` → IP VPS.
- Подождать резолв (`dig` / `ping`).
- Для Telegram webhook нужен именно hostname + HTTPS (не голый IP).

#### 3. Caddy на хосте

- Ставится на VPS **не в Docker** (один proxy на все будущие приложения).
- Caddyfile:

```caddy
repost.example.com {
    reverse_proxy 127.0.0.1:8080
}
```

- TLS Let's Encrypt сам; в файрволе открыты 80/443.
- Бот в compose слушает только `127.0.0.1:8080:8080` (не торчит в интернет напрямую).

#### 4. Выкат на VPS (автодеплой)

Образ на `main` собирается сам; **на сервер — по явной команде** (не после каждого пуша: так спокойнее откатывать и не ловить сюрпризы).

Два одинаковых по сути способа (оба ок):

| | Как |
|--|-----|
| **Кнопка в CI** | workflow `Deploy` с `workflow_dispatch` → SSH на VPS → `docker compose pull && up -d` |
| **Локально** | `./scripts/deploy.sh` (тот же SSH + pull/up) |

На VPS один раз: каталог с `docker-compose.yml` + `.env`, `docker login ghcr.io` (если private), пользователь для деплоя с правом на docker.

В GitHub Secrets (для кнопки): `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` (и при необходимости `DEPLOY_PATH`).

Порядок внедрения:
1. Workflow: test → build/push GHCR на push в `main`.
2. VPS: `.env`, compose под `image:`, login GHCR, первый `pull && up` (polling).
3. Workflow Deploy +/или `scripts/deploy.sh`.
4. Поддомен + Caddy.
5. Код webhook + проверка.

**Не сейчас:** Watchtower, деплой на каждый push без кнопки, k8s, Caddy в compose бота.

### VPS + webhook (инфра, кратко)

- Shared VPS (EU предпочтительнее РФ из‑за исходящего доступа к `api.telegram.org`).
- Caddy на хосте; бот в контейнере; поддомен → proxy на localhost:8080.
- Локально webhook не обязателен; на VPS в итоге webhook.

```text
Internet → :443 Caddy (хост, TLS)
              → 127.0.0.1:8080 bot (aiogram webhook)
```

## Что нужно подготовить до кода

- BotFather → токен
- Бот добавлен **админом канала** с правом читать сообщения
- VK: сообщество, токен с `wall` (community token)
- ID канала (обычно `-100...`) и ID группы VK (число, в API `owner_id = -group_id`)

## Следующий шаг

1. CI: test → build/push GHCR на `main`.
2. VPS: первый pull, polling-проверка.
3. Deploy: кнопка `workflow_dispatch` + скрипт локально.
4. Поддомен + Caddy.
5. Webhook в коде и на сервере.
