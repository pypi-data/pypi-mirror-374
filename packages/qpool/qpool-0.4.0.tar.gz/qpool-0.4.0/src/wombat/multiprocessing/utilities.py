from __future__ import annotations

import asyncio
from queue import Empty
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wombat.multiprocessing.queues import ModelQueue


def is_async_context_manager(obj):
    return hasattr(obj, "__aenter__") and hasattr(obj, "__aexit__")

def is_sync_context_manager(obj):
    return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")


async def queue_get_async(
    loop: asyncio.AbstractEventLoop, queue: "ModelQueue"
) -> object:
    """
    Asynchronously gets an item from a multiprocessing.Queue by running the
    blocking get() in a thread with a timeout. This prevents the worker from
    hanging on shutdown.
    """
    while True:
        try:
            # Use a timeout to prevent the thread from blocking indefinitely.
            return await loop.run_in_executor(None, queue.get, True, 1.0)
        except Empty:
            # Timeout occurred. Yield control to the event loop to allow
            # other tasks (like shutdown) to run. This also allows the
            # task to be cancelled here if needed.
            await asyncio.sleep(0)
