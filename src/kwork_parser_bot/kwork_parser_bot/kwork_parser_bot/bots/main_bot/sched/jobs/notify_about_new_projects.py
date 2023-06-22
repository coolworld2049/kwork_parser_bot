import asyncio

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import (
    cached_projects,
    cached_categories,
    get_parent_category,
    get_category,
)
from kwork_parser_bot.schemas.project import ProjectExtended
from kwork_parser_bot.template_engine import render_template


async def notify_about_new_projects(user_id: int, categories_ids: int | list[int]):
    categories = await cached_categories(redis)
    projects = await cached_projects(
        redis, prefix=str(user_id), categories_ids=categories_ids
    )
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
        projects=new_projects,
    )
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack()
    )
    if len(rendered) < 4096:
        await main_bot.send_message(
            user_id,
            rendered,
            reply_markup=builder.as_markup(),
        )
    else:
        for item in rendered.split("<b>"):
            await asyncio.sleep(2)
            await main_bot.send_message(user_id, item, reply_markup=builder.as_markup())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(notify_about_new_projects(1070277776, [11]))
