from . import auth, category, blacklist
from .menu import router

router.include_routers(auth.router, category.router, blacklist.router)
