from kwork import Kwork

from kwork_parser_bot.bots.main_bot.loader import main_bot


async def notify_about_kwork_notifications(
    kwork_api: Kwork,
    chat_id: int,
    user_id: int = None,
):
    if not user_id:
        user_id = chat_id
    notifications = await kwork_api.get_notifications()
    await main_bot.send_message(chat_id, notifications.__str__())
