import asyncio
import random

from loguru import logger

from kwork_parser_bot.bot.loader import main_bot
from kwork_parser_bot.services.kwork.schemas import KworkAccount
from kwork_parser_bot.services.kwork.session import get_kwork_api
from kwork_parser_bot.template_engine import render_template


async def notify_about_kwork_notifications(
    kwork_account: dict,
    user_id: int,
    chat_id: int | None,
    send_message: bool = True,
):
    if not chat_id:
        chat_id = user_id
    async with get_kwork_api(KworkAccount(**kwork_account)) as kwork_api:
        await asyncio.sleep(random.randint(5, 30))
        notifications = await kwork_api.get_notifications()
        if send_message and notifications.get("response"):
            await main_bot.send_message(
                chat_id,
                render_template(
                    "account_notif.html",
                    data=notifications.__str__(),
                ),
            )
        logger.info(f"user_id:{user_id}")
        return notifications
