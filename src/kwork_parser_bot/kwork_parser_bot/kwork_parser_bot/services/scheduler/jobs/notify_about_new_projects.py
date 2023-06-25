from loguru import logger

from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.schemas.kwork.project import ProjectExtended
from kwork_parser_bot.services.kwork.kwork.types import Project
from kwork_parser_bot.services.kwork.lifetime import get_kwork_api
from kwork_parser_bot.services.kwork.main import KworkCreds
from kwork_parser_bot.services.scheduler.lifetime import scheduler
from kwork_parser_bot.template_engine import render_template


async def notify_about_new_projects(
    kwork_creds: dict,
    user_id: int,
    chat_id: int | None,
    categories_ids: int | list[int],
    job_id: str = None,
    send_message: bool = True,
):
    if not chat_id:
        chat_id = user_id
    rendered = None
    job = scheduler.get_job(job_id)
    projects = []
    async with get_kwork_api(KworkCreds(**kwork_creds)) as api:
        old_projects: list[Project] = await api.cached_projects(user_id, categories_ids)
        new_projects: list[Project] = await api.get_projects(categories_ids)
        if old_projects:
            projects_diff_ids = set([x.id for x in new_projects]).difference(
                set([x.id for x in old_projects])
            )
            new_projects: list[Project | None] = list(
                filter(
                    lambda x: x
                    if x.id in projects_diff_ids and not x.is_viewed
                    else None,
                    new_projects,
                )
            )
            if not len(new_projects) > 0:
                logger.debug(
                    f"old_projects:{len(old_projects)},"
                    f" new_projects:{len(new_projects)},"
                )
                return None
        await api.cached_projects(user_id, categories_ids, new_projects, update=True)
        category = await api.cached_category()
        for p in new_projects:
            p = ProjectExtended(**p.dict())
            p.category_id = api.get_category(
                category, p.parent_category_id, p.category_id
            ).name
            p.parent_category_id = api.get_parent_category(
                category, p.parent_category_id
            ).name
            projects.append(p)
    rendered = render_template(
        "projects.html",
        job=job,
        projects=projects,
    )
    await main_bot.send_message(
        chat_id,
        rendered,
        disable_web_page_preview=True,
    )
    return projects
