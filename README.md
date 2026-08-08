# light-repost

Репост текстовых постов из Telegram-канала в сообщество VK.

## Локально

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заполнить токены и ID
python -m app.main
```

Нужны: бот — админ канала; VK community token с правом `wall`.

## Docker

Локально (сборка на машине):

```bash
cp .env.example .env   # если ещё нет
docker compose up -d --build
docker compose logs -f bot
```

На VPS образ берётся из GHCR (`ghcr.io/lightalloy/light-repost`): push в `main` → CI тесты → build/push. Дальше на сервере: `docker compose pull && docker compose up -d`.

## Тесты

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```
