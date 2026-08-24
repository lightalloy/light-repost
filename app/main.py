import asyncio
import logging

import socket
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings
from app.services.vk import wall_post, create_comment
from app.services.telegram_format import extract_links

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
        links = extract_links(message.entities or message.caption_entities or [])
        if links:
            try:
                await create_comment(post_id, "\n".join(links))
            except Exception:
                logger.exception("failed to comment links on vk post_id=%s", post_id)

    except Exception:
        logger.exception("failed to repost to vk")

async def run_polling(bot: Bot) -> None:
    logger.info("Starting polling...")
    await dp.start_polling(bot)

async def run_webhook(bot: Bot) -> None:
    if not settings.webhook_base_url or not settings.webhook_secret:
        raise ValueError("WEBHOOK_BASE_URL and WEBHOOK_SECRET are required when BOT_MODE=webhook")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    )
    app = web.Application()
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    await start_server(app)

async def start_server(app: web.Application) -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.webhook_host, port=settings.webhook_port)
    await site.start()
    logger.info("Webhook server listening on %s:%s", settings.webhook_host, settings.webhook_port)
    try:
        await asyncio.Event().wait()  # держим процесс живым
    finally:
        await runner.cleanup()

async def on_startup(bot: Bot) -> None:
    url = f"{settings.webhook_base_url.rstrip('/')}{settings.webhook_path}"
    await bot.set_webhook(url, secret_token=settings.webhook_secret)
    logger.info("Webhook set: %s", url)

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()
    logger.info("Webhook deleted")


async def main() -> None:
    bot_kwargs: dict = {"token": settings.bot_token}
    if settings.force_ipv4:
        bot_kwargs["session"] = IPv4Session()
    bot = Bot(**bot_kwargs)
    if settings.bot_mode == "webhook":
        await run_webhook(bot)
    else:
        await run_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
