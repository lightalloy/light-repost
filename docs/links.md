# Ссылки TG → VK

Кратко: **жирный/курсив как в TG в VK через `wall.post` нормально не переносятся**. Ссылки — да.

**Решение для MVP:**
- текст поста на стену **как есть** (`wall.post`);
- entity типа **`url`** (голый `https://...` в тексте) — **не дублируем**: уже в теле поста, в VK обычно сами становятся кликабельными;
- entity типа **`text_link`** (видимая подпись ≠ URL) — URL в **комментарий** к посту (`wall.createComment`), от имени сообщества.

Не дописывать блок ссылок в `message` поста.

В общем плане — шаг после webhook (`docs/PLAN.md`, п. 6). Код: `app/services/telegram_format.py`, `create_comment` в `vk.py`, хендлер в `main.py`.

## Почему так

| Entity | В тексте поста | В комментарии |
|--------|----------------|---------------|
| `url` | да (сам URL) | нет — дублировать незачем |
| `text_link` | только подпись («тут») | да — иначе VK потеряет URL |

Комментарий вместо «вклеить URL в тело поста» — стена = как в канале; гиперссылки TG не ломаем костылём в `message`.

Альтернатива «блок ссылок внизу `wall.post`» — отвергнута для MVP.

## VK API

| Метод | Роль |
|-------|------|
| `wall.post` | текст поста без дописки |
| `wall.createComment` | URL из `text_link`; `from_group=1`, `owner_id=-vk_group_id`, обязателен `post_id` |

Community token с `wall` обычно хватает. На стене комментарии должны быть **включены**.

## Как сделано

```python
def extract_links(entities: list) -> list[str]:
    # только text_link → entity.url
    ...
```

Хендлер:

```python
post_id = await wall_post(text)
links = extract_links(message.entities or message.caption_entities or [])
if links:
    try:
        await create_comment(post_id, "\n".join(links))
    except Exception:
        logger.exception("failed to comment links on vk post_id=%s", post_id)
```

Ошибка комментария не откатывает пост.

## Тесты / проверка

- `extract_links`: только `text_link`; голый `url` → `[]`; пустые entities → `[]`
- хендлер: без `text_link` — `create_comment` не вызывается; с ним — комментарий с URL
- руками: пост с голым URL (только стена); пост с гиперссылкой-подписью (комментарий от сообщества)

## Что не делать пока

- HTML/Markdown / bold/italic в VK
- встраивание url в строку поста (`Текст (https://...)`)
- дублирование entity `url` в комментарий
- правка комментария при edit поста в TG

## Зависимости

- Нужен `post_id` от `wall.post`.
- Mapping/delete для ссылок не обязателен: с постом уйдут и комментарии.
- Webhook не мешает: тот же хендлер.

### TODO
- класс-клиент VK
