import pytest

from kwork_parser_bot.services.kwork.api.types import Actor
from kwork_parser_bot.services.kwork.kwork import KworkApi
from kwork_parser_bot.services.kwork.schemas import KworkAccount
from kwork_parser_bot.services.kwork.session import get_kwork_api


@pytest.mark.asyncio
async def test_kwork_api(kwork_account: KworkAccount):
    async with get_kwork_api(kwork_account) as api:
        api: KworkApi
        me = await api.get_me()
        assert me and isinstance(me, Actor)
