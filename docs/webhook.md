# Webhook — план внедрения

Хендлеры (`/start`, `channel_post` → VK) **не меняем**. Меняется только способ получения апдейтов: polling ↔ webhook.

## Схема

```text
Локально (BOT_MODE=polling):
  python -m app.main  →  getUpdates  →  api.telegram.org

VPS (BOT_MODE=webhook):
  Telegram  →  HTTPS  →  Caddy :443  →  127.0.0.1:8080  →  aiohttp /webhook  →  dp  →  хендлеры
```

Caddy уже на хосте; path webhook: **`/webhook`**.

---

## Auth — как это устроено

Это **не** логин пользователя. Два слоя:

1. **HTTPS** — Telegram шлёт webhook только на `https://…` (Caddy + Let's Encrypt).
2. **`secret_token`** — при `setWebhook` передаёшь случайную строку. Telegram добавляет заголовок:
   ```http
   X-Telegram-Bot-Api-Secret-Token: <твой secret>
   ```
   `SimpleRequestHandler(..., secret_token=…)` в aiogram отбрасывает чужие POST.

`BOT_TOKEN` в URL webhook **не** кладём. Токен — для **исходящих** вызовов API (`setWebhook`, ответы в чат).

---

## Регистрация webhook

**Отдельно да.** Не в BotFather, не в Caddy.

| Режим | Что делать |
|-------|------------|
| polling | `start_polling()` — регистрация не нужна |
| webhook | при **старте** приложения: `await bot.set_webhook(url, secret_token=…)` |

При остановке контейнера (опционально, но полезно): `await bot.delete_webhook()`.

**Один `BOT_TOKEN` = один режим.** Нельзя одновременно polling локально и webhook на VPS с одним токеном. Перед деплоем webhook локальный polling остановить.

Проверка после деплоя:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

---

## Переменные окружения

### `app/config.py`

| Поле | Локально | VPS |
|------|----------|-----|
| `bot_mode` | `polling` (default) | `webhook` |
| `webhook_base_url` | — | `https://repost.твой-домен` (без trailing slash) |
| `webhook_path` | `/webhook` (default) | `/webhook` |
| `webhook_secret` | — | длинная случайная строка (32+ символов) |
| `webhook_host` | — | `0.0.0.0` |
| `webhook_port` | — | `8080` |
| `force_ipv4` | `true` если IPv6 ломает TG локально | обычно не нужен |

Тип: `bot_mode: Literal["polling", "webhook"]`, default `"polling"`.

В webhook-режиме валидировать, что заданы `webhook_base_url` и `webhook_secret`.

Pydantic env: `WEBHOOK_BASE_URL`, `BOT_MODE`, …

### `.env.example`

```env
# --- polling (local default) ---
BOT_MODE=polling
# FORCE_IPV4=true

# --- webhook (VPS) ---
# BOT_MODE=webhook
# WEBHOOK_BASE_URL=https://repost.example.com
# WEBHOOK_SECRET=change-me-long-random-string
# WEBHOOK_HOST=0.0.0.0
# WEBHOOK_PORT=8080
```

На VPS в `.env` (не в git) — только webhook-блок + существующие `BOT_TOKEN`, `CHANNEL_ID`, VK.

---

## Изменения в коде

### 1. `app/main.py`

Разделить запуск (хендлеры и `dp` оставить как есть):

```python
async def run_polling(bot: Bot) -> None:
    logger.info("Starting polling...")
    await dp.start_polling(bot)

async def run_webhook(bot: Bot) -> None:
    # startup: set_webhook
    # aiohttp Application
    # SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=settings.webhook_secret)
    #   .register(app, path=settings.webhook_path)
    # setup_application(app, dp, bot=bot)
    # shutdown: delete_webhook
    # web.run_app(app, host=settings.webhook_host, port=settings.webhook_port)
```

Ориентир: [aiogram webhook docs](https://docs.aiogram.dev/en/latest/dispatcher/webhook.html), пример `echo_bot_webhook.py`.

`main()`:

```python
bot = Bot(...)  # IPv4Session только если settings.force_ipv4
if settings.bot_mode == "webhook":
    await run_webhook(bot)
else:
    await run_polling(bot)
```

Startup hook (webhook):

```python
async def on_startup(bot: Bot) -> None:
    url = f"{settings.webhook_base_url.rstrip('/')}{settings.webhook_path}"
    await bot.set_webhook(url, secret_token=settings.webhook_secret)
    logger.info("Webhook set: %s", url)
```

### 2. `docker-compose.yml`

Проброс порта только на localhost (Caddy снаружи):

```yaml
services:
  bot:
    image: ghcr.io/lightalloy/light-repost:latest
    build: .
    env_file: .env
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
```

### 3. Caddy (на хосте, уже есть)

```caddy
repost.example.com {
    reverse_proxy 127.0.0.1:8080
}
```

Path `/webhook` проксируется как есть — отдельный блок в Caddy не нужен.

---

## Порядок внедрения

1. `config.py` — поля + default `polling`
2. `main.py` — `run_polling` / `run_webhook`
3. `docker-compose.yml` — ports
4. `.env.example`, README (кратко)
5. Локально проверить, что `BOT_MODE=polling` (или без переменной) — как раньше
6. Merge → CI build → на VPS дописать `.env` (webhook) → обновить compose → Deploy
7. Остановить локальный polling с тем же токеном
8. Проверка (таблица ниже)

---

## Проверка

| Шаг | Действие |
|-----|----------|
| Webhook зарегистрирован | `getWebhookInfo` → правильный `url` |
| TLS | `curl -I https://repost.домен/` (502 до запуска бота — ок) |
| Логи контейнера | `docker compose logs -f bot` → «Webhook set: …» |
| Бот | `/start` в личке |
| Репост | текст в канал → пост в VK |

---

## Polling локально — оставляем?

**Да.** Default `BOT_MODE=polling`:

- без домена и Caddy;
- те же хендлеры;
- для редких постов long poll почти ничего не жрёт.

Webhook на VPS — когда есть поддомен + Caddy. Tunnel для локального webhook не нужен.

---

## Что не в этом шаге

- healthcheck `/health`
- автодеплой при смене режима (Deploy как сейчас)
- вынос хендлеров в `app/handlers/` (опционально)

---

## Ссылки

- [PLAN.md](./PLAN.md) — инфра VPS, Caddy, GHCR, Deploy
- [aiogram webhook](https://docs.aiogram.dev/en/latest/dispatcher/webhook.html)
