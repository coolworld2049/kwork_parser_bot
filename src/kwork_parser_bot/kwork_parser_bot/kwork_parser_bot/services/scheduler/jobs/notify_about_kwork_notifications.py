import asyncio

from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.kwork.base_class import KworkCreds
from kwork_parser_bot.services.kwork.lifetime import get_user_kwork_api
from kwork_parser_bot.template_engine import render_template


async def notify_about_kwork_notifications(
    kwork_creds: dict,
    chat_id: int,
    user_id: int = None,
):
    async with get_user_kwork_api(KworkCreds(**kwork_creds)) as kwork_api:
        if not user_id:
            user_id = chat_id
        notifications = await kwork_api.get_notifications()
        send_message = await main_bot.send_message(
            chat_id,
            render_template(
                "account_notifications.html",
                data=notifications.__str__(),
            ),
        )


if __name__ == "__main__":
    kwork_creds = KworkCreds(
        login=get_app_settings().KWORK_LOGIN,
        password=get_app_settings().KWORK_PASSWORD,
        phone=get_app_settings().KWORK_PHONE,
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        notify_about_kwork_notifications(kwork_creds.dict(), 1070277776, 1070277776)
    )
