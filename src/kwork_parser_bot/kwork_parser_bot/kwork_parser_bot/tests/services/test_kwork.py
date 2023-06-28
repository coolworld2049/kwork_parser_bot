import pytest

from kwork_parser_bot.services.kwork.schemas import KworkAccount
from kwork_parser_bot.services.kwork.kwork import get_kwork_api


@pytest.mark.asyncio
async def test_kwork_api(event_loop, kwork_account: KworkAccount):
    async with get_kwork_api(kwork_account) as api:
        assert api
