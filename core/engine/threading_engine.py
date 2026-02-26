from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor


class ThreadingEngine:
    def __init__(self, workers: int):
        self.workers = max(1, workers)

    def map(self, func: Callable, items: Iterable):
        values = list(items)
        if not values:
            return []
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            return list(executor.map(func, values))
