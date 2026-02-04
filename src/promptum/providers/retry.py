from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum


class RetryStrategy(Enum):
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_DELAY = "fixed_delay"


@dataclass(frozen=True, slots=True)
class RetryConfig:
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    retryable_status_codes: Sequence[int] = (429, 500, 502, 503, 504)
    timeout: float = 60.0
