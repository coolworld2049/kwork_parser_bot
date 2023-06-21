import asyncio

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import cached_projects
from kwork_parser_bot.schemas.project import ProjectExtended
from kwork_parser_bot.template_engine import render_template


async def notify_about_new_projects(user_id: int, categories_ids: int | list[int]):
    projects = await cached_projects(
        redis, prefix=str(user_id), categories_ids=categories_ids
    )
    projects = [ProjectExtended(**x.dict()) for x in projects]
    rendered = render_template(
        "projects.html",
        projects=projects,
    )
    if len(rendered) < 4096:
        await main_bot.send_message(user_id, rendered)
    else:
        for item in rendered.split("<b>"):
            await asyncio.sleep(2)
            await main_bot.send_message(user_id, item)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(notify_about_new_projects(1070277776, [11]))
