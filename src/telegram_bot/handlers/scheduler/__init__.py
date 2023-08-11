from . import add_job, remove_job
from .menu import router

router.include_routers(add_job.router, remove_job.router)
