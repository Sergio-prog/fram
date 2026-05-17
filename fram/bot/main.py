import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from fram.bot.config import settings
from fram.bot.handlers import setup_handlers


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("FRAM_BOT_TOKEN is required.")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dispatcher = Dispatcher()
    dispatcher.include_router(setup_handlers())

    if settings.bot_mode == "webhook":
        if not settings.bot_webhook_url:
            raise RuntimeError("FRAM_BOT_WEBHOOK_URL is required for webhook mode.")
        await bot.set_webhook(settings.bot_webhook_url)
        return

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
