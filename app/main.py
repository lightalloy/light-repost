import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
dp = Dispatcher()

@dp.message(CommandStart())

async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Бот живой.")

async def main() -> None:
    bot = Bot(token=settings.bot_token)
    logger.info("Starting polling...")
    await dp.start_polling(bot)

@dp.channel_post(F.chat.id == settings.channel_id)
async def on_channel_post(message: Message) -> None:
    text = message.text or message.caption or ""
    logger.info(
        "channel_post chat_id=%s message_id=%s text=%r",
        message.chat.id,
        message.message_id,
        text,
    )

if __name__ == "__main__":
    asyncio.run(main())

