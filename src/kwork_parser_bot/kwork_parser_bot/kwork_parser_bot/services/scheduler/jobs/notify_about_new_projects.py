import asyncio

from kwork.types import Project

from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.schemas.kwork.project import ProjectExtended
from kwork_parser_bot.services.kwork.base_class import KworkCreds
from kwork_parser_bot.services.kwork.lifetime import get_kwork_api
from kwork_parser_bot.services.redis.lifetime import redis_pool
from kwork_parser_bot.services.scheduler.lifetime import scheduler
from kwork_parser_bot.template_engine import render_template


async def notify_about_new_projects(
    kwork_creds: dict,
    chat_id: int,
    user_id: int,
    categories_ids: int | list[int],
    job_id: str = None,
    send_message: bool = True,
):
    if not user_id:
        user_id = chat_id
    rendered = None
    async with get_kwork_api(KworkCreds(**kwork_creds)) as kwork_api:
        categories = await kwork_api.cached_category(redis_pool)
        projects: list[Project] = await kwork_api.get_projects(categories_ids)
        assert projects, f"kwork_api.get_projects():{projects}"

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
        job = scheduler.get_job(job_id)
        rendered = render_template(
            "projects.html",
            job=job,
            projects=new_projects,
        )
    send_messages = []
    if send_message and len(rendered) < 4096:
        if rendered:
            send_message = await main_bot.send_message(
                chat_id,
                rendered,
                disable_web_page_preview=True,
            )
            send_messages.append(send_message)
        else:
            for item in rendered.split("<b>"):
                await asyncio.sleep(2)
                send_message = await main_bot.send_message(
                    chat_id,
                    item,
                    disable_web_page_preview=True,
                )
                send_messages.append(send_message)
