import asyncio

from kwork.types import Project

from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas.project import ProjectExtended
from kwork_parser_bot.services.kwork.base_class import KworkCreds
from kwork_parser_bot.services.kwork.lifetime import get_user_kwork_api
from kwork_parser_bot.services.redis.lifetime import redis_pool
from kwork_parser_bot.services.scheduler.lifetime import scheduler
from kwork_parser_bot.template_engine import render_template


async def notify_about_new_projects(
    kwork_creds: dict,
    chat_id: int,
    user_id: int,
    categories_ids: int | list[int],
    job_id: str = None,
):
    if not user_id:
        user_id = chat_id
    rendered = None
    async with get_user_kwork_api(KworkCreds(**kwork_creds)) as kwork_api:
        categories = await kwork_api.cached_category(redis_pool)
        projects: list[Project] = await kwork_api.get_projects(categories_ids)
        new_projects = []
        for p in projects:
            p = ProjectExtended(**p.dict())
            p.category_id = kwork_api.get_category(
                categories, p.parent_category_id, p.category_id
            ).name
            p.parent_category_id = kwork_api.get_parent_category(
                categories, p.parent_category_id
            ).name
            new_projects.append(p)
        job = scheduler.get_user_job(user_id, job_id)
        rendered = render_template(
            "projects.html",
            job=job,
            projects=new_projects,
        )
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack()
    )
    send_messages = []
    if len(rendered) < 4096:
        if rendered:
            send_message = await main_bot.send_message(
                chat_id,
                rendered,
                reply_markup=builder.as_markup(),
                disable_web_page_preview=True,
            )
            send_messages.append(send_message)
        else:
            for item in rendered.split("<b>"):
                await asyncio.sleep(2)
                send_message = await main_bot.send_message(
                    chat_id,
                    item,
                    reply_markup=builder.as_markup(),
                    disable_web_page_preview=True,
                )
                send_messages.append(send_message)


if __name__ == "__main__":
    kwork_creds = KworkCreds(
        login=get_app_settings().KWORK_LOGIN,
        password=get_app_settings().KWORK_PASSWORD,
        phone_last=get_app_settings().KWORK_PHONE_LAST
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        notify_about_new_projects(
            kwork_creds.dict(), 1070277776, 1070277776, [11], "scheduler:job:add:1070277776:11:41"
        )
    )
