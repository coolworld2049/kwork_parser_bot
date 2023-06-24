import asyncio
import html
from functools import wraps


def message_process(func):
    async def process_error(e, *args, **kwargs):
        message = args[0]
        bot = kwargs.get("state").bot
        message_answer = await message.answer(
            f"Error <code>{html.escape(e.args.__str__())}</code>. Try again"
        )
        await asyncio.sleep(1.5)
        await bot.delete_message(message.from_user.id, message_answer.message_id)

    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                await process_error(e, *args, **kwargs)

        return wrapper
    else:

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(process_error(e, *args, **kwargs))

        return wrapper
