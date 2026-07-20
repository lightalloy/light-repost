Аналогии с Ruby
Ruby  |	Python
rbenv | asdf
pyenv | asdf / uv (умеет и версии)
bundler + Gemfile | pip + requirements.txt или uv / Poetry
bundle exec | активированный venv (или uv run)
Gemfile.lock | requirements.lock / uv.lock / poetry.lock

uv — сейчас самый близкий «один инструмент вместо rbenv+bundler»: быстро, lockfile, может ставить Python.

Poetry — тоже ок (ближе к Gemfile-философии), но для mvp чуть тяжелее, чем venv+pip.

pyenv — только если хочешь явно жить как с rbenv; ради одного 3.12.3 ставить не обязательно.

настройка системный питон + венв

```bash
cd ~/apps/light-repost
python3 -m venv .venv # Команда создаёт изолированное окружение для проекта — папку .venv со своей копией Python и местом для пакетов.
source .venv/bin/activate   # как вход в bundler-окружение
pip install -U pip # Это обновление самого pip внутри текущего окружения, -U - update, pip обновляет
pip install aiogram httpx pydantic-settings
pip freeze > requirements.txt
```

Дальше всегда: source .venv/bin/activate перед работой (или настроить IDE на .venv).

Создаём изолированное окружение venv
Чтобы либы не ставились в системный Python и не конфликтовали с другими проектами. 

После source в PATH первым оказывается .venv/bin, и python / pip — уже из этого окружения (в промпте часто появляется (.venv)).

Выйти: deactivate



