import asyncio
from contextlib import suppress
from functools import wraps

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger


def message_process(func):
    async def process_error(e, *args, **kwargs):
        message: Message = args[0]
        state: FSMContext = kwargs.get("state")
        bot = state.bot
        message_answer = await message.answer(
            f"<code>{str(e) if e else 'Error'}</code>"
        )
        await asyncio.sleep(1.5)
        with suppress(TelegramBadRequest):
            for m_id in range(
                message_answer.message_id - 1, message_answer.message_id + 1
            ):
                await bot.delete_message(message.from_user.id, m_id)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(e)
            await process_error(e, *args, **kwargs)

    return wrapper
