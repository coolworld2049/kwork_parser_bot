import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, APIRouter
from loguru import logger

from settings import settings
from telegram_bot.dispatcher import dp
from telegram_bot.lifecycle import startup_bot, shutdown_bot
from telegram_bot.loader import bot

app = FastAPI()
router = APIRouter()


@router.post(settings().BOT_TOKEN, include_in_schema=False)
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


@app.on_event("startup")
async def startup():
    if not settings().WEBHOOK_URL:
        raise ValueError(f"WEBHOOK_URL={settings().WEBHOOK_URL}")
    await startup_bot(dp)
    app.include_router(router, prefix="/telegram_bot", tags=["telegram"])
    webhook_info = await bot.get_webhook_info()
    if settings().webhook_url != webhook_info.url:
        await bot.delete_webhook()
        await bot.set_webhook(
            url=settings().webhook_url,
            drop_pending_updates=True,
            max_connections=30,
        )
    logger.info(await bot.get_webhook_info())


@app.on_event("shutdown")
async def shutdown():
    await shutdown_bot(dp)


def main():
    uvicorn.run(app, host=settings().WEB_APP_HOST, port=settings().WEB_APP_PORT)


if __name__ == "__main__":
    main()
