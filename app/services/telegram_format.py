def extract_links(entities: list) -> list[str]:
    """URL из text_link (подпись ≠ ссылка). Обычный url в тексте не трогаем — уйдёт в wall.post как есть."""
    links: list[str] = []
    for e in entities or []:
        if e.type == "text_link" and e.url:
            links.append(e.url)
    return links
