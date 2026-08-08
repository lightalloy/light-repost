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

```bash
cp .env.example .env   # если ещё нет
docker compose up -d --build
docker compose logs -f bot
```

## Тесты

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```
