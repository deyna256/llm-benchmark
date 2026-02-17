from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Summary:
    total: int
    passed: int
    failed: int
    pass_rate: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    total_cost_usd: float
    total_tokens: int
    execution_errors: int
    validation_failures: int
