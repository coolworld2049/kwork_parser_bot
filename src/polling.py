import asyncio

from telegram_bot.dispatcher import dp
from telegram_bot.loader import bot
from telegram_bot.lifecycle import startup_bot, shutdown_bot


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await startup_bot(dp)
        await dp.start_polling(bot)
    finally:
        await shutdown_bot(dp)


if __name__ == "__main__":
    asyncio.run(main())
