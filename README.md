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
cp .env.example .env
docker compose up -d --build
docker compose logs -f bot
```

### Первый раз на VPS

```bash
sudo mkdir -p /opt/light-repost
# скопировать docker-compose.yml и создать .env на сервере
cd /opt/light-repost
# если пакет GHCR private:
#   echo TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker compose pull
docker compose up -d
docker compose logs -f bot
```

Образ: `ghcr.io/lightalloy/light-repost` (CI на push в `main`: tests → build → push).

### Деплой обновления

После того как в GHCR есть новый `latest`:

- **кнопка:** Actions → Deploy → Run workflow  
  (секреты репо: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`, `DEPLOY_PATH`)
- **локально:**

```bash
export DEPLOY_HOST=… DEPLOY_USER=… DEPLOY_PATH=/opt/light-repost
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Нужен SSH-доступ к VPS (ключ без пароля или ssh-agent).

## Тесты

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```
