from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Metrics:
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None
    retry_delays: Sequence[float] = ()

    @property
    def total_attempts(self) -> int:
        return len(self.retry_delays) + 1
