# AGENTS.md — light-repost

Инструкции для coding-агентов. README — для людей; этот файл — как работать в репо.

## Что это

Бот: текстовый пост в Telegram-канале → пост на стену одного VK-сообщества.
Учебный MVP (Ruby → Python / ai-assisted), не «полный кросспостер».

## Стек

| Слой | Выбор |
|------|--------|
| Python | 3.12+ локально; в Docker — как в `Dockerfile` |
| Telegram | aiogram 3 (async) |
| VK | httpx + прямые вызовы API (`wall.post`; позже `wall.delete`) |
| Конфиг | pydantic-settings + `.env` |
| Тесты | pytest (+ pytest-asyncio) |
| Деплой | Docker Compose → образ `ghcr.io/lightalloy/light-repost`; push в `main` → test → build → deploy |

Не тянуть sync-библиотеки (`requests`, `vk_api`) в основной код без явной просьбы.

## Команды

```bash
# окружение
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # тесты + watchfiles

# запуск
cp .env.example .env   # если ещё нет; секреты не коммитить
python -m app.main

# локальный hot reload (рестарт процесса при изменении app/)
./scripts/dev.sh

# тесты
pytest -q

# docker (локально)
docker compose up -d --build
docker compose logs -f bot
```

Hot reload — только для локальной отладки; в образ/VPS не тащить. Не гонять параллельно второй `python -m app.main` на тот же токен.

После правок логики — прогнать `pytest -q`, если затронуты `app/` или контракты конфига/VK.

## Структура

```
app/
  main.py           # Bot, Dispatcher, polling/webhook, хендлеры
  config.py         # Settings из .env
  services/vk.py    # wall_post (и дальше VK)
tests/              # conftest задаёт env до импорта app.*
docs/               # план, заметки, учебные разборы — не «источник правды» для кода
```

Сейчас хендлеры живут в `main.py`. Выносить в `handlers/` — только когда это следующий шаг плана или явная просьба, не «на будущее».

## Режимы бота

- `BOT_MODE=polling` — локальная отладка.
- `BOT_MODE=webhook` — VPS за Caddy; нужны `WEBHOOK_BASE_URL` и `WEBHOOK_SECRET`.
- `FORCE_IPV4` — только если без него ломается исходящий доступ к Telegram/VK.

Секреты и токены — только в `.env` / GitHub Secrets / env на сервере. В код, логи и коммиты не класть.

## Scope MVP (делать / не делать)

**В scope (по `docs/PLAN.md` / `docs/mvp.md`):**
- текст (`message.text` / `caption`) → `wall.post`
- polling + webhook
- ссылки: `text_link` → комментарий VK (`wall.createComment`); entity `url` не дублируем (уже в тексте поста). План: `docs/links.md`
- mapping TG↔VK + удаление (когда дойдём)
- Docker / GHCR / автодеплой на push в `main` (после test→build); ручной Deploy — запасной путь

**Вне scope, пока не попросили иначе:**
- фото/видео/media group на стену VK (community token + upload — отдельная боль)
- БД связок канал↔сообщество, режим «переслал боту»
- редактирование постов, «красивое» форматирование TG→VK
- Watchtower, k8s
- деплой с PR (только `main` после test→build)

Маленькие шаги: одна фича за раз, без рефакторинга «заодно».

## Стиль кода

- Async-first: aiogram + httpx.
- Type hints на публичных функциях.
- Логирование через `logging`, без `print` в прод-пути.
- Ошибки VK: смотреть JSON `error` в ответе API, не только HTTP-статус (как в `wall_post`).
- `owner_id` для группы VK = `-vk_group_id`.
- Тесты: перед импортом `app.*` нужны env-заглушки (`tests/conftest.py`).
- Не переформатировать чужие файлы и не раздувать diff.

Язык комментариев и пользовательских сообщений бота — русский, как в существующем коде.

## Как помогать автору

Это учебный репо: цель — разобраться, не только «чтобы работало».

- Предпочитать короткие диффы и объяснение «почему», а не большой авторефакторинг.
- Сверяться с `docs/PLAN.md` / `docs/mvp.md` перед новой фичей; детали webhook/links — в `docs/webhook.md`, `docs/links.md`.
- Не коммитить и не пушить без явной просьбы.
- Не трогать `.env` с реальными секретами; для примеров — `.env.example`.

## Definition of done

- Изменение в рамках текущего шага MVP.
- Код и тесты согласованы; `pytest -q` зелёный, если менялась логика.
- Секреты не утекли; `.env` не в коммите.
- README/docs обновлять только если изменился способ запуска, деплоя или контракт env.
