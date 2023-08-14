import asyncio

from loguru import logger

from telegram_bot.dispatcher import dp
from lifetime import startup_bot, shutdown_bot
from loader import bot


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await startup_bot(dp)
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(e)
    finally:
        await shutdown_bot(dp)


if __name__ == "__main__":
    asyncio.run(main())
