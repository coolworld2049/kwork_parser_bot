import asyncio
from datetime import timedelta

import pytest
from kwork.types import Actor

from kwork_parser_bot.services.kwork.base_class import KworkCreds, KworkApi
from kwork_parser_bot.services.kwork.lifetime import get_kwork_api


@pytest.mark.asyncio
async def test_kwork_creds(kwork_creds: KworkCreds):
    user_id = 1111
    data = KworkCreds(login="user", password="1234", phone="+11111111111")
    expiration = timedelta(seconds=4)
    await kwork_creds.set_cache(user_id, data.dict(), expiration)
    cached_data = await kwork_creds.get_cached(user_id)
    assert cached_data == data
    await asyncio.sleep(4)
    cached_data = await kwork_creds.get_cached(user_id)
    assert not cached_data


@pytest.mark.asyncio
async def test_kwork_api(kwork_creds: KworkCreds):
    async with get_kwork_api(kwork_creds) as api:
        api: KworkApi
        me = await api.get_me()
        assert me and isinstance(me, Actor)
