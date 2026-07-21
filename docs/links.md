# Ссылки и форматирование TG → VK

Кратко: **жирный/курсив как в TG в VK через `wall.post` нормально не переносятся**. Ссылки — да, и для MVP этого достаточно.

В плане реализации — пункт после webhook (`docs/PLAN.md`, шаг 8).

## Что умеет каждая сторона

**Telegram** отдаёт не только текст, но и `entities` / `caption_entities`: где ссылка, bold, italic, `text_link` (текст ≠ URL) и т.д.

**VK `wall.post`** принимает обычную строку `message`.

- URL в тексте обычно **сам становится кликабельным**
- «красивых» hyperlink как в TG (`слово` → url) у стены почти нет
- bold/italic через API стены по сути нет

Поэтому «Сетка» и подобные кросспостеры чаще всего: **текст как есть + URL явно в тексте** (в конце или рядом), иногда сниппет по ссылке. Не настоящий перенос форматирования TG → VK.

## MVP для ссылок (отдельно от текста)

Идея: вытащить URL из entities и дописать блоком внизу.

```python
def format_for_vk(message: Message) -> str:
    text = message.text or message.caption or ""
    entities = message.entities or message.caption_entities or []

    links: list[str] = []
    for ent in entities:
        if ent.type == "url":
            # URL уже лежит в тексте
            links.append(text[ent.offset : ent.offset + ent.length])
        elif ent.type == "text_link" and ent.url:
            # подпись в TG, url отдельно
            label = text[ent.offset : ent.offset + ent.length]
            links.append(f"{label}: {ent.url}")

    # уникальные, порядок сохранить
    seen: set[str] = set()
    unique_links: list[str] = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)

    if not unique_links:
        return text

    return text.rstrip() + "\n\n" + "\n".join(unique_links)
```

В хендлере:

```python
vk_text = format_for_vk(message)
if not vk_text.strip():
    ...
await wall_post(vk_text)
```

Можно вынести `format_for_vk` в `app/services/telegram_format.py`.

### Нюанс UTF-16

`offset` / `length` в Telegram — в **UTF-16 code units**. Для текста только из BMP (обычный русский/латиница) совпадает с `text[i:j]`. Если появятся эмодзи/редкие символы — понадобится аккуратный слайс (для MVP часто хватает простого среза).

## Что не делать пока

- HTML/Markdown в VK «как parse_mode» — API стены так не работает
- Полный паритет со Сеткой — долго, для обучения рано

## Альтернатива позже

Встраивать url вместо `text_link` в ту же строку: `Текст (https://...)`, а не блок внизу.
