import asyncio
import logging

import socket
from aiohttp import TCPConnector
from aiogram.client.session.aiohttp import AiohttpSession

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings
from app.services.vk import wall_post

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPv4Session(AiohttpSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connector_init["family"] = socket.AF_INET

dp = Dispatcher()

@dp.message(CommandStart())

async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Бот живой.")

@dp.channel_post(F.chat.id == settings.channel_id)

async def on_channel_post(message: Message) -> None:
    text = message.text or message.caption or ""
    logger.info(
        "channel_post chat_id=%s message_id=%s text=%r",
        message.chat.id,
        message.message_id,
        text,
    )
    if not text.strip():
        logger.info("skip - empty text")
        return
    try:
        post_id = await wall_post(text)
        logger.info("reposted to vk post_id=%s", post_id)
    except Exception:
        logger.exception("failed to repost to vk")

async def main() -> None:
    bot = Bot(token=settings.bot_token, session=IPv4Session())
    logger.info("Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
