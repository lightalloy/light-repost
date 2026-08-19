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

запуск

```bash
source .venv/bin/activate
python -m app.main
```

Декоратор — это обёртка вокруг следующего определения (функции или класса). Синтаксис с @ — сахар: Python сразу после чтения «что декорируем» вызывает декоратор.

Правило одно: @что_то относится к ближайшему следующему def / async def / class. Пустые строки между ними не мешают.

```python
@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Бот живой.")
```

аналогично

```python
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Бот живой.")

cmd_start = dp.message(CommandStart())(cmd_start)
```

dp — объект-«шкаф с крючками». Декоратор вешает функцию на крючок. Потом start_polling достаёт апдейт и ищет подходящий крючок.

декоратор — «измени/зарегистрируй эту функцию на этапе объявления»

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print("calling", func.__name__)
        return func(*args, **kwargs)
    return wrapper
@log_call
def hello():
    print("hi")

hello()  # calling hello / hi
```

Настройки:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    bot_token: str
    channel_id: int
    vk_token: str
    vk_group_id: int
    bot_mode: Literal["polling", "webhook"] = "webhook"  # дефолт
    webhook_path: str = "/webhook"
    force_ipv4: bool = False
settings = Settings()
```






