import logging
import httpx

from app.config import settings
logger = logging.getLogger(__name__)
VK_API = "https://api.vk.com/method"
VK_API_VERSION = "5.199"
async def wall_post(text: str) -> int:
    """Публикует текст на стену сообщества. Возвращает id поста VK."""
    owner_id = -settings.vk_group_id  # группа всегда с минусом
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{VK_API}/wall.post",
            data={
                "owner_id": owner_id,
                "from_group": 1,
                "message": text,
                "access_token": settings.vk_token,
                "v": VK_API_VERSION,
            },
        )
        response.raise_for_status()
        payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"VK error: {payload['error']}")
    post_id = payload["response"]["post_id"]
    logger.info("vk wall.post ok owner_id=%s post_id=%s", owner_id, post_id)
    return post_id

async def create_comment(post_id: int, text: str) -> int:
    """Публикует комментарий к посту. Возвращает id комментария VK."""
    owner_id = -settings.vk_group_id  # группа всегда с минусом
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{VK_API}/wall.createComment",
            data={
                "owner_id": owner_id,
                "post_id": post_id,
                "from_group": 1,
                "message": text,
                "access_token": settings.vk_token,
                "v": VK_API_VERSION,
            },
        )
        response.raise_for_status()
        payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"VK error: {payload['error']}")
    comment_id = payload["response"]["comment_id"]
    logger.info("vk wall.createComment ok owner_id=%s post_id=%s comment_id=%s", owner_id, post_id, comment_id)
    return comment_id
