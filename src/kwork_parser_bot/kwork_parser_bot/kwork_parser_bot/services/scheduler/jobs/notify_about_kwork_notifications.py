from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.services.kwork.base_class import KworkCreds
from kwork_parser_bot.services.kwork.lifetime import get_kwork_api
from kwork_parser_bot.template_engine import render_template


async def notify_about_kwork_notifications(
    kwork_creds: dict,
    chat_id: int,
    user_id: int = None,
    send_message: bool = True,
):
    async with get_kwork_api(KworkCreds(**kwork_creds)) as kwork_api:
        if not user_id:
            user_id = chat_id
        notifications = await kwork_api.get_notifications()
        assert notifications, f"kwork_api.get_notifications():{notifications}"
        if send_message:
            await main_bot.send_message(
                chat_id,
                render_template(
                    "account_notifications.html",
                    data=notifications.__str__(),
                ),
            )
