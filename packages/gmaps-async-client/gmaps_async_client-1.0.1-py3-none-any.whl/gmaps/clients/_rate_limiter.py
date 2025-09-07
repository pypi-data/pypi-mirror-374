import asyncio
import time
from collections import deque
from typing import Optional


class AsyncRateLimiter:
    """
    Async sliding-window QPM limiter. Ensures at most `qpm` acquisitions per rolling 60s window.

    Implementation detail: loop-based wait (no recursion) to prevent stack growth under load.
    """

    def __init__(self, qpm: Optional[int]) -> None:
        self.qpm = qpm
        self._lock = asyncio.Lock()
        self._hits: deque[float] = deque()

    async def acquire(self) -> None:
        if self.qpm is None or self.qpm <= 0:
            return  # disabled
        window = 60.0
        while True:
            now = time.monotonic()
            async with self._lock:
                # Drop old timestamps
                while self._hits and (now - self._hits[0]) >= window:
                    self._hits.popleft()
                if len(self._hits) < self.qpm:
                    self._hits.append(now)
                    return
                wait_for = window - (now - self._hits[0])
            await asyncio.sleep(wait_for)
