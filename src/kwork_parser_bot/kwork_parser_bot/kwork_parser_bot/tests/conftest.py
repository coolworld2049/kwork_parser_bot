import asyncio

import pytest


@pytest.fixture()
def event_loop():
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()
