import asyncio

from kwork.types import Project

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.sched.main import get_user_job
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import (
    cached_categories,
    get_parent_category,
    get_category,
    kwork_api,
)
from kwork_parser_bot.schemas.project import ProjectExtended
from kwork_parser_bot.template_engine import render_template


async def notify_about_new_projects(
    chat_id: int,
    user_id: int,
    categories_ids: int | list[int],
    job_id: str = None,
):
    if not user_id:
        user_id = chat_id
    categories = await cached_categories(redis, kwork_api=kwork_api)
    job = get_user_job(user_id, job_id)
    projects: list[Project] = await kwork_api.get_projects(categories_ids)
    new_projects = []
    for p in projects:
        p = ProjectExtended(**p.dict())
        p.category_id = get_category(
            categories, p.parent_category_id, p.category_id
        ).name
        p.parent_category_id = get_parent_category(
            categories, p.parent_category_id
        ).name
        new_projects.append(p)
    rendered = render_template(
        "projects.html",
        job=job,
        projects=new_projects,
    )
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack()
    )
    if len(rendered) < 4096:
        await main_bot.send_message(
            chat_id,
            rendered,
            reply_markup=builder.as_markup(),
            disable_web_page_preview=True,
        )
    else:
        for item in rendered.split("<b>"):
            await asyncio.sleep(2)
            await main_bot.send_message(
                chat_id,
                item,
                reply_markup=builder.as_markup(),
                disable_web_page_preview=True,
            )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        notify_about_new_projects(1070277776, 1070277776, [11], "sched:job:add:1070277776:11:41")
    )
