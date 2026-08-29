import asyncio

import pytest

from core.events import message_queue


def test_message_queue_is_an_asyncio_queue():
    assert isinstance(message_queue, asyncio.Queue)


@pytest.mark.asyncio
async def test_message_queue_put_get_round_trip_and_fifo_order():
    item1 = ("Alice", 1, 10, None, "hello")
    item2 = ("Bob", 1, 11, None, "world")

    await message_queue.put(item1)
    await message_queue.put(item2)

    assert message_queue.qsize() == 2
    first = await message_queue.get()
    second = await message_queue.get()

    assert first == item1
    assert second == item2
    assert message_queue.empty()
