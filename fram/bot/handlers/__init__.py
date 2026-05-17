from aiogram import Router

from fram.bot.handlers import common, media


def setup_handlers() -> Router:
    router = Router()
    router.include_router(common.router)
    router.include_router(media.router)
    return router

