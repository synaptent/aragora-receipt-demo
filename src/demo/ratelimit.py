"""A small token-bucket rate limiter: the code that demo pull requests change."""

from __future__ import annotations

import time
from collections.abc import Callable


class TokenBucket:
    """Allow up to ``capacity`` requests in a burst, refilled at ``rate`` tokens per second."""

    def __init__(
        self,
        capacity: int,
        rate: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if rate <= 0:
            raise ValueError("rate must be positive")
        self.capacity = capacity
        self.rate = rate
        self._clock = clock
        self._tokens = float(capacity)
        self._updated = clock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = max(0.0, now - self._updated)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._updated = now

    def allow(self, cost: int = 1) -> bool:
        """Spend ``cost`` tokens if available and report whether the request may proceed."""
        if cost <= 0:
            raise ValueError("cost must be positive")
        if cost > self.capacity:
            raise ValueError("cost exceeds bucket capacity and can never be satisfied")
        self._refill()
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False
