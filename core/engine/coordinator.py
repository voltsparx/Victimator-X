from collections.abc import Callable, Iterable
from logging import Logger

from .async_engine import AsyncEngine
from .parallel_engine import ParallelEngine
from .threading_engine import ThreadingEngine


class EngineCoordinator:
    def __init__(self, mode: str, workers: int, logger: Logger | None = None):
        self.requested_mode = mode
        self.workers = max(1, workers)
        self.logger = logger
        self.last_mode = mode

    def _resolve_mode(self, item_count: int) -> str:
        if self.requested_mode != "auto":
            return self.requested_mode
        if item_count > 15000:
            return "parallel"
        if item_count > 2000:
            return "threading"
        return "async"

    def _engine_for_mode(self, mode: str):
        if mode == "threading":
            return ThreadingEngine(self.workers)
        if mode == "async":
            return AsyncEngine(self.workers)
        if mode == "parallel":
            return ParallelEngine(self.workers)
        raise ValueError(f"Unknown engine mode: {mode}")

    def map(self, func: Callable, items: Iterable):
        values = list(items)
        if not values:
            self.last_mode = "none"
            return []

        mode = self._resolve_mode(len(values))
        self.last_mode = mode
        engine = self._engine_for_mode(mode)
        try:
            return engine.map(func, values)
        except Exception as error:
            if self.logger:
                self.logger.warning(
                    "Engine '%s' failed (%s). Falling back to threading.",
                    mode,
                    error,
                )
            self.last_mode = "threading-fallback"
            fallback = ThreadingEngine(self.workers)
            return fallback.map(func, values)
