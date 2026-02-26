import asyncio
from collections.abc import Callable, Iterable


class AsyncEngine:
    def __init__(self, workers: int):
        self.workers = max(1, workers)

    async def _map_async(self, func: Callable, values: list):
        semaphore = asyncio.Semaphore(self.workers)

        async def wrapped(item):
            async with semaphore:
                return await asyncio.to_thread(func, item)

        tasks = [wrapped(item) for item in values]
        return await asyncio.gather(*tasks)

    def map(self, func: Callable, items: Iterable):
        values = list(items)
        if not values:
            return []
        try:
            return asyncio.run(self._map_async(func, values))
        except RuntimeError:
            # Fallback for environments where an event loop is already running.
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self._map_async(func, values))
            finally:
                loop.close()
