import asyncio

from loguru import logger

from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.services.kwork import kwork_api
from kwork_parser_bot.template_engine import render_template


async def notify_about_kwork_notifications(
    chat_id: int,
    user_id: int = None,
):
    logger.debug(f"func run:{__file__}")
    if not user_id:
        user_id = chat_id
    notifications = await kwork_api.get_notifications()
    send_message = await main_bot.send_message(
        chat_id,
        render_template(
            "notification.html",
            data=notifications.__str__(),
        ),
    )
    logger.debug(f"func completed:{__file__}, send_messages: {send_message.message_id}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(notify_about_kwork_notifications(1070277776, 1070277776))
