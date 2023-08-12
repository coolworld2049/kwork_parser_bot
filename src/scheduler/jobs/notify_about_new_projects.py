import asyncio

from aredis_om import NotFoundError
from loguru import logger
from redis.exceptions import ResponseError

from kwork_api.api.types import Project
from kwork_api.kwork import get_kwork_api
from kwork_api.models import (
    KworkProject,
    KworkAccount,
    Blacklist,
)
from telegram_bot.loader import bot, scheduler, redis_pool
from template_engine import render_template


async def notify_about_new_projects(
    kwork_account: dict,
    user_id: int,
    chat_id: int | None,
    subcategories_ids: int | list[int],
    job_id: str = None,
    send_message: bool = True,
    ex: int = 43200,
):
    if not chat_id:
        chat_id = user_id
    rendered = None
    job = scheduler.get_job(job_id) if job_id else None
    projects = []
    old_projects = []
    try:
        blacklist: Blacklist = await Blacklist.find(
            Blacklist.telegram_user_id == user_id
        ).first()
    except* (NotFoundError, ResponseError) as e:
        blacklist = Blacklist(telegram_user_id=user_id)

    async with get_kwork_api(KworkAccount(**kwork_account)) as api:
        cached_projects = await api.cached_projects(
            redis_pool, subcategories_ids, ex=ex
        )
        if cached_projects:
            old_projects = cached_projects
        new_projects: list[Project] = await api.get_projects(subcategories_ids)

        def log_msg(*args):
            return (
                f"user_id:{user_id}"
                f" job_id:{job.id if job else None}"
                f" job_name:{job.name if job else None}"
                f" categories_ids:{subcategories_ids}"
                f" old_projects:{args[0]},"
                f" new_projects:{args[1]},"
            )

        if old_projects:
            projects_diff_ids = set([x.id for x in new_projects]).difference(
                set([x.id for x in old_projects])
            )
            new_projects: list[Project | None] = list(
                filter(
                    lambda x: Project(id=x.id, username=x.username)
                    if x.id in projects_diff_ids
                    and x.username not in blacklist.usernames
                    else None,
                    new_projects,
                )
            )
            if not len(new_projects) > 0:
                logger.info(log_msg(len(old_projects), len(new_projects)))
                return None
        logger.info(log_msg(len(old_projects), len(new_projects)))
        old_projects.extend(new_projects)
        await api.cached_projects(
            redis_pool, subcategories_ids, old_projects, update=True, ex=ex
        )
        category = await api.cached_category(redis_pool)
        for p in new_projects:
            p = KworkProject(**p.dict())
            p.description = p.description.replace("<br>", "\n").replace("</br>", "\n")
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
    if send_message:
        if len(rendered) >= 4096:
            for r in rendered.split("\n\n"):
                await asyncio.sleep(1.1)
                try:
                    await bot.send_message(
                        chat_id,
                        r,
                        disable_web_page_preview=True,
                    )
                except Exception as e:
                    logger.error(e)
        else:
            try:
                await bot.send_message(
                    chat_id,
                    rendered,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.error(e)
